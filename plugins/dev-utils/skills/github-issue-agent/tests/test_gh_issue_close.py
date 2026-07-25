"""Unit tests for gh_issue_close.py script.

Purpose:
    Validates dry-run execution, secret scanning, and resolution taxonomy enforcement for issue closure.

Key Input Dependencies:
    - gh_issue_close.py
"""

from pathlib import Path
import sys
from unittest.mock import MagicMock, patch
import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gh_issue_close import close_issue


@patch("subprocess.run")
def test_close_issue_dry_run(mock_run: MagicMock) -> None:
    """Test dry-run closure return payload without invoking gh CLI."""
    res = close_issue(issue_number=42, resolution="resolution:fixed", comment="Fixed in PR #453", execute=False)
    assert res["would_execute"] is False
    assert res["action"] == "close_issue"
    assert res["issue_number"] == 42
    assert res["resolution"] == "resolution:fixed"
    assert res["comment"] == "Fixed in PR #453"
    assert res["success"] is True
    mock_run.assert_not_called()


@patch("subprocess.run")
def test_close_issue_invalid_resolution_fails(mock_run: MagicMock) -> None:
    """Test invalid resolution error handling."""
    res = close_issue(issue_number=42, resolution="resolution:invalid_res", comment="Fixed", execute=False)
    assert res["success"] is False
    assert any("Invalid resolution" in err for err in res["errors"])
    mock_run.assert_not_called()


@patch("subprocess.run")
def test_close_issue_secret_scanning_fails(mock_run: MagicMock) -> None:
    """Test secret redaction failure when comment contains a secret."""
    res = close_issue(
        issue_number=42,
        resolution="resolution:fixed",
        comment="Fixed using token ghp_123456789012345678901234567890123456",
        execute=False,
    )
    assert res["success"] is False
    assert any("Detected potential secret" in err for err in res["errors"])
    mock_run.assert_not_called()


@patch("subprocess.run")
def test_close_issue_execute(mock_run: MagicMock) -> None:
    """Test live execution calls gh CLI comment, edit (label), and close."""
    mock_run.return_value = MagicMock(stdout="", returncode=0)
    res = close_issue(issue_number=42, resolution="resolution:fixed", comment="Fixed issue", execute=True)
    assert res["would_execute"] is True
    assert res["success"] is True
    assert mock_run.call_count == 3
    mock_run.assert_any_call(["gh", "issue", "comment", "42", "--body", "Fixed issue"], check=True)
    mock_run.assert_any_call(["gh", "issue", "edit", "42", "--add-label", "resolution:fixed"], check=True)
    mock_run.assert_any_call(["gh", "issue", "close", "42"], check=True)
