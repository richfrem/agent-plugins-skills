"""
Issue body section quality validator module for GitHub issues.

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
