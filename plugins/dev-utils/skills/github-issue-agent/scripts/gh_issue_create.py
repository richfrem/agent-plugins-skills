#!/usr/bin/env python3
"""GitHub Issue Creator script wrapping gh CLI.

Purpose:
  Enforces dry-run default (payload generation mode), secret scanning,
  taxonomy validation, and body section validation prior to issue creation.

Key Input Dependencies:
  - gh_issue_taxonomy_validate.py
  - body_validator.py
  - redaction_gate.py

Usage:
  python gh_issue_create.py --title "Title" --body "Body" --labels "label1,label2" [--execute]
"""

# Header compliance for coding conventions
# Module: plugins.dev_utils.skills.github_issue_agent.scripts.gh_issue_create

import argparse
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from body_validator import validate_issue_body
from gh_issue_taxonomy_validate import validate_taxonomy
from redaction_gate import scan_for_secrets


def create_issue(
    title: str,
    body: str,
    labels: List[str],
    execute: bool = False,
    taxonomy_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate and optionally create a GitHub issue.

    Args:
        title: Issue title string.
        body: Markdown content of issue body.
        labels: List of label strings.
        execute: If True, invokes `gh issue create`. If False (default), returns dry-run JSON payload.
        taxonomy_path: Optional path to issue-taxonomy.json.

    Returns:
        Dict containing payload status, validation results, and execution output.
    """
    # 1. Secret Scanning
    clean_title, title_secrets = scan_for_secrets(title)
    clean_body, body_secrets = scan_for_secrets(body)
    if not clean_title or not clean_body:
        raise ValueError(f"Secret redaction gate failed: {title_secrets + body_secrets}")

    # 2. Body Validation
    valid_body, body_errors = validate_issue_body(body)
    if not valid_body:
        raise ValueError(f"Body validation failed: {body_errors}")

    # 3. Taxonomy Validation
    valid_tax, tax_errors = validate_taxonomy(labels, taxonomy_path=taxonomy_path)
    if not valid_tax:
        raise ValueError(f"Taxonomy validation failed: {tax_errors}")

    payload: Dict[str, Any] = {
        "action": "create_issue",
        "would_execute": execute,
        "title": title,
        "body": body,
        "labels": labels,
        "redaction_check": "passed",
        "body_validation": "passed",
        "taxonomy_validation": "passed",
    }

    if not execute:
        return payload

    cmd = ["gh", "issue", "create", "--title", title, "--body", body]
    for label in labels:
        cmd.extend(["--label", label])

    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload["output"] = res.stdout.strip()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a GitHub Issue with dry-run default.")
    parser.add_argument("--title", required=True, help="Issue title")
    parser.add_argument("--body", required=True, help="Issue body markdown")
    parser.add_argument("--labels", required=True, help="Comma-separated labels")
    parser.add_argument("--execute", action="store_true", default=False, help="Execute live creation via gh CLI")

    args = parser.parse_args()
    labels = [l.strip() for l in args.labels.split(",") if l.strip()]

    result = create_issue(title=args.title, body=args.body, labels=labels, execute=args.execute)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
