"""
test_pre_push_review_guard.py — Contract Test for pre-push-review-guard's Silent-Pass Behavior
================================================================================================

Purpose:
    Verifies pre-push-review-guard emits a visible warning (not a silent pass) when
    invoked with no control_plane.db present, or with no task row matching the current
    branch — both previously exited 0 with zero output, making an ungated push
    indistinguishable from a properly-gated one in CI/terminal logs.

Key Input Dependencies:
    - plugins/agent-agentic-os/scripts/pre-push-review-guard
    - sqlite3 CLI (must be on PATH)

Key Functions:
    - test_warns_when_no_control_plane_db_present() — no DB case
    - test_warns_when_no_task_matches_current_branch() — DB exists, no matching task row
    - test_still_blocks_when_task_state_not_cleared() — regression: real gate still enforced
"""

import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
GUARD_SCRIPT = REPO_ROOT / "plugins" / "agent-agentic-os" / "scripts" / "pre-push-review-guard"

SCRIPTS_DIR = REPO_ROOT / "plugins" / "agent-agentic-os" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
from agent_control import ControlPlane


@pytest.fixture
def git_repo_on_branch(tmp_path):
    """Creates a throwaway git repo checked out on a non-main feature branch."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    (repo / "README.md").write_text("# Test\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "feat/some-work"], cwd=repo, check=True, capture_output=True)
    return repo


def _run_guard(repo: Path):
    """Invokes pre-push-review-guard as a subprocess with cwd set to the given repo."""
    return subprocess.run(["bash", str(GUARD_SCRIPT)], cwd=repo, capture_output=True, text=True)


def test_warns_when_no_control_plane_db_present(git_repo_on_branch):
    """No context/control_plane.db at all — must warn visibly, not silently pass."""
    res = _run_guard(git_repo_on_branch)
    assert res.returncode == 0
    assert "WARNING" in res.stderr
    assert "no control_plane.db" in res.stderr.lower() or "ungated" in res.stderr.lower()


def test_warns_when_no_task_matches_current_branch(git_repo_on_branch):
    """control_plane.db exists but no task row matches the current branch — must warn, not silently pass."""
    db_path = git_repo_on_branch / "context" / "control_plane.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    ControlPlane(db_path=db_path).init_db()

    res = _run_guard(git_repo_on_branch)
    assert res.returncode == 0
    assert "WARNING" in res.stderr
    assert "no task" in res.stderr.lower() or "ungated" in res.stderr.lower()


def test_still_blocks_when_task_state_not_cleared(git_repo_on_branch):
    """Regression: a real task on this branch, not yet review-cleared, must still hard-block."""
    db_path = git_repo_on_branch / "context" / "control_plane.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    cp.create_task(task_id="test-guard-001", title="Guard Test", runtime_tool="claude")
    cp.update_worktree(task_id="test-guard-001", worktree_path=".", worktree_branch="feat/some-work", worktree_state="written_in_worktree")

    res = _run_guard(git_repo_on_branch)
    assert res.returncode == 1
    assert "GIT PUSH BLOCKED" in res.stdout


def test_sql_injection_via_branch_name_cannot_forge_a_cleared_state(git_repo_on_branch):
    """A branch name crafted as a SQL injection payload must not be able to talk the guard
    into believing a decoy VERIFY_EXIT-state row applies to it (PoC from security review:
    git checkout -b "x'OR(state)IN('VERIFY_EXIT')--")."""
    db_path = git_repo_on_branch / "context" / "control_plane.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    # Decoy task with a review-cleared state, on an unrelated branch — the injection payload
    # tries to make the guard's query match this row regardless of the real branch.
    cp.create_task(task_id="decoy-cleared-task", title="Decoy", runtime_tool="claude")
    cp.update_worktree(task_id="decoy-cleared-task", worktree_path=".", worktree_branch="unrelated-branch", worktree_state="written_in_worktree")
    conn_path = str(db_path)
    import sqlite3
    conn = sqlite3.connect(conn_path)
    conn.execute("UPDATE tasks SET state = 'VERIFY_EXIT' WHERE task_id = 'decoy-cleared-task'")
    conn.commit()
    conn.close()

    injection_branch = "x'OR(state)IN('VERIFY_EXIT')--"
    subprocess.run(["git", "checkout", "-b", injection_branch], cwd=git_repo_on_branch, check=True, capture_output=True)

    res = _run_guard(git_repo_on_branch)
    # Must NOT silently succeed as if review-cleared (returncode 0 with no warning would mean
    # the injection worked). No real task is registered for this branch, so the correct
    # outcome is the ungated warning, not a forged "cleared" pass-through.
    assert res.returncode == 0
    assert "WARNING" in res.stderr
