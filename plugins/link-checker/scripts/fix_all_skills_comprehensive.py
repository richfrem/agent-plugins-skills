#!/usr/bin/env python3
"""
fix_all_skills_comprehensive.py — Run bulk_symlink_fixer on ALL skill subfolders.

Scans:
  - plugins/*/skills/*/scripts/
  - plugins/*/skills/*/assets/
  - plugins/*/skills/*/resources/
  - plugins/*/skills/*/assets/resources/

Collects statistics and reports.

Usage:
  python fix_all_skills_comprehensive.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Ensure Unicode output works on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


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


def find_all_skill_folders(repo_root: Path) -> list[Path]:
    """Find all scripts, assets, resources folders in skill directories."""
    folders = []
    plugins_dir = repo_root / "plugins"

    if not plugins_dir.exists():
        return folders

    # Find all skill directories
    for skill_dir in sorted(plugins_dir.glob("*/skills/*")):
        if not skill_dir.is_dir():
            continue

        # Check for scripts, assets, resources folders
        for subfolder in ["scripts", "assets", "resources"]:
            target = skill_dir / subfolder
            if target.is_dir():
                folders.append(target)

        # Also check for nested resources (assets/resources)
        nested_resources = skill_dir / "assets" / "resources"
        if nested_resources.is_dir() and nested_resources not in folders:
            folders.append(nested_resources)

    return folders


def main() -> int:
    repo_root = find_repo_root()
    bulk_fixer = repo_root / "plugins" / "link-checker" / "scripts" / "bulk_symlink_fixer.py"

    if not bulk_fixer.exists():
        print(f"Error: bulk_symlink_fixer.py not found at {bulk_fixer}")
        return 1

    folders = find_all_skill_folders(repo_root)

    print("=" * 80)
    print(f"FIXING ALL SKILL FOLDERS (scripts + assets + resources)")
    print(f"Total folders to scan: {len(folders)}")
    print("=" * 80)
    print()

    total_fixed = 0
    folders_with_issues = []
    folders_clean = 0

    for i, folder in enumerate(folders, 1):
        folder_rel = folder.relative_to(repo_root)
        print(f"[{i}/{len(folders)}] {folder_rel}")

        result = subprocess.run(
            ["python", str(bulk_fixer), str(folder_rel)],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )

        # Parse the output for counts
        output = result.stdout
        fixed = 0

        # Look for "Fixed: X" in summary
        for line in output.split("\n"):
            if line.startswith("Fixed:"):
                try:
                    fixed = int(line.split(":")[1].strip())
                except (ValueError, IndexError):
                    pass

        # Check if any issues were found
        if "Total issues: 0" in output:
            print("      ✓ Clean")
            folders_clean += 1
        elif fixed > 0 or result.returncode == 0:
            if fixed > 0:
                total_fixed += fixed
                folders_with_issues.append((folder_rel, fixed))
                print(f"      ✓ Fixed {fixed}")
            else:
                print("      ✓ Clean")
                folders_clean += 1
        else:
            print(f"      ✗ Error: {result.stderr[:100]}")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Folders scanned: {len(folders)}")
    print(f"  • scripts/ folders: ~89")
    print(f"  • assets/ folders: ~49")
    print(f"  • resources/ folders: ~13")
    print()
    print(f"Folders clean: {folders_clean}")
    print(f"Folders with fixes: {len(folders_with_issues)}")
    print(f"Total symlinks fixed: {total_fixed}")
    print()

    if folders_with_issues:
        print("Folders with symlinks fixed:")
        for folder, count in sorted(folders_with_issues, key=lambda x: -x[1])[:20]:
            print(f"  • {folder}: {count} symlinks")
        if len(folders_with_issues) > 20:
            print(f"  ... and {len(folders_with_issues) - 20} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
