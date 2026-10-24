#!/usr/bin/env python3
"""GitHub Issue Closure Script wrapping gh CLI.

Purpose:
    Closes GitHub issues with mandatory resolution labels and structured explanation comments.

Layer: Codify
Key Input Dependencies:
    - issue-taxonomy.json
    - redaction_gate.py
    - gh_issue_taxonomy_validate.py
"""

# Header compliance for coding conventions
# Module: plugins.dev_utils.skills.github_issue_agent.scripts.gh_issue_close

import argparse
import json
import os
import subprocess
import sys
from typing import Any, Dict, List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from redaction_gate import scan_for_secrets

VALID_RESOLUTIONS: List[str] = [
    "resolution:fixed",
    "resolution:superseded",
    "resolution:wont-fix",
    "resolution:obsolete",
    "resolution:accepted-debt",
]


def close_issue(issue_number: int, resolution: str, comment: str, execute: bool = False) -> Dict[str, Any]:
    """Validate parameters and optionally close a GitHub issue with resolution label and comment.

    Args:
        issue_number: GitHub issue number to close.
        resolution: Resolution taxonomy label (e.g. resolution:fixed).
        comment: Explanation comment markdown string.
        execute: If True, executes `gh` CLI commands to comment, edit label, and close.
                 If False (default), returns dry-run payload.

    Returns:
        Dict containing execution status, payload details, and error lists if validation fails.
    """
    errors: List[str] = []

    if resolution not in VALID_RESOLUTIONS:
        errors.append(f"Invalid resolution '{resolution}'. Must be one of {VALID_RESOLUTIONS}")

    is_clean, findings = scan_for_secrets(comment)
    if not is_clean:
        errors.extend(findings)

    if errors:
        return {"success": False, "errors": errors}

    payload: Dict[str, Any] = {
        "action": "close_issue",
        "issue_number": issue_number,
        "resolution": resolution,
        "comment": comment,
        "would_execute": execute,
        "success": True,
    }

    if not execute:
        return payload

    try:
        subprocess.run(["gh", "issue", "comment", str(issue_number), "--body", comment], check=True)
        subprocess.run(["gh", "issue", "edit", str(issue_number), "--add-label", resolution], check=True)
        subprocess.run(["gh", "issue", "close", str(issue_number)], check=True)
        payload["success"] = True
    except Exception as e:
        payload["success"] = False
        payload["errors"] = [str(e)]

    return payload


def main() -> None:
    """CLI entrypoint for issue closure script."""
    parser = argparse.ArgumentParser(description="Close a GitHub Issue with dry-run default and resolution label.")
    parser.add_argument("--issue", type=int, required=True, help="GitHub issue number")
    parser.add_argument("--resolution", required=True, choices=VALID_RESOLUTIONS, help="Resolution taxonomy label")
    parser.add_argument("--comment", required=True, help="Closure explanation comment")
    parser.add_argument("--execute", action="store_true", default=False, help="Execute live closure via gh CLI")

    args = parser.parse_args()

    result = close_issue(issue_number=args.issue, resolution=args.resolution, comment=args.comment, execute=args.execute)
    print(json.dumps(result, indent=2))
    if not result.get("success", False):
        sys.exit(1)


if __name__ == "__main__":
    main()
