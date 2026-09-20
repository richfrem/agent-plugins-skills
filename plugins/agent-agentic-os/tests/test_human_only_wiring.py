"""
tests/test_human_only_wiring.py
===============================

Purpose:
    Failing-first acceptance tests for Gate 1 (AWAITING_APPROVAL -> APPROVED) of
    auth-ciba-increment-b (issue #639). This file grows across tasks: T4 (this
    section) covers the atomic commit hook in
    SqlitePersistenceAdapter.apply_transition_with_receipts and the invalidation of
    stale PENDING requests on every occupancy-exit path; T6/T7 add the approve
    command, the request phase, the remediation error and the prerequisite-denial
    tests. Spec section 4 cases 2, 3, 5, 21 and 22.
    Real disposable SQLite databases, the real ssh-keygen with throwaway keys, and
    a real temporary trigger for crash injection; nothing is mocked.

Key Input Dependencies:
    - control_plane/adapters.py (apply_transition_with_receipts, apply_transition,
      apply_recovery_transition), ports.py (TransitionCommitRequest, AuthorizationProof)
    - control_plane/transition_request.py (consume_with_signature and its exceptions)
    - control_plane/ssh_signing.py, snapshot.py (from T2/T3)
    - tests/helpers/control_plane_fixtures.py (create_task_in_state)

Key Functions (test cases, T4):
    - test_valid_signature_advances_state_and_consumes_request
    - test_signed_decisions_are_exactly_the_three_assertions
    - test_gate1_commit_without_proof_is_refused
    - test_gate1_commit_with_caller_staged_human_decisions_is_refused
    - test_proof_on_a_non_proof_edge_is_refused
    - test_wrong_signature_leaves_everything_unchanged
    - test_content_change_after_request_is_refused
    - test_expired_request_is_refused
    - test_stale_occupancy_request_is_refused
    - test_cross_request_signature_is_refused
    - test_request_for_another_task_is_refused
    - test_consumed_request_cannot_be_replayed
    - test_crash_before_state_advance_rolls_back_and_keeps_the_approval_usable
    - test_pending_requests_expire_on_every_occupancy_exit_path
"""

import io
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from agent_control import ControlPlane
from control_plane.ports import AuthorizationProof, PersistenceInvariantViolation, TransitionCommitRequest
from control_plane.snapshot import build_snapshot, gate1_artifact_paths
from control_plane.ssh_signing import (
    SIGN_NAMESPACE,
    SignatureInvalid,
    derive_challenge_from_row,
)
from control_plane.transition_request import (
    ContentChanged,
    PayloadMismatch,
    StaleOccupancy,
    TokenExpired,
    TokenReplayed,
    create_transition_request,
)
from control_plane.coordinator import HumanProofRequired, TransitionCoordinator, TransitionCoordinatorError
from helpers.gate1_fixtures import reach_awaiting_approval as _reach_awaiting_approval
from control_plane.registry import TransitionRegistry

TASK = "gate1-task-001"
_FOUND = shutil.which("ssh-keygen")
SSH_KEYGEN: str = _FOUND or "ssh-keygen"

pytestmark = [pytest.mark.no_auto_signer, pytest.mark.skipif(_FOUND is None, reason="ssh-keygen not installed")]  # coordinator tests assert the halt


def _sign(key: Path, message: bytes, workdir: Path) -> bytes:
    target = workdir / "challenge"
    target.write_bytes(message)
    subprocess.run(
        [SSH_KEYGEN, "-Y", "sign", "-f", str(key), "-n", SIGN_NAMESPACE, str(target)],
        check=True, capture_output=True,
    )
    signature = (workdir / "challenge.sig").read_bytes()
    (workdir / "challenge.sig").unlink()
    return signature


class Gate1:
    """A task waiting at Gate 1 with a content-bound request and an enrolled human key."""

    def __init__(self, tmp_path: Path):
        self.tmp = tmp_path
        self.db_path = tmp_path / "control_plane.db"
        self.cp = _reach_awaiting_approval(tmp_path, TASK).control_plane
        self.persistence = self.cp._persistence
        self.occupancy = self.persistence.get_last_transition(TASK).transition_id
        self.repo = tmp_path / "repo"
        folder = self.repo / "docs" / "plans" / "work-tasks" / TASK
        folder.mkdir(parents=True)
        (folder / f"{TASK}-spec.md").write_text("spec v1\n")
        (folder / f"{TASK}-implementation-plan.md").write_text("plan v1\n")
        keys = tmp_path / "keys"
        keys.mkdir()
        self.key = keys / "id"
        subprocess.run([SSH_KEYGEN, "-q", "-t", "ed25519", "-N", "", "-C", "op", "-f", str(self.key)], check=True, capture_output=True)
        pub = (keys / "id.pub").read_text().split()
        self.allowed = keys / "allowed_signers"
        self.allowed.write_text(f'op@local namespaces="{SIGN_NAMESPACE}" {pub[0]} {pub[1]}\n')
        os.chmod(self.allowed, 0o600)
        self.conn = sqlite3.connect(self.db_path)
        self.signdir = tmp_path / "sign"
        self.signdir.mkdir()

    def live_snapshot(self):
        return build_snapshot(gate1_artifact_paths(self.repo, TASK))

    def request(self, occupancy_id=None, ttl=300.0, now=None, task_id=TASK):
        return create_transition_request(
            self.conn, task_id=task_id, from_state="AWAITING_APPROVAL", to_state="APPROVED",
            occupancy_id=self.occupancy if occupancy_id is None else occupancy_id,
            content_snapshot=self.live_snapshot(), ttl_seconds=ttl, now=now,
        )

    def proof(self, record, signature=None, request_id=None):
        if signature is None:
            signature = _sign(self.key, derive_challenge_from_row(self.conn, record.request_id), self.signdir)
        return AuthorizationProof(
            kind="sshsig", request_id=record.request_id if request_id is None else request_id,
            signature=signature, allowed_signers=self.allowed, principal="op@local",
            live_snapshot_fn=self.live_snapshot,
        )

    def commit(self, proof, staged=None, to_state="APPROVED", template="awaiting_approval_to_approved"):
        return self.persistence.apply_transition_with_receipts(
            TransitionCommitRequest(
                task_id=TASK, expected_from_state="AWAITING_APPROVAL", to_state=to_state,
                source_occupancy_transition_id=self.occupancy, template_id=template, actor="human",
                reason="signed approval", staged_decisions=list(staged or []), staged_receipts=[], proof=proof,
            )
        )

    def state(self):
        return sqlite3.connect(self.db_path).execute("SELECT state FROM tasks WHERE task_id = ?", (TASK,)).fetchone()[0]

    def request_status(self, record):
        return sqlite3.connect(self.db_path).execute(
            "SELECT status FROM transition_request WHERE request_id = ?", (record.request_id,)
        ).fetchone()[0]

    def decisions(self):
        return sqlite3.connect(self.db_path).execute(
            "SELECT question_id, answer, decision_type, actor FROM transition_decisions "
            "WHERE task_id = ? AND from_state = 'AWAITING_APPROVAL' AND to_state = 'APPROVED'", (TASK,)
        ).fetchall()


@pytest.fixture
def gate1(tmp_path):
    return Gate1(tmp_path)


def test_valid_signature_advances_state_and_consumes_request(gate1):
    record = gate1.request()
    result = gate1.commit(gate1.proof(record))
    assert result.to_state == "APPROVED"
    assert gate1.state() == "APPROVED"
    row = sqlite3.connect(gate1.db_path).execute(
        "SELECT status, consumed_at, jti FROM transition_request WHERE request_id = ?", (record.request_id,)
    ).fetchone()
    assert row[0] == "CONSUMED" and row[1] is not None and row[2].startswith("sshsig:SHA256:")


def test_a_signed_commit_writes_no_decision_rows(gate1):
    """auth-ciba-increment-b: the consumed, signature-verified request is the authority for Gate 1. The earlier
    model wrote three trigger-satisfying human decision rows (signed 'assertions'); that model is gone."""
    record = gate1.request()
    gate1.commit(gate1.proof(record))
    assert list(gate1.decisions()) == []


def _forged_human_decisions(gate1):
    from control_plane.ports import TransitionDecision

    now = time.time()
    return [
        TransitionDecision(
            task_id=TASK, source_occupancy_transition_id=gate1.occupancy, from_state="AWAITING_APPROVAL",
            to_state="APPROVED", question_id=key, answer=answer, decision_type=dtype, actor="human", recorded_at=now,
        )
        for key, answer, dtype in (
            ("human_implementation_approval", "Yes, approve implementation [Recommended]", "ANSWER"),
            ("approval_awaiting_approval_to_approved", "APPROVAL", "APPROVAL"),
            ("guidance_compliance_confirmation", "YES", "CONFIRMATION"),
        )
    ]


def test_gate1_commit_without_proof_is_refused(gate1):
    """The pre-T4 way: human-attributed decisions staged by the caller, no proof."""
    with pytest.raises(PersistenceInvariantViolation):
        gate1.commit(None, staged=_forged_human_decisions(gate1))
    assert gate1.state() == "AWAITING_APPROVAL"
    assert gate1.decisions() == []


def test_gate1_commit_with_caller_staged_human_decisions_is_refused(gate1):
    record = gate1.request()
    with pytest.raises(PersistenceInvariantViolation):
        gate1.commit(gate1.proof(record), staged=_forged_human_decisions(gate1))
    assert gate1.state() == "AWAITING_APPROVAL"
    assert gate1.request_status(record) == "PENDING"


def test_proof_on_a_non_proof_edge_is_refused(gate1):
    record = gate1.request()
    with pytest.raises(PersistenceInvariantViolation):
        gate1.commit(gate1.proof(record), to_state="DRAFT_PLAN", template="awaiting_approval_to_draft_plan")
    assert gate1.state() == "AWAITING_APPROVAL"


def test_wrong_signature_leaves_everything_unchanged(gate1):
    record = gate1.request()
    other = gate1.request()
    wrong = _sign(gate1.key, derive_challenge_from_row(gate1.conn, other.request_id), gate1.signdir)
    with pytest.raises(SignatureInvalid):
        gate1.commit(gate1.proof(record, signature=wrong))
    assert gate1.state() == "AWAITING_APPROVAL"
    assert gate1.request_status(record) == "PENDING"
    assert gate1.decisions() == []


def test_content_change_after_request_is_refused(gate1):
    record = gate1.request()
    proof = gate1.proof(record)
    (gate1.repo / "docs" / "plans" / "work-tasks" / TASK / f"{TASK}-spec.md").write_text("spec EDITED\n")
    with pytest.raises(ContentChanged):
        gate1.commit(proof)
    assert gate1.state() == "AWAITING_APPROVAL"
    assert gate1.request_status(record) == "PENDING"


def test_expired_request_is_refused(gate1):
    record = gate1.request(ttl=10.0, now=time.time() - 1000)
    with pytest.raises(TokenExpired):
        gate1.commit(gate1.proof(record))
    assert gate1.state() == "AWAITING_APPROVAL"


def test_stale_occupancy_request_is_refused(gate1):
    record = gate1.request(occupancy_id=gate1.occupancy - 1)
    with pytest.raises(StaleOccupancy):
        gate1.commit(gate1.proof(record))
    assert gate1.state() == "AWAITING_APPROVAL"


def test_cross_request_signature_is_refused(gate1):
    """A signature over request A's challenge cannot approve via request B."""
    a, b = gate1.request(), gate1.request()
    signature_for_a = _sign(gate1.key, derive_challenge_from_row(gate1.conn, a.request_id), gate1.signdir)
    with pytest.raises(SignatureInvalid):
        gate1.commit(gate1.proof(b, signature=signature_for_a))
    assert gate1.state() == "AWAITING_APPROVAL"


def test_request_for_another_task_is_refused(gate1):
    other = "gate1-other-task"
    _reach_awaiting_approval(gate1.tmp, other)
    record = gate1.request(task_id=other)
    with pytest.raises(PayloadMismatch):
        gate1.commit(gate1.proof(record))
    assert gate1.state() == "AWAITING_APPROVAL"


def test_consumed_request_cannot_be_replayed(gate1):
    record = gate1.request()
    proof = gate1.proof(record)
    gate1.commit(proof)
    # Put the task back to Gate 1 legitimately-shaped is not possible; the replay is
    # attempted at the request level by re-using the same proof on the same state.
    with pytest.raises((TokenReplayed, ValueError)):
        gate1.commit(proof)
    assert gate1.request_status(record) == "CONSUMED"


def test_crash_before_state_advance_rolls_back_and_keeps_the_approval_usable(gate1):
    """Crash injection with a real trigger: the state UPDATE aborts after the request was
    consumed inside the same transaction. Neither half may remain."""
    record = gate1.request()
    proof = gate1.proof(record)
    conn = sqlite3.connect(gate1.db_path)
    conn.execute(
        "CREATE TRIGGER inject_crash BEFORE UPDATE OF state ON tasks WHEN NEW.state = 'APPROVED' "
        "BEGIN SELECT RAISE(ABORT, 'injected crash'); END;"
    )
    conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        gate1.commit(proof)
    assert gate1.state() == "AWAITING_APPROVAL"
    assert gate1.request_status(record) == "PENDING"
    assert gate1.decisions() == []

    conn.execute("DROP TRIGGER inject_crash")
    conn.commit()
    gate1.commit(proof)  # the approval was not burned by the crash
    assert gate1.state() == "APPROVED"
    assert gate1.request_status(record) == "CONSUMED"


# ---------------------------------------- invalidation on occupancy exit
def _pending(gate1, task_id):
    return create_transition_request(
        gate1.conn, task_id=task_id, from_state="AWAITING_APPROVAL", to_state="APPROVED",
        occupancy_id=1, content_snapshot=gate1.live_snapshot(),
    )


def _status(gate1, record):
    return sqlite3.connect(gate1.db_path).execute(
        "SELECT status FROM transition_request WHERE request_id = ?", (record.request_id,)
    ).fetchone()[0]


@pytest.mark.parametrize("to_state,template", [("DRAFT_PLAN", "awaiting_approval_to_draft_plan"), ("ESCALATED", "awaiting_approval_to_escalated")])
def test_pending_requests_expire_when_apply_transition_with_receipts_leaves_the_occupancy(gate1, to_state, template):
    record = gate1.request()
    assert _status(gate1, record) == "PENDING"
    gate1.commit(None, to_state=to_state, template=template)
    assert _status(gate1, record) == "EXPIRED"


def test_pending_requests_expire_when_apply_transition_leaves_the_occupancy(gate1):
    other = "gate1-apply-transition"
    _reach_awaiting_approval(gate1.tmp, other)
    record = _pending(gate1, other)
    assert _status(gate1, record) == "PENDING"
    gate1.cp.transition(other, "ESCALATED", "tester", "leave the occupancy")
    assert _status(gate1, record) == "EXPIRED"


def test_pending_requests_expire_when_recovery_transition_leaves_the_occupancy(gate1):
    other = "gate1-recovery"
    gate1.cp.create_task(task_id=other, title="recovery", runtime_tool="claude")
    gate1.cp.transition(other, "ESCALATED", "tester", "escalate")
    occ = gate1.persistence.get_last_transition(other).transition_id
    record = _pending(gate1, other)
    token = gate1.persistence.record_recovery_approval(
        task_id=other, expected_source_state="ESCALATED", destination_state="INTAKE",
        source_occupancy_transition_id=occ, approver="admin", actor="human", decision="APPROVAL", reason="recover",
    )
    gate1.persistence.apply_recovery_transition(
        task_id=other, expected_source_state="ESCALATED", destination_state="INTAKE",
        source_occupancy_transition_id=occ, approval_receipt_token=token, actor="admin", reason="recover",
    )
    assert _status(gate1, record) == "EXPIRED"


# ------------------------------------- T10: audited legacy_input proof + audit receipts
def _proof_receipts(gate1):
    return sqlite3.connect(gate1.db_path).execute(
        "SELECT command_executed FROM verification_receipts WHERE task_id = ? AND gate_name = 'human_gate_proof'", (TASK,)
    ).fetchall()


def test_legacy_input_proof_kind_is_refused_and_writes_nothing(gate1):
    """The audited legacy_input proof kind was removed (2026-09-20): a proof of that kind, with the caller's
    forged human decisions attached, changes nothing."""
    proof = AuthorizationProof(kind="legacy_input", request_id=0)
    with pytest.raises(PersistenceInvariantViolation):
        gate1.commit(proof, staged=_forged_human_decisions(gate1))
    assert gate1.state() == "AWAITING_APPROVAL"
    assert _proof_receipts(gate1) == []


def test_the_legacy_policy_vouching_field_no_longer_exists():
    with pytest.raises(TypeError):
        AuthorizationProof(kind="legacy_input", request_id=0, legacy_policy_ok=True)


def test_unknown_proof_kind_is_refused(gate1):
    with pytest.raises(PersistenceInvariantViolation):
        gate1.commit(AuthorizationProof(kind="password", request_id=0), staged=_forged_human_decisions(gate1))
    assert gate1.state() == "AWAITING_APPROVAL"


def test_signed_commit_writes_an_audit_receipt_with_the_key_fingerprint(gate1):
    record = gate1.request()
    gate1.commit(gate1.proof(record))
    receipts = _proof_receipts(gate1)
    assert len(receipts) == 1
    assert "proof=sshsig" in receipts[0][0] and "SHA256:" in receipts[0][0] and f"request={record.request_id}" in receipts[0][0]


# ------------------------------------------------ T7: coordinator wiring at Gate 1
def _write_gate1_plan_files(sim, task_id):
    folder = sim.control_plane.repo_root / "docs" / "plans" / "work-tasks" / task_id
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{task_id}-spec.md").write_text("spec v1\n")
    (folder / f"{task_id}-implementation-plan.md").write_text("plan v1\n")


def _coord(sim, input_fn=None, **kwargs):
    return TransitionCoordinator(
        sim.control_plane, registry=sim.registry, input_fn=input_fn, output_stream=io.StringIO(), **kwargs,
    )


def _state_of(sim, task_id):
    return sqlite3.connect(sim.control_plane.db_path).execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()[0]


def test_strict_gate1_returns_structured_remediation_and_creates_a_request(tmp_path):
    task = "gate1-strict"
    sim = _reach_awaiting_approval(tmp_path, task)
    _write_gate1_plan_files(sim, task)
    prompts = []
    coord = _coord(sim, input_fn=lambda p: prompts.append(p) or "1")
    with pytest.raises(HumanProofRequired) as excinfo:
        coord.coordinate_transition(task_id=task, to_state="APPROVED", actor="human", reason="try", interactive=True)
    info = excinfo.value.remediation
    assert prompts == []  # no prompt may be offered as authorization
    assert info["code"] == "HUMAN_PROOF_REQUIRED" and info["edge"] == "AWAITING_APPROVAL -> APPROVED"
    assert "questions" not in info  # no decision answers are shown for signing: the signature is the authority
    assert {"show_challenge", "approve", "setup_identity", "setup_docs"} <= set(info["commands"])
    assert f"--request-id {info['request_id']}" in info["commands"]["show_challenge"]
    assert isinstance(info["failed_checks"], list)
    assert "HUMAN_PROOF_REQUIRED" in str(excinfo.value)
    assert _state_of(sim, task) == "AWAITING_APPROVAL"
    row = sqlite3.connect(sim.control_plane.db_path).execute(
        "SELECT status, challenge_version, content_snapshot, occupancy_id FROM transition_request WHERE request_id = ?",
        (info["request_id"],),
    ).fetchone()
    assert row[0] == "PENDING" and row[1] == "control-plane-challenge/1" and row[2] and row[3] > 0


@pytest.mark.parametrize("actor,interactive", [("human", True), ("agent", False), ("human", False)])
def test_piped_or_scripted_answers_cannot_authorize_gate1_in_strict_mode(tmp_path, actor, interactive):
    """The #621 reproduction: injected input_fn / scripted answers / non-interactive agent."""
    task = f"gate1-repro-{actor}-{int(interactive)}"
    sim = _reach_awaiting_approval(tmp_path, task)
    _write_gate1_plan_files(sim, task)
    coord = _coord(sim, input_fn=lambda _p: "y")
    with pytest.raises(HumanProofRequired):
        coord.coordinate_transition(
            task_id=task, to_state="APPROVED", actor=actor, reason="scripted", interactive=interactive,
            provided_answers={"human_implementation_approval": "Yes, approve implementation [Recommended]"} if not interactive else None,
        )
    assert _state_of(sim, task) == "AWAITING_APPROVAL"


def test_missing_plan_artifacts_give_an_actionable_error_not_a_request(tmp_path):
    task = "gate1-noplan"
    sim = _reach_awaiting_approval(tmp_path, task)
    coord = _coord(sim)
    with pytest.raises(TransitionCoordinatorError) as excinfo:
        coord.coordinate_transition(task_id=task, to_state="APPROVED", actor="human", reason="x", interactive=True)
    assert not isinstance(excinfo.value, HumanProofRequired)
    assert f"work-tasks/{task}" in str(excinfo.value)


def test_a_typed_yes_at_an_interactive_terminal_cannot_approve_gate1(tmp_path):
    """The removed legacy_input flow (typed answers at a terminal, audited as proof=input_unhardened) must not
    come back: the same typed answers now halt with HUMAN_PROOF_REQUIRED and change nothing."""
    task = "gate1-typed-yes"
    sim = _reach_awaiting_approval(tmp_path, task)
    _write_gate1_plan_files(sim, task)
    answers = iter(["1", "y", "YES", "YES"])
    coord = _coord(sim, input_fn=lambda _p: next(answers))
    with pytest.raises(HumanProofRequired):
        coord.coordinate_transition(task_id=task, to_state="APPROVED", actor="human", reason="typed", interactive=True)
    assert _state_of(sim, task) == "AWAITING_APPROVAL"
    receipts = sqlite3.connect(sim.control_plane.db_path).execute(
        "SELECT command_executed FROM verification_receipts WHERE task_id = ? AND gate_name = 'human_gate_proof'", (task,)
    ).fetchall()
    assert receipts == []


def test_other_edges_are_untouched_by_the_gate1_wiring(tmp_path):
    task = "gate1-other-edge"
    sim = _reach_awaiting_approval(tmp_path, task)
    coord = _coord(sim)
    record = coord.coordinate_transition(
        task_id=task, to_state="DRAFT_PLAN", actor="agent", reason="revise",
        provided_answers={"guidance_compliance_confirmation": "YES"},
    )
    assert record.to_state == "DRAFT_PLAN"


def test_gate_edges_are_human_only_and_review_routing_edges_stay_agent_or_human():
    """Gate 1 and both Gate 3 edges are human_only (auth-ciba-increment-b promoted Gate 3); routing into review
    stays agent_or_human, because only ACCEPTING the work is the human's signed act."""
    registry = TransitionRegistry.load_default()
    for frm, to in (("AWAITING_APPROVAL", "APPROVED"), ("WORKTREE_REVIEW", "VERIFY_EXIT"), ("MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT")):
        assert registry.get_template(frm, to).authorized_actor == "human_only", (frm, to)
        assert (frm, to) in registry.proof_required_edges(), (frm, to)
    for frm, to in (("PLAN_REVIEW", "MULTI_AGENT_REVIEW"), ("WORKTREE_REVIEW", "MULTI_AGENT_CODE_REVIEW")):
        assert registry.get_template(frm, to).authorized_actor == "agent_or_human", (frm, to)
