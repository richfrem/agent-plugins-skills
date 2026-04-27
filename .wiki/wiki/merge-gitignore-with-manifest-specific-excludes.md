---
concept: merge-gitignore-with-manifest-specific-excludes
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/context-bundler/scripts/bundle.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.308231+00:00
cluster: path
content_hash: 4016475dac05acb2
---

# Merge .gitignore with manifest-specific excludes

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/context-bundler/scripts/bundle.py -->
#!/usr/bin/env python3
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
        path_str = entry.get('path', '')
        note = entry.get('note', '')
        actual_path = project_root / path_str

        if actual_path.is_dir():
            for file_path in sorted(actual_path.rglob('*')):
                if not file_path.is_file():
                    continue
                if is_ignored(file_path, project_root, ignore_patterns):
                    continue

                rel_path = str(file_path.relative_to(project_root)).replace('\\', '/')
                real_path = os.path.realpath(file_path)
                is_symlink = file_path.is_symlink()

                # Deduplication: if real path already seen, record as symlink reference only
                if real_path in seen_real_paths:
                    resolved_files.append({
                        'path': rel_path,
                        'note': note,
                        'symlink_to': seen_real_paths[real_path],
                    })
                    continue

                seen_real_paths[real_path] = rel_path

                if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
                    resolved_files.append({'path': rel_path, 'note': note, 'too_large': True})
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as peek:
                        content = peek.read()

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/red-team-bundler/scripts/bundle.py -->
#!/usr/bin/env python3
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

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB safety limit


def load_gitignore_patterns(project_root: Path) -> list:
    patterns = ['.git', '__pycache__', 'node_modules', '.env']
    gi_path = project_root / '.gitignore'
    if gi_pat

*(combined content truncated)*

## See Also

- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[atomically-replace-an-existing-path-with-a-new-symlink-pointing-to-src]]
- [[default-excludes]]
- [[default-file-extensions-to-index-if-manifest-is-empty]]
- [[distiller-manifest]]
- [[file-manifest]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/context-bundler/scripts/bundle.py`
- **Indexed:** 2026-04-27T05:21:04.308231+00:00
