#!/usr/bin/env python3
"""
Unit tests for GitHub Issue Prioritizer (`gh_issue_prioritize.py`).
==================================================================
Purpose:
    Test priority score calculation (P0, P1, P2, P3) based on friction tier,
    frequency, and blockages, and verify GitHub Projects v2 custom field payload generation.

Layer: Quality Assurance / Test Suite
Key Input Dependencies:
    - `plugins.dev_utils.skills.github_issue_prioritizer.scripts.gh_issue_prioritize` module
"""

import sys
from pathlib import Path
import pytest

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from gh_issue_prioritize import (
    calculate_priority,
    generate_projects_v2_payload,
    prioritize_issue,
)


def test_calculate_priority_p0_tier3():
    """Tier 3 friction tier should automatically yield P0 priority."""
    priority, score = calculate_priority(friction_tier=3, frequency=1, is_blocking=False)
    assert priority == "P0"
    assert score >= 100


def test_calculate_priority_p0_blocking_high_freq():
    """Blocking issues with frequency >= 3 should yield P0 priority."""
    priority, score = calculate_priority(friction_tier=2, frequency=3, is_blocking=True)
    assert priority == "P0"


def test_calculate_priority_p1():
    """Tier 2 or high frequency or blocking issues should yield P1 priority."""
    priority, score = calculate_priority(friction_tier=2, frequency=2, is_blocking=False)
    assert priority == "P1"

    priority_b, score_b = calculate_priority(friction_tier=1, frequency=1, is_blocking=True)
    assert priority_b == "P1"


def test_calculate_priority_p2():
    """Tier 1 with frequency >= 2 should yield P2 priority."""
    priority, score = calculate_priority(friction_tier=1, frequency=2, is_blocking=False)
    assert priority == "P2"


def test_calculate_priority_p3():
    """Low friction tier (0 or 1) with low frequency and non-blocking should yield P3 priority."""
    priority, score = calculate_priority(friction_tier=0, frequency=1, is_blocking=False)
    assert priority == "P3"


def test_generate_projects_v2_payload():
    """Verify Projects v2 custom field GraphQL mutation payload generation."""
    payload = generate_projects_v2_payload(
        project_id="PVT_kwDOA12345",
        item_id="PVTI_lADOA12345",
        field_id="PVTF_priority123",
        single_select_option_id="opt_p0_123"
    )

    assert payload["query"].startswith("mutation")
    assert "PVT_kwDOA12345" in payload["variables"]["projectId"]
    assert "PVTI_lADOA12345" in payload["variables"]["itemId"]
    assert "PVTF_priority123" in payload["variables"]["fieldId"]
    assert "opt_p0_123" in payload["variables"]["value"]["singleSelectOptionId"]


def test_prioritize_issue_dictionary():
    """Test prioritizing an issue dictionary structure."""
    issue_data = {
        "number": 42,
        "title": "Critical sandbox crash on macOS",
        "labels": [
            {"name": "tier:3"},
            {"name": "blocking"},
            {"name": "area:agentic-os"}
        ],
        "occurrence_count": 5
    }

    result = prioritize_issue(issue_data)
    assert result["issue_number"] == 42
    assert result["priority"] == "P0"
    assert result["friction_tier"] == 3
    assert result["is_blocking"] is True
    assert result["frequency"] == 5
    assert result["priority_label"] == "priority:P0"
