"""
Issue body section quality validator module for GitHub issues.

Purpose:
    Validates that a drafted GitHub issue body contains all 5 required
    markdown sections (Summary, Observed Behavior, Expected Behavior,
    Evidence, Impact) per github-issue-logging-policy.md before submission.

Key Input Dependencies:
    - Issue body text passed in by the caller (github-issue-agent scripts)

Copyright (c) 2026. All rights reserved.
"""

from typing import List, Tuple

REQUIRED_SECTIONS: List[str] = [
    "## Summary",
    "## Observed Behavior",
    "## Expected Behavior",
    "## Evidence",
    "## Impact",
]


def validate_issue_body(body: str) -> Tuple[bool, List[str]]:
    """Validate that issue body contains all mandatory standard sections.

    Args:
        body: Markdown content of the issue body.

    Returns:
        Tuple of (is_valid, errors) where is_valid is True if all required sections are present.
    """
    errors: List[str] = []
    for section in REQUIRED_SECTIONS:
        if section not in body:
            errors.append(f"Missing required issue body section: '{section}'")
    return (len(errors) == 0, errors)
