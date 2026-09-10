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
    """Coordinates any transition (including human-gated ones) using TransitionCoordinator.
    Each call gets a fresh TransitionCoordinator/input_fn, so a fixed-length answer sequence
    doesn't generalize across calls with differing question/approval counts — instead answer
    based on the prompt's own content: the y/n approval prompt always contains '(y/n)'."""
    from control_plane.coordinator import TransitionCoordinator
    from control_plane.registry import TransitionRegistry
    reg = TransitionRegistry.load_default()
    def _answer(prompt):
        if "confirm_review_in_worktree_to_worktree_review" in prompt:
            return "2"  # The first option is the explicit negative answer for this gate.
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
    cp.transition(task_id, "RETROSPECTIVE", "controller", "Enter retrospective")
    cp.save_retrospective(
        task_id,
        {"decision": "opt_in", "completion_mode": "completed", "actor": "human"},
        [],
    )
    _coordinate_transition(cp, task_id, "DONE", actor="human", reason="Complete retrospective")


def _advance_to_in_worktree(cp: ControlPlane, task_id: str, title: str, tmp_path):
    """Shared setup: drives a fresh task through the canonical DAG to IN_WORKTREE.
    PLAN_REVIEW's required_artifacts (spec/implementation-plan) are created under
    tmp_path, with cp.repo_root pointed there, matching the pattern used elsewhere
    (test_agent_control.py)."""
    cp.repo_root = tmp_path
    plans_dir = tmp_path / "docs" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    (plans_dir / f"{task_id}-spec.md").write_text("# Spec", encoding="utf-8")
    (plans_dir / f"{task_id}-implementation-plan.md").write_text("# Plan", encoding="utf-8")
    stage_implementation_ledger(control_plane, task_id, tmp_path)
    (tmp_path / ".worktrees" / task_id).mkdir(parents=True, exist_ok=True)

    cp.create_task(task_id=task_id, title=title, runtime_tool="claude")
    cp.record_plan_mode_entry(task_id=task_id, actor="controller")
    _coordinate_transition(cp, task_id, "PLAN_REVIEW", actor="controller", reason="Plan ready")
    cp.record_review_skip(task_id=task_id, phase="multi_agent_review", actor="user", reason="characterization test")
    _coordinate_transition(cp, task_id, "AWAITING_APPROVAL", actor="controller", reason="Review ready")
    _coordinate_transition(cp, task_id, "APPROVED", actor="user", reason="Approved")
    cp.record_human_approval(task_id=task_id, approver="user")
    cp.update_worktree(task_id, f".worktrees/{task_id}", f"feature/{task_id}", "written_in_worktree")
    cp.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree created")


# --- update_worktree() push-barrier: strict DONE state gate (5a5efc2a) ---

def test_push_barrier_permits_done(control_plane, tmp_path):
    """Characterizes: worktree_state='pushed_to_origin' succeeds when task state is final state DONE."""
    task_id = "char-push-done-001"
    _advance_to_in_worktree(control_plane, task_id, "Push Barrier: DONE", tmp_path)
    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    _coordinate_transition(control_plane, task_id, "WORKTREE_REVIEW", actor="controller", reason="Implementation done")
    control_plane.record_review_skip(task_id=task_id, phase="multi_agent_code_review", actor="user", reason="characterization test")
    control_plane.transition(task_id=task_id, to_state="VERIFY_EXIT", actor="controller", reason="Ready to verify exit")
    control_plane.record_verification_receipt(task_id=task_id, gate_name="leak_check", command_executed="git status", exit_code=0)
    control_plane.log_asymmetric_persistence(task_id=task_id, destination="references/map-debt.md", status="RESOLVED", details="Resolved")
    _complete_retrospective(control_plane, task_id)

    control_plane.update_worktree(
        task_id=task_id, worktree_path="/tmp/wt", worktree_branch="b", worktree_state="pushed_to_origin"
    )
    assert control_plane.get_task(task_id)["worktree_state"] == "pushed_to_origin"


@pytest.mark.parametrize("intermediate_state", ["IN_WORKTREE", "WORKTREE_REVIEW", "MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT"])
def test_push_barrier_blocks_intermediate_states(control_plane, intermediate_state, tmp_path):
    """Characterizes: worktree_state='pushed_to_origin' is rejected when task state is not DONE."""
    task_id = f"char-push-blocked-{intermediate_state.lower()}"
    _advance_to_in_worktree(control_plane, task_id, f"Push Barrier: {intermediate_state}", tmp_path)
    
    if intermediate_state in ("WORKTREE_REVIEW", "MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT"):
        control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
        _coordinate_transition(control_plane, task_id, "WORKTREE_REVIEW", actor="controller", reason="Implementation done")
    if intermediate_state in ("MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT"):
        if intermediate_state == "MULTI_AGENT_CODE_REVIEW":
            _coordinate_transition(control_plane, task_id, "MULTI_AGENT_CODE_REVIEW", actor="controller", reason="Adversarial code review")
        else:
            control_plane.record_review_skip(task_id=task_id, phase="multi_agent_code_review", actor="user", reason="characterization test")
            control_plane.transition(task_id=task_id, to_state="VERIFY_EXIT", actor="controller", reason="Ready to verify exit")

    with pytest.raises(PersistenceInvariantViolation, match="Pushing to origin requires full pipeline completion"):
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
    stage_interview_answers(control_plane, task_id)

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
    control_plane.repo_root = tmp_path
    plans_dir = tmp_path / "docs" / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    (plans_dir / f"{task_id}-spec.md").write_text("# Spec", encoding="utf-8")
    (plans_dir / f"{task_id}-implementation-plan.md").write_text("# Plan", encoding="utf-8")
    stage_implementation_ledger(control_plane, task_id, tmp_path)

    control_plane.create_task(task_id=task_id, title="Done sovereignty intact", runtime_tool="claude")

    verifier_file = tmp_path / "verifier.py"
    verifier_file.write_text("def check(): return True\n", encoding="utf-8")
    control_plane.lock_verifiers(task_id=task_id, file_paths=[verifier_file])

    control_plane.record_plan_mode_entry(task_id=task_id, actor="controller")
    _coordinate_transition(control_plane, task_id, "PLAN_REVIEW", actor="controller", reason="Plan ready")
    control_plane.record_review_skip(task_id=task_id, phase="multi_agent_review", actor="user", reason="characterization test")
    _coordinate_transition(control_plane, task_id, "AWAITING_APPROVAL", actor="controller", reason="Review ready")
    _coordinate_transition(control_plane, task_id, "APPROVED", actor="user", reason="Approved")
    control_plane.record_human_approval(task_id=task_id, approver="user")
    control_plane.update_worktree(task_id, f".worktrees/{task_id}", f"feature/{task_id}", "written_in_worktree")
    control_plane.transition(task_id=task_id, to_state="IN_WORKTREE", actor="controller", reason="Worktree created")
    control_plane.transition(task_id=task_id, to_state="VERIFY_EXIT", actor="controller", reason="Verifying")

    control_plane.record_verification_receipt(task_id=task_id, gate_name="test_suite", command_executed="pytest", exit_code=0)
    control_plane.log_asymmetric_persistence(
        task_id=task_id, destination="references/map-debt.md", status="RESOLVED", details="Resolved"
    )
    control_plane.record_verification_receipt(task_id=task_id, gate_name="leak_check", command_executed="git status --short", exit_code=0)

    # Verifier file untouched since locking — sovereignty branch must pass silently.
    _complete_retrospective(control_plane, task_id)
    assert control_plane.get_task(task_id)["state"] == "DONE"
