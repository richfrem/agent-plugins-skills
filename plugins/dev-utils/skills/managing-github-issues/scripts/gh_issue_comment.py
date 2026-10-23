#!/usr/bin/env python3
"""GitHub Issue Commenter script wrapping gh CLI.

Purpose:
  Enforces dry-run default (payload generation mode) and secret scanning prior to issue commenting.

Key Input Dependencies:
  - redaction_gate.py

Usage:
  python gh_issue_comment.py --issue 42 --body "Comment body" [--execute]
"""

# Header compliance for coding conventions
# Module: plugins.dev_utils.skills.github_issue_agent.scripts.gh_issue_comment

import argparse
import json
import os
import subprocess
import sys
from typing import Any, Dict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from redaction_gate import scan_for_secrets


def comment_issue(issue_number: int, body: str, execute: bool = False) -> Dict[str, Any]:
    """Validate and optionally comment on a GitHub issue.

    Args:
        issue_number: GitHub issue number.
        body: Comment body markdown string.
        execute: If True, invokes `gh issue comment`. If False (default), returns dry-run JSON payload.

    Returns:
        Dict containing payload status, validation results, and execution output.
    """
    clean_body, body_secrets = scan_for_secrets(body)
    if not clean_body:
        raise ValueError(f"Secret redaction gate failed: {body_secrets}")

    payload: Dict[str, Any] = {
        "action": "comment_issue",
        "would_execute": execute,
        "issue_number": issue_number,
        "body": body,
        "redaction_check": "passed",
    }

    if not execute:
        return payload

    cmd = ["gh", "issue", "comment", str(issue_number), "--body", body]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload["output"] = res.stdout.strip()
    return payload


def main() -> None:
    """CLI entry point: parse args and post (or dry-run) a comment on the given issue."""
    parser = argparse.ArgumentParser(description="Comment on a GitHub Issue with dry-run default.")
    parser.add_argument("--issue", type=int, required=True, help="GitHub issue number")
    parser.add_argument("--body", required=True, help="Comment body markdown")
    parser.add_argument("--execute", action="store_true", default=False, help="Execute live commenting via gh CLI")

    args = parser.parse_args()

    result = comment_issue(issue_number=args.issue, body=args.body, execute=args.execute)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
