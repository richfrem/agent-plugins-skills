"""
helpers/control_plane_fixtures.py
=================================

Provides isolated test state setup for ControlPlane test suites,
avoiding polluting production ControlPlane with test helpers.
"""

from typing import Optional
from agent_control import ControlPlane
from control_plane.constants import STATE_ABSORBED_BY


def create_task_in_state(
    control_plane: ControlPlane,
    task_id: str,
    target_state: str,
    title: str = "Test Task",
    runtime_tool: str = "claude",
    spec_path: Optional[str] = None,
) -> None:
    """Helper to transition a task to target_state (10-state v15 machine) for testing."""
    # Map legacy v14 retired state names to their absorbing v15 state when callers pass them.
    resolved = STATE_ABSORBED_BY.get(target_state, target_state)

    control_plane.create_task(
        task_id=task_id,
        title=title,
        runtime_tool=runtime_tool,
        spec_path=spec_path,
    )
    if resolved == "INTAKE":
        return

    # INTAKE -> DRAFT_PLAN
    control_plane.record_plan_mode_entry(task_id, "tester")
    control_plane.transition(task_id, "DRAFT_PLAN", "tester", "setup draft plan")
    if resolved == "DRAFT_PLAN":
        return

    # DRAFT_PLAN -> PLAN_REVIEW
    control_plane.transition(task_id, "PLAN_REVIEW", "tester", "setup plan review")
    if resolved == "PLAN_REVIEW":
        return

    if resolved == "APPROVED":
        control_plane.transition(task_id, "APPROVED", "approver", "setup approved")
        return

    if resolved == "IN_WORKTREE":
        control_plane.transition(task_id, "APPROVED", "approver", "setup approved")
        control_plane.record_human_approval(task_id, "approver")
        control_plane.update_worktree(task_id, f".worktrees/{task_id}", f"feature/{task_id}", "written_in_worktree")
        control_plane.transition(task_id, "IN_WORKTREE", "tester", "setup worktree")
        return

    if resolved == "WORKTREE_REVIEW":
        control_plane.transition(task_id, "APPROVED", "approver", "setup approved")
        control_plane.record_human_approval(task_id, "approver")
        control_plane.update_worktree(task_id, f".worktrees/{task_id}", f"feature/{task_id}", "written_in_worktree")
        control_plane.transition(task_id, "IN_WORKTREE", "tester", "setup worktree")
        control_plane.record_verification_receipt(task_id, "test_suite_deferred_to_review", "deferred", 0)
        control_plane.transition(task_id, "WORKTREE_REVIEW", "tester", "setup worktree review")
        return
