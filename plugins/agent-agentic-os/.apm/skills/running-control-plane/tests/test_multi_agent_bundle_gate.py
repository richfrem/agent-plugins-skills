"""Test multi-agent bundle gate transitions and Socratic cadence constraints."""
import sys
from pathlib import Path
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_control import ControlPlane, CANONICAL_STATES, InvalidStateTransition
from interview_helpers import stage_interview_answers
from control_plane.constants import (
    STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_MULTI_AGENT_REVIEW, STATE_PLAN_REVIEW, STATE_AWAITING_APPROVAL,
)

def test_draft_plan_and_multi_agent_review_states_exist():
    assert STATE_DRAFT_PLAN in CANONICAL_STATES
    assert STATE_MULTI_AGENT_REVIEW in CANONICAL_STATES

def test_full_intake_to_approval_lifecycle(tmp_path, monkeypatch):
    """Schema v15 10-state flow: INTAKE -> DRAFT_PLAN -> PLAN_REVIEW (+ critic review) -> APPROVED."""
    db_file = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_file)
    cp.repo_root = tmp_path
    cp.init_db()

    task_id = "test-bundle-001"
    cp.create_task(task_id=task_id, title="Test Bundle Gate", runtime_tool="antigravity")

    from control_plane.coordinator import TransitionCoordinator
    from control_plane.registry import TransitionRegistry
    reg = TransitionRegistry.load_default()
    inputs = iter(["1"])
    coord = TransitionCoordinator(control_plane=cp, registry=reg, input_fn=lambda prompt: next(inputs))
    monkeypatch.setattr(coord, "_resolve_repo_root", lambda: tmp_path)

    # INTAKE -> DRAFT_PLAN
    coord.coordinate_transition(
        task_id=task_id, to_state=STATE_DRAFT_PLAN, actor="human",
        reason="Intake outline confirmed", interactive=True,
    )
    assert cp.get_task(task_id)["state"] == STATE_DRAFT_PLAN

    plan_dir = tmp_path / "docs" / "plans" / "work-tasks" / task_id
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / f"{task_id}-spec.md").write_text("# Test specification\n", encoding="utf-8")
    (plan_dir / f"{task_id}-implementation-plan.md").write_text("# Test implementation plan\n\n- Strategy: direct\n", encoding="utf-8")

    # DRAFT_PLAN -> PLAN_REVIEW
    coord.coordinate_transition(
        task_id=task_id, to_state=STATE_PLAN_REVIEW, actor="agent",
        reason="Submit plan for disposition", interactive=True,
    )
    assert cp.get_task(task_id)["state"] == STATE_PLAN_REVIEW

    # Critic review runs inside PLAN_REVIEW; Gate 1 signs PLAN_REVIEW -> APPROVED
    cp.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="External review passed")
    coord.coordinate_transition(
        task_id=task_id, to_state="APPROVED", actor="human",
        reason="User approved reviewed plan", interactive=True,
    )
    assert cp.get_task(task_id)["state"] == "APPROVED"


def test_skip_multi_agent_review_gate(tmp_path, monkeypatch):
    """Schema v15 10-state flow: user skips review inside PLAN_REVIEW and approves via Gate 1."""
    db_file = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_file)
    cp.repo_root = tmp_path
    cp.init_db()

    task_id = "test-bundle-002"
    cp.create_task(task_id=task_id, title="Test Skip Gate", runtime_tool="claude")

    from control_plane.coordinator import TransitionCoordinator
    from control_plane.registry import TransitionRegistry
    reg = TransitionRegistry.load_default()
    inputs = iter(["1"])
    coord = TransitionCoordinator(control_plane=cp, registry=reg, input_fn=lambda prompt: next(inputs))
    monkeypatch.setattr(coord, "_resolve_repo_root", lambda: tmp_path)

    coord.coordinate_transition(
        task_id=task_id, to_state=STATE_DRAFT_PLAN, actor="human",
        reason="Intake outline confirmed", interactive=True,
    )
    plan_dir = tmp_path / "docs" / "plans" / "work-tasks" / task_id
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / f"{task_id}-spec.md").write_text("# Test specification\n", encoding="utf-8")
    (plan_dir / f"{task_id}-implementation-plan.md").write_text("# Test implementation plan\n\n- Strategy: direct\n", encoding="utf-8")

    coord.coordinate_transition(
        task_id=task_id, to_state=STATE_PLAN_REVIEW, actor="agent",
        reason="Submit plan", interactive=True,
    )
    cp.record_review_skip(task_id=task_id, phase="multi_agent_review", actor="user", reason="User opted to skip multi-agent review")
    coord.coordinate_transition(
        task_id=task_id, to_state="APPROVED", actor="human",
        reason="User approved unreviewed plan", interactive=True,
    )
    assert cp.get_task(task_id)["state"] == "APPROVED"
