"""Behavioral contract for the interview plan-outline artifact."""

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from agent_control import ControlPlane
from control_plane.wrappers.record_interview_question import record_interview_question


def _interview_cp(tmp_path: Path):
    repo_root = tmp_path / "repo"
    (repo_root / "context").mkdir(parents=True)
    cp = ControlPlane(db_path=repo_root / "context" / "control_plane.db")
    cp.init_db()
    cp.create_task("outline-task", "Outline task", "codex")
    cp.log_asymmetric_persistence("outline-task", "references/map-debt.md", "OBSERVED", "prior_art_scan")
    cp.transition("outline-task", "INTERVIEW", "agent", "begin interview")
    cp.repo_root = repo_root
    return cp, repo_root


def test_recording_interview_answer_persists_outline_and_artifact(tmp_path):
    cp, repo_root = _interview_cp(tmp_path)

    result = record_interview_question(
        task_id="outline-task",
        question="interview_summary",
        options={},
        recommended="",
        answer="Make the pipeline continue after each answer.",
        target_state="DRAFT_PLAN",
        control_plane=cp,
    )

    outline = cp._persistence.get_interview_plan_outline("outline-task")
    assert outline["revision"] == 1
    assert outline["bullets"][0]["question_id"] == "interview_summary"
    assert outline["artifact_path"] == "docs/plans/outline-task-plan-outline.md"
    artifact = repo_root / outline["artifact_path"]
    assert artifact.exists()
    assert "Make the pipeline continue after each answer." in artifact.read_text(encoding="utf-8")
    assert result["outline_artifact"] == "docs/plans/outline-task-plan-outline.md"


def test_revising_same_outline_question_updates_revision_without_duplicate_decision(tmp_path):
    cp, _ = _interview_cp(tmp_path)
    record_interview_question(
        task_id="outline-task", question="interview_summary", options={}, recommended="",
        answer="First wording", target_state="DRAFT_PLAN", control_plane=cp,
    )

    cp.update_interview_plan_outline(
        "outline-task", "interview_summary", "Revised wording", actor="human"
    )
    outline = cp._persistence.get_interview_plan_outline("outline-task")
    assert outline["revision"] == 2
    assert outline["bullets"][0]["text"] == "Revised wording"


def test_interview_exit_to_draft_plan_requires_outline_artifact(tmp_path):
    cp, _ = _interview_cp(tmp_path)
    with __import__("pytest").raises(Exception, match="plan outline"):
        cp.transition("outline-task", "DRAFT_PLAN", "agent", "draft plan")
