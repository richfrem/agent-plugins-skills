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


def _advance_to_in_worktree(cp: ControlPlane, task_id: str, title: str):
    """Shared setup: drives a fresh task through the canonical DAG to IN_WORKTREE."""
    cp.create_task(task_id=task_id, title=title, runtime_tool="claude")
    cp.record_plan_mode_entry(task_id=task_id, actor="controller")
    cp.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="controller", reason="Plan ready")
    cp.record_review_skip(task_id=task_id, phase="multi_agent_review", actor="user", reason="characterization test")
    cp.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="controller", reason="Review ready")
    cp.transition(task_id=task_id, to_state="APPROVED", actor="user", reason="Approved")
    cp.record_human_approval(task_id=task_id, approver="user")
    cp.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree created")


# --- update_worktree() push-barrier: each permitted state proven individually ---

def test_push_barrier_permits_worktree_review(control_plane):
    """Characterizes: worktree_state='pushed_to_origin' succeeds when task state is WORKTREE_REVIEW."""
    task_id = "char-push-wr-001"
    _advance_to_in_worktree(control_plane, task_id, "Push Barrier: WORKTREE_REVIEW")
    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    control_plane.transition(task_id=task_id, to_state="WORKTREE_REVIEW", actor="controller", reason="Implementation done")

    control_plane.update_worktree(
        task_id=task_id, worktree_path="/tmp/wt", worktree_branch="b", worktree_state="pushed_to_origin"
    )
    assert control_plane.get_task(task_id)["worktree_state"] == "pushed_to_origin"


def test_push_barrier_permits_multi_agent_code_review(control_plane):
    """Characterizes: worktree_state='pushed_to_origin' succeeds when task state is MULTI_AGENT_CODE_REVIEW."""
    task_id = "char-push-macr-001"
    _advance_to_in_worktree(control_plane, task_id, "Push Barrier: MULTI_AGENT_CODE_REVIEW")
    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    control_plane.transition(task_id=task_id, to_state="WORKTREE_REVIEW", actor="controller", reason="Implementation done")
    control_plane.transition(task_id=task_id, to_state="MULTI_AGENT_CODE_REVIEW", actor="controller", reason="Adversarial code review")

    control_plane.update_worktree(
        task_id=task_id, worktree_path="/tmp/wt", worktree_branch="b", worktree_state="pushed_to_origin"
    )
    assert control_plane.get_task(task_id)["worktree_state"] == "pushed_to_origin"


def test_push_barrier_permits_verify_exit(control_plane):
    """Characterizes: worktree_state='pushed_to_origin' succeeds when task state is VERIFY_EXIT."""
    task_id = "char-push-vx-001"
    _advance_to_in_worktree(control_plane, task_id, "Push Barrier: VERIFY_EXIT")
    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    control_plane.transition(task_id=task_id, to_state="WORKTREE_REVIEW", actor="controller", reason="Implementation done")
    control_plane.record_review_skip(task_id=task_id, phase="multi_agent_code_review", actor="user", reason="characterization test")
    control_plane.transition(task_id=task_id, to_state="VERIFY_EXIT", actor="controller", reason="Ready to verify exit")

    control_plane.update_worktree(
        task_id=task_id, worktree_path="/tmp/wt", worktree_branch="b", worktree_state="pushed_to_origin"
    )
    assert control_plane.get_task(task_id)["worktree_state"] == "pushed_to_origin"


def test_push_barrier_blocks_in_worktree(control_plane):
    """Characterizes: worktree_state='pushed_to_origin' is rejected when task state is IN_WORKTREE
    (the blocked case — any state outside {WORKTREE_REVIEW, MULTI_AGENT_CODE_REVIEW, VERIFY_EXIT})."""
    task_id = "char-push-blocked-001"
    _advance_to_in_worktree(control_plane, task_id, "Push Barrier: blocked")

    with pytest.raises(PersistenceInvariantViolation, match="Post-implementation review stage gate required"):
        control_plane.update_worktree(
            task_id=task_id, worktree_path="/tmp/wt", worktree_branch="b", worktree_state="pushed_to_origin"
        )


# --- _check_prior_art_guard: branches not exercised elsewhere ---

def test_prior_art_guard_not_applicable_to_general_task(control_plane):
    """Characterizes: the prior-art guard is a no-op for task_type='GENERAL' (only EVOLUTION
    tasks are gated) — already exercised end-to-end in test_agent_control.py's
    test_general_task_advances_without_prior_art_scan; restated here as part of the
    consolidated matrix this file exists to be."""
    task_id = "char-priorart-general-001"
    control_plane.create_task(task_id=task_id, title="General", runtime_tool="claude", task_type="GENERAL")
    control_plane.transition(task_id=task_id, to_state="INTERVIEW", actor="user", reason="Starting")
    assert control_plane.get_task(task_id)["state"] == "INTERVIEW"


def test_prior_art_guard_does_not_re_fire_on_later_edge_after_intake_satisfied(control_plane):
    """Characterizes: the prior-art guard only fires on the (INTAKE, INTERVIEW) edge. This test
    proves the guard does NOT re-run on a later edge (INTERVIEW->DRAFT_PLAN) once the INTAKE
    gate was already satisfied — it does NOT prove the task has no prior-art log at all (prior
    art IS logged here, before entering INTERVIEW, to legitimately clear that first gate).
    Renamed/reworded after external review correctly flagged the original name/docstring
    ("no prior-art scan logged") as inaccurate — the scan is logged, just not re-logged for the
    second transition, which is the actual behavior being characterized."""
    task_id = "char-priorart-nonedge-001"
    control_plane.create_task(task_id=task_id, title="Evolution no-scan mid-pipeline", runtime_tool="claude", task_type="EVOLUTION")
    control_plane.log_asymmetric_persistence(
        task_id=task_id, destination="references/map-debt.md", status="OBSERVED",
        details="prior_art_scan: summary=scanned; repeat_yes_entries=none"
    )
    control_plane.transition(task_id=task_id, to_state="INTERVIEW", actor="controller", reason="Prior art scanned")
    control_plane.record_plan_mode_entry(task_id=task_id, actor="controller")

    # No further prior-art logging done here — guard must not re-fire on this later edge.
    control_plane.transition(task_id=task_id, to_state="DRAFT_PLAN", actor="controller", reason="Compiled spec")
    assert control_plane.get_task(task_id)["state"] == "DRAFT_PLAN"


# --- _check_done_guard: locked-verifier sovereignty sub-branch, intact case ---

def test_done_guard_locked_verifier_sovereignty_branch_passes_when_intact(control_plane, tmp_path):
    """Characterizes: when locked_verifier_baselines has rows for this task AND the files are
    still intact (unmutated), the DONE guard's sovereignty sub-check passes silently and DONE
    succeeds — the positive path through `if locked_count > 0: self.verify_sovereignty(task_id)`
    that test_agent_control.py only exercises via the mutated/failing branch."""
    task_id = "char-done-sovereignty-intact-001"
    control_plane.create_task(task_id=task_id, title="Done sovereignty intact", runtime_tool="claude")

    verifier_file = tmp_path / "verifier.py"
    verifier_file.write_text("def check(): return True\n", encoding="utf-8")
    control_plane.lock_verifiers(task_id=task_id, file_paths=[verifier_file])

    control_plane.record_plan_mode_entry(task_id=task_id, actor="controller")
    control_plane.transition(task_id=task_id, to_state="PLAN_REVIEW", actor="controller", reason="Plan ready")
    control_plane.record_review_skip(task_id=task_id, phase="multi_agent_review", actor="user", reason="characterization test")
    control_plane.transition(task_id=task_id, to_state="AWAITING_APPROVAL", actor="controller", reason="Review ready")
    control_plane.transition(task_id=task_id, to_state="APPROVED", actor="user", reason="Approved")
    control_plane.record_human_approval(task_id=task_id, approver="user")
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree created")
    control_plane.transition(task_id=task_id, to_state="VERIFY_EXIT", actor="controller", reason="Verifying")

    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    control_plane.log_asymmetric_persistence(
        task_id=task_id, destination="references/map-debt.md", status="RESOLVED", details="Resolved"
    )
    control_plane.record_verification_receipt(task_id=task_id, gate_name="leak_check", command_executed="git status --short", exit_code=0)

    # Verifier file untouched since locking — sovereignty branch must pass silently.
    control_plane.transition(task_id=task_id, to_state="DONE", actor="controller", reason="All exit gates passed")
    assert control_plane.get_task(task_id)["state"] == "DONE"
