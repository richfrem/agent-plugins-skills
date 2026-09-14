"""
helpers/control_plane_fixtures.py
=================================

Provides isolated test state setup for ControlPlane test suites,
avoiding polluting production ControlPlane with test helpers.
"""

from typing import Optional
from agent_control import ControlPlane


def create_task_in_state(
    control_plane: ControlPlane,
    task_id: str,
    target_state: str,
    title: str = "Test Task",
    runtime_tool: str = "claude",
    spec_path: Optional[str] = None,
) -> None:
    """Helper to transition a task to target_state for testing."""
    control_plane.create_task(
        task_id=task_id,
        title=title,
        runtime_tool=runtime_tool,
        spec_path=spec_path,
    )
    if target_state == "INTAKE":
        return

    # Inbound path to INTERVIEW
    control_plane.transition(task_id, "INTERVIEW", "tester", "setup interview")
    if target_state == "INTERVIEW":
        return

    # To DRAFT_PLAN
    control_plane.record_plan_mode_entry(task_id, "tester")
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "setup draft plan")
    if target_state == "DRAFT_PLAN":
        return

    if target_state == "MULTI_AGENT_REVIEW":
        control_plane.transition(task_id, "MULTI_AGENT_REVIEW", "tester", "setup multi agent review")
        return

    if target_state == "PLAN_REVIEW":
        control_plane.transition(task_id, "PLAN_REVIEW", "tester", "setup plan review")
        return

    if target_state == "AWAITING_APPROVAL":
        control_plane.record_review_skip(task_id, "multi_agent_review", "tester", "skip review")
        control_plane.transition(task_id, "AWAITING_APPROVAL", "tester", "setup awaiting approval")
        return

    if target_state == "APPROVED":
        control_plane.record_review_skip(task_id, "multi_agent_review", "tester", "skip review")
        control_plane.transition(task_id, "AWAITING_APPROVAL", "tester", "setup awaiting approval")
        control_plane.transition(task_id, "APPROVED", "approver", "setup approved")
        return

    if target_state == "IN_WORKTREE":
        control_plane.record_review_skip(task_id, "multi_agent_review", "tester", "skip review")
        control_plane.transition(task_id, "AWAITING_APPROVAL", "tester", "setup awaiting approval")
        control_plane.transition(task_id, "APPROVED", "approver", "setup approved")
        control_plane.record_human_approval(task_id, "approver")
        control_plane.update_worktree(task_id, f".worktrees/{task_id}", f"feature/{task_id}", "written_in_worktree")
        control_plane.transition(task_id, "IN_WORKTREE", "tester", "setup worktree")
        return
