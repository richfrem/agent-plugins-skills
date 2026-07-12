#!/usr/bin/env python
"""
bulk_symlink_fixer.py — Find and fix broken symlinks in a folder hierarchy.

Purpose:
    Scans a folder for symlink stand-ins (plain text files containing paths),
    generates an inventory, and calls symlink_manager.py to fix them.

Key Input Dependencies:
    - Git repository (uses `git rev-parse --show-toplevel` to find repo root)
    - symlink_manager.py (in .agents/skills/symlink-manager/scripts/ or
      plugins/dev-utils/scripts/, used to create the corrected symlinks)
    - Target folder to scan (positional CLI argument)

Usage:
  python bulk_symlink_fixer.py <folder-path>
  python bulk_symlink_fixer.py plugins/plugin-manager/skills/plugin-installer/scripts

Returns:
  0 if all fixed successfully
  1 if any repairs failed
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

# Ensure Unicode output works on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


class SymlinkIssue(NamedTuple):
    """A detected broken symlink or stand-in."""
    path: Path
    issue_type: str  # "text-file-standin" or "broken-symlink"
    target: str | None  # what it claims to point to


def find_repo_root() -> Path:
    """Walk up from cwd to find the git repo root."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except FileNotFoundError:
        pass
    return Path.cwd()


def _check_broken_symlink(item: Path) -> SymlinkIssue | None:
    """Return a SymlinkIssue if item is a symlink pointing to a nonexistent target."""
    if not (item.is_symlink() and not item.resolve().exists()):
        return None
    try:
        target = item.readlink()
        return SymlinkIssue(path=item, issue_type="broken-symlink", target=str(target))
    except Exception:
        return None


def _check_text_standin(item: Path, repo_root: Path) -> SymlinkIssue | None:
    """Return a SymlinkIssue if item is a small text file that looks like a stand-in path."""
    if item.is_symlink() or item.stat().st_size >= 512:
        return None
    try:
        content = item.read_text(encoding="utf-8", errors="ignore").strip()
        # Heuristic: looks like a relative path (contains / or \)
        if not (("/" in content or "\\" in content) and "\n" not in content and not content.startswith("#")):
            return None

        # Try to resolve it: first from the file's directory, then from repo root
        # Normalize path separators
        normalized = content.replace("\\", "/")

        # Try relative to the file's parent directory
        candidate = (item.parent / normalized).resolve()

        # If that doesn't work, try from repo root
        if not candidate.exists():
            candidate = (repo_root / normalized).resolve()

        # If it exists or looks like a valid repo path, mark it as an issue
        if candidate.exists() or (normalized.startswith("../../") or normalized.startswith("../../../")):
            return SymlinkIssue(path=item, issue_type="text-file-standin", target=content)
    except Exception:
        pass
    return None


def find_broken_symlinks(folder: Path) -> list[SymlinkIssue]:
    """
    Find broken symlinks and text-file stand-ins in a folder hierarchy.

    Returns list of SymlinkIssue objects.
    """
    issues = []
    repo_root = find_repo_root()

    if not folder.exists():
        print(f"Error: folder does not exist: {folder}")
        return issues

    print(f"[*] Scanning {folder} for broken symlinks and stand-ins...")
    print()

    for item in folder.rglob("*"):
        if not item.is_file():
            continue

        broken = _check_broken_symlink(item)
        if broken:
            issues.append(broken)
            continue

        standin = _check_text_standin(item, repo_root)
        if standin:
            issues.append(standin)

    return issues


def generate_inventory(issues: list[SymlinkIssue], folder: Path) -> dict:
    """Generate an inventory report of found issues."""
    inventory = {
        "folder": str(folder),
        "total_issues": len(issues),
        "by_type": {
            "text-file-standin": len([i for i in issues if i.issue_type == "text-file-standin"]),
            "broken-symlink": len([i for i in issues if i.issue_type == "broken-symlink"]),
        },
        "issues": [
            {
                "path": str(issue.path),
                "type": issue.issue_type,
                "target": issue.target
            }
            for issue in issues
        ]
    }
    return inventory


def print_inventory(inventory: dict) -> None:
    """Pretty-print the inventory."""
    print("=" * 80)
    print("INVENTORY")
    print("=" * 80)
    print(f"Folder: {inventory['folder']}")
    print(f"Total issues: {inventory['total_issues']}")
    print()
    print(f"  Text-file stand-ins: {inventory['by_type']['text-file-standin']}")
    print(f"  Broken symlinks: {inventory['by_type']['broken-symlink']}")

    if inventory['issues']:
        print()
        print("Issues found:")
        print()
        for issue in inventory['issues']:
            print(f"  [{issue['type']}] {issue['path']}")
            print(f"    → {issue['target']}")
    else:
        print()
        print("  No issues found.")


def _fix_one_symlink(issue: SymlinkIssue, repo_root: Path, symlink_manager: Path,
                      index: int, total: int) -> str:
    """Resolve paths and invoke symlink_manager.py create for one issue. Returns 'fixed' or 'failed'."""
    # For text-file stand-ins, convert the local relative path to repo-relative path
    # issue.target is relative to the file's directory (e.g., "../../scripts/file.py")
    # We need to convert it to repo-relative (e.g., "plugins/dev-utils/scripts/file.py")

    # Resolve from the file's directory
    file_dir = issue.path.parent
    resolved_src = (file_dir / issue.target).resolve()
    src = str(resolved_src.relative_to(repo_root))

    dst = str(issue.path.relative_to(repo_root))

    print(f"[{index}/{total}] Fixing: {dst}")

    try:
        result = subprocess.run(
            ["python", str(symlink_manager), "create", "--src", src, "--dst", dst],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )

        if result.returncode == 0:
            print(f"      ✓ Fixed")
            return "fixed"
        print(f"      ✗ Failed: {result.stderr.strip()}")
        return "failed"
    except Exception as e:
        print(f"      ✗ Error: {e}")
        return "failed"


def fix_symlinks(issues: list[SymlinkIssue]) -> tuple[int, int, int]:
    """
    Fix symlinks by calling symlink_manager.py create for each issue.

    Returns (fixed_count, skipped_count, failed_count).
    """
    if not issues:
        print()
        print("No issues to fix.")
        return 0, 0, 0

    print()
    print("=" * 80)
    print("FIXING SYMLINKS")
    print("=" * 80)
    print()

    repo_root = find_repo_root()
    # Try installed location first, then plugin source as fallback
    symlink_manager = repo_root / ".agents" / "skills" / "symlink-manager" / "scripts" / "symlink_manager.py"
    if not symlink_manager.exists():
        symlink_manager = repo_root / "plugins" / "dev-utils" / "scripts" / "symlink_manager.py"

    if not symlink_manager.exists():
        print(f"Error: symlink_manager.py not found at {symlink_manager}")
        return 0, 0, len(issues)

    fixed = 0
    skipped = 0
    failed = 0

    for i, issue in enumerate(issues, 1):
        status = _fix_one_symlink(issue, repo_root, symlink_manager, i, len(issues))
        if status == "fixed":
            fixed += 1
        else:
            failed += 1

    return fixed, skipped, failed


def main() -> int:
    """Parse CLI arguments, scan for broken symlinks/stand-ins, and fix them via symlink_manager.py."""
    parser = argparse.ArgumentParser(
        description="Find and fix broken symlinks in a folder hierarchy"
    )
    parser.add_argument(
        "folder",
        help="Folder to scan (relative to repo root)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output inventory as JSON"
    )

    args = parser.parse_args()

    repo_root = find_repo_root()
    folder = repo_root / args.folder

    print()

    # Find issues
    issues = find_broken_symlinks(folder)
    inventory = generate_inventory(issues, folder)

    # Print inventory
    if args.json:
        print(json.dumps(inventory, indent=2))
    else:
        print_inventory(inventory)

    # Fix symlinks
    if issues:
        fixed, skipped, failed = fix_symlinks(issues)

        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Fixed: {fixed}")
        print(f"Skipped: {skipped}")
        print(f"Failed: {failed}")
        print()

        return 0 if failed == 0 else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
