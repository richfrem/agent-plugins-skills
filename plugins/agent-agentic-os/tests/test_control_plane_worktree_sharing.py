"""
test_control_plane_worktree_sharing.py — Contract Test for Cross-Worktree DB Sharing
======================================================================================

Purpose:
    Verifies ControlPlane's auto-discovery (db_path=None) resolves the SAME
    context/control_plane.db whether invoked from the main checkout or from a git
    worktree of the same repo — previously each worktree got an independent, empty
    DB (since the discovery walk found the worktree's own local `.git` file and
    treated it as a separate repo boundary), disconnecting task state registered in
    the main checkout from work done inside the worktree.

Key Input Dependencies:
    - plugins/agent-agentic-os/scripts/agent_control.py (copied into a throwaway repo)
    - git CLI (init, worktree add)
"""

import shutil
import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
AGENT_CONTROL_SRC = REPO_ROOT / "plugins" / "agent-agentic-os" / "scripts" / "agent_control.py"


@pytest.fixture
def repo_with_worktree(tmp_path):
    """Creates a throwaway git repo with agent_control.py copied in, plus a real
    git worktree checked out from it — mimicking a consumer repo's layout."""
    main_repo = tmp_path / "main_repo"
    main_repo.mkdir()
    subprocess.run(["git", "init"], cwd=main_repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=main_repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=main_repo, check=True)

    scripts_dir = main_repo / "plugins" / "agent-agentic-os" / "scripts"
    scripts_dir.mkdir(parents=True)
    shutil.copy(AGENT_CONTROL_SRC, scripts_dir / "agent_control.py")

    subprocess.run(["git", "add", "."], cwd=main_repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=main_repo, check=True, capture_output=True)

    worktree_dir = tmp_path / "worktree_copy"
    subprocess.run(
        ["git", "worktree", "add", str(worktree_dir), "-b", "feat/test-branch"],
        cwd=main_repo, check=True, capture_output=True
    )
    return main_repo, worktree_dir


def _run_cli(cwd: Path, *args: str):
    """Invokes the copied agent_control.py CLI as a subprocess with cwd set to the given repo/worktree."""
    script = cwd / "plugins" / "agent-agentic-os" / "scripts" / "agent_control.py"
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(cwd), capture_output=True, text=True
    )


def test_worktree_shares_control_plane_db_with_main_checkout(repo_with_worktree):
    """A task registered from the main checkout must be visible from the worktree."""
    main_repo, worktree_dir = repo_with_worktree

    res_init = _run_cli(main_repo, "init", "--task-id", "shared-task-001", "--title", "Shared Task", "--runtime", "claude")
    assert res_init.returncode == 0, res_init.stderr

    res_status = _run_cli(worktree_dir, "status", "--task-id", "shared-task-001")
    assert res_status.returncode == 0, res_status.stderr
    assert "shared-task-001" in res_status.stdout
    assert '"state": "INTAKE"' in res_status.stdout
