#!/usr/bin/env python3
"""Task to Issue Bridge Script.

Purpose:
  Parses local task scratchpads (`tasks/*.md`) and promotes them into durable,
  evidence-validated GitHub Issue payloads via `gh_issue_create.py`.

Key Input Dependencies:
  - gh_issue_create.py (located in plugins/dev-utils/skills/github-issue-agent/scripts)

Usage:
  python task_to_issue_bridge.py --task-path /path/to/tasks/backlog/0042-item.md --labels "area:dev-utils,tier:2-structural" [--execute]
"""

# Header compliance for coding conventions
# Module: plugins.dev_utils.skills.github_issue_backlog_agent.scripts.task_to_issue_bridge

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Locate github-issue-agent scripts directory for gh_issue_create import
SCRIPT_DIR = Path(__file__).resolve().parent
GH_ISSUE_AGENT_SCRIPTS = SCRIPT_DIR.parents[1] / "github-issue-agent" / "scripts"

if str(GH_ISSUE_AGENT_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(GH_ISSUE_AGENT_SCRIPTS))

from gh_issue_create import create_issue


def parse_task_file(task_path: Path) -> Dict[str, Any]:
    """Parse a task markdown file into structured metadata and content sections.

    Args:
        task_path: Path object pointing to task markdown file.

    Returns:
        Dict containing frontmatter metadata and section content strings.
    """
    content = task_path.read_text(encoding="utf-8")
    
    # 1. Parse Frontmatter
    frontmatter: Dict[str, Any] = {}
    body_text = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body_text = parts[2]
            for line in fm_text.strip().splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    val_str = val.strip().strip('"').strip("'")
                    if val_str.isdigit():
                        frontmatter[key.strip()] = int(val_str)
                    else:
                        frontmatter[key.strip()] = val_str

    # Fallback ID extraction from filename (e.g. 0042-title.md)
    if "id" not in frontmatter:
        match = re.search(r"^(\d+)-", task_path.name)
        if match:
            frontmatter["id"] = int(match.group(1))
        else:
            frontmatter["id"] = "unknown"

    if "title" not in frontmatter:
        title_match = re.search(r"^#\s+(.+)$", body_text, re.MULTILINE)
        if title_match:
            frontmatter["title"] = title_match.group(1).strip()
        else:
            frontmatter["title"] = task_path.stem

    if "lane" not in frontmatter:
        frontmatter["lane"] = task_path.parent.name

    # 2. Parse Markdown Sections
    sections: Dict[str, str] = {
        "objective": "",
        "acceptance_criteria": "",
        "notes": "",
    }
    
    current_section: Optional[str] = None
    section_lines: List[str] = []

    for line in body_text.splitlines():
        line_stripped = line.strip()
        if line_stripped.startswith("#"):
            if current_section and current_section in sections:
                sections[current_section] = "\n".join(section_lines).strip()
            
            header_title = line_stripped.lstrip("#").strip().lower()
            if "objective" in header_title:
                current_section = "objective"
            elif "acceptance" in header_title or "criteria" in header_title:
                current_section = "acceptance_criteria"
            elif "note" in header_title:
                current_section = "notes"
            else:
                current_section = None
            section_lines = []
        else:
            if current_section:
                section_lines.append(line)

    if current_section and current_section in sections:
        sections[current_section] = "\n".join(section_lines).strip()

    return {
        "id": frontmatter["id"],
        "title": frontmatter["title"],
        "lane": frontmatter["lane"],
        "objective": sections["objective"] or "No objective specified.",
        "acceptance_criteria": sections["acceptance_criteria"] or "No criteria specified.",
        "notes": sections["notes"] or "None.",
        "raw_path": str(task_path),
    }


def build_issue_payload(task_data: Dict[str, Any], extra_labels: Optional[List[str]] = None) -> Dict[str, Any]:
    """Construct an issue title, body, and label set compliant with issue-taxonomy.json.

    Args:
        task_data: Dict parsed from parse_task_file.
        extra_labels: Optional list of additional labels.

    Returns:
        Dict containing title, body, and labels keys.
    """
    task_id = task_data["id"]
    title = f"[Task #{task_id}] {task_data['title']}"

    body = f"""## Summary
Escalating local task scratchpad item #{task_id} to durable GitHub issue backlog.

## Observed Behavior
Item was logged in local task scratchpad (`{task_data['lane']}` lane) and requires multi-session tracking or durable resolution.

## Expected Behavior
{task_data['objective']}

## Evidence
Acceptance Criteria:
{task_data['acceptance_criteria']}

Notes:
{task_data['notes']}

## Impact
Improves repository operational memory by promoting temporary task scratchpads into durable tracked GitHub issues.
"""

    labels = ["type:enhancement", "source:agent", "risk:low"]
    if extra_labels:
        for lbl in extra_labels:
            if lbl not in labels:
                labels.append(lbl)

    # Ensure tier label present
    if not any(lbl.startswith("tier:") for lbl in labels):
        labels.append("tier:1-friction")

    # Ensure location label present
    if not any(lbl.startswith("area:") or lbl.startswith("plugin:") for lbl in labels):
        labels.append("area:dev-utils")

    return {
        "title": title,
        "body": body,
        "labels": labels,
    }


def promote_task_to_issue(
    task_path: Path,
    extra_labels: Optional[List[str]] = None,
    execute: bool = False,
) -> Dict[str, Any]:
    """Promote a local task file to a GitHub issue.

    Args:
        task_path: Path object to task markdown file.
        extra_labels: Optional list of additional labels.
        execute: If True, executes live issue creation via gh. Default False.

    Returns:
        Dict containing action status and issue creation results.
    """
    task_data = parse_task_file(task_path)
    payload = build_issue_payload(task_data, extra_labels=extra_labels)

    creation_result = create_issue(
        title=payload["title"],
        body=payload["body"],
        labels=payload["labels"],
        execute=execute,
    )

    return {
        "action": "promote_task_to_issue",
        "would_execute": execute,
        "task_id": task_data["id"],
        "task_path": str(task_path),
        "issue_payload": payload,
        "result": creation_result,
    }


def main() -> None:
    """CLI entry point: parse a task file, build the issue payload, and promote it (or dry-run)."""
    parser = argparse.ArgumentParser(description="Promote local task file into GitHub Issue.")
    parser.add_argument("--task-path", required=True, help="Path to local task file")
    parser.add_argument("--labels", default="", help="Comma-separated extra labels")
    parser.add_argument("--execute", action="store_true", default=False, help="Execute live creation via gh CLI")

    args = parser.parse_args()
    task_path = Path(args.task_path)
    extra_labels = [l.strip() for l in args.labels.split(",") if l.strip()]

    result = promote_task_to_issue(task_path=task_path, extra_labels=extra_labels, execute=args.execute)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
