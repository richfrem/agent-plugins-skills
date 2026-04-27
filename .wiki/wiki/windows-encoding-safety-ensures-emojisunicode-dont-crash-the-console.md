---
concept: windows-encoding-safety-ensures-emojisunicode-dont-crash-the-console
source: plugin-code
source_file: context-bundler/scripts/bundle.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.958393+00:00
cluster: path
content_hash: 12eb3dc54b09bfab
---

# Windows encoding safety: ensures emojis/unicode don't crash the console

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
bundle.py
=====================================
Purpose: Reads a JSON manifest file and concatenates contents into a single Markdown artifact.
[v2.2] Adds symlink deduplication: symlinked files whose real path was already included are
       noted in the index but their content is NOT repeated.
[v2.1] Adds manifest 'excludes', 5MB large-file safety, cumulative tokens, and expanded lang map.
"""

import os
import sys
import json
import argparse
import fnmatch
from pathlib import Path
from datetime import datetime

# Windows encoding safety: ensures emojis/unicode don't crash the console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, Exception):
        pass

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB safety limit


def load_gitignore_patterns(project_root: Path) -> list:
    patterns = ['.git', '__pycache__', 'node_modules', '.env']
    gi_path = project_root / '.gitignore'
    if gi_path.exists():
        try:
            with open(gi_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception:
            pass
    return patterns


def is_ignored(file_path: Path, project_root: Path, patterns: list) -> bool:
    try:
        rel_path = str(file_path.relative_to(project_root)).replace('\\', '/')
    except ValueError:
        return False

    for pattern in patterns:
        clean_pattern = pattern.strip('/')
        if (fnmatch.fnmatch(rel_path, clean_pattern) or
                fnmatch.fnmatch(rel_path, f"{clean_pattern}/*") or
                fnmatch.fnmatch(rel_path, f"*/{clean_pattern}/*") or
                fnmatch.fnmatch(rel_path, f"*/{clean_pattern}")):
            return True
    return False


def bundle_files(manifest_path: Path, output_path: Path) -> None:
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"❌ Error loading manifest '{manifest_path}': {e}")
        sys.exit(1)

    title = manifest.get('title', 'Context Bundle')
    description = manifest.get('description', '')
    files = manifest.get('files', [])

    # Merge .gitignore with manifest-specific excludes
    project_root = Path.cwd()
    ignore_patterns = load_gitignore_patterns(project_root)
    ignore_patterns.extend(manifest.get('excludes', []))

    resolved_files = []
    total_tokens = 0
    valid_file_count = 0
    missing_files = []

    # Track real filesystem paths → first-encountered rel_path to avoid duplicating symlinked content
    seen_real_paths: dict = {}

    print("🔍 Resolving files and calculating token budgets...")

    for entry in files:
        path_str = entry.get('path', '').strip()
        note = entry.get('note', '')

        # Guard: skip entries with empty/blank paths — likely a manifest key typo
        # (e.g. "path:" instead of "path"). Without this, project_root / '' resolves
        # to the project root dir and rglob crawls the entire workspace.
        if not path_str:
            print(f"⚠️  Skipping manifest entry with empty 'path' — possible key typo: {entry}")
            resolved_files.append({'path': '(empty path — skipped)', 'note': str(entry), 'missing': True})
            continue

        actual_path = project_root / path_str

        if actual_path.is_dir():
            for file_path in sorted(actual_path.rglob('*')):
                if not file_path.is_file():
                    continue
                if is_ignored(file_path, project_root, ignore_patterns):
                    continue

                rel_path = str(file_path.relative_to(project_root)).replace('\\', '/') if file_path.is_relative_to(project_root) else str(file_path).replace('\\', '/')
 

*(content truncated)*

## See Also

- [[1-parse-the-hook-payload]]
- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]
- [[add-the-scripts-directory-so-we-can-import-rlm-config]]
- [[all-event-types-recognised-by-the-claude-code-hook-system]]
- [[ensure-unicode-output-works-on-windows]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `context-bundler/scripts/bundle.py`
- **Indexed:** 2026-04-27T05:21:03.958393+00:00
