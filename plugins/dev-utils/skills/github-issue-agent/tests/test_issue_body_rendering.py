"""
Unit tests for issue body quality validation in github-issue-agent.

Copyright (c) 2026. All rights reserved.
"""

import sys
from pathlib import Path

# Add script directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import pytest
from body_validator import validate_issue_body


def test_validate_issue_body_complete() -> None:
    """Test that issue body containing all 5 required sections passes validation."""
    body = """
## Summary
Script failed to run due to missing dependency.

## Observed Behavior
ImportError thrown on line 5.

## Expected Behavior
Script should import module cleanly.

## Evidence
Traceback log snippet attached.

## Impact
Blocks build pipeline.
"""
    is_valid, errors = validate_issue_body(body)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_issue_body_missing_evidence() -> None:
    """Test that issue body missing ## Evidence fails validation."""
    body = """
## Summary
Script failed to run.

## Observed Behavior
Error thrown.

## Expected Behavior
No error.

## Impact
Blocks build.
"""
    is_valid, errors = validate_issue_body(body)
    assert is_valid is False
    assert any("## Evidence" in err for err in errors)


def test_validate_issue_body_missing_multiple_sections() -> None:
    """Test that issue body missing several sections reports all missing headers."""
    body = "## Summary\nJust a quick summary without required sections."
    is_valid, errors = validate_issue_body(body)
    assert is_valid is False
    assert len(errors) == 4
