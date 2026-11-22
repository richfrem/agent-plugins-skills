"""Focused P00 contract tests for the live baseline handoff."""

import io
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from agent_control import ControlPlane
from control_plane.constants import (
    STATE_INTAKE, STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_MULTI_AGENT_REVIEW,
    STATE_AWAITING_APPROVAL, STATE_APPROVED, STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW,
    STATE_VERIFY_EXIT, STATE_RETROSPECTIVE, STATE_DONE,
)
from control_plane import adapters
from control_plane.coordinator import TransitionCoordinator
from control_plane.wrappers.record_interview_question import (
    record_interview_question,
    ERROR_CODE_CONTRACT_DENIED,
)
from control_plane.wrappers.write_plan_document import write_plan_document


QUESTION_ANSWERS = {
    "intake_outline_confirmation": "Confirm outline and enter DRAFT_PLAN [Recommended]",
}


def _interview_cp(tmp_path: Path):
    repo_root = tmp_path / "repo"
    (repo_root / "context").mkdir(parents=True)
    cp = ControlPlane(db_path=repo_root / "context" / "control_plane.db")
    cp.init_db()
    cp.repo_root = repo_root
    cp.create_task("p00-test", "P00 test", "codex")
    cp.log_asymmetric_persistence("p00-test", "references/map-debt.md", "OBSERVED", "prior_art_scan")
    return cp


def _record(cp: ControlPlane, question_id: str, answer: str):
    return record_interview_question(
        task_id="p00-test",
        question=question_id,
        options={},
        recommended="",
        answer=answer,
        actor="human",
        target_state=STATE_DRAFT_PLAN,
        control_plane=cp,
    )


def test_answer_receipt_binds_legal_target_and_exposes_next_action(tmp_path):
    cp = _interview_cp(tmp_path)

    result = _record(cp, "intake_outline_confirmation", QUESTION_ANSWERS["intake_outline_confirmation"])

    assert result["status"] == "RECORDED"
    assert isinstance(result["decision_id"], int)
    assert isinstance(result["task_id"], str)
    assert isinstance(result["source_occupancy_transition_id"], int)
    assert result["question_id"] == "intake_outline_confirmation"
    assert result["target_state"] == STATE_DRAFT_PLAN
    assert isinstance(result["outline_revision"], int)
    assert isinstance(result["artifact_path"], str)
    assert set(result["next_action"]) == {"kind", "state", "command"}
    assert result["next_action"]["state"] == STATE_DRAFT_PLAN
    assert result["next_action"]["command"]

    outline = cp._persistence.get_interview_plan_outline("p00-test")
    assert outline["revision"] == result["outline_revision"] == 1
    assert outline["artifact_path"] == result["artifact_path"]
    assert (cp.repo_root / result["artifact_path"]).is_file()


def test_invalid_target_is_denied_without_decision_or_outline_mutation(tmp_path):
    cp = _interview_cp(tmp_path)

    with pytest.raises(ValueError, match="legal target"):
        record_interview_question(
            task_id="p00-test",
            question="intake_outline_confirmation",
            options={},
            recommended="",
            answer="Invalid route",
            actor="human",
            target_state=STATE_VERIFY_EXIT,
            control_plane=cp,
        )

    assert cp.get_unconsumed_transition_answers("p00-test", STATE_INTAKE, STATE_DRAFT_PLAN) == {}
    assert cp._persistence.get_interview_plan_outline("p00-test") is None


def test_unknown_question_and_empty_answer_are_denied_without_mutation(tmp_path):
    cp = _interview_cp(tmp_path)

    for question_id, answer in (("not_canonical", "answer"), ("intake_outline_confirmation", "")):
        with pytest.raises((ValueError, TypeError)):
            _record(cp, question_id, answer)

    assert cp.get_unconsumed_transition_answers("p00-test", STATE_INTAKE, STATE_DRAFT_PLAN) == {}
    assert cp._persistence.get_interview_plan_outline("p00-test") is None


def test_answer_recorder_requires_explicit_target_and_answer(tmp_path):
    cp = _interview_cp(tmp_path)

    with pytest.raises(ValueError, match="target_state must be explicit"):
        record_interview_question(
            task_id="p00-test",
            question="intake_outline_confirmation",
            options={},
            recommended="A recommended default",
            answer="An explicit answer",
            actor="human",
            control_plane=cp,
        )

    with pytest.raises(ValueError, match="Answer.*must be explicit"):
        record_interview_question(
            task_id="p00-test",
            question="intake_outline_confirmation",
            options={},
            recommended="A recommended default",
            answer=None,
            actor="human",
            target_state=STATE_DRAFT_PLAN,
            control_plane=cp,
        )

    assert cp.get_unconsumed_transition_answers("p00-test", STATE_INTAKE, STATE_DRAFT_PLAN) == {}
    assert cp._persistence.get_interview_plan_outline("p00-test") is None


def test_denial_envelope_reports_unchanged_occupancy_and_one_recovery(tmp_path):
    from control_plane.wrappers.record_interview_question import _denial_response

    cp = _interview_cp(tmp_path)
    with pytest.raises(ValueError) as denied:
        record_interview_question(
            task_id="p00-test",
            question="intake_outline_confirmation",
            options={},
            recommended="A recommended default",
            answer="An explicit answer",
            actor="human",
            target_state=STATE_VERIFY_EXIT,
            control_plane=cp,
        )

    envelope = _denial_response(cp, "p00-test", denied.value)
    assert envelope["status"] == "DENIED"
    assert set(envelope["error"]) == {"code", "check", "state", "occupancy", "recovery"}
    assert envelope["error"]["code"] == ERROR_CODE_CONTRACT_DENIED
    assert envelope["error"]["state"] == STATE_INTAKE
    assert isinstance(envelope["error"]["occupancy"], int)
    assert "retry record_interview_question.py" in envelope["error"]["recovery"]


def test_draft_plan_releases_only_plan_write_and_writes_bound_documents(tmp_path):
    cp = _interview_cp(tmp_path)
    for question_id, answer in QUESTION_ANSWERS.items():
        _record(cp, question_id, answer)

    transition = TransitionCoordinator(cp, input_fn=lambda p: "1", output_stream=io.StringIO()).coordinate_transition(
        task_id="p00-test",
        to_state=STATE_DRAFT_PLAN,
        actor="human",
        reason="complete standard intake",
        interactive=True,
    )

    assert transition.to_state == STATE_DRAFT_PLAN
    assert cp.verify_phase_capability("p00-test", "plan_write").current_state == STATE_DRAFT_PLAN
    with pytest.raises(Exception):
        cp.verify_phase_capability("p00-test", "implementation_write")

    spec = tmp_path / "repo" / "docs" / "plans" / "work-tasks" / "p00-test" / "p00-test-spec.md"
    implementation_plan = tmp_path / "repo" / "docs" / "plans" / "work-tasks" / "p00-test" / "p00-test-implementation-plan.md"
    for destination, content in (
        (spec, "# P00 specification\n"),
        (implementation_plan, "# P00 implementation plan\n"),
    ):
        result = write_plan_document(
            task_id="p00-test",
            destination_path=destination,
            content=content,
            control_plane=cp,
        )
        assert result["status"] == "WRITTEN"
        assert destination.read_text(encoding="utf-8") == content


def test_answer_and_outline_roll_back_together_on_projection_failure(tmp_path, monkeypatch):
    cp = _interview_cp(tmp_path)

    def fail_projection(*_args, **_kwargs):
        raise RuntimeError("injected outline serialization failure")

    monkeypatch.setattr(adapters.json, "dumps", fail_projection)
    with pytest.raises(RuntimeError, match="outline serialization failure"):
        _record(cp, "intake_outline_confirmation", QUESTION_ANSWERS["intake_outline_confirmation"])

    assert cp.get_unconsumed_transition_answers("p00-test", STATE_INTAKE, STATE_DRAFT_PLAN) == {}
    assert cp._persistence.get_interview_plan_outline("p00-test") is None


def test_duplicate_answer_is_rejected_without_revision(tmp_path):
    cp = _interview_cp(tmp_path)
    _record(cp, "intake_outline_confirmation", QUESTION_ANSWERS["intake_outline_confirmation"])

    with pytest.raises(ValueError, match="Duplicate decision"):
        _record(cp, "intake_outline_confirmation", "A second answer")

    outline = cp._persistence.get_interview_plan_outline("p00-test")
    assert outline["revision"] == 1
    assert len(outline["bullets"]) == 1


def test_seven_answers_use_supported_path_before_one_lifecycle_transition(tmp_path):
    cp = _interview_cp(tmp_path)

    for question_id, answer in QUESTION_ANSWERS.items():
        _record(cp, question_id, answer)

    coordinator = TransitionCoordinator(cp, input_fn=lambda p: "1", output_stream=io.StringIO())
    transition = coordinator.coordinate_transition(
        task_id="p00-test",
        to_state=STATE_DRAFT_PLAN,
        actor="human",
        reason="complete standard intake",
        interactive=True,
    )

    assert transition.from_state == STATE_INTAKE
    assert transition.to_state == STATE_DRAFT_PLAN
    assert cp.get_task("p00-test")["state"] == STATE_DRAFT_PLAN
    assert cp.verify_phase_capability("p00-test", "plan_write").current_state == STATE_DRAFT_PLAN

    conn = cp._persistence.get_connection()
    rows = conn.execute(
        "SELECT question_id, bound_transition_id, consumed_at "
        "FROM transition_decisions WHERE task_id = ? ORDER BY decision_id",
        ("p00-test",),
    ).fetchall()
    conn.close()
    assert len(rows) == 1
    assert all(row["bound_transition_id"] == transition.transition_id for row in rows)
    assert all(row["consumed_at"] is not None for row in rows)

    outline = cp._persistence.get_interview_plan_outline("p00-test")
    assert outline["revision"] == 1
    assert len(outline["bullets"]) == 1
    assert len(cp._persistence.get_verification_receipts("p00-test")) == 0
