"""Reproduces issue: TransitionCoordinator.coordinate_transition's interactive
path from INTERVIEW to DRAFT_PLAN collects the 5 canonical interview answers
one-at-a-time via input_fn, but never persists them into the plan-outline
artifact (update_interview_plan_outline) before the commit path checks
assert_interview_plan_outline_ready. Every interactive DRAFT_PLAN transition
therefore fails with "interview plan outline is missing", even though the
human answered every question correctly.
"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_control import ControlPlane
from control_plane.coordinator import TransitionCoordinator
from interview_helpers import REASON_INTERVIEW_COMPLETE
from control_plane.constants import (
    STATE_INTERVIEW, STATE_DRAFT_PLAN,
)


def test_interactive_draft_plan_transition_persists_answers_to_outline(tmp_path):
    control_plane = ControlPlane(db_path=tmp_path / "control_plane.db")
    control_plane.create_task("t1", "Test task", "codex")
    control_plane.transition("t1", STATE_INTERVIEW, "human", "start interview")

    answers = iter([
        "STANDARD",
        "Fix the bug.",
        "agent_control.py only.",
        "Tests pass.",
        "Not applicable; this route is STANDARD, not TRIVIAL.",
        "Preserve existing gates.",
        "medium",
        "YES",
    ])
    coordinator = TransitionCoordinator(
        control_plane,
        input_fn=lambda _prompt: next(answers),
    )

    record = coordinator.coordinate_transition(
        task_id="t1",
        to_state=STATE_DRAFT_PLAN,
        actor="human",
        reason=REASON_INTERVIEW_COMPLETE,
        interactive=True,
    )

    assert record.to_state == STATE_DRAFT_PLAN
    outline = control_plane._persistence.get_interview_plan_outline("t1")
    assert outline and outline.get("bullets"), (
        "Interview answers given interactively were never persisted to the "
        "plan outline before the DRAFT_PLAN transition committed."
    )
    artifact_path = control_plane._resolve_plan_outline_path(outline["artifact_path"])
    assert artifact_path.is_file() and artifact_path.read_text(encoding="utf-8").strip()
