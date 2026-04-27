---
concept: capture-optional-leading-so-image-links-are-preserved-correctly
source: plugin-code
source_file: link-checker/scripts/04_autofix_unique_links.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.247933+00:00
cluster: basename
content_hash: ec77c63b6b4ca225
---

# Capture optional leading '!' so image links are preserved correctly.

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/link-checker/scripts/04_autofix_unique_links.py -->
#!/usr/bin/env python
"""
04_autofix_unique_links.py (CLI)
=====================================

Purpose:
    Fixer: Auto-corrects broken links using unique filename matches in the inventory.
    This is Phase 4 of the Link Checker pipeline.
    Reads broken_links.json (from Step 3) to target only files with known broken links.
    Falls back to a full repo walk if broken_links.json is not present.
    After fixing, writes remaining_broken_links.json so Step 5 reflects post-fix state.

Usage:
    python04_autofix_unique_links.py --root . [--dry-run] [--backup]

Scope:
    Only fixes markdown links [label](path) and image links ![alt](path).
    Code path references (e.g. './config.json' in .py or .js files) are audited
    by Step 3 but are intentionally NOT modified by this script.
"""
import os
import json
import re
import shutil
import argparse
from urllib.parse import unquote
from typing import Dict, List, Any


def calculate_relative_path(start_file: str, target_abs_path: str) -> str:
    """Calculates relative path from start_file to target_abs_path."""
    start_dir = os.path.dirname(start_file)
    return os.path.relpath(target_abs_path, start_dir).replace('\\', '/')


def lookup_basename(inventory: Dict[str, List[str]], basename: str) -> List[str]:
    """
    Returns inventory candidates for basename.
    Tries an exact match first, then falls back to a case-insensitive search
    for compatibility with case-insensitive filesystems (macOS, Windows).
    """
    candidates = inventory.get(basename, [])
    if not candidates:
        lower = basename.lower()
        candidates = next((v for k, v in inventory.items() if k.lower() == lower), [])
    return candidates


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
    Skips links inside backtick (```) and tilde (~~~) fenced code blocks.
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

        # It's broken — look up by basename (case-insensitive fallback)
        basename = os.path.basename(clean_link)
        if not basename or basename.lower() == 'readme.md':
            return match.group(0)

        candidates = lookup_basename(inventory, basename)

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

    # Proce

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/link-checker-agent/scripts/04_autofix_unique_links.py -->
#!/usr/bin/env python3
"""
04_autofix_unique_links.py (CLI)
=====================================

Purpose:
    Fixer: Auto-corrects broken links using unique filename matches in the inventory.
    This is Phase 4 of the Link Checker pipeline.
    Reads broken_links.json (from Step 3) to target only files with known broken links.
    Falls back to a full repo walk if broken_links.json is not present.
    After fixing, writes remaining_broken_links.json so Step 5 reflects post-fix state.

Usage:
    python3 04_autofix_unique_links.py --root . [--dry-run] [--backup]

Scope:
    Only fixes markdown links [label](path) and image links ![alt](path).
    Code path references (e.g. './config.json' in .py or .js files) are audited
    by Step 3 but are intentionally NOT modified 

*(combined content truncated)*

## See Also

- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]
- [[add-the-scripts-directory-so-we-can-import-rlm-config]]
- [[business-requirements-capture]]
- [[commands-that-are-unconditionally-safe-and-bypass-further-checks]]
- [[complex-regex-to-capture-wikilinks-while-avoiding-transclusions]]
- [[fix-1-literal-n-chars-write-back-immediately-so-json-parse-can-proceed]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `link-checker/scripts/04_autofix_unique_links.py`
- **Indexed:** 2026-04-27T05:21:04.247933+00:00
