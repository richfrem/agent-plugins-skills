"""
tests/test_round3_fixes.py
==========================

Purpose:
    Failing-first tests for the confirmed round-3 review findings (auth-ciba-increment-b, #639):
    A1 `invalidate-receipt` and `record-review-skip` must be routed and refuse (not silently exit 0) without a
    terminal; S2 Gate 1 rejections raised as signing/request/snapshot errors must leave a `transition_violations`
    audit row; S1 the human-only receipt verbs refuse to run as the agent account; S4 verification tries every
    matching principal, not just the first. Real SQLite, real ssh-keygen; the terminal/identity is injected.

Key Input Dependencies:
    - agent_control.py (_dispatch_command, _build_parser), control_plane/receipt_provenance.py,
      control_plane/adapters.py, control_plane/ssh_signing.py; tests/test_approve_transition.py (Gate fixture)

Key Functions (test cases):
    - test_invalidate_receipt_is_routed_and_refuses_without_a_terminal
    - test_record_review_skip_is_routed_and_refuses_without_a_terminal
    - test_a_bad_gate1_signature_leaves_a_violation_row
    - test_human_only_receipt_verbs_refuse_the_agent_account
    - test_verification_tries_every_matching_principal
"""

import os
import sqlite3
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

import agent_control
from control_plane.receipt_provenance import ReceiptError, invalidate_receipt, record_human_skip
from control_plane.ssh_signing import SIGN_NAMESPACE, verify_signature
from test_approve_transition import TASK as GATE_TASK, Gate, GateApprovalError
from helpers.gate1_fixtures import reach_awaiting_approval

_FOUND = shutil.which("ssh-keygen")
SSH_KEYGEN = _FOUND or "ssh-keygen"
pytestmark = pytest.mark.skipif(_FOUND is None, reason="ssh-keygen not installed")


@pytest.fixture
def cp(tmp_path):
    return reach_awaiting_approval(tmp_path, "round3-task-001").control_plane


def _run_verb(cp, *argv):
    args = agent_control._build_parser().parse_args(list(argv))
    agent_control._dispatch_command(cp, args)


def test_invalidate_receipt_is_routed_and_refuses_without_a_terminal(cp):
    cp.record_review_skip("round3-task-001", "multi_agent_review", "agent", "x")
    with pytest.raises(SystemExit) as excinfo:  # stdin is not a terminal under pytest
        _run_verb(cp, "invalidate-receipt", "--receipt-id", "1", "--reason", "forged")
    assert "REFUSED" in str(excinfo.value) and "terminal" in str(excinfo.value).lower()
    assert cp._persistence.has_receipt("round3-task-001", "multi_agent_review_skipped")


def test_record_review_skip_is_routed_and_refuses_without_a_terminal(cp):
    with pytest.raises(SystemExit) as excinfo:
        _run_verb(cp, "record-review-skip", "--task-id", "round3-task-001", "--phase", "multi_agent_review", "--reason", "x", "--interactive")
    assert "REFUSED" in str(excinfo.value)
    assert not cp._persistence.has_receipt("round3-task-001", "multi_agent_review_skipped")


def test_a_bad_gate1_signature_leaves_a_violation_row(tmp_path):
    gate = Gate(tmp_path)
    attacker = tmp_path / "attacker"
    attacker.mkdir()
    Gate._keygen(attacker / "id")
    path, _ = gate.show()
    gate.sign(path, key=attacker / "id")
    with pytest.raises(GateApprovalError):
        gate.approve()
    rows = gate.db().execute(
        "SELECT attempted_from_state, attempted_to_state, detail FROM transition_violations WHERE task_id = ?", (GATE_TASK,)
    ).fetchall()
    assert rows and rows[-1][0] == "AWAITING_APPROVAL" and rows[-1][1] == "APPROVED"
    assert gate.state() == "AWAITING_APPROVAL"


def test_human_only_receipt_verbs_refuse_the_agent_account(cp):
    kwargs = dict(tty_fn=lambda: True, input_fn=lambda _p: "multi_agent_review", out=lambda *_: None, agent_uid=os.geteuid())
    with pytest.raises(ReceiptError) as excinfo:
        record_human_skip(cp, "round3-task-001", "multi_agent_review", "x", **kwargs)
    assert "agent" in str(excinfo.value).lower()
    with pytest.raises(ReceiptError):
        invalidate_receipt(cp, 1, "x", **kwargs)
    assert not cp._persistence.has_receipt("round3-task-001", "multi_agent_review_skipped")


def test_verification_tries_every_matching_principal(tmp_path):
    key = tmp_path / "id"
    subprocess.run([SSH_KEYGEN, "-q", "-t", "ed25519", "-N", "", "-C", "t", "-f", str(key)], check=True, capture_output=True)
    pub = (tmp_path / "id.pub").read_text().split()
    allowed = tmp_path / "allowed_signers"
    allowed.write_text(
        f'alpha@x namespaces="other-app@example.org" {pub[0]} {pub[1]}\n'
        f'op@local namespaces="{SIGN_NAMESPACE}" {pub[0]} {pub[1]}\n'
    )
    os.chmod(allowed, 0o600)
    data = tmp_path / "challenge"
    data.write_bytes(b"challenge bytes")
    subprocess.run([SSH_KEYGEN, "-Y", "sign", "-f", str(key), "-n", SIGN_NAMESPACE, str(data)], check=True, capture_output=True)
    verified = verify_signature(b"challenge bytes", Path(str(data) + ".sig").read_bytes(), allowed_signers=allowed)
    assert verified.principal == "op@local"


# ---- Round 4 findings (N1, N2) --------------------------------------------------------------------------
def test_a_rejected_attempt_does_not_block_a_later_valid_commit_check(tmp_path):
    """N1: a failed Gate 1 attempt is kept for audit but must not poison pipeline-history validation."""
    gate = Gate(tmp_path)
    attacker = tmp_path / "attacker"
    attacker.mkdir()
    Gate._keygen(attacker / "id")
    path, _ = gate.show()
    gate.sign(path, key=attacker / "id")
    with pytest.raises(GateApprovalError):
        gate.approve()
    kinds = [r[0] for r in gate.db().execute("SELECT kind FROM transition_violations WHERE task_id = ?", (GATE_TASK,))]
    assert kinds == ["REJECTED_ATTEMPT"]  # history is kept
    Path(str(path) + ".sig").unlink()  # ssh-keygen will not overwrite the earlier signature file
    gate.sign(path)  # the human retries with the right key
    gate.approve()
    verdict = gate.cp._persistence.validate_task_pipeline_history(GATE_TASK, "APPROVED")
    assert verdict is None or "violation" not in verdict.lower(), verdict


def test_a_trigger_recorded_illegal_transition_still_blocks(tmp_path):
    """N1: rows written by the enforce_valid_transition trigger keep blocking commit validation."""
    from test_review_selection import TASK, _plan_review_task

    sim = _plan_review_task(tmp_path)
    with pytest.raises(Exception):
        sim.control_plane.transition(TASK, "MULTI_AGENT_REVIEW", "tester", "no decisions")  # trigger rejects
    kinds = [r[0] for r in sqlite3.connect(sim.control_plane.db_path).execute("SELECT kind FROM transition_violations WHERE task_id = ?", (TASK,))]
    assert kinds == ["ILLEGAL_TRANSITION"]
    assert "violation" in (sim.control_plane._persistence.validate_task_pipeline_history(TASK, "PLAN_REVIEW") or "").lower()


def test_principal_lists_are_split_into_individual_identities(tmp_path):
    """N2: `alice@x,bob@x` in allowed_signers must be tried as alice@x and bob@x, not as one identity."""
    key = tmp_path / "id"
    subprocess.run([SSH_KEYGEN, "-q", "-t", "ed25519", "-N", "", "-C", "t", "-f", str(key)], check=True, capture_output=True)
    pub = (tmp_path / "id.pub").read_text().split()
    allowed = tmp_path / "allowed_signers"
    allowed.write_text(
        f'other@x namespaces="other-app@example.org" {pub[0]} {pub[1]}\n'
        f'alice@x,bob@x namespaces="{SIGN_NAMESPACE}" {pub[0]} {pub[1]}\n'
    )
    os.chmod(allowed, 0o600)
    data = tmp_path / "challenge"
    data.write_bytes(b"challenge bytes")
    subprocess.run([SSH_KEYGEN, "-Y", "sign", "-f", str(key), "-n", SIGN_NAMESPACE, str(data)], check=True, capture_output=True)
    verified = verify_signature(b"challenge bytes", Path(str(data) + ".sig").read_bytes(), allowed_signers=allowed)
    assert verified.principal in ("alice@x", "bob@x")


def test_a_refused_signature_tells_the_human_to_delete_the_old_signature_file(tmp_path):
    """After a failed approval ssh-keygen will not overwrite the earlier .sig; the refusal must say how to retry."""
    gate = Gate(tmp_path)
    attacker = tmp_path / "attacker"
    attacker.mkdir()
    Gate._keygen(attacker / "id")
    path, _ = gate.show()
    gate.sign(path, key=attacker / "id")
    with pytest.raises(GateApprovalError) as excinfo:
        gate.approve()
    assert "delete" in str(excinfo.value).lower() and ".sig" in str(excinfo.value)
