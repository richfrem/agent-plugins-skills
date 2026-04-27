---
concept: track-real-filesystem-paths-first-encountered-rel-path-to-avoid-archiving-duplicate-symlinked-content
source: plugin-code
source_file: context-bundler/scripts/bundle_zip.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.309041+00:00
cluster: import
content_hash: 67e130d80acf9a34
---

# Track real filesystem paths → first-encountered rel_path to avoid archiving duplicate symlinked content

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/context-bundler/scripts/bundle_zip.py -->
#!/usr/bin/env python
"""
bundle_zip.py
=====================================
Purpose: Reads a JSON manifest file and archives targets into a .zip file.
[v2.2] Adds symlink deduplication: symlinked files whose real path was already archived
       are listed in the manifest notes but NOT added to the zip again.
[v2.1] Adds manifest 'excludes', large-file tracking, and cumulative tokens.
"""

import os
import sys
import json
import argparse
import zipfile
import fnmatch
from pathlib import Path
from datetime import datetime

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB safety limit for ZIPs


def load_gitignore_patterns(project_root: Path) -> list:
    patterns = ['.git', '__pycache__', 'node_modules', '.env', '*.zip']
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


def generate_zip_bundle(manifest_path: Path, output_path: Path) -> None:
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"❌ Error loading manifest '{manifest_path}': {e}")
        sys.exit(1)

    title = manifest.get('title', 'Context Bundle')
    description = manifest.get('description', '')
    files = manifest.get('files', [])

    project_root = Path.cwd()
    ignore_patterns = load_gitignore_patterns(project_root)
    ignore_patterns.extend(manifest.get('excludes', []))

    resolved_files = []
    total_tokens = 0
    valid_file_count = 0

    # Track real filesystem paths → first-encountered rel_path to avoid archiving duplicate symlinked content
    seen_real_paths: dict = {}

    print("🔍 Scanning directories and estimating tokens...")

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
                real_path = os.path.realpath(file_path)
                is_symlink = file_path.is_symlink()

                # Deduplication: record as symlink reference, do not archive again
                if real_path in seen_real_paths:
                    resolved_files.append({
                        'path': rel_path,
                        'note': no

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/context-bundler/scripts/bundle_zip.py -->
#!/usr/bin/env python3
"""
bundle_zip.py
=====================================
Purpose: Reads a JSON manifest file and archives targets into a .zip file.
[v2.2] Adds symlink deduplication: symlinked files whose real path was already archived
       are listed in the manifest notes but NOT added to the zip again.
[v2.1] Adds manifest 'excludes', large-file tracking, and cumulative tokens.
"""

import os
import sys
import json
import argparse
import zipfile
import fnmatch
from pathlib import Path
from datetime import datetime

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB safety limit for ZIPs


def load_gitignore_patterns(project_root: Path) -> list:
    patterns = ['.git', '__pycache__', 'node_modules', '.env', '*.zip']
    gi_path = project_root / '.gitignore'
    if gi_path.exists():
        t

*(combined content truncated)*

## See Also

- [[absolute-path-prefixes-that-should-never-be-written-to]]
- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[atomically-replace-an-existing-path-with-a-new-symlink-pointing-to-src]]
- [[check-if-we-already-emitted-for-this-completion-avoid-duplicate-events]]
- [[match-pythonexecution-paths-that-are-hardcoded-to-the-repo-root-plugins-folder]]
- [[use-yaml-block-scalar-to-avoid-breaking-on-quotes-in-description]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `context-bundler/scripts/bundle_zip.py`
- **Indexed:** 2026-04-27T05:21:04.309041+00:00
