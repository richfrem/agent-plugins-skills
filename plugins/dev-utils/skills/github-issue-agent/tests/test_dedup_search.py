#!/usr/bin/env python3
"""Tests for GitHub issue deduplication search and root-cause consolidation.

Purpose:
  Unit tests for searching duplicate issues and evaluating root-cause consolidation using mocked gh CLI calls.

Key Input Dependencies:
  - gh_issue_search.py
"""

# Header compliance for coding conventions
# Module: plugins.dev_utils.skills.github_issue_agent.tests.test_dedup_search

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add script directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from gh_issue_search import consolidate_and_search_dedup


@patch("subprocess.run")
def test_consolidate_and_search_finds_existing_root_cause(mock_run: MagicMock) -> None:
    """Test that existing broader root cause issue is matched and recommended for comment."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=json.dumps([
            {
                "number": 42,
                "title": "Repository lacks standardized file existence validation",
                "labels": [{"name": "type:friction"}, {"name": "area:scripts"}]
            }
        ])
    )
    result = consolidate_and_search_dedup(
        title="Script x.py failed because file missing",
        area_label="area:scripts",
        file_paths=["plugins/dev-utils/scripts/x.py"]
    )
    assert result["has_existing_root_cause"] is True
    assert result["target_issue_number"] == 42
    assert result["recommendation"] == "comment_and_append_evidence"


@patch("subprocess.run")
def test_consolidate_and_search_ranks_candidates_and_queries(mock_run: MagicMock) -> None:
    """Test candidate ranking and query generation when no broad root cause matches, and the
    best candidate scores below the consolidation threshold (weak, not-quite-a-match overlap)."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=json.dumps([
            {
                "number": 15,
                "title": "Unrelated dashboard rendering glitch on mobile Safari",
                "labels": [{"name": "type:bug"}, {"name": "area:scripts"}]
            }
        ])
    )
    result = consolidate_and_search_dedup(
        title="Script x.py failed because file missing",
        area_label="area:scripts",
        file_paths=["plugins/dev-utils/scripts/x.py"]
    )
    assert result["has_existing_root_cause"] is False
    assert len(result["candidates"]) == 0
    assert result["recommendation"] == "create_new_issue"


@patch("subprocess.run")
def test_consolidate_and_search_flags_high_scoring_candidate_as_root_cause(mock_run: MagicMock) -> None:
    """Test that a candidate whose computed title-overlap score meets the consolidation
    threshold actually sets has_existing_root_cause=True — previously the scoring loop
    computed a score but never fed it back into the decision, so even a perfect 1.0 match
    fell through to 'create_new_issue' (only 5 hardcoded unrelated phrases ever triggered
    consolidation)."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=json.dumps([
            {
                "number": 519,
                "title": "control_plane.db is gitignored with no durable export",
                "labels": [{"name": "type:architecture"}, {"name": "area:agentic-os"}]
            }
        ])
    )
    result = consolidate_and_search_dedup(
        title="control_plane.db is gitignored with no durable export",
        area_label="area:agentic-os",
        file_paths=["plugins/agent-agentic-os/scripts/agent_control.py"]
    )
    assert result["has_existing_root_cause"] is True
    assert result["target_issue_number"] == 519
    assert result["recommendation"] == "comment_and_append_evidence"
