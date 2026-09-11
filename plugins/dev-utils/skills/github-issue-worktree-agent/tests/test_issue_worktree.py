"""Unit test for issue_worktree_manage.py script.

Purpose:
    Validates worktree creation, listing, and removal operations using subprocess mocking.

Key Input Dependencies:
    - issue_worktree_manage.py
"""

from pathlib import Path
import sys
from unittest.mock import MagicMock, patch
import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from issue_worktree_manage import (
    create_worktree,
    list_worktrees,
    remove_worktree,
)


@patch("subprocess.run")
def test_create_worktree_success(mock_run: MagicMock) -> None:
    """Tests successful creation of a worktree."""
    mock_run.return_value = MagicMock(returncode=0, stdout="Preparing worktree\n", stderr="")

    result = create_worktree(issue_number=123, branch_name="fix-issue-123", base_branch="main")

    assert result["success"] is True
    assert result["issue_number"] == 123
    assert result["branch_name"] == "fix-issue-123"
    assert ".worktrees/issue-123" in result["worktree_path"]

    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert args[:3] == ["git", "worktree", "add"]
    assert "-b" in args
    assert "fix-issue-123" in args
    assert "main" in args


@patch("subprocess.run")
def test_list_worktrees(mock_run: MagicMock) -> None:
    """Tests parsing output from git worktree list."""
    mock_stdout = (
        "/repo  abc1234 [main]\n"
        "/repo/.worktrees/issue-123  def5678 [fix-issue-123]\n"
        "/repo/.worktrees/issue-456  7890abc [feature-456]\n"
    )
    mock_run.return_value = MagicMock(returncode=0, stdout=mock_stdout, stderr="")

    worktrees = list_worktrees()

    assert len(worktrees) == 3
    assert worktrees[1]["path"].endswith("issue-123")
    assert worktrees[1]["branch"] == "fix-issue-123"
    assert worktrees[2]["path"].endswith("issue-456")
    assert worktrees[2]["branch"] == "feature-456"


@patch("subprocess.run")
def test_remove_worktree_success(mock_run: MagicMock) -> None:
    """Tests successful removal of a worktree."""
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    result = remove_worktree(issue_number=123, force=False)

    assert result["success"] is True
    assert result["issue_number"] == 123
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert args[:3] == ["git", "worktree", "remove"]
    assert ".worktrees/issue-123" in args[3]
