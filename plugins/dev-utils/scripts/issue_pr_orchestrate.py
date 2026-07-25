#!/usr/bin/env python3
"""Issue PR Lifecycle Orchestrator Script.

Purpose:
    Orchestrates the end-to-end lifecycle flow: Issue -> Worktree -> Implementation -> PR Creation -> Resolution Closure.

Key Input Dependencies:
    - issue_worktree_manage.py (for git worktree creation and cleanup)
    - GitHub CLI (`gh`) for PR creation and issue closure

Usage:
    python issue_pr_orchestrate.py --issue 42 --title "Fix login bug" --body "Resolves crash on empty password" [--dry-run]
"""

# Header compliance for coding conventions
# Module: plugins.dev_utils.scripts.issue_pr_orchestrate

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from issue_worktree_manage import create_worktree, remove_worktree


def _build_lifecycle_steps(
    issue_number: int,
    branch_name: str,
    worktree_path: str,
    base_branch: str,
    title: str,
    pr_body: str,
    draft: bool,
) -> list[Dict[str, Any]]:
    """Builds step sequence dicts for lifecycle orchestration."""
    return [
        {
            "step": "worktree_create",
            "cmd": ["git", "worktree", "add", "-b", branch_name, worktree_path, base_branch],
        },
        {
            "step": "pr_create",
            "cmd": [
                "gh",
                "pr",
                "create",
                "--title",
                title,
                "--body",
                pr_body,
                "--base",
                base_branch,
                "--head",
                branch_name,
            ] + (["--draft"] if draft else []),
        },
        {
            "step": "issue_close",
            "cmd": ["gh", "issue", "close", str(issue_number), "--comment", f"Resolved via PR for issue #{issue_number}."],
        },
        {
            "step": "worktree_remove",
            "cmd": ["git", "worktree", "remove", worktree_path],
        },
    ]


def generate_lifecycle_payload(
    issue_number: int,
    title: str,
    body: str,
    base_branch: str = "main",
    draft: bool = False,
) -> Dict[str, Any]:
    """Generates the dry-run lifecycle payload and command plan for an issue."""
    branch_name = f"issue-{issue_number}"
    worktree_path = f".worktrees/issue-{issue_number}"
    pr_body = f"{body}\n\nCloses #{issue_number}" if f"#{issue_number}" not in body else body

    steps = _build_lifecycle_steps(
        issue_number=issue_number,
        branch_name=branch_name,
        worktree_path=worktree_path,
        base_branch=base_branch,
        title=title,
        pr_body=pr_body,
        draft=draft,
    )

    return {
        "issue_number": issue_number,
        "branch_name": branch_name,
        "worktree_path": worktree_path,
        "base_branch": base_branch,
        "pr_title": title,
        "pr_body": pr_body,
        "draft": draft,
        "steps": steps,
    }


def _execute_lifecycle_steps(
    issue_number: int,
    payload: Dict[str, Any],
    base_branch: str,
) -> Dict[str, Any]:
    """Executes live subprocess steps for lifecycle flow."""
    results: Dict[str, Any] = {"success": True, "dry_run": False, "steps": {}}

    wt_res = create_worktree(
        issue_number=issue_number,
        branch_name=payload["branch_name"],
        base_branch=base_branch,
    )
    results["steps"]["worktree_create"] = wt_res
    if not wt_res.get("success"):
        results["success"] = False
        results["error"] = "Failed to create worktree."
        return results

    pr_cmd = payload["steps"][1]["cmd"]
    pr_proc = subprocess.run(pr_cmd, capture_output=True, text=True)
    results["steps"]["pr_create"] = {
        "success": pr_proc.returncode == 0,
        "stdout": pr_proc.stdout,
        "stderr": pr_proc.stderr,
        "returncode": pr_proc.returncode,
    }
    if pr_proc.returncode != 0:
        results["success"] = False
        results["error"] = "Failed to create PR."
        return results

    close_cmd = payload["steps"][2]["cmd"]
    close_proc = subprocess.run(close_cmd, capture_output=True, text=True)
    results["steps"]["issue_close"] = {
        "success": close_proc.returncode == 0,
        "stdout": close_proc.stdout,
        "stderr": close_proc.stderr,
        "returncode": close_proc.returncode,
    }

    rm_res = remove_worktree(issue_number=issue_number)
    results["steps"]["worktree_remove"] = rm_res

    return results


def orchestrate_lifecycle(
    issue_number: int,
    title: str,
    body: str,
    base_branch: str = "main",
    draft: bool = False,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Orchestrates the lifecycle flow: Worktree -> PR -> Close -> Cleanup."""
    payload = generate_lifecycle_payload(
        issue_number=issue_number,
        title=title,
        body=body,
        base_branch=base_branch,
        draft=draft,
    )

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "payload": payload,
            "message": f"Dry-run lifecycle plan generated for issue #{issue_number}.",
        }

    return _execute_lifecycle_steps(
        issue_number=issue_number,
        payload=payload,
        base_branch=base_branch,
    )


def main() -> None:
    """CLI entrypoint for issue PR lifecycle orchestration."""
    parser = argparse.ArgumentParser(description="Orchestrate issue PR lifecycle flow.")
    parser.add_argument("--issue", type=int, required=True, help="GitHub issue number")
    parser.add_argument("--title", type=str, required=True, help="PR title")
    parser.add_argument("--body", type=str, required=True, help="PR body description")
    parser.add_argument("--base", type=str, default="main", help="Base target branch")
    parser.add_argument("--draft", action="store_true", help="Create PR as draft")
    parser.add_argument("--execute", action="store_true", help="Execute live lifecycle commands")

    args = parser.parse_args()
    res = orchestrate_lifecycle(
        issue_number=args.issue,
        title=args.title,
        body=args.body,
        base_branch=args.base,
        draft=args.draft,
        dry_run=not args.execute,
    )
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
