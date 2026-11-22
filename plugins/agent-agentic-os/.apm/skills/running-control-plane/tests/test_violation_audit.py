"""
tests/test_violation_audit.py
=============================

Purpose:
    Failing-first test for the transition_violations audit gap (auth-ciba-increment-b, #639, U2):
    when the commit path rejects a transition (the database trigger reverts the state and the
    coordinator aborts and rolls back the transaction) the trigger's own `transition_violations` row
    used to be rolled back with it, leaving no audit record. The adapter now writes the rejection
    (actor, reason, detail) in a SEPARATE, autonomous transaction after the rollback, so a rolled-back
    attempt leaves a persistent row while the state stays unchanged. Real SQLite, real trigger.

Key Input Dependencies:
    - control_plane/adapters.py (apply_transition_with_receipts, transition_violations columns)
    - tests/test_review_selection.py helper (_plan_review_task)

Key Functions (test cases):
    - test_a_rolled_back_trigger_rejection_leaves_a_persistent_violation_row
    - test_a_successful_transition_writes_no_violation
    - test_logging_failure_never_masks_the_original_error
"""

import sqlite3
import sys
import time
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from control_plane.ports import PersistenceInvariantViolation, TransitionCommitRequest, TransitionDecision
from control_plane.pipeline_simulator import PipelineSimulator
from control_plane.coordinator import TransitionCoordinator
import io

TASK = "violation-audit-001"


def _intake_task(tmp_path):
    sim = PipelineSimulator(tmp_path / "control_plane.db")
    sim.create_task(TASK, "Violation audit test")
    return sim


def _rejected_request(cp):
    """A commit whose decisions are attributed to the agent, so the trigger rejects INTAKE -> DRAFT_PLAN."""
    conn = sqlite3.connect(cp.db_path)
    occupancy = conn.execute("SELECT MAX(transition_id) FROM task_transitions WHERE task_id = ?", (TASK,)).fetchone()[0]
    decisions = [
        TransitionDecision(
            task_id=TASK, source_occupancy_transition_id=occupancy, from_state="INTAKE", to_state="DRAFT_PLAN",
            question_id="intake_outline_confirmation", answer="x", decision_type="ANSWER", actor="agent", recorded_at=time.time(),
        )
    ]
    return TransitionCommitRequest(
        task_id=TASK, expected_from_state="INTAKE", to_state="DRAFT_PLAN",
        source_occupancy_transition_id=occupancy, template_id="intake_to_draft_plan",
        actor="tester", reason="forged agent answers", staged_decisions=decisions, staged_receipts=[],
    )


def _violations(cp):
    conn = sqlite3.connect(cp.db_path)
    conn.row_factory = sqlite3.Row
    return [dict(r) for r in conn.execute("SELECT * FROM transition_violations WHERE task_id = ?", (TASK,))]


def test_a_rolled_back_trigger_rejection_leaves_a_persistent_violation_row(tmp_path):
    sim = _intake_task(tmp_path)
    cp = sim.control_plane
    with pytest.raises(PersistenceInvariantViolation):
        cp._persistence.apply_transition_with_receipts(_rejected_request(cp))
    assert cp._persistence.read_current_state(TASK) == "INTAKE"  # the transition really rolled back
    rows = _violations(cp)
    assert rows, "the rejection must leave an audit row despite the rollback"
    row = rows[-1]
    assert (row["attempted_from_state"], row["attempted_to_state"]) == ("INTAKE", "DRAFT_PLAN")
    assert row["actor"] == "tester"
    assert "rejected" in (row["detail"] or "").lower()


def test_a_successful_transition_writes_no_violation(tmp_path):
    sim = _intake_task(tmp_path)
    feed = iter(["1"])
    TransitionCoordinator(
        sim.control_plane, registry=sim.registry, input_fn=lambda _p: next(feed), output_stream=io.StringIO(),
    ).coordinate_transition(task_id=TASK, to_state="DRAFT_PLAN", actor="human", reason="ok", interactive=True)
    assert _violations(sim.control_plane) == []


def test_logging_failure_never_masks_the_original_error(tmp_path, monkeypatch):
    sim = _intake_task(tmp_path)
    cp = sim.control_plane
    monkeypatch.setattr(type(cp._persistence), "_write_violation_autonomously", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("audit db down")))
    with pytest.raises(PersistenceInvariantViolation):
        cp._persistence.apply_transition_with_receipts(_rejected_request(cp))
