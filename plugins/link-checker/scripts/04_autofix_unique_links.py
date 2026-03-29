#!/usr/bin/env python3
"""
04_autofix_unique_links.py (CLI)
=====================================

Purpose:
    Fixer: Auto-corrects broken links using unique filename matches in the inventory.
    This is Phase 4 of the Link Checker pipeline.
    Reads broken_links.json (from Step 3) to target only files with known broken links.
    Falls back to a full repo walk if broken_links.json is not present.

Usage:
    python3 04_autofix_unique_links.py --root . [--dry-run] [--backup]
"""
import os
import json
import re
import shutil
import argparse
from urllib.parse import unquote
from typing import Dict, List, Optional, Set, Any


def calculate_relative_path(start_file: str, target_abs_path: str) -> str:
    """Calculates relative path from start_file to target_abs_path."""
    start_dir = os.path.dirname(start_file)
    return os.path.relpath(target_abs_path, start_dir).replace('\\', '/')


def fix_links_in_file(
    file_path: str,
    inventory: Dict[str, List[str]],
    root_dir: str,
    dry_run: bool,
    backup: bool,
) -> int:
    """
    Scans a file for broken markdown and image links and attempts to fix them
    if a unique basename match exists in the inventory.
    Handles both standard links [label](path) and image links ![alt](path).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return 0

    original_content = content

    # Capture optional leading '!' so image links are preserved correctly.
    # Group 1: label portion (e.g. [text] or ![alt])
    # Group 2: path inside parentheses
    link_pattern = re.compile(r'(!?\[.*?\])\((.*?)\)')

    fix_count = 0
    in_code_block = False

    def replace_link(match: re.Match) -> str:
        nonlocal fix_count
        label = match.group(1)
        link_path = match.group(2)

        # Skip web links, anchors, and root-absolute paths
        if link_path.startswith(('http', 'mailto:', '#', '/')):
            return match.group(0)

        clean_link = unquote(link_path.split('#')[0])
        anchor = '#' + link_path.split('#')[1] if '#' in link_path else ''

        # Check if the path already resolves
        file_dir = os.path.dirname(file_path)
        if os.path.exists(os.path.join(file_dir, clean_link)):
            return match.group(0)

        # It's broken — look up by basename
        basename = os.path.basename(clean_link)
        if not basename or basename.lower() == 'readme.md':
            return match.group(0)

        candidates = inventory.get(basename, [])

        # Only fix if the match is UNIQUE
        if len(candidates) == 1:
            target_abs = os.path.join(root_dir, candidates[0])
            new_rel = calculate_relative_path(file_path, target_abs)

            if dry_run:
                print(f"  [DRY-RUN] {file_path}: {basename} -> {new_rel}")
            else:
                print(f"  [FIXED]   {file_path}: {basename} -> {new_rel}")

            fix_count += 1
            return f"{label}({new_rel}{anchor})"

        return match.group(0)

    # Process line-by-line to skip code blocks
    lines = content.splitlines(keepends=True)
    processed_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code_block = not in_code_block
        if in_code_block:
            processed_lines.append(line)
        else:
            processed_lines.append(link_pattern.sub(replace_link, line))

    new_content = ''.join(processed_lines)

    if not dry_run and new_content != original_content:
        if backup:
            shutil.copy2(file_path, file_path + '.bak')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

    return fix_count


def collect_files_from_broken_links(
    broken_links_path: str, root_dir: str
) -> Optional[Set[str]]:
    """
    Reads broken_links.json to get the targeted set of files that need fixing.
    Returns None if the file doesn't exist (triggers fallback full-walk mode).
    """
    if not os.path.exists(broken_links_path):
        return None
    with open(broken_links_path, 'r', encoding='utf-8') as f:
        broken_list: List[Dict[str, Any]] = json.load(f)
    return {os.path.join(root_dir, item['source_file']) for item in broken_list}


def main() -> None:
    parser = argparse.ArgumentParser(description="Step 4: Auto-fix unique link matches.")
    parser.add_argument("--root", default=".", help="Root directory of the repo")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--backup", action="store_true", help="Write .bak copy before modifying each file")
    parser.add_argument("--broken-links", default="broken_links.json",
                        help="broken_links.json from Step 3 (used to target only affected files)")
    args = parser.parse_args()

    root_dir = os.path.abspath(args.root)
    inventory_path = "file_inventory.json"

    if not os.path.exists(inventory_path):
        print("Error: file_inventory.json not found. Run Step 1 first.")
        return

    with open(inventory_path, 'r', encoding='utf-8') as f:
        inventory = json.load(f)

    print(f"Repairing links in {root_dir} (Dry-run: {args.dry_run})...")

    # Prefer targeted mode: only visit files flagged by the auditor in Step 3
    files_to_fix = collect_files_from_broken_links(args.broken_links, root_dir)

    if files_to_fix is not None:
        print(f"Targeting {len(files_to_fix)} file(s) from broken_links.json.")
        file_iter = sorted(f for f in files_to_fix if f.endswith(('.md', '.markdown')))
    else:
        print("Warning: broken_links.json not found — falling back to full repo walk.")
        print("Run Step 3 first for targeted, efficient fixing.")
        file_iter = []
        for walk_root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '.venv', '.next', 'bin', 'obj'}]
            for filename in files:
                if filename.endswith(('.md', '.markdown')):
                    file_iter.append(os.path.join(walk_root, filename))

    total_fixed = 0
    for file_path in file_iter:
        total_fixed += fix_links_in_file(file_path, inventory, root_dir, args.dry_run, args.backup)

    print(f"{'Would have fixed' if args.dry_run else 'Fixed'} {total_fixed} link(s).")


if __name__ == "__main__":
    main()