#!/usr/bin/env python3
"""
Audit Stale References
======================

Purpose:
    Scan the codebase for any remaining references to OLD tool paths
    that should have been migrated to their new plugin locations.
    Searches by both full relative path and bare filename.

Usage:
    python3 plugins/migration-utils/scripts/audit_stale_refs.py
    python3 plugins/migration-utils/scripts/audit_stale_refs.py --fix     # auto-replace
    python3 plugins/migration-utils/scripts/audit_stale_refs.py --json    # JSON output

Input:
    plugins/migration-utils/scripts/migration_inventory.json

Output:
    Report of files containing stale references, grouped by old path.
"""

import json
import os
import sys
import argparse
from pathlib import Path
from collections import defaultdict

# --- Configuration ---

SCAN_EXTENSIONS = {
    ".py", ".md", ".sh", ".yaml", ".yml", ".json",
    ".toml", ".mmd", ".txt", ".cfg", ".ini", ".rst",
    ".html", ".css", ".js", ".ts", ".tsx", ".jsx",
}

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
    "plugins/migration-utils",  # Don't audit ourselves
}

SKIP_FILES = {"migration_inventory.json", "package-lock.json"}


def load_inventory(inventory_path: str) -> dict:
    """Load the migration inventory JSON."""
    with open(inventory_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_search_terms(inventory: dict) -> dict:
    """
    Build a mapping of search terms to their info.
    Returns: {search_term: {"old_path": str, "new_path": str, "match_type": str}}
    """
    terms = {}

    for old_path, info in inventory.items():
        new_path = info.get("new_path")
        if not new_path or info.get("status") == "unmapped":
            continue

        # 1. Full relative path match
        terms[old_path] = {
            "old_path": old_path,
            "new_path": new_path,
            "match_type": "path",
        }

        # 2. Bare filename match (only for .py files to avoid false positives)
        basename = os.path.basename(old_path)
        if basename.endswith(".py") and basename not in {
            "__init__.py", "setup.py", "conftest.py"
        }:
            # Only add filename if it's unique enough
            new_basename = os.path.basename(new_path)
            if basename == new_basename:
                # Same filename in both locations — skip filename match
                # (would cause false positives on the new location)
                pass
            else:
                terms[basename] = {
                    "old_path": old_path,
                    "new_path": new_path,
                    "match_type": "filename",
                }

    return terms


def scan_file(filepath: str, search_terms: dict) -> list:
    """Scan a single file for stale references. Returns list of matches."""
    matches = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        for term, info in search_terms.items():
            if term in content:
                # Count occurrences and find line numbers
                lines_with_match = []
                for i, line in enumerate(content.splitlines(), 1):
                    if term in line:
                        lines_with_match.append((i, line.strip()))

                matches.append({
                    "file": filepath,
                    "term": term,
                    "old_path": info["old_path"],
                    "new_path": info["new_path"],
                    "match_type": info["match_type"],
                    "occurrences": len(lines_with_match),
                    "lines": lines_with_match[:5],  # Cap at 5 examples
                })
    except (OSError, UnicodeDecodeError):
        pass

    return matches


def scan_codebase(root: str, search_terms: dict) -> list:
    """Walk the codebase and scan all eligible files."""
    all_matches = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skipped directories
        rel_dir = os.path.relpath(dirpath, root)
        dirnames[:] = [
            d for d in dirnames
            if os.path.join(rel_dir, d) not in SKIP_DIRS
            and d not in {s.split("/")[0] for s in SKIP_DIRS}
        ]

        for filename in filenames:
            if filename in SKIP_FILES:
                continue
            _, ext = os.path.splitext(filename)
            if ext not in SCAN_EXTENSIONS:
                continue

            filepath = os.path.join(dirpath, filename)
            matches = scan_file(filepath, search_terms)
            all_matches.extend(matches)

    return all_matches


def fix_references(root: str, all_matches: list) -> int:
    """Replace old references with new ones in matched files."""
    # Group by file
    by_file = defaultdict(list)
    for m in all_matches:
        if m["match_type"] == "path":  # Only auto-fix full path matches
            by_file[m["file"]].append(m)

    fixed_count = 0
    for filepath, matches in by_file.items():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            original = content
            for m in matches:
                content = content.replace(m["old_path"], m["new_path"])

            if content != original:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                fixed_count += 1
                print(f"  [FIXED] {filepath}")
        except (OSError, UnicodeDecodeError):
            pass

    return fixed_count


def print_report(all_matches: list):
    """Print a human-readable audit report."""
    if not all_matches:
        print("\n✅ No stale references found. Migration is clean!")
        return

    # Group by old_path
    by_old = defaultdict(list)
    for m in all_matches:
        by_old[m["old_path"]].append(m)

    print(f"\n{'='*70}")
    print(f"  STALE REFERENCE AUDIT REPORT")
    print(f"  {len(all_matches)} stale references across {len(set(m['file'] for m in all_matches))} files")
    print(f"{'='*70}\n")

    for old_path in sorted(by_old.keys()):
        matches = by_old[old_path]
        new_path = matches[0]["new_path"]
        print(f"❌ {old_path}")
        print(f"   → Should be: {new_path}")
        print(f"   Found in {len(matches)} location(s):")
        for m in matches:
            match_tag = "📁" if m["match_type"] == "path" else "📄"
            print(f"     {match_tag} {m['file']} ({m['occurrences']} occurrences)")
            for line_no, line_text in m["lines"][:2]:
                print(f"        L{line_no}: {line_text[:100]}")
        print()

    print(f"{'='*70}")
    print(f"Total: {len(all_matches)} stale refs | {len(by_old)} old paths")
    print(f"Run with --fix to auto-replace full path matches.")
    print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(
        description="Audit codebase for stale tool path references"
    )
    parser.add_argument(
        "--inventory",
        default=None,
        help="Path to migration_inventory.json (auto-detected)",
    )
    parser.add_argument(
        "--fix", action="store_true",
        help="Auto-replace stale full-path references",
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--root", default=None,
        help="Project root (auto-detected)",
    )
    args = parser.parse_args()

    # Auto-detect paths
    script_dir = Path(__file__).resolve().parent
    if args.root:
        root = args.root
    else:
        root = str(script_dir.parent.parent.parent)  # plugins/migration-utils/scripts -> root

    if args.inventory:
        inv_path = args.inventory
    else:
        inv_path = str(script_dir / "migration_inventory.json")

    if not os.path.exists(inv_path):
        print(f"Error: Inventory not found at {inv_path}")
        sys.exit(1)

    print(f"🔍 Auditing stale references...")
    print(f"   Root: {root}")
    print(f"   Inventory: {inv_path}")

    # Load and build search terms
    inventory = load_inventory(inv_path)
    search_terms = build_search_terms(inventory)
    print(f"   Search terms: {len(search_terms)}")

    # Scan
    all_matches = scan_codebase(root, search_terms)

    # Output
    if args.json_output:
        # Strip non-serializable data
        for m in all_matches:
            m["lines"] = [(ln, txt) for ln, txt in m["lines"]]
        print(json.dumps(all_matches, indent=2))
    elif args.fix:
        print_report(all_matches)
        path_matches = [m for m in all_matches if m["match_type"] == "path"]
        if path_matches:
            print(f"\n🔧 Fixing {len(path_matches)} full-path references...")
            fixed = fix_references(root, path_matches)
            print(f"✅ Fixed {fixed} files.")
        else:
            print("\n✅ No fixable path references found.")
    else:
        print_report(all_matches)


if __name__ == "__main__":
    main()
