"""Unit test for task_to_issue_bridge.py script.

Purpose:
    Validates task markdown parsing, payload construction, taxonomy integration, and dry-run execution.

Key Input Dependencies:
    - task_to_issue_bridge.py
"""

from pathlib import Path
import sys
import pytest

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from task_to_issue_bridge import (
    parse_task_file,
    build_issue_payload,
    promote_task_to_issue,
)


@pytest.fixture
def sample_task_file(tmp_path: Path) -> Path:
    """Write and return a synthetic task markdown file for parsing tests."""
    task_content = """---
id: 42
title: Fix database migration deadlock on startup
lane: backlog
created: 2026-07-25
---

# Objective
Fix the deadlock issue occurring during parallel microservice startup migrations.

# Acceptance Criteria
- [ ] Migration lock timeout added
- [ ] Unit tests for parallel migrations pass

# Notes
Seen 3 times in production staging.
"""
    task_file = tmp_path / "0042-fix-database-migration-deadlock.md"
    task_file.write_text(task_content, encoding="utf-8")
    return task_file


def test_parse_task_file(sample_task_file: Path) -> None:
    """parse_task_file() must correctly extract fields from a sample task file."""
    task_data = parse_task_file(sample_task_file)
    assert str(task_data["id"]) == "42"
    assert task_data["title"] == "Fix database migration deadlock on startup"
    assert task_data["lane"] == "backlog"
    assert "Fix the deadlock issue" in task_data["objective"]
    assert "Migration lock timeout added" in task_data["acceptance_criteria"]
    assert "Seen 3 times" in task_data["notes"]


def test_build_issue_payload(sample_task_file: Path) -> None:
    """build_issue_payload() must produce a well-formed GitHub issue payload."""
    task_data = parse_task_file(sample_task_file)
    payload = build_issue_payload(task_data, extra_labels=["area:dev-utils", "tier:2-structural"])

    assert payload["title"] == "[Task #42] Fix database migration deadlock on startup"
    assert "## Summary" in payload["body"]
    assert "## Observed Behavior" in payload["body"]
    assert "## Expected Behavior" in payload["body"]
    assert "## Evidence" in payload["body"]
    assert "## Impact" in payload["body"]

    assert any(lbl.startswith("type:") for lbl in payload["labels"])
    assert "source:agent" in payload["labels"]
    assert "risk:low" in payload["labels"]
    assert "area:dev-utils" in payload["labels"]
    assert "tier:2-structural" in payload["labels"]


def test_promote_task_to_issue_dry_run(sample_task_file: Path) -> None:
    """Dry-run promotion must report the intended issue without creating it."""
    result = promote_task_to_issue(
        task_path=sample_task_file,
        extra_labels=["area:dev-utils", "tier:1-friction"],
        execute=False,
    )

    assert result["action"] == "promote_task_to_issue"
    assert result["would_execute"] is False
    assert str(result["task_id"]) == "42"
    assert result["issue_payload"]["title"] == "[Task #42] Fix database migration deadlock on startup"
