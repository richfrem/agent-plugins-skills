"""
test_pre_commit_pipeline_guard.py — Deterministic Pipeline Execution & Stage Gate Tests
========================================================================================

Purpose:
    Tests the git pre-commit pipeline execution guard (`pre-commit-pipeline-guard`) and the
    policy engine operation rule (`OPERATION_RULES["commit"]`).
    Validates:
    - Bypasses non-task branches (main, master, untracked) with exit 0.
    - Permits planning documentation commits (docs/plans/*, docs/superpowers/*) during proposal mode.
    - Blocks code commits during proposal mode (INTAKE, INTERVIEW, DRAFT_PLAN, etc.) with exit 1.
    - Permits commits during implementation (IN_WORKTREE, WORKTREE_REVIEW, etc.) when pipeline
      execution history is valid and contiguous.
    - Blocks commits if transition_violations are recorded for the task.
    - Blocks commits if transitions in task_transitions do not exist in valid_transitions.
    - Blocks commits if the transition chain is broken (skipped stages).
"""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.adapters import SqlitePersistenceAdapter, FilesystemAdapter
from control_plane.policy import evaluate_operation, PolicyViolation
from agent_control import ControlPlane, PersistenceInvariantViolation
from interview_helpers import stage_interview_answers
from helpers.implementation_ledger import stage_implementation_ledger
from control_plane.constants import (
    STATE_INTERVIEW, STATE_DRAFT_PLAN, STATE_PLAN_REVIEW, STATE_AWAITING_APPROVAL, STATE_APPROVED, STATE_IN_WORKTREE, STATE_WORKTREE_REVIEW, STATE_VERIFY_EXIT, STATE_RETROSPECTIVE, STATE_DONE,
)

HOOK_PATH = SCRIPTS_DIR / "pre-commit-pipeline-guard"


def _setup_git_repo_with_db(tmp_path):
    """Creates a temporary git repository with initialized control_plane.db."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=str(repo), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(repo), check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(repo), check=True)

    # Initial commit so HEAD exists
    readme = repo / "README.md"
    readme.write_text("# Test Repo\n", encoding="utf-8")
    # The control-plane database lives in this repo and changes on every write, so it must be ignored: Gate 3 signs
    # the untracked-files hash, and a churning untracked DB would invalidate every request before it is signed.
    (repo / ".gitignore").write_text("context/\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md", ".gitignore"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(repo), check=True)

    db_path = repo / "context" / "control_plane.db"
    adapter = SqlitePersistenceAdapter(db_path, FilesystemAdapter())
    adapter.ensure_schema()
    return repo, db_path


def _advance_task_to_in_worktree(cp, task_id, repo, branch):
    """Advances task through all required v15 10-state pipeline stages to IN_WORKTREE."""
    from control_plane.coordinator import TransitionCoordinator

    cp.repo_root = repo
    cp.create_task(task_id, f"Task {task_id}", "claude")
    TransitionCoordinator(control_plane=cp, input_fn=lambda _p: "1").coordinate_transition(
        task_id=task_id, to_state=STATE_DRAFT_PLAN, actor="human", reason="Confirm intake outline", interactive=True,
    )
    cp.record_plan_mode_entry(task_id, "tester")
    plans = repo / "docs" / "plans" / "work-tasks" / task_id
    plans.mkdir(parents=True, exist_ok=True)
    (plans / f"{task_id}-spec.md").write_text("# Spec\n", encoding="utf-8")
    (plans / f"{task_id}-implementation-plan.md").write_text("# Plan\n\n- Strategy: direct\n", encoding="utf-8")
    stage_implementation_ledger(cp, task_id, repo)
    TransitionCoordinator(control_plane=cp).coordinate_transition(
        task_id=task_id, to_state=STATE_PLAN_REVIEW, actor="agent", reason="Submit plan for review", interactive=False,
    )
    cp.record_verification_receipt(
        task_id=task_id, gate_name="main_dirty_before_approval_exception",
        command_executed="test-fixture-uses-real-dirty-planning-files", exit_code=0,
    )
    TransitionCoordinator(control_plane=cp).coordinate_transition(
        task_id=task_id, to_state=STATE_APPROVED, actor="human", reason="Approved", interactive=True,
    )
    cp.record_human_approval(task_id, "tester")
    cp.update_worktree(task_id, str(repo), branch, "written_in_worktree")
    cp.record_verification_receipt(
        task_id=task_id, gate_name="existing_worktree_exception",
        command_executed="test-fixture-reuses-repo-as-worktree", exit_code=0,
    )
    cp.transition(task_id, STATE_IN_WORKTREE, "tester", "in worktree")


def test_hook_bypasses_main_branch(tmp_path):
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    res = subprocess.run([str(HOOK_PATH)], cwd=str(repo), capture_output=True, text=True)
    assert res.returncode == 0


def test_hook_bypasses_untracked_branch_with_warning(tmp_path):
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    subprocess.run(["git", "checkout", "-b", "feat/untracked-work"], cwd=str(repo), check=True, capture_output=True)
    res = subprocess.run([str(HOOK_PATH)], cwd=str(repo), capture_output=True, text=True)
    assert res.returncode == 0
    assert "WARNING" in res.stderr
    assert "no task registered for branch 'feat/untracked-work'" in res.stderr


def test_hook_blocks_code_commit_during_planning_states(tmp_path):
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    task_id = "task-planning-001"
    branch = "feat/planning-task"
    subprocess.run(["git", "checkout", "-b", branch], cwd=str(repo), check=True, capture_output=True)

    cp = ControlPlane(db_path=db_path)
    cp.create_task(task_id, "Planning Task", "claude")
    cp.update_worktree(task_id, str(repo), branch, "written_in_worktree")

    # Stage production code
    code_file = repo / "src.py"
    code_file.write_text("print('code')\n", encoding="utf-8")
    subprocess.run(["git", "add", "src.py"], cwd=str(repo), check=True)

    res = subprocess.run([str(HOOK_PATH)], cwd=str(repo), capture_output=True, text=True)
    assert res.returncode == 1
    assert "GIT COMMIT BLOCKED: Proposal Mode Violation!" in res.stdout
    assert "src.py" in res.stdout


def test_hook_allows_plan_doc_commit_during_planning_states(tmp_path):
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    task_id = "task-plan-docs-002"
    branch = "feat/plan-docs-task"
    subprocess.run(["git", "checkout", "-b", branch], cwd=str(repo), check=True, capture_output=True)

    cp = ControlPlane(db_path=db_path)
    cp.repo_root = repo
    cp.create_task(task_id, "Plan Docs Task", "claude")
    from control_plane.coordinator import TransitionCoordinator
    TransitionCoordinator(control_plane=cp, input_fn=lambda _p: "1").coordinate_transition(
        task_id=task_id, to_state=STATE_DRAFT_PLAN, actor="human", reason="draft", interactive=True,
    )
    cp.record_plan_mode_entry(task_id, "tester")
    cp.update_worktree(task_id, str(repo), branch, "written_in_worktree")

    # Stage plan documentation only
    plan_file = repo / "docs" / "plans" / f"{task_id}-spec.md"
    plan_file.parent.mkdir(parents=True, exist_ok=True)
    plan_file.write_text("# Spec\n", encoding="utf-8")
    subprocess.run(["git", "add", "docs/plans/"], cwd=str(repo), check=True)

    res = subprocess.run([str(HOOK_PATH)], cwd=str(repo), capture_output=True, text=True)
    assert res.returncode == 0


def test_hook_allows_code_commit_with_valid_contiguous_history(tmp_path):
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    task_id = "task-valid-exec-003"
    branch = "feat/valid-execution"
    subprocess.run(["git", "checkout", "-b", branch], cwd=str(repo), check=True, capture_output=True)

    cp = ControlPlane(db_path=db_path)
    _advance_task_to_in_worktree(cp, task_id, repo, branch)

    # Stage production code
    code_file = repo / "feature.py"
    code_file.write_text("def run(): pass\n", encoding="utf-8")
    subprocess.run(["git", "add", "feature.py"], cwd=str(repo), check=True)

    res = subprocess.run([str(HOOK_PATH)], cwd=str(repo), capture_output=True, text=True)
    assert res.returncode == 0


def test_hook_blocks_if_transition_violations_exist(tmp_path):
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    task_id = "task-viol-004"
    branch = "feat/viol-task"
    subprocess.run(["git", "checkout", "-b", branch], cwd=str(repo), check=True, capture_output=True)

    cp = ControlPlane(db_path=db_path)
    _advance_task_to_in_worktree(cp, task_id, repo, branch)

    # Log an illegal transition violation directly in DB
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO transition_violations (task_id, attempted_from_state, attempted_to_state) VALUES (?, 'INTAKE', 'IN_WORKTREE')",
        (task_id,)
    )
    conn.commit()
    conn.close()

    code_file = repo / "feature.py"
    code_file.write_text("def run(): pass\n", encoding="utf-8")
    subprocess.run(["git", "add", "feature.py"], cwd=str(repo), check=True)

    res = subprocess.run([str(HOOK_PATH)], cwd=str(repo), capture_output=True, text=True)
    assert res.returncode == 1
    assert "GIT COMMIT BLOCKED: Control Plane Transition Violations Detected!" in res.stdout


def test_hook_blocks_if_transition_not_in_valid_transitions(tmp_path):
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    task_id = "task-invalid-edge-005"
    branch = "feat/invalid-edge"
    subprocess.run(["git", "checkout", "-b", branch], cwd=str(repo), check=True, capture_output=True)

    cp = ControlPlane(db_path=db_path)
    _advance_task_to_in_worktree(cp, task_id, repo, branch)

    # Inject invalid transition into task_transitions
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO task_transitions (task_id, from_state, to_state, actor, reason) VALUES (?, 'ESCALATED', 'IN_WORKTREE', 'attacker', 'bypass')",
        (task_id,)
    )
    conn.commit()
    conn.close()

    code_file = repo / "feature.py"
    code_file.write_text("def run(): pass\n", encoding="utf-8")
    subprocess.run(["git", "add", "feature.py"], cwd=str(repo), check=True)

    res = subprocess.run([str(HOOK_PATH)], cwd=str(repo), capture_output=True, text=True)
    assert res.returncode == 1
    assert "GIT COMMIT BLOCKED: Invalid State Transition Detected!" in res.stdout


def test_hook_blocks_if_transition_chain_is_broken(tmp_path):
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    task_id = "task-broken-chain-006"
    branch = "feat/broken-chain"
    subprocess.run(["git", "checkout", "-b", branch], cwd=str(repo), check=True, capture_output=True)

    cp = ControlPlane(db_path=db_path)
    _advance_task_to_in_worktree(cp, task_id, repo, branch)

    # Inject a gap in task_transitions: e.g. delete DRAFT_PLAN -> AWAITING_APPROVAL so chain is broken
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "DELETE FROM task_transitions WHERE task_id = ? AND from_state = 'DRAFT_PLAN'",
        (task_id,)
    )
    conn.commit()
    conn.close()

    code_file = repo / "feature.py"
    code_file.write_text("def run(): pass\n", encoding="utf-8")
    subprocess.run(["git", "add", "feature.py"], cwd=str(repo), check=True)

    res = subprocess.run([str(HOOK_PATH)], cwd=str(repo), capture_output=True, text=True)
    assert res.returncode == 1
    assert "GIT COMMIT BLOCKED: Broken Pipeline State Chain!" in res.stdout


def test_control_plane_verify_commit_api(tmp_path):
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    cp = ControlPlane(db_path=db_path)
    task_id = "task-api-007"
    branch = "feat/api-test"

    cp.create_task(task_id, "API Task", "claude")
    cp.update_worktree(task_id, str(repo), branch, "written_in_worktree")

    # In proposal mode with code staged -> raises PersistenceInvariantViolation
    with pytest.raises(PersistenceInvariantViolation, match="Proposal Mode"):
        cp.verify_commit(branch=branch, staged_files=["src/code.py"])

    # In proposal mode with docs staged -> allowed
    res = cp.verify_commit(branch=branch, staged_files=["docs/plans/spec.md"])
    assert res["status"] == "ALLOWED"

    # Once advanced to IN_WORKTREE -> allowed for code
    from control_plane.coordinator import TransitionCoordinator
    cp.repo_root = repo
    TransitionCoordinator(control_plane=cp, input_fn=lambda _p: "1").coordinate_transition(
        task_id=task_id, to_state=STATE_DRAFT_PLAN, actor="human", reason="draft", interactive=True,
    )
    cp.record_plan_mode_entry(task_id, "tester")
    plans = repo / "docs" / "plans" / "work-tasks" / task_id
    plans.mkdir(parents=True, exist_ok=True)
    (plans / f"{task_id}-spec.md").write_text("# Spec\n", encoding="utf-8")
    (plans / f"{task_id}-implementation-plan.md").write_text("# Plan\n\n- Strategy: direct\n", encoding="utf-8")
    TransitionCoordinator(control_plane=cp).coordinate_transition(
        task_id=task_id, to_state=STATE_PLAN_REVIEW, actor="agent", reason="Submit plan", interactive=False,
    )
    cp.record_verification_receipt(
        task_id=task_id, gate_name="main_dirty_before_approval_exception",
        command_executed="test-fixture-uses-real-dirty-planning-files", exit_code=0,
    )
    TransitionCoordinator(control_plane=cp).coordinate_transition(
        task_id=task_id, to_state=STATE_APPROVED, actor="human", reason="approved", interactive=True,
    )
    cp.record_human_approval(task_id, "tester")
    cp.update_worktree(task_id, str(repo), branch, "written_in_worktree")
    cp.record_verification_receipt(
        task_id=task_id, gate_name="existing_worktree_exception",
        command_executed="test-fixture-reuses-repo-as-worktree", exit_code=0,
    )
    cp.transition(task_id, STATE_IN_WORKTREE, "tester", "in worktree")

    res2 = cp.verify_commit(branch=branch, staged_files=["src/code.py"])
    assert res2["status"] == "ALLOWED"


PUSH_HOOK_PATH = SCRIPTS_DIR / "pre-push-review-guard"


def test_push_hook_blocks_when_not_done(tmp_path):
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    task_id = "task-push-not-done-008"
    branch = "feat/push-not-done"
    subprocess.run(["git", "checkout", "-b", branch], cwd=str(repo), check=True, capture_output=True)

    cp = ControlPlane(db_path=db_path)
    _advance_task_to_in_worktree(cp, task_id, repo, branch)

    # In IN_WORKTREE, push is blocked
    res = subprocess.run([str(PUSH_HOOK_PATH)], cwd=str(repo), capture_output=True, text=True)
    assert res.returncode == 1
    assert "GIT PUSH BLOCKED: Pipeline Not Complete (Final State 'DONE' Required)!" in res.stdout


def test_push_hook_allows_when_done_with_valid_history(tmp_path):
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    task_id = "task-push-done-009"
    branch = "feat/push-done"
    subprocess.run(["git", "checkout", "-b", branch], cwd=str(repo), check=True, capture_output=True)

    cp = ControlPlane(db_path=db_path)
    _advance_task_to_in_worktree(cp, task_id, repo, branch)
    
    # Advance task to DONE (schema v15: IN_WORKTREE -> WORKTREE_REVIEW -> VERIFY_EXIT -> DONE)
    cp.record_verification_receipt(task_id, "test_suite", "pytest", 0)
    cp.record_verification_receipt(task_id, "full_test_suite", "pytest -q", 0)
    from control_plane.coordinator import TransitionCoordinator
    TransitionCoordinator(control_plane=cp).coordinate_transition(
        task_id, STATE_WORKTREE_REVIEW, "agent", "review", interactive=False,
    )
    TransitionCoordinator(control_plane=cp).coordinate_transition(
        task_id, STATE_VERIFY_EXIT, "human", "verify", interactive=True,
    )
    cp.record_verification_receipt(task_id, "leak_check", "git status", 0)
    cp.log_asymmetric_persistence(task_id, "references/map-debt.md", "RESOLVED", "test")
    cp.save_retrospective(
        task_id,
        {"decision": "skip", "completion_mode": "skipped", "actor": "human", "skip_reason": "hook fixture"},
        [],
    )
    TransitionCoordinator(control_plane=cp, input_fn=lambda _p: "2").coordinate_transition(
        task_id, STATE_DONE, "human", "done", interactive=True,
    )

    res = subprocess.run([str(PUSH_HOOK_PATH)], cwd=str(repo), capture_output=True, text=True)
    assert res.returncode == 0


@pytest.mark.xfail(strict=True, reason=(
    "OPEN map-debt (2026-09-20): apply_recovery_transition() leaves the consumed recovery approval with "
    "bound_transition_id NULL, so the commit/push guards see a NON-DAG recovery edge as unapproved. The previous "
    "version of this test used IN_WORKTREE -> DONE, which is a DAG edge, so the recovery-approval branch of the "
    "hooks was never actually exercised. strict=True: fixing the binding turns this into a hard pass."
))
def test_git_guards_allow_exact_human_approved_recovery_edge(tmp_path):
    """Allow a non-DAG edge only when its exact recovery approval is persisted and consumed."""
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    task_id = "task-approved-recovery-010"
    branch = "feat/approved-recovery"
    subprocess.run(["git", "checkout", "-b", branch], cwd=str(repo), check=True, capture_output=True)

    cp = ControlPlane(db_path=db_path)
    _advance_task_to_in_worktree(cp, task_id, repo, branch)
    # Recovery into DONE is refused by design (it would bypass the signed closure gate), so the exact-approved
    # non-DAG edge exercised here is IN_WORKTREE -> DRAFT_PLAN.
    from control_plane.constants import STATE_DRAFT_PLAN as _RECOVERY_TARGET
    token = cp.record_recovery_approval(
        task_id, _RECOVERY_TARGET, "human-reviewer", actor="human",
        reason="Reopen only through the explicitly approved recovery edge.",
    )
    cp.apply_recovery_transition(
        task_id, _RECOVERY_TARGET, token, "human", "Apply the approved recovery edge for code review."
    )

    code_file = repo / "feature.py"
    code_file.write_text("def run(): pass\n", encoding="utf-8")
    subprocess.run(["git", "add", "feature.py"], cwd=str(repo), check=True)

    commit_check = subprocess.run([str(HOOK_PATH)], cwd=str(repo), capture_output=True, text=True)
    push_check = subprocess.run([str(PUSH_HOOK_PATH)], cwd=str(repo), capture_output=True, text=True)
    assert commit_check.returncode == 0, commit_check.stdout + commit_check.stderr
    assert push_check.returncode == 0, push_check.stdout + push_check.stderr


def test_recovery_into_done_is_refused_because_closure_needs_a_signature(tmp_path):
    """A recovery approval can never be used to reach DONE: every inbound edge to DONE is a cryptographic gate, and
    the recovery path has no signature, so it fails closed instead of bypassing the gate."""
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    task_id = "task-recovery-into-done-011"
    branch = "feat/recovery-into-done"
    subprocess.run(["git", "checkout", "-b", branch], cwd=str(repo), check=True, capture_output=True)

    cp = ControlPlane(db_path=db_path)
    _advance_task_to_in_worktree(cp, task_id, repo, branch)
    with pytest.raises(ValueError, match="Recovery into 'DONE' is not permitted"):
        cp.record_recovery_approval(
            task_id, STATE_DONE, "human-reviewer", actor="human", reason="Attempt to close through recovery.",
        )
    assert cp.get_task(task_id)["state"] == STATE_IN_WORKTREE


# --- Registered-worktree location-check regression tests -------------------
# Regression coverage for a confirmed defect (see references/map-debt.md,
# tracked separately from GitHub issue #621's human-authorization finding):
# the hook's RESOLVED_TASK_WORKTREE resolution (~line 97) previously resolved
# a repository-relative registered worktree_path against the *current shell
# CWD* instead of REPO_ROOT, so a legitimate commit made from inside the
# correctly registered worktree was misclassified as "Commit Outside
# Registered Worktree" whenever worktree_path was stored relative (as it
# normally is in real usage, e.g. ".worktrees/task-<id>"). Only an
# absolute worktree_path happened to work by accident. Fixed by resolving
# relative paths against REPO_ROOT explicitly (restoring the case-statement
# semantics originally reviewed in commit 45b3fe51).

def test_hook_allows_commit_from_relative_registered_worktree(tmp_path):
    """A: relative registered worktree path + commit from that worktree -> PASS."""
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    task_id = "task-relwt-pass-011"
    branch = "feat/relwt-pass"
    subprocess.run(["git", "checkout", "-b", branch], cwd=str(repo), check=True, capture_output=True)

    cp = ControlPlane(db_path=db_path)
    _advance_task_to_in_worktree(cp, task_id, repo, branch)

    # Free `branch` from the main checkout so it can be checked out in the
    # new worktree (git disallows the same branch in two checkouts at once).
    subprocess.run(["git", "checkout", "main"], cwd=str(repo), check=True, capture_output=True)
    worktree_dir = repo / ".worktrees" / "relwt-pass"
    subprocess.run(
        ["git", "worktree", "add", str(worktree_dir), branch],
        cwd=str(repo), check=True, capture_output=True,
    )
    # Register the DB path exactly as real usage does: repository-relative.
    cp.update_worktree(task_id, ".worktrees/relwt-pass", branch, "written_in_worktree")

    code_file = worktree_dir / "feature.py"
    code_file.write_text("def run(): pass\n", encoding="utf-8")
    subprocess.run(["git", "add", "feature.py"], cwd=str(worktree_dir), check=True)

    res = subprocess.run([str(HOOK_PATH)], cwd=str(worktree_dir), capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_hook_blocks_commit_from_main_checkout_when_relative_worktree_registered(tmp_path):
    """B: relative registered worktree path + commit from main checkout -> BLOCK."""
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    task_id = "task-relwt-block-012"
    branch = "feat/relwt-block"
    subprocess.run(["git", "checkout", "-b", branch], cwd=str(repo), check=True, capture_output=True)

    cp = ControlPlane(db_path=db_path)
    _advance_task_to_in_worktree(cp, task_id, repo, branch)

    # Register an isolated worktree path that is never actually populated with
    # this commit -- the commit below happens from the main checkout instead,
    # which still has `branch` checked out (git's own worktree exclusivity
    # means the same branch cannot be checked out twice, so the main checkout
    # is the realistic stand-in for "wrong location" here).
    cp.update_worktree(task_id, ".worktrees/relwt-block", branch, "written_in_worktree")

    code_file = repo / "feature.py"
    code_file.write_text("def run(): pass\n", encoding="utf-8")
    subprocess.run(["git", "add", "feature.py"], cwd=str(repo), check=True)

    res = subprocess.run([str(HOOK_PATH)], cwd=str(repo), capture_output=True, text=True)
    assert res.returncode == 1
    assert "Commit Outside Registered Worktree" in res.stdout


def test_hook_allows_commit_from_absolute_registered_worktree(tmp_path):
    """C: absolute registered worktree path + commit from that worktree -> PASS."""
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    task_id = "task-abswt-pass-013"
    branch = "feat/abswt-pass"
    subprocess.run(["git", "checkout", "-b", branch], cwd=str(repo), check=True, capture_output=True)

    cp = ControlPlane(db_path=db_path)
    _advance_task_to_in_worktree(cp, task_id, repo, branch)

    subprocess.run(["git", "checkout", "main"], cwd=str(repo), check=True, capture_output=True)
    worktree_dir = repo / ".worktrees" / "abswt-pass"
    subprocess.run(
        ["git", "worktree", "add", str(worktree_dir), branch],
        cwd=str(repo), check=True, capture_output=True,
    )
    cp.update_worktree(task_id, str(worktree_dir), branch, "written_in_worktree")

    code_file = worktree_dir / "feature.py"
    code_file.write_text("def run(): pass\n", encoding="utf-8")
    subprocess.run(["git", "add", "feature.py"], cwd=str(worktree_dir), check=True)

    res = subprocess.run([str(HOOK_PATH)], cwd=str(worktree_dir), capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_hook_blocks_commit_from_main_checkout_when_absolute_worktree_registered(tmp_path):
    """D: absolute registered worktree path + commit from the wrong checkout -> BLOCK."""
    repo, db_path = _setup_git_repo_with_db(tmp_path)
    task_id = "task-abswt-block-014"
    branch = "feat/abswt-block"
    subprocess.run(["git", "checkout", "-b", branch], cwd=str(repo), check=True, capture_output=True)

    cp = ControlPlane(db_path=db_path)
    _advance_task_to_in_worktree(cp, task_id, repo, branch)

    worktree_dir = repo / ".worktrees" / "abswt-block"
    cp.update_worktree(task_id, str(worktree_dir), branch, "written_in_worktree")
    # Note: worktree_dir is deliberately never created via `git worktree add`
    # here -- the registered absolute path exists only in the DB, and the
    # commit below is attempted from the main checkout (which still holds
    # `branch`), exercising the same "wrong location" path as test B but for
    # an absolute registered path instead of a relative one.

    code_file = repo / "feature.py"
    code_file.write_text("def run(): pass\n", encoding="utf-8")
    subprocess.run(["git", "add", "feature.py"], cwd=str(repo), check=True)

    res = subprocess.run([str(HOOK_PATH)], cwd=str(repo), capture_output=True, text=True)
    assert res.returncode == 1
    assert "Commit Outside Registered Worktree" in res.stdout
