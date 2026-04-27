---
concept: ensure-unicode-output-works-on-windows
source: plugin-code
source_file: link-checker/scripts/bulk_symlink_fixer.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.000387+00:00
cluster: path
content_hash: fd364852f93479fd
---

# Ensure Unicode output works on Windows

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/link-checker/scripts/bulk_symlink_fixer.py -->
#!/usr/bin/env python
"""
bulk_symlink_fixer.py — Find and fix broken symlinks in a folder hierarchy.

Scans a folder for symlink stand-ins (plain text files containing paths),
generates an inventory, and calls symlink_manager.py to fix them.

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

        # Check if it's a broken symlink
        if item.is_symlink() and not item.resolve().exists():
            try:
                target = item.readlink()
                issues.append(SymlinkIssue(
                    path=item,
                    issue_type="broken-symlink",
                    target=str(target)
                ))
            except Exception:
                pass

        # Check if it's a text-file stand-in (small file containing a path)
        elif not item.is_symlink() and item.stat().st_size < 512:
            try:
                content = item.read_text(encoding="utf-8", errors="ignore").strip()
                # Heuristic: looks like a relative path (contains / or \)
                if ("/" in content or "\\" in content) and "\n" not in content and not content.startswith("#"):
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
                        issues.append(SymlinkIssue(
                            path=item,
                            issue_type="text-file-standin",
                            target=content
                        ))
            except Exception:
                pass

    return issues


def generate_inventory(issues: list[SymlinkIssue], folder: Path) -> dict:
    """Generate an inventory report of found issues."""
    inventory = {
        "folder": str(fold

*(content truncated)*

<!-- Source: plugin-code/link-checker/scripts/fix_all_skills_comprehensive.py -->
#!/usr/bin/env python
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
            ["g

*(combined content truncated)*

## See Also

- [[ensure-unicode-output-works-on-windows-terminals-that-default-to-cp1252]]
- [[force-utf-8-output-on-windows-if-possible]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[files-to-exclude-from-output-listings]]
- [[force-utf-8-for-windows-consoles]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `link-checker/scripts/bulk_symlink_fixer.py`
- **Indexed:** 2026-04-27T05:21:04.000387+00:00
