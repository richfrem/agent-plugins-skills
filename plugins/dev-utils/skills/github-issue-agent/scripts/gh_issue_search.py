#!/usr/bin/env python3
"""GitHub Issue Deduplication Search & Root-Cause Consolidator.

Purpose:
  Evaluates potential duplicate issues and broader root-cause issues using the gh CLI.
  Determines whether an observed friction/bug event is itself a standalone issue or evidence
  for an existing broader root-cause issue.

Key Input Dependencies:
  - gh CLI (`gh issue list`)

Usage:
  python gh_issue_search.py --title "Issue title" --area "area:scripts"
"""

# Header compliance for coding conventions
# Module: plugins.dev_utils.skills.github_issue_agent.scripts.gh_issue_search

import json
import subprocess
import sys
from typing import Any, Dict, List, Optional


def consolidate_and_search_dedup(
    title: str,
    area_label: str,
    file_paths: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Search for matching GitHub issues, rank duplicate candidates, and evaluate root-cause consolidation.

    Args:
        title: Title/summary of the issue candidate.
        area_label: Mandatory area or plugin label filter (e.g., 'area:scripts' or 'plugin:agent-loops').
        file_paths: Optional list of affected file paths.

    Returns:
        Dict containing search results, candidate ranking, root cause match flag, and recommendation.
    """
    file_paths = file_paths or []
    cmd = [
        "gh", "issue", "list",
        "--json", "number,title,labels",
        "--label", area_label,
        "--limit", "30"
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        issues = json.loads(res.stdout) if res.stdout else []
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        issues = []

    has_root_cause = False
    target_issue_num: Optional[int] = None
    candidates: List[Dict[str, Any]] = []

    # Broad root-cause indicator phrases
    root_cause_keywords = [
        "file existence validation",
        "standardized validation",
        "centralized error handling",
        "unified schema enforcement",
        "global lock policy"
    ]

    title_words = [w.lower() for w in title.split() if len(w) > 3]

    for issue in issues:
        issue_num = issue.get("number")
        issue_title = issue.get("title", "")
        issue_title_lower = issue_title.lower()

        # 1. Check for broader root cause match
        if any(keyword in issue_title_lower for keyword in root_cause_keywords):
            has_root_cause = True
            target_issue_num = issue_num
            return {
                "has_existing_root_cause": True,
                "target_issue_number": target_issue_num,
                "candidates": [{"number": issue_num, "title": issue_title, "score": 1.0}],
                "recommendation": "comment_and_append_evidence"
            }

        # 2. Score title/keyword overlap for candidate duplicates
        matching_words = [w for w in title_words if w in issue_title_lower]
        if matching_words:
            score = round(len(matching_words) / max(len(title_words), 1), 2)
            candidates.append({
                "number": issue_num,
                "title": issue_title,
                "score": score
            })

    # Sort candidates by match score descending
    candidates.sort(key=lambda c: c["score"], reverse=True)

    return {
        "has_existing_root_cause": False,
        "target_issue_number": None,
        "candidates": candidates,
        "recommendation": "create_new_issue"
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: gh_issue_search.py <title> <area_label> [file_path1 ...]")
        sys.exit(1)

    search_title = sys.argv[1]
    search_label = sys.argv[2]
    search_files = sys.argv[3:]

    result_data = consolidate_and_search_dedup(search_title, search_label, search_files)
    print(json.dumps(result_data, indent=2))
