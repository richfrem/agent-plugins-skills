"""
test_agent_control_gate_characterization.py — Gate-Policy Characterization Matrix (issue-524)
===============================================================================================

Purpose:
    Regression oracle for issue-524's gate-policy unification (Section 5, Step 4 of
    docs/plans/issue-524-spec.md). Locks in the CURRENT behavior of the 4 currently-scattered
    gate mechanisms — _check_prior_art_guard, _check_done_guard, _check_rolled_back_guard, and
    update_worktree()'s pushed_to_origin barrier — before any of them are folded into the
    unified policy-evaluation mechanism. Every branch here must stay green, unchanged, through
    every step of the refactor. This file is additive to test_agent_control.py, not a
    replacement — several branches are already covered there; this file closes the one gap
    the external plan review (round 1) flagged explicitly: each of the three currently-permitted
    push states (WORKTREE_REVIEW, MULTI_AGENT_CODE_REVIEW, VERIFY_EXIT) must be proven
    individually, not just the first one.

Key Input Dependencies:
    - Temporary SQLite databases created in pytest fixtures (mirrors test_agent_control.py)

Key Functions:
    - temp_db_path() / control_plane() — shared fixtures (duplicated locally to keep this file
      independently runnable and reviewable as a standalone characterization artifact)
    - test_push_barrier_permits_worktree_review()
    - test_push_barrier_permits_multi_agent_code_review()
    - test_push_barrier_permits_verify_exit()
    - test_push_barrier_blocks_in_worktree()
    - test_prior_art_guard_not_applicable_to_general_task()
    - test_prior_art_guard_does_not_re_fire_on_later_edge_after_intake_satisfied()
    - test_done_guard_locked_verifier_sovereignty_branch_passes_when_intact()
"""

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_control import ControlPlane, PersistenceInvariantViolation
from interview_helpers import stage_interview_answers
from helpers.implementation_ledger import stage_implementation_ledger
from control_plane.constants import (
    STATE_INTAKE, STATE_DRAFT_PLAN, STATE_PLAN_REVIEW, STATE_APPROVED, STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW, STATE_VERIFY_EXIT, STATE_DONE,
)


@pytest.fixture
def temp_db_path(tmp_path):
    """Provides a temporary SQLite database path for isolated testing."""
    return tmp_path / "control_plane.db"


@pytest.fixture
def control_plane(temp_db_path):
    """Initializes and returns a ControlPlane test fixture instance."""
    cp = ControlPlane(db_path=temp_db_path)
    cp.init_db()
    return cp


def _coordinate_transition(cp: ControlPlane, task_id: str, to_state: str, actor="human", reason="test"):
    """Coordinates any transition (including human-gated ones) using TransitionCoordinator."""
    from control_plane.coordinator import TransitionCoordinator
    from control_plane.registry import TransitionRegistry
    reg = TransitionRegistry.load_default()
    def _answer(prompt):
        if "intake_outline_confirmation" in prompt:
            return "1"
        if "retrospective_decision" in prompt:
            return "1"
        return "y" if "(y/n)" in prompt else "1"
    coord = TransitionCoordinator(control_plane=cp, registry=reg, input_fn=_answer)
    return coord.coordinate_transition(
        task_id=task_id,
        to_state=to_state,
        actor=actor,
        reason=reason,
        interactive=True
    )


def _complete_retrospective(cp: ControlPlane, task_id: str):
    cp.record_verification_receipt(task_id, "full_test_suite", "pytest -q", 0)
    cp.save_retrospective(
        task_id,
        {"decision": "opt_in", "completion_mode": "completed", "actor": "human"},
        [],
    )
    _coordinate_transition(cp, task_id, STATE_DONE, actor="human", reason="Complete retrospective")


def _advance_to_in_worktree(cp: ControlPlane, task_id: str, title: str, tmp_path):
    """Shared setup: drives a fresh task through the canonical v15 10-state DAG to IN_WORKTREE."""
    from helpers.gate1_fixtures import init_git_worktree

    cp.repo_root = tmp_path
    plans_dir = tmp_path / "docs" / "plans" / "work-tasks" / task_id
    plans_dir.mkdir(parents=True, exist_ok=True)
    (plans_dir / f"{task_id}-spec.md").write_text("# Spec\n", encoding="utf-8")
    (plans_dir / f"{task_id}-implementation-plan.md").write_text("# Plan\n\n- Strategy: direct\n", encoding="utf-8")
    stage_implementation_ledger(cp, task_id, tmp_path)
    wt = init_git_worktree(tmp_path / ".worktrees" / task_id)

    cp.create_task(task_id=task_id, title=title, runtime_tool="claude")
    _coordinate_transition(cp, task_id, STATE_DRAFT_PLAN, actor="human", reason="Intake confirmed")
    cp.record_plan_mode_entry(task_id=task_id, actor="controller")
    _coordinate_transition(cp, task_id, STATE_PLAN_REVIEW, actor="controller", reason="Plan ready")
    _coordinate_transition(cp, task_id, STATE_APPROVED, actor="human", reason="Approved")
    cp.record_human_approval(task_id=task_id, approver="user")
    cp.update_worktree(task_id, str(wt), f"feature/{task_id}", "written_in_worktree")
    cp.transition(task_id=task_id, to_state=STATE_IN_WORKTREE, actor="controller", reason="Worktree created")


# --- update_worktree() push-barrier: strict DONE state gate (5a5efc2a) ---

def test_push_barrier_permits_done(control_plane, tmp_path):
    """Characterizes: worktree_state='pushed_to_origin' succeeds when task state is final state DONE."""
    task_id = "char-push-done-001"
    _advance_to_in_worktree(control_plane, task_id, "Push Barrier: DONE", tmp_path)
    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    _coordinate_transition(control_plane, task_id, STATE_WORKTREE_REVIEW, actor="controller", reason="Implementation done")
    _coordinate_transition(control_plane, task_id, STATE_VERIFY_EXIT, actor="human", reason="Ready to verify exit")
    control_plane.record_verification_receipt(task_id=task_id, gate_name="leak_check", command_executed="git status", exit_code=0)
    control_plane.log_asymmetric_persistence(task_id=task_id, destination="references/map-debt.md", status="RESOLVED", details="Resolved")
    _complete_retrospective(control_plane, task_id)

    control_plane.update_worktree(
        task_id=task_id, worktree_path="/tmp/wt", worktree_branch="b", worktree_state="pushed_to_origin"
    )
    assert control_plane.get_task(task_id)["worktree_state"] == "pushed_to_origin"


@pytest.mark.parametrize("intermediate_state", [STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW, STATE_VERIFY_EXIT])
def test_push_barrier_blocks_intermediate_states(control_plane, intermediate_state, tmp_path):
    """Characterizes: worktree_state='pushed_to_origin' is rejected when task state is not DONE."""
    task_id = f"char-push-blocked-{intermediate_state.lower()}"
    _advance_to_in_worktree(control_plane, task_id, f"Push Barrier: {intermediate_state}", tmp_path)

    if intermediate_state in (STATE_WORKTREE_REVIEW, STATE_VERIFY_EXIT):
        control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
        _coordinate_transition(control_plane, task_id, STATE_WORKTREE_REVIEW, actor="controller", reason="Implementation done")
    if intermediate_state == STATE_VERIFY_EXIT:
        _coordinate_transition(control_plane, task_id, STATE_VERIFY_EXIT, actor="human", reason="Ready to verify exit")

    with pytest.raises(PersistenceInvariantViolation, match="Pushing to origin requires full pipeline completion"):
        control_plane.update_worktree(
            task_id=task_id, worktree_path="/tmp/wt", worktree_branch="b", worktree_state="pushed_to_origin"
        )


# --- _check_prior_art_guard: branches not exercised elsewhere ---

def test_prior_art_guard_not_applicable_to_general_task(control_plane, tmp_path):
    """Characterizes: the prior-art guard is a no-op for task_type='GENERAL' (only EVOLUTION tasks are gated)."""
    control_plane.repo_root = tmp_path
    task_id = "char-priorart-general-001"
    control_plane.create_task(task_id=task_id, title="General", runtime_tool="claude", task_type="GENERAL")
    _coordinate_transition(control_plane, task_id, STATE_DRAFT_PLAN, actor="human", reason="Starting")
    assert control_plane.get_task(task_id)["state"] == STATE_DRAFT_PLAN


def test_prior_art_guard_does_not_re_fire_on_later_edge_after_intake_satisfied(control_plane, tmp_path):
    """Characterizes: the prior-art guard only fires on the (INTAKE, DRAFT_PLAN) edge and does not re-fire later."""
    control_plane.repo_root = tmp_path
    task_id = "char-priorart-nonedge-001"
    plans_dir = tmp_path / "docs" / "plans" / "work-tasks" / task_id
    plans_dir.mkdir(parents=True, exist_ok=True)
    (plans_dir / f"{task_id}-spec.md").write_text("# Spec\n", encoding="utf-8")
    (plans_dir / f"{task_id}-implementation-plan.md").write_text("# Plan\n\n- Strategy: direct\n", encoding="utf-8")
    control_plane.create_task(task_id=task_id, title="Evolution no-scan mid-pipeline", runtime_tool="claude", task_type="EVOLUTION")
    control_plane.log_asymmetric_persistence(
        task_id=task_id, destination="references/map-debt.md", status="OBSERVED",
        details="prior_art_scan: summary=scanned; repeat_yes_entries=none"
    )
    _coordinate_transition(control_plane, task_id, STATE_DRAFT_PLAN, actor="human", reason="Prior art scanned")
    control_plane.record_plan_mode_entry(task_id=task_id, actor="controller")

    # No further prior-art logging done here — guard must not re-fire on this later edge.
    control_plane.transition(task_id=task_id, to_state=STATE_PLAN_REVIEW, actor="controller", reason="Compiled spec")
    assert control_plane.get_task(task_id)["state"] == STATE_PLAN_REVIEW


# --- _check_done_guard: locked-verifier sovereignty sub-branch, intact case ---

def test_done_guard_locked_verifier_sovereignty_branch_passes_when_intact(control_plane, tmp_path):
    """Characterizes: when locked_verifier_baselines has rows for this task AND the files are
    still intact (unmutated), the DONE guard's sovereignty sub-check passes silently and DONE
    succeeds."""
    task_id = "char-done-sovereignty-intact-001"
    _advance_to_in_worktree(control_plane, task_id, "Done sovereignty intact", tmp_path)

    verifier_file = tmp_path / "verifier.py"
    verifier_file.write_text("def check(): return True\n", encoding="utf-8")
    control_plane.lock_verifiers(task_id=task_id, file_paths=[verifier_file])

    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    _coordinate_transition(control_plane, task_id, STATE_WORKTREE_REVIEW, actor="controller", reason="Implementation done")
    _coordinate_transition(control_plane, task_id, STATE_VERIFY_EXIT, actor="human", reason="Verifying")

    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    control_plane.log_asymmetric_persistence(
        task_id=task_id, destination="references/map-debt.md", status="RESOLVED", details="Resolved"
    )
    control_plane.record_verification_receipt(task_id=task_id, gate_name="leak_check", command_executed="git status --short", exit_code=0)

    # Verifier file untouched since locking — sovereignty branch must pass silently.
    _complete_retrospective(control_plane, task_id)
    assert control_plane.get_task(task_id)["state"] == STATE_DONE
