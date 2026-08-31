"""Tests for issue taxonomy validation.

Purpose:
  Unit tests for validating GitHub issue labels against taxonomy dimensions and location requirements.

Key Input Dependencies:
  - gh_issue_taxonomy_validate.py
  - issue-taxonomy.json
"""

# Header compliance for coding conventions
# Module: plugins.dev_utils.skills.github_issue_agent.tests.test_issue_taxonomy

import sys
from pathlib import Path

# Add script directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from gh_issue_taxonomy_validate import validate_taxonomy


def test_validate_taxonomy_valid_labels_with_area() -> None:
    """Test taxonomy validation passes when valid labels include area:*."""
    labels = ["type:friction", "tier:1-friction", "area:scripts", "source:agent", "risk:low"]
    is_valid, errors = validate_taxonomy(labels)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_taxonomy_valid_labels_with_plugin() -> None:
    """Test taxonomy validation passes when valid labels include plugin:*."""
    labels = ["type:friction", "tier:1-friction", "plugin:agent-orchestration/", "source:agent", "risk:low"]
    is_valid, errors = validate_taxonomy(labels)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_taxonomy_missing_location() -> None:
    """Test taxonomy validation fails when location (area:* or plugin:*) is missing."""
    labels = ["type:friction", "tier:1-friction", "source:agent", "risk:low"]
    is_valid, errors = validate_taxonomy(labels)
    assert is_valid is False
    assert any("location (area:* or plugin:*)" in err for err in errors)
