"""
tests/test_legacy_input_fallback.py
===================================

Purpose:
    Acceptance tests for the proof policy (auth-ciba-increment-b, issue #639). Originally T10 (human decisions
    D1/D5): strict-by-default plus an audited, off-by-default `legacy_input` fallback. On 2026-09-20 the human
    REMOVED the fallback, so these tests now assert that STRICT is the only answer for every input -- including a
    policy file that explicitly requests `legacy_input` -- and that the removed mode leaves a diagnostic reason.
    (Historical description of the original scope follows.) `context/isolation-policy.json` selects the mode;
    a missing/invalid/symlinked policy means strict; the policy is honored only if the
    agent identity cannot write it (downgrade resistance); in an unprovisioned
    same-account setup the fallback is the honestly-labelled unhardened posture.
    The adapter accepts a legacy proof only when the coordinator vouches for the policy
    and records an audit receipt (`proof=input_unhardened` / `proof=sshsig`).
    Real files and modes in tmp_path, real SQLite; identity injected, nothing mocked.
    The coordinator/TTY behavior of legacy mode is tested with T7 in
    test_human_only_wiring.py.

Key Input Dependencies:
    - control_plane/proof_policy.py (load_proof_policy, ProofPolicy)
    - control_plane/ports.py (AuthorizationProof.legacy_policy_ok)
    - control_plane/adapters.py (audit receipt on Gate 1 commit)

Key Functions (test cases):
    - test_missing_policy_is_strict / test_invalid_policy_is_strict / test_unknown_mode_is_strict
    - test_symlinked_policy_is_strict
    - test_legacy_honored_when_identity_is_unprovisioned
    - test_legacy_honored_when_policy_is_protected_from_the_agent
    - test_policy_writable_by_agent_is_ignored (downgrade resistance)
    - test_policy_owned_by_agent_is_ignored
    - test_explicit_strict_stays_strict
"""

import json
import os
import pwd
import sys
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from control_plane.proof_policy import STRICT, ProofPolicy, load_proof_policy


def _other_uid() -> int:
    for name in ("nobody", "daemon"):
        try:
            uid = pwd.getpwnam(name).pw_uid
            if uid != os.geteuid():
                return uid
        except KeyError:
            continue
    return os.geteuid() + 4242


@pytest.fixture
def policy_file(tmp_path):
    folder = tmp_path / "context"
    folder.mkdir()
    os.chmod(folder, 0o700)
    path = folder / "isolation-policy.json"
    path.write_text(json.dumps({"human_only_proof": "legacy_input"}))
    os.chmod(path, 0o600)
    return path


def _load(path, **over):
    kwargs = dict(agent_name="no-such-account-xyz-123", agent_uid=None, agent_gids=set())
    kwargs.update(over)
    return load_proof_policy(path, **kwargs)


def test_missing_policy_is_strict(tmp_path):
    policy = _load(tmp_path / "context" / "isolation-policy.json")
    assert isinstance(policy, ProofPolicy)
    assert policy.mode == STRICT and policy.reason


@pytest.mark.parametrize("content", ["not json", "[]", '{"human_only_proof": 5}', "{}", ""])
def test_invalid_policy_is_strict(policy_file, content):
    policy_file.write_text(content)
    assert _load(policy_file).mode == STRICT


def test_unknown_mode_is_strict(policy_file):
    policy_file.write_text(json.dumps({"human_only_proof": "trust_me"}))
    assert _load(policy_file).mode == STRICT


def test_symlinked_policy_is_strict(policy_file, tmp_path):
    real = tmp_path / "elsewhere.json"
    real.write_text(json.dumps({"human_only_proof": "legacy_input"}))
    os.chmod(real, 0o600)
    policy_file.unlink()
    policy_file.symlink_to(real)
    assert _load(policy_file).mode == STRICT


def test_explicit_strict_stays_strict(policy_file):
    policy_file.write_text(json.dumps({"human_only_proof": "strict"}))
    assert _load(policy_file).mode == STRICT


def test_a_policy_requesting_legacy_input_is_ignored_and_named_when_identity_is_unprovisioned(policy_file):
    """The audited legacy_input fallback was REMOVED (2026-09-20). A policy file that still asks for it is not
    honored -- not even in the same-account/unprovisioned setup where it used to be the labelled weak posture."""
    policy = _load(policy_file)
    assert policy.mode == STRICT
    assert "legacy_input" in policy.reason and "removed" in policy.reason.lower()


def test_a_policy_requesting_legacy_input_is_ignored_when_it_is_protected_from_the_agent(policy_file):
    """Even a well-protected policy (owned by another uid, mode 0600) cannot re-enable the removed mode."""
    policy = _load(policy_file, agent_name="agentic-os-local-agent", agent_uid=_other_uid())
    assert policy.mode == STRICT
    assert "removed" in policy.reason.lower()


@pytest.mark.parametrize("mode", [0o666, 0o664, 0o646])
def test_policy_writable_by_agent_is_ignored(policy_file, mode):
    """Downgrade resistance is now trivially total: whatever the file's permissions, the answer is STRICT."""
    os.chmod(policy_file, mode)
    policy = _load(policy_file, agent_name="agentic-os-local-agent", agent_uid=_other_uid())
    assert policy.mode == STRICT


def test_policy_owned_by_agent_is_ignored(policy_file):
    """Files here are owned by the current user; declare that uid to be the agent."""
    policy = _load(policy_file, agent_name="agentic-os-local-agent", agent_uid=os.geteuid(), euid=os.geteuid() + 1)
    assert policy.mode == STRICT


def test_policy_in_agent_writable_directory_is_ignored(policy_file):
    os.chmod(policy_file.parent, 0o777)
    try:
        policy = _load(policy_file, agent_name="agentic-os-local-agent", agent_uid=_other_uid())
    finally:
        os.chmod(policy_file.parent, 0o700)
    assert policy.mode == STRICT


def test_the_removed_legacy_mode_constant_no_longer_exists():
    """Nothing can import a LEGACY_INPUT mode any more: the fallback is gone, not merely defaulted off."""
    import control_plane.proof_policy as proof_policy

    assert not hasattr(proof_policy, "LEGACY_INPUT")
