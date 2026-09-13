"""Focused P00 contract tests for the live baseline handoff."""

import io
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from agent_control import ControlPlane
from control_plane import adapters
from control_plane.coordinator import TransitionCoordinator
from control_plane.wrappers.record_interview_question import record_interview_question
from control_plane.wrappers.write_plan_document import write_plan_document


QUESTION_ANSWERS = {
    "interview_classification": "STANDARD",
    "interview_summary": "Make the handoff self-proving.",
    "interview_scope": "Only the bounded P00 pipeline path.",
    "interview_verification": "Focused production-path evidence is captured.",
    "interview_acceptance_criteria": "Preserve approval and authority boundaries.",
    "interview_planning_model_effort": "gpt-5.6-luna at high effort.",
}


def _interview_cp(tmp_path: Path):
    repo_root = tmp_path / "repo"
    (repo_root / "context").mkdir(parents=True)
    cp = ControlPlane(db_path=repo_root / "context" / "control_plane.db")
    cp.init_db()
    cp.create_task("p00-test", "P00 test", "codex")
    cp.log_asymmetric_persistence("p00-test", "references/map-debt.md", "OBSERVED", "prior_art_scan")
    cp.transition("p00-test", "INTERVIEW", "agent", "begin interview")
    cp.repo_root = repo_root
    return cp


def _record(cp: ControlPlane, question_id: str, answer: str):
    return record_interview_question(
        task_id="p00-test",
        question=question_id,
        options={},
        recommended="",
        answer=answer,
        actor="human",
        target_state="DRAFT_PLAN",
        control_plane=cp,
    )


def test_answer_receipt_binds_legal_target_and_exposes_next_action(tmp_path):
    cp = _interview_cp(tmp_path)

    result = _record(cp, "interview_summary", QUESTION_ANSWERS["interview_summary"])

    assert result["status"] == "RECORDED"
    assert isinstance(result["decision_id"], int)
    assert isinstance(result["task_id"], str)
    assert isinstance(result["source_occupancy_transition_id"], int)
    assert result["question_id"] == "interview_summary"
    assert result["target_state"] == "DRAFT_PLAN"
    assert isinstance(result["outline_revision"], int)
    assert isinstance(result["artifact_path"], str)
    assert set(result["next_action"]) == {"kind", "state", "command"}
    assert result["next_action"]["state"] == "INTERVIEW"
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
            question="interview_summary",
            options={},
            recommended="",
            answer="Invalid route",
            actor="human",
            target_state="RETROSPECTIVE",
            control_plane=cp,
        )

    assert cp._persistence.get_unconsumed_transition_answers("p00-test", "INTERVIEW", "DRAFT_PLAN") == {}
    assert cp._persistence.get_interview_plan_outline("p00-test") is None


def test_unknown_question_and_empty_answer_are_denied_without_mutation(tmp_path):
    cp = _interview_cp(tmp_path)

    for question_id, answer in (("not_canonical", "answer"), ("interview_summary", "")):
        with pytest.raises((ValueError, TypeError)):
            _record(cp, question_id, answer)

    assert cp._persistence.get_unconsumed_transition_answers("p00-test", "INTERVIEW", "DRAFT_PLAN") == {}
    assert cp._persistence.get_interview_plan_outline("p00-test") is None


def test_answer_recorder_requires_explicit_target_and_answer(tmp_path):
    cp = _interview_cp(tmp_path)

    with pytest.raises(ValueError, match="target_state must be explicit"):
        record_interview_question(
            task_id="p00-test",
            question="interview_summary",
            options={},
            recommended="A recommended default",
            answer="An explicit answer",
            actor="human",
            control_plane=cp,
        )

    with pytest.raises(ValueError, match="Answer.*must be explicit"):
        record_interview_question(
            task_id="p00-test",
            question="interview_summary",
            options={},
            recommended="A recommended default",
            answer=None,
            actor="human",
            target_state="DRAFT_PLAN",
            control_plane=cp,
        )

    assert cp._persistence.get_unconsumed_transition_answers("p00-test", "INTERVIEW", "DRAFT_PLAN") == {}
    assert cp._persistence.get_interview_plan_outline("p00-test") is None


def test_denial_envelope_reports_unchanged_occupancy_and_one_recovery(tmp_path):
    from control_plane.wrappers.record_interview_question import _denial_response

    cp = _interview_cp(tmp_path)
    with pytest.raises(ValueError) as denied:
        record_interview_question(
            task_id="p00-test",
            question="interview_summary",
            options={},
            recommended="A recommended default",
            answer="An explicit answer",
            actor="human",
            target_state="RETROSPECTIVE",
            control_plane=cp,
        )

    envelope = _denial_response(cp, "p00-test", denied.value)
    assert envelope["status"] == "DENIED"
    assert set(envelope["error"]) == {"code", "check", "state", "occupancy", "recovery"}
    assert envelope["error"]["code"] == "CONTRACT_DENIED"
    assert envelope["error"]["state"] == "INTERVIEW"
    assert isinstance(envelope["error"]["occupancy"], int)
    assert "retry record_interview_question.py" in envelope["error"]["recovery"]


def test_draft_plan_releases_only_plan_write_and_writes_bound_documents(tmp_path):
    cp = _interview_cp(tmp_path)
    for question_id, answer in QUESTION_ANSWERS.items():
        _record(cp, question_id, answer)

    transition = TransitionCoordinator(cp, output_stream=io.StringIO()).coordinate_transition(
        task_id="p00-test",
        to_state="DRAFT_PLAN",
        actor="agent",
        reason="complete standard interview",
    )

    assert transition.to_state == "DRAFT_PLAN"
    assert cp.verify_phase_capability("p00-test", "plan_write").current_state == "DRAFT_PLAN"
    with pytest.raises(Exception):
        cp.verify_phase_capability("p00-test", "implementation_write")

    spec = tmp_path / "repo" / "docs" / "plans" / "p00-test-spec.md"
    implementation_plan = tmp_path / "repo" / "docs" / "plans" / "p00-test-implementation-plan.md"
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
        _record(cp, "interview_summary", QUESTION_ANSWERS["interview_summary"])

    assert cp._persistence.get_unconsumed_transition_answers("p00-test", "INTERVIEW", "DRAFT_PLAN") == {}
    assert cp._persistence.get_interview_plan_outline("p00-test") is None


def test_duplicate_answer_is_rejected_without_revision(tmp_path):
    cp = _interview_cp(tmp_path)
    _record(cp, "interview_summary", QUESTION_ANSWERS["interview_summary"])

    with pytest.raises(ValueError, match="Duplicate decision"):
        _record(cp, "interview_summary", "A second answer")

    outline = cp._persistence.get_interview_plan_outline("p00-test")
    assert outline["revision"] == 1
    assert len(outline["bullets"]) == 1


def test_six_answers_use_supported_path_before_one_lifecycle_transition(tmp_path):
    cp = _interview_cp(tmp_path)

    for question_id, answer in QUESTION_ANSWERS.items():
        _record(cp, question_id, answer)

    coordinator = TransitionCoordinator(cp, output_stream=io.StringIO())
    transition = coordinator.coordinate_transition(
        task_id="p00-test",
        to_state="DRAFT_PLAN",
        actor="agent",
        reason="complete standard interview",
    )

    assert transition.from_state == "INTERVIEW"
    assert transition.to_state == "DRAFT_PLAN"
    assert cp.get_task("p00-test")["state"] == "DRAFT_PLAN"
    assert cp.verify_phase_capability("p00-test", "plan_write").current_state == "DRAFT_PLAN"

    conn = cp._persistence.get_connection()
    rows = conn.execute(
        "SELECT question_id, bound_transition_id, consumed_at "
        "FROM transition_decisions WHERE task_id = ? ORDER BY decision_id",
        ("p00-test",),
    ).fetchall()
    conn.close()
    assert len(rows) == 6
    assert all(row["bound_transition_id"] == transition.transition_id for row in rows)
    assert all(row["consumed_at"] is not None for row in rows)

    outline = cp._persistence.get_interview_plan_outline("p00-test")
    assert outline["revision"] == 6
    assert len(outline["bullets"]) == 6
    assert len(cp._persistence.get_verification_receipts("p00-test")) == 0
