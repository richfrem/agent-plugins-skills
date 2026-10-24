"""Unit tests for gh_issue_create.py script.

Purpose:
    Validates dry-run execution and the auto-default status:* label behavior
    (every created issue gets a sequencing signal even if the caller omits one).

Key Input Dependencies:
    - gh_issue_create.py
"""

from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gh_issue_create import create_issue

_VALID_BODY = (
    "## Summary\nA thing broke.\n\n"
    "## Observed Behavior\nIt broke.\n\n"
    "## Expected Behavior\nIt should not break.\n\n"
    "## Evidence\nStack trace here.\n\n"
    "## Impact\nBlocks the pipeline.\n"
)


@patch("subprocess.run")
def test_create_issue_defaults_status_when_omitted(mock_run: MagicMock) -> None:
    """A caller who doesn't include any status:* label gets status:needs-triage added."""
    res = create_issue(
        title="Something broke",
        body=_VALID_BODY,
        labels=["type:bug", "tier:2-structural", "source:agent", "risk:low", "area:agentic-os"],
        execute=False,
    )
    assert res["taxonomy_validation"] == "passed"
    assert "status:needs-triage" in res["labels"]
    mock_run.assert_not_called()


@patch("subprocess.run")
def test_create_issue_preserves_explicit_status(mock_run: MagicMock) -> None:
    """A caller who already knows the status keeps their explicit label, no default added."""
    res = create_issue(
        title="Something broke",
        body=_VALID_BODY,
        labels=["type:bug", "tier:2-structural", "source:agent", "risk:low", "area:agentic-os", "status:ready"],
        execute=False,
    )
    assert res["labels"].count("status:ready") == 1
    assert "status:needs-triage" not in res["labels"]
    mock_run.assert_not_called()
