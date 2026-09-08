"""Test multi-agent bundle gate transitions and Socratic cadence constraints."""
import sys
from pathlib import Path
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_control import ControlPlane, CANONICAL_STATES, InvalidStateTransition
from interview_helpers import stage_interview_answers

def test_draft_plan_and_multi_agent_review_states_exist():
    assert "DRAFT_PLAN" in CANONICAL_STATES
    assert "MULTI_AGENT_REVIEW" in CANONICAL_STATES

def test_full_intake_to_approval_lifecycle(tmp_path, monkeypatch):
    db_file = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_file)
    cp.init_db()
    
    task_id = "test-bundle-001"
    cp.create_task(task_id=task_id, title="Test Bundle Gate", runtime_tool="antigravity")
    
    # INTAKE -> INTERVIEW
    cp.transition(task_id=task_id, to_state="INTERVIEW", actor="user", reason="1-question-at-a-time interview")
    assert cp.get_task(task_id)["state"] == "INTERVIEW"
    
    # INTERVIEW -> DRAFT_PLAN
    cp.record_plan_mode_entry(task_id=task_id, actor="agent")
    stage_interview_answers(cp, task_id)
    cp.transition(task_id=task_id, to_state="DRAFT_PLAN", actor="agent", reason="Compiled draft spec and plan")
    assert cp.get_task(task_id)["state"] == "DRAFT_PLAN"

    # Task 1's artifact gate is intentional: provide real test-local artifacts
    # instead of weakening the DRAFT_PLAN review contract.
    plan_dir = tmp_path / "docs" / "plans"
    plan_dir.mkdir(parents=True)
    (plan_dir / f"{task_id}-spec.md").write_text("# Test specification\n", encoding="utf-8")
    (plan_dir / f"{task_id}-implementation-plan.md").write_text("# Test implementation plan\n", encoding="utf-8")

    # Path A: DRAFT_PLAN -> MULTI_AGENT_REVIEW -> AWAITING_APPROVAL
    from control_plane.coordinator import TransitionCoordinator
    from control_plane.registry import TransitionRegistry
    reg = TransitionRegistry.load_default()
    inputs = iter(["5"])  # Option 5: external bundle
    coord = TransitionCoordinator(control_plane=cp, registry=reg, input_fn=lambda prompt: next(inputs))
    monkeypatch.setattr(coord, "_resolve_repo_root", lambda: tmp_path)
    coord.coordinate_transition(
        task_id=task_id,
        to_state="MULTI_AGENT_REVIEW",
        actor="human",
        reason="User opted for external review bundle",
        interactive=True
    )
    assert cp.get_task(task_id)["state"] == "MULTI_AGENT_REVIEW"

    cp.record_critic_review(task_id=task_id, iteration=1, model="gpt-5-mini", verdict="PASS", findings="External review passed")
    cp.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="user", reason="External review iterations complete")
    assert cp.get_task(task_id)["state"] == "AWAITING_APPROVAL"

def test_skip_multi_agent_review_gate(tmp_path):
    db_file = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_file)
    cp.init_db()
    
    task_id = "test-bundle-002"
    cp.create_task(task_id=task_id, title="Test Skip Gate", runtime_tool="claude")
    
    cp.transition(task_id=task_id, to_state="INTERVIEW", actor="user", reason="Interviewing")
    cp.record_plan_mode_entry(task_id=task_id, actor="agent")
    stage_interview_answers(cp, task_id)
    cp.transition(task_id=task_id, to_state="DRAFT_PLAN", actor="agent", reason="Draft compiled")

    # Path B: User skips directly to AWAITING_APPROVAL
    cp.record_review_skip(task_id=task_id, phase="multi_agent_review", actor="user", reason="User opted to skip multi-agent review")
    cp.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="user", reason="User opted to skip multi-agent review")
    assert cp.get_task(task_id)["state"] == "AWAITING_APPROVAL"
