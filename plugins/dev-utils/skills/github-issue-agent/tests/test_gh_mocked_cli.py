"""
Unit tests for gh_issue_create and gh_issue_comment CLI scripts.

Copyright (c) 2026. All rights reserved.
"""

from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add script directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from gh_issue_comment import comment_issue
from gh_issue_create import create_issue


def test_create_issue_dry_run_default():
    """Verify that execute=False (dry-run default) returns payload JSON and does NOT invoke subprocess."""
    labels = ["type:friction", "tier:1-friction", "area:scripts", "source:agent", "risk:low"]
    body = (
        "## Summary\nTest issue summary.\n"
        "## Observed Behavior\nError occurred.\n"
        "## Expected Behavior\nShould succeed.\n"
        "## Evidence\nLog output attached.\n"
        "## Impact\nLow impact."
    )

    with patch("subprocess.run") as mock_run:
        res = create_issue(title="Test Issue", body=body, labels=labels, execute=False)
        assert mock_run.call_count == 0
        assert res["would_execute"] is False
        assert res["action"] == "create_issue"
        assert res["title"] == "Test Issue"
        assert res["labels"] == labels
        assert res["body"] == body
        assert res["redaction_check"] == "passed"
        assert res["body_validation"] == "passed"
        assert res["taxonomy_validation"] == "passed"


def test_create_issue_live_mode_calls_gh():
    """Verify that execute=True calls gh CLI cleanly when all validations pass."""
    labels = ["type:friction", "tier:1-friction", "area:scripts", "source:agent", "risk:low"]
    body = (
        "## Summary\nTest issue summary.\n"
        "## Observed Behavior\nError occurred.\n"
        "## Expected Behavior\nShould succeed.\n"
        "## Evidence\nLog output attached.\n"
        "## Impact\nLow impact."
    )

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout='[{"name": "type:friction"}, {"name": "tier:1-friction"}, '
                                            '{"name": "area:scripts"}, {"name": "source:agent"}, '
                                            '{"name": "risk:low"}]', stderr=""),
            MagicMock(returncode=0, stdout="https://github.com/owner/repo/issues/101\n", stderr=""),
        ]
        res = create_issue(title="Test Issue", body=body, labels=labels, execute=True)
        assert mock_run.call_count == 2
        assert res["would_execute"] is True
        assert res["action"] == "create_issue"
        assert res["output"] == "https://github.com/owner/repo/issues/101"


def test_create_issue_live_mode_auto_creates_missing_labels():
    """Verify that execute=True creates any repo labels not already present before filing the issue."""
    labels = ["type:friction", "tier:1-friction", "area:scripts", "source:agent", "risk:low"]
    body = (
        "## Summary\nTest issue summary.\n"
        "## Observed Behavior\nError occurred.\n"
        "## Expected Behavior\nShould succeed.\n"
        "## Evidence\nLog output attached.\n"
        "## Impact\nLow impact."
    )

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="[]", stderr=""),  # no labels exist yet
            MagicMock(returncode=0, stdout="", stderr=""),  # label create: type:friction
            MagicMock(returncode=0, stdout="", stderr=""),  # label create: tier:1-friction
            MagicMock(returncode=0, stdout="", stderr=""),  # label create: area:scripts
            MagicMock(returncode=0, stdout="", stderr=""),  # label create: source:agent
            MagicMock(returncode=0, stdout="", stderr=""),  # label create: risk:low
            MagicMock(returncode=0, stdout="https://github.com/owner/repo/issues/102\n", stderr=""),
        ]
        res = create_issue(title="Test Issue", body=body, labels=labels, execute=True)
        assert mock_run.call_count == 7
        assert mock_run.call_args_list[1].args[0][:3] == ["gh", "label", "create"]
        assert res["output"] == "https://github.com/owner/repo/issues/102"


def test_create_issue_fails_on_secret():
    """Verify that creation fails if secret scanning finds credentials."""
    labels = ["type:friction", "tier:1-friction", "area:scripts", "source:agent", "risk:low"]
    body = (
        "## Summary\nToken exposed ghp_123456789012345678901234567890123456.\n"
        "## Observed Behavior\nError occurred.\n"
        "## Expected Behavior\nShould succeed.\n"
        "## Evidence\nLog output attached.\n"
        "## Impact\nLow impact."
    )

    with patch("subprocess.run") as mock_run:
        with pytest.raises(ValueError, match="Secret redaction gate failed"):
            create_issue(title="Secret Issue", body=body, labels=labels, execute=False)
        assert mock_run.call_count == 0


def test_create_issue_fails_on_invalid_body():
    """Verify that creation fails if body validation fails."""
    labels = ["type:friction", "tier:1-friction", "area:scripts", "source:agent", "risk:low"]
    body = "## Summary\nMissing sections here."

    with patch("subprocess.run") as mock_run:
        with pytest.raises(ValueError, match="Body validation failed"):
            create_issue(title="Invalid Body Issue", body=body, labels=labels, execute=False)
        assert mock_run.call_count == 0


def test_comment_issue_dry_run_default():
    """Verify that comment_issue with execute=False returns payload preview."""
    body = "Additional evidence from run."
    with patch("subprocess.run") as mock_run:
        res = comment_issue(issue_number=42, body=body, execute=False)
        assert mock_run.call_count == 0
        assert res["would_execute"] is False
        assert res["action"] == "comment_issue"
        assert res["issue_number"] == 42
        assert res["body"] == body
        assert res["redaction_check"] == "passed"


def test_comment_issue_fails_on_secret():
    """Verify that comment_issue fails if secret scanning finds credentials."""
    body = "Exposing secret: sk-12345678901234567890123456789012"
    with patch("subprocess.run") as mock_run:
        with pytest.raises(ValueError, match="Secret redaction gate failed"):
            comment_issue(issue_number=42, body=body, execute=False)
        assert mock_run.call_count == 0
