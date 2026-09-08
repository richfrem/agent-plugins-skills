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
    subprocess.run(["git", "add", "README.md"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(repo), check=True)

    db_path = repo / "context" / "control_plane.db"
    adapter = SqlitePersistenceAdapter(db_path, FilesystemAdapter())
    adapter.ensure_schema()
    return repo, db_path


def _advance_task_to_in_worktree(cp, task_id, repo, branch):
    """Advances task through all required pipeline stages to IN_WORKTREE."""
    cp.create_task(task_id, f"Task {task_id}", "claude")
    cp.transition(task_id, "INTERVIEW", "tester", "interview")
    cp.record_plan_mode_entry(task_id, "tester")
    cp.transition(task_id, "DRAFT_PLAN", "tester", "draft")
    cp.record_review_skip(task_id, "multi_agent_review", "tester", "skip")
    cp.transition(task_id, "AWAITING_APPROVAL", "tester", "awaiting")
    cp.record_human_approval(task_id, "tester")
    conn = sqlite3.connect(cp.db_path)
    last_trans = conn.execute("SELECT transition_id FROM task_transitions WHERE task_id = ? ORDER BY transition_id DESC LIMIT 1", (task_id,)).fetchone()[0]
    conn.execute(
        """
        INSERT INTO transition_decisions (
            task_id, source_occupancy_transition_id, from_state, to_state,
            question_id, answer, decision_type, actor, recorded_at
        ) VALUES (?, ?, 'AWAITING_APPROVAL', 'APPROVED', 'human_implementation_approval', 'Yes, approve implementation [Recommended]', 'ANSWER', 'human', 12345.0),
                 (?, ?, 'AWAITING_APPROVAL', 'APPROVED', 'approval_awaiting_approval_to_approved', 'APPROVAL', 'APPROVAL', 'human', 12345.0)
        """,
        (task_id, last_trans, task_id, last_trans)
    )
    conn.commit()
    conn.close()
    cp.transition(task_id, "APPROVED", "tester", "approved")
    cp.transition(task_id, "IN_WORKTREE", "tester", "in worktree")
    cp.update_worktree(task_id, str(repo), branch, "written_in_worktree")


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
    cp.create_task(task_id, "Plan Docs Task", "claude")
    cp.transition(task_id, "INTERVIEW", "tester", "interview")
    cp.record_plan_mode_entry(task_id, "tester")
    cp.transition(task_id, "DRAFT_PLAN", "tester", "draft")
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
    cp.transition(task_id, "INTERVIEW", "tester", "interview")
    cp.record_plan_mode_entry(task_id, "tester")
    cp.transition(task_id, "DRAFT_PLAN", "tester", "draft")
    cp.record_review_skip(task_id, "multi_agent_review", "tester", "skip")
    cp.transition(task_id, "AWAITING_APPROVAL", "tester", "awaiting")
    cp.record_human_approval(task_id, "tester")
    conn = sqlite3.connect(cp.db_path)
    last_trans = conn.execute("SELECT transition_id FROM task_transitions WHERE task_id = ? ORDER BY transition_id DESC LIMIT 1", (task_id,)).fetchone()[0]
    conn.execute(
        """
        INSERT INTO transition_decisions (
            task_id, source_occupancy_transition_id, from_state, to_state,
            question_id, answer, decision_type, actor, recorded_at
        ) VALUES (?, ?, 'AWAITING_APPROVAL', 'APPROVED', 'human_implementation_approval', 'Yes, approve implementation [Recommended]', 'ANSWER', 'human', 12345.0),
                 (?, ?, 'AWAITING_APPROVAL', 'APPROVED', 'approval_awaiting_approval_to_approved', 'APPROVAL', 'APPROVAL', 'human', 12345.0)
        """,
        (task_id, last_trans, task_id, last_trans)
    )
    conn.commit()
    conn.close()
    cp.transition(task_id, "APPROVED", "tester", "approved")
    cp.transition(task_id, "IN_WORKTREE", "tester", "in worktree")

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
    
    # Advance task to DONE (record test_suite before entering WORKTREE_REVIEW)
    cp.record_verification_receipt(task_id, "test_suite", "pytest", 0)
    conn = sqlite3.connect(cp.db_path)
    last_trans = conn.execute("SELECT transition_id FROM task_transitions WHERE task_id = ? ORDER BY transition_id DESC LIMIT 1", (task_id,)).fetchone()[0]
    conn.execute(
        """
        INSERT INTO transition_decisions (
            task_id, source_occupancy_transition_id, from_state, to_state,
            question_id, answer, decision_type, actor, recorded_at
        ) VALUES (?, ?, 'IN_WORKTREE', 'WORKTREE_REVIEW', 'confirm_review_in_worktree_to_worktree_review', 'Proceed with review [Recommended]', 'ANSWER', 'human', 12345.0)
        """,
        (task_id, last_trans)
    )
    conn.commit()
    conn.close()
    cp.transition(task_id, "WORKTREE_REVIEW", "tester", "review")
    cp.record_review_skip(task_id, "multi_agent_code_review", "tester", "skip")
    cp.transition(task_id, "VERIFY_EXIT", "tester", "verify")
    cp.record_verification_receipt(task_id, "leak_check", "git status", 0)
    cp.log_asymmetric_persistence(task_id, "references/map-debt.md", "RESOLVED", "test")
    cp.transition(task_id, "DONE", "tester", "done")

    res = subprocess.run([str(PUSH_HOOK_PATH)], cwd=str(repo), capture_output=True, text=True)
    assert res.returncode == 0
