"""
tests/conftest.py
=================

Purpose:
    Shared pytest configuration for the agent-agentic-os tests (auth-ciba-increment-b, T7).

    Gate 1 (AWAITING_APPROVAL -> APPROVED) is strict-by-default: the coordinator refuses to let a
    prompt authorize it and returns a structured remediation instead. The many pre-existing suites
    that walk a task through the pipeline to APPROVED with scripted answers predate that, and they
    still need to exercise the interactive flow. The autouse `_auto_human_signer` fixture below gives every
    coordinator a REAL test signer (throwaway key, real ssh-keygen sign/verify, real request consumption);
    the removed `legacy_input` fallback no longer exists. Tests marked `no_auto_signer` drive the strict
    flow themselves. This is a documented test-only seam, not a production bypass: production code never
    imports this module.

Key Input Dependencies:
    - control_plane/coordinator.py (module-level load_proof_policy default)
    - helpers/human_signer.py (throwaway-key signer), control_plane/snapshot.py (gate1_artifact_paths)

Key Functions:
    - _legacy_default_proof_policy() -- autouse fixture (function scope)
"""

import sys
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)


def pytest_configure(config):
    config.addinivalue_line("markers", "no_auto_signer: test drives the strict proof flow itself (no automatic human signer)")


@pytest.fixture(scope="session")
def _test_human():
    from helpers.human_signer import get_test_human

    return get_test_human()


@pytest.fixture(autouse=True)
def _auto_human_signer(request, monkeypatch):
    """Test-only stand-in for the human at the three cryptographic-proof gates (APPROVED, VERIFY_EXIT, DONE).

    Production has no legacy or typed path for those edges: the coordinator halts with HUMAN_PROOF_REQUIRED unless a
    `human_signer` completes the request. This fixture gives every coordinator built in a test that signer by default,
    and it performs the REAL flow (challenge, ssh-keygen -Y sign, signature verification, request consumption) with
    a throwaway key. Tests marked `no_auto_signer` build coordinators without it and assert the halt themselves.
    ControlPlane.transition() shortcuts into a proof edge are routed through the same signed flow."""
    if request.node.get_closest_marker("no_auto_signer"):
        yield
        return
    try:
        import yaml  # noqa: F401  (the control plane loads transition_templates.yaml)
    except ImportError:
        # The evolution-guard CI job installs only pytest, and its tests never touch the control plane. Without PyYAML
        # a control-plane test would fail at its own import anyway, so do not break the unrelated ones here.
        yield
        return
    _test_human = request.getfixturevalue("_test_human")  # lazy: no throwaway key unless the control plane is in play
    from control_plane.coordinator import TransitionCoordinator
    import agent_control

    original_init = TransitionCoordinator.__init__

    def init(self, *args, human_signer=None, **kwargs):
        original_init(self, *args, human_signer=human_signer or _test_human.sign_request, **kwargs)

    monkeypatch.setattr(TransitionCoordinator, "__init__", init)

    original_create_request = TransitionCoordinator._create_proof_request

    def create_request(self, task_id, from_state, to_state, occupancy_id, repo_root):
        # Gate 1 signs the reviewed spec and plan. Pre-existing suites walk a task to APPROVED without ever
        # writing those files; the stand-in human is shown a minimal pair so their real subject (the gate
        # or hook under test) still runs. Existing files are never overwritten, and tests marked
        # `no_auto_signer` (which assert the refusal to sign missing content) do not get this seam.
        if (from_state, to_state) == ("AWAITING_APPROVAL", "APPROVED"):
            from control_plane.snapshot import gate1_artifact_paths

            for label, path in gate1_artifact_paths(repo_root, task_id):
                if not path.exists():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(f"# {label} for {task_id} (test stand-in)\n")
        return original_create_request(self, task_id, from_state, to_state, occupancy_id, repo_root)

    monkeypatch.setattr(TransitionCoordinator, "_create_proof_request", create_request)

    original_signed = TransitionCoordinator._signed_transition

    def signed_transition(self, task_id, from_state, to_state, actor, interactive):
        # Gate 3 signs the registered worktree's commit/diff/untracked hashes, so that worktree must be a real git
        # repository. Pre-existing suites register a worktree path in the tasks table without creating it; the
        # stand-in human is given a real one-commit repo there (never replacing an existing directory's contents),
        # so the gate or hook under test still runs against real hashing. `no_auto_signer` tests do not get this.
        if to_state == "VERIFY_EXIT":
            from control_plane.proof_edges import resolve_worktree
            from control_plane.snapshot import SnapshotError
            from helpers.gate1_fixtures import init_git_worktree

            try:
                worktree = resolve_worktree(self._cp, task_id, self._resolve_repo_root())
            except SnapshotError:
                worktree = None
            if worktree is not None and not (worktree / ".git").exists():
                init_git_worktree(worktree)
        return original_signed(self, task_id, from_state, to_state, actor, interactive)

    monkeypatch.setattr(TransitionCoordinator, "_signed_transition", signed_transition)

    original_transition = agent_control.ControlPlane.transition

    def transition(self, task_id, to_state, actor, reason, bypass_adjacency=False):
        current = self._read_current_state_for_update(task_id)
        if not hasattr(self, "_transition_registry"):
            from control_plane.registry import TransitionRegistry

            self._transition_registry = TransitionRegistry.load_default()
        if (current, to_state) in self._transition_registry.proof_required_edges():
            record = self.coordinate_transition(task_id=task_id, to_state=to_state, actor="human", reason=reason, interactive=True)
            return record
        return original_transition(self, task_id, to_state, actor, reason, bypass_adjacency=bypass_adjacency)

    monkeypatch.setattr(agent_control.ControlPlane, "transition", transition)
    yield


@pytest.fixture(autouse=True, scope="session")
def _no_review_menus_by_default():
    """Test-only seam: pre-existing suites type free-text runtime/model/effort answers for the internal
    review questions. Their default menu resolver returns no menu (free text), so they do not depend on
    which CLIs are installed on the machine. test_review_option_menus.py injects real fake-CLI resolvers
    through the coordinator's `review_choices_fn` parameter and covers the validation."""
    from control_plane import review_options

    # session scope: module-scoped fixtures (e.g. test_inspect_verbs.py) also walk a task through the review edge
    patch = pytest.MonkeyPatch()
    patch.setattr(review_options, "choices_for", lambda kind, runtime=None, path=None, profile_path=None: review_options.ChoiceSet([], None))
    yield
    patch.undo()
