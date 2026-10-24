"""Git worktree manager script for issue isolation.

Purpose:
    Provides programmatic interface for creating, listing, and removing isolated git worktrees
    for GitHub issue execution branches under `.worktrees/issue-NNN`.

Key Input Dependencies:
    - Git binary available in environment path
    - Repository initialized as git repository
"""

import argparse
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List, Optional


def create_worktree(
    issue_number: int,
    branch_name: Optional[str] = None,
    base_branch: str = "main",
    worktree_dir: str = ".worktrees",
) -> Dict[str, Any]:
    """Creates a new git worktree for a specific issue.

    Args:
        issue_number: GitHub issue number.
        branch_name: Optional custom branch name. Defaults to 'issue-{issue_number}'.
        base_branch: Base commit or branch to branch off of.
        worktree_dir: Directory where worktrees are stored.

    Returns:
        Dict containing success status, worktree path, branch name, and stderr/stdout.
    """
    if not branch_name:
        branch_name = f"issue-{issue_number}"

    target_path = Path(worktree_dir) / f"issue-{issue_number}"
    cmd = [
        "git",
        "worktree",
        "add",
        "-b",
        branch_name,
        str(target_path),
        base_branch,
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    success = proc.returncode == 0

    return {
        "success": success,
        "issue_number": issue_number,
        "branch_name": branch_name,
        "worktree_path": str(target_path),
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "returncode": proc.returncode,
    }


def list_worktrees() -> List[Dict[str, str]]:
    """Lists active git worktrees.

    Returns:
        List of dictionaries containing path, commit, and branch information.
    """
    cmd = ["git", "worktree", "list"]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    worktrees: List[Dict[str, str]] = []
    if proc.returncode != 0:
        return worktrees

    for line in proc.stdout.strip().splitlines():
        if not line.strip():
            continue
        parts = line.split(maxsplit=2)
        if len(parts) >= 1:
            path = parts[0]
            commit = parts[1] if len(parts) >= 2 else ""
            branch = parts[2].strip("[]") if len(parts) >= 3 else ""
            worktrees.append({
                "path": path,
                "commit": commit,
                "branch": branch,
            })

    return worktrees


def remove_worktree(
    issue_number: int,
    force: bool = False,
    worktree_dir: str = ".worktrees",
) -> Dict[str, Any]:
    """Removes an existing git worktree for a specific issue.

    Args:
        issue_number: GitHub issue number.
        force: Whether to force removal of worktree with uncommitted changes.
        worktree_dir: Directory where worktrees are stored.

    Returns:
        Dict containing success status, issue number, and output.
    """
    target_path = Path(worktree_dir) / f"issue-{issue_number}"
    cmd = ["git", "worktree", "remove"]
    if force:
        cmd.append("--force")
    cmd.append(str(target_path))

    proc = subprocess.run(cmd, capture_output=True, text=True)
    success = proc.returncode == 0

    return {
        "success": success,
        "issue_number": issue_number,
        "worktree_path": str(target_path),
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "returncode": proc.returncode,
    }


def main() -> None:
    """CLI entrypoint for managing issue worktrees."""
    parser = argparse.ArgumentParser(description="Manage issue git worktrees.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a worktree")
    create_parser.add_argument("--issue", type=int, required=True, help="Issue number")
    create_parser.add_argument("--branch", type=str, help="Branch name")
    create_parser.add_argument("--base", type=str, default="main", help="Base branch")

    list_parser = subparsers.add_parser("list", help="List worktrees")

    remove_parser = subparsers.add_parser("remove", help="Remove a worktree")
    remove_parser.add_argument("--issue", type=int, required=True, help="Issue number")
    remove_parser.add_argument("--force", action="store_true", help="Force removal")

    args = parser.parse_args()

    if args.command == "create":
        res = create_worktree(issue_number=args.issue, branch_name=args.branch, base_branch=args.base)
        print(res)
    elif args.command == "list":
        res = list_worktrees()
        print(res)
    elif args.command == "remove":
        res = remove_worktree(issue_number=args.issue, force=args.force)
        print(res)


if __name__ == "__main__":
    main()
