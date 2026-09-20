"""
tests/test_gate3_code_acceptance.py
===================================

Purpose:
    Failing-first acceptance tests for the hardening of Gate 3 (auth-ciba-increment-b, human decision 2026-09-20):
    BOTH edges into VERIFY_EXIT -- WORKTREE_REVIEW -> VERIFY_EXIT (direct code acceptance) and
    MULTI_AGENT_CODE_REVIEW -> VERIFY_EXIT (post-review code acceptance) -- are the moment human authority
    accepts the agent's code into the release pipeline, so they need the same cryptographic proof as Gate 1: the
    coordinator halts with HUMAN_PROOF_REQUIRED and a request_id, the challenge binds the task, the edge, the
    commit SHA, the diff hash and the untracked-file hash (a plain `git diff` would miss new files), and only a
    verified `ssh-keygen -Y sign` signature consumed in the commit transaction advances the state. The soft
    `--skip-review` / `--skip-reason` flags are gone. Real git repository, real SQLite, real ssh-keygen; the
    identity is injected, nothing is mocked.

Key Input Dependencies:
    - control_plane/proof_edges.py, snapshot.py (code_acceptance_snapshot), ssh_signing.py (EDGE_ASSERTIONS),
      coordinator.py (HumanProofRequired), adapters.py, gate1_approval.py, transition_templates.yaml, agent_control.py
    - tests/helpers/gate1_fixtures.py, tests/test_approve_transition.py (key helpers)

Key Functions (test cases):
    - test_both_edges_halt_for_a_signature_and_change_nothing
    - test_challenge_binds_head_diff_and_untracked
    - test_a_valid_signature_commits_verify_exit (both edges)
    - test_a_changed_tracked_file_or_new_untracked_file_refuses_and_audits
    - test_a_forged_signature_refuses_and_audits
    - test_staged_human_decisions_are_refused_without_a_proof
    - test_skip_flags_are_gone_and_skip_is_refused_on_proof_edges
    - test_registry_has_no_skip_semantics_on_the_gate3_edges
"""

import io
import os
import pwd
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

import agent_control
from control_plane.coordinator import HumanProofRequired, TransitionCoordinator, TransitionCoordinatorError
from control_plane.gate1_approval import GateApprovalError, approve_transition, show_challenge
from control_plane.identity_layout import default_layout
from control_plane.ports import PersistenceInvariantViolation, TransitionCommitRequest, TransitionDecision
from control_plane.registry import TransitionRegistry
from control_plane.ssh_signing import SIGN_NAMESPACE
from helpers.gate1_fixtures import init_git_worktree, reach_multi_agent_code_review, reach_worktree_review

TASK = "gate3-task-001"
DIRECT = ("WORKTREE_REVIEW", "VERIFY_EXIT")
POST_REVIEW = ("MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT")
_FOUND = shutil.which("ssh-keygen")
SSH_KEYGEN = _FOUND or "ssh-keygen"
pytestmark = [pytest.mark.no_auto_signer, pytest.mark.skipif(_FOUND is None or shutil.which("git") is None, reason="ssh-keygen and git are required")]


def _other_uid() -> int:
    for name in ("nobody", "daemon"):
        try:
            uid = pwd.getpwnam(name).pw_uid
            if uid != os.geteuid():
                return uid
        except KeyError:
            continue
    return os.geteuid() + 4242


class CodeGate:
    """A task sitting at WORKTREE_REVIEW (or MULTI_AGENT_CODE_REVIEW) with a real git worktree and a real key."""

    def __init__(self, tmp_path: Path, edge):
        self.tmp = tmp_path.resolve()
        self.edge = edge
        self.worktree = init_git_worktree(self.tmp / "worktree")
        self.sim = reach_worktree_review(self.tmp, TASK, self.worktree)
        if edge == POST_REVIEW:
            reach_multi_agent_code_review(self.sim, TASK)
        self.cp = self.sim.control_plane
        self.repo = Path(self.cp.repo_root)
        (self.worktree / "module.py").write_text("VALUE = 2\n")  # the agent's uncommitted work
        (self.worktree / "new_file.py").write_text("NEW = 1\n")  # and a brand-new untracked file
        self.layout = default_layout(self.repo)
        for d in (self.layout.root, self.layout.challenge_dir):
            d.mkdir(parents=True, exist_ok=True)
            os.chmod(d, 0o700)
        keys = self.tmp / "keys"
        keys.mkdir()
        self.key = keys / "id"
        self.keygen(self.key)
        pub = (keys / "id.pub").read_text().split()
        self.layout.allowed_signers.write_text(f'op@local namespaces="{SIGN_NAMESPACE}" {pub[0]} {pub[1]}\n')
        self.layout.allowed_signers_selftest.write_text(f'op@local namespaces="control-plane-selftest@agentic-os.local" {pub[0]} {pub[1]}\n')
        for f in (self.layout.allowed_signers, self.layout.allowed_signers_selftest):
            os.chmod(f, 0o600)
        self.identity = {"agent_name": "agentic-os-local-agent", "agent_uid": _other_uid(), "agent_gids": set()}

    @staticmethod
    def keygen(path: Path) -> None:
        subprocess.run([SSH_KEYGEN, "-q", "-t", "ed25519", "-N", "", "-C", "op", "-f", str(path)], check=True, capture_output=True)

    def coordinator(self):
        return TransitionCoordinator(
            self.cp, registry=self.sim.registry, output_stream=io.StringIO(),
        )

    def request(self) -> int:
        with pytest.raises(HumanProofRequired) as excinfo:
            self.coordinator().coordinate_transition(task_id=TASK, to_state="VERIFY_EXIT", actor="agent", reason="request", interactive=False)
        self.request_id = excinfo.value.remediation["request_id"]
        return self.request_id

    def show(self):
        out = io.StringIO()
        path = show_challenge(self.cp, self.request_id, layout=self.layout, key_hint=str(self.key), agent_identity=self.identity, out=out)
        return path, out.getvalue()

    def sign(self, path: Path, key: Path = None) -> None:
        sig = Path(str(path) + ".sig")
        if sig.exists():
            sig.unlink()
        subprocess.run([SSH_KEYGEN, "-Y", "sign", "-f", str(key or self.key), "-n", SIGN_NAMESPACE, str(path)], check=True, capture_output=True)

    def approve(self):
        return approve_transition(self.cp, self.request_id, layout=self.layout, principal="op@local", agent_identity=self.identity, out=io.StringIO())

    def db(self):
        return sqlite3.connect(self.cp.db_path)

    def state(self):
        return self.db().execute("SELECT state FROM tasks WHERE task_id = ?", (TASK,)).fetchone()[0]

    def violations(self):
        return self.db().execute("SELECT kind, detail FROM transition_violations WHERE task_id = ?", (TASK,)).fetchall()


@pytest.fixture(params=[DIRECT, POST_REVIEW], ids=["direct", "post-review"])
def gate(request, tmp_path):
    return CodeGate(tmp_path, request.param)


def test_both_edges_halt_for_a_signature_and_change_nothing(gate):
    with pytest.raises(HumanProofRequired) as excinfo:
        gate.coordinator().coordinate_transition(task_id=TASK, to_state="VERIFY_EXIT", actor="agent", reason="try", interactive=False)
    assert excinfo.value.remediation["request_id"]
    assert "HUMAN_PROOF_REQUIRED" in str(excinfo.value)
    assert gate.state() == gate.edge[0]
    assert gate.db().execute("SELECT COUNT(*) FROM transition_decisions WHERE task_id = ? AND to_state = 'VERIFY_EXIT'", (TASK,)).fetchone()[0] == 0


def test_challenge_binds_head_diff_and_untracked(gate):
    gate.request()
    path, printed = gate.show()
    head = subprocess.run(["git", "-C", str(gate.worktree), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    assert head in printed and "tracked_diff:" in printed and "untracked:" in printed
    assert f"transition: {gate.edge[0]} -> VERIFY_EXIT" in printed and f"task: {TASK}" in printed
    assert "nonce:" in printed and "expires:" in printed


def test_a_valid_signature_commits_verify_exit(gate):
    gate.request()
    path, _ = gate.show()
    gate.sign(path)
    record = gate.approve()
    assert record.to_state == "VERIFY_EXIT" and gate.state() == "VERIFY_EXIT"
    assert gate.db().execute("SELECT status FROM transition_request WHERE request_id = ?", (gate.request_id,)).fetchone()[0] == "CONSUMED"
    # no decision rows, no actor strings: the consumed, signature-verified request is the authority
    assert gate.db().execute("SELECT COUNT(*) FROM transition_decisions WHERE task_id = ? AND to_state = 'VERIFY_EXIT'", (TASK,)).fetchone()[0] == 0


@pytest.mark.parametrize("tamper", ["tracked", "untracked-new", "untracked-edit"])
def test_a_changed_tracked_file_or_new_untracked_file_refuses_and_audits(gate, tamper):
    gate.request()
    path, _ = gate.show()
    gate.sign(path)
    if tamper == "tracked":
        (gate.worktree / "module.py").write_text("VALUE = 3\n")
    elif tamper == "untracked-new":
        (gate.worktree / "sneaky.py").write_text("import os\n")
    else:
        (gate.worktree / "new_file.py").write_text("NEW = 999\n")
    with pytest.raises(GateApprovalError):
        gate.approve()
    assert gate.state() == gate.edge[0]
    assert gate.violations(), "the refused attempt must leave an audit row"
    assert {v[0] for v in gate.violations()} == {"REJECTED_ATTEMPT"}


def test_a_forged_signature_refuses_and_audits(gate, tmp_path):
    attacker = tmp_path / "attacker"
    attacker.mkdir()
    CodeGate.keygen(attacker / "id")
    gate.request()
    path, _ = gate.show()
    gate.sign(path, key=attacker / "id")
    with pytest.raises(GateApprovalError):
        gate.approve()
    assert gate.state() == gate.edge[0] and gate.violations()


def test_staged_human_decisions_are_refused_without_a_proof(gate):
    """No soft `actor='human'` decision rows: the commit path itself refuses them on a proof edge."""
    conn = gate.db()
    occupancy = conn.execute("SELECT MAX(transition_id) FROM task_transitions WHERE task_id = ?", (TASK,)).fetchone()[0]
    template = gate.sim.registry.get_template(*gate.edge[:1], "VERIFY_EXIT")
    decisions = [
        TransitionDecision(
            task_id=TASK, source_occupancy_transition_id=occupancy, from_state=gate.edge[0], to_state="VERIFY_EXIT",
            question_id=q["question_id"], answer=q["accepted_answers"][0], decision_type="ANSWER", actor="human", recorded_at=1.0,
        )
        for q in template.human_questions
    ]
    request = TransitionCommitRequest(
        task_id=TASK, expected_from_state=gate.edge[0], to_state="VERIFY_EXIT", source_occupancy_transition_id=occupancy,
        template_id=template.transition_id, actor="human", reason="soft", staged_decisions=decisions, staged_receipts=[],
    )
    with pytest.raises(PersistenceInvariantViolation):
        gate.cp._persistence.apply_transition_with_receipts(request)
    assert gate.state() == gate.edge[0]


def test_skip_flags_are_gone_and_skip_is_refused_on_proof_edges(gate):
    parser = agent_control._build_parser()
    for verb in ("coordinate-transition", "transition"):
        with pytest.raises(SystemExit):
            parser.parse_args([verb, "--task-id", TASK, "--to", "VERIFY_EXIT", "--skip-review", "--skip-reason", "x", "--human-confirmed", "HUMAN-CONFIRMED: x"])
    with pytest.raises((TransitionCoordinatorError, HumanProofRequired)):
        gate.coordinator().coordinate_transition(
            task_id=TASK, to_state="VERIFY_EXIT", actor="human", reason="skip", interactive=True, skip_review=True, skip_reason="x",
        )
    assert gate.state() == gate.edge[0]


def test_registry_has_no_skip_semantics_on_the_gate3_edges():
    registry = TransitionRegistry.load_default()
    for edge in (DIRECT, POST_REVIEW):
        template = registry.get_template(*edge)
        assert template.requires_cryptographic_proof is True
        assert template.skip.get("allowed") is False
        assert "code_review_or_skip" not in template.deterministic_checks
        assert template.human_questions == []
        assert "skip" not in template.next_steps_hint.lower(), edge


def _write_lock_is_free(db_path) -> bool:
    """True if another connection can take the write lock right now (0.3s budget)."""
    probe = sqlite3.connect(db_path, timeout=0.3, isolation_level=None)
    try:
        probe.execute("BEGIN IMMEDIATE;")
        probe.execute("ROLLBACK;")
        return True
    except sqlite3.OperationalError:
        return False
    finally:
        probe.close()


def test_no_write_lock_is_held_during_snapshot_or_signature_verification(gate, monkeypatch):
    """The commit's BEGIN IMMEDIATE must not span external work (git snapshot hashing, the
    `ssh-keygen -Y verify` subprocess): both run BEFORE the write lock is taken, or a concurrent
    writer gets `database is locked` for the full duration of the subprocess."""
    from control_plane import gate1_approval, transition_request

    observed = {"snapshot": [], "verify": []}
    real_snapshot, real_verify = gate1_approval.snapshot_for_edge, transition_request.verify_signature

    def snapshot_probe(*args, **kwargs):
        observed["snapshot"].append(_write_lock_is_free(gate.cp.db_path))
        return real_snapshot(*args, **kwargs)

    def verify_probe(*args, **kwargs):
        observed["verify"].append(_write_lock_is_free(gate.cp.db_path))
        return real_verify(*args, **kwargs)

    monkeypatch.setattr(gate1_approval, "snapshot_for_edge", snapshot_probe)
    monkeypatch.setattr(transition_request, "verify_signature", verify_probe)

    gate.request()
    path, _ = gate.show()
    gate.sign(path)
    observed["snapshot"].clear()  # show/challenge-time snapshots are not under test
    gate.approve()

    assert gate.state() == "VERIFY_EXIT"
    assert observed["verify"] and all(observed["verify"]), f"write lock held during ssh-keygen verify: {observed['verify']}"
    assert observed["snapshot"] and all(observed["snapshot"]), f"write lock held during live snapshot: {observed['snapshot']}"
