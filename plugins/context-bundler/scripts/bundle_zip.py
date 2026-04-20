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
                        'note': note,
                        'symlink_to': seen_real_paths[real_path],
                    })
                    continue

                seen_real_paths[real_path] = rel_path

                if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
                    resolved_files.append({'path': rel_path, 'note': note, 'too_large': True})
                    continue

                tokens = None
                try:
                    with open(file_path, 'r', encoding='utf-8') as peek:
                        tokens = len(peek.read()) // 4
                        total_tokens += tokens
                except UnicodeDecodeError:
                    pass

                file_note = f"{note} (from {path_str})" if note else f"from {path_str}"
                if is_symlink:
                    real_rel = str(Path(real_path).relative_to(project_root)).replace('\\', '/') \
                        if Path(real_path).is_relative_to(project_root) else real_path
                    file_note = f"{file_note} [symlink → {real_rel}]"

                resolved_files.append({
                    'path': rel_path,
                    'actual_path': file_path,
                    'note': file_note,
                    'tokens': tokens,
                })
                valid_file_count += 1
        else:
            if not actual_path.exists():
                resolved_files.append({'path': path_str, 'note': note, 'missing': True})
            elif not is_ignored(actual_path, project_root, ignore_patterns):
                real_path = os.path.realpath(actual_path)
                is_symlink = actual_path.is_symlink()

                if real_path in seen_real_paths:
                    resolved_files.append({
                        'path': path_str,
                        'note': note,
                        'symlink_to': seen_real_paths[real_path],
                    })
                    continue

                seen_real_paths[real_path] = path_str

                if actual_path.stat().st_size > MAX_FILE_SIZE_BYTES:
                    resolved_files.append({'path': path_str, 'note': note, 'too_large': True})
                    continue

                tokens = None
                try:
                    with open(actual_path, 'r', encoding='utf-8') as peek:
                        tokens = len(peek.read()) // 4
                        total_tokens += tokens
                except UnicodeDecodeError:
                    pass

                file_note = note
                if is_symlink:
                    real_rel = str(Path(real_path).relative_to(project_root)).replace('\\', '/') \
                        if Path(real_path).is_relative_to(project_root) else real_path
                    file_note = f"{note} [symlink → {real_rel}]" if note else f"[symlink → {real_rel}]"

                resolved_files.append({
                    'path': path_str,
                    'actual_path': actual_path,
                    'note': file_note,
                    'tokens': tokens,
                })
                valid_file_count += 1

    manifest_doc = [
        f"# {title}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ""
    ]
    if description:
        manifest_doc.extend([description, ""])

    manifest_doc.extend([
        "### 📊 Bundle Metadata",
        f"- **Total Files:** {valid_file_count}",
        f"- **Estimated Tokens (Text Files Only):** ~{total_tokens:,}",
        "",
        "## 📑 Index",
        ""
    ])

    cumulative_tokens = 0
    for idx, entry in enumerate(resolved_files, 1):
        path_str = entry.get('path', '')
        note = entry.get('note', '')

        if entry.get('missing'):
            manifest_doc.append(f"{idx}. ❌ `{path_str}` - *FILE NOT FOUND*")
        elif entry.get('too_large'):
            manifest_doc.append(f"{idx}. ⚠️ `{path_str}` - *[Skipped: Exceeds 50MB Archive Limit]*")
        elif entry.get('symlink_to'):
            manifest_doc.append(
                f"{idx}. 🔗 `{path_str}` - *[Symlink — content already archived from `{entry['symlink_to']}`]*"
            )
        else:
            tokens = entry.get('tokens')
            if tokens is not None:
                cumulative_tokens += tokens
                token_str = f" ({tokens:,} tokens | {cumulative_tokens:,} total)"
            else:
                token_str = " ([Binary Data])"

            listing = f"{idx}. `{path_str}`{token_str}"
            if note:
                listing += f" - {note}"
            manifest_doc.append(listing)

    manifest_doc.extend(["", "---", ""])

    print(f"📦 Archiving files into {output_path}...")
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for entry in resolved_files:
                if entry.get('missing') or entry.get('too_large') or entry.get('symlink_to'):
                    continue

                path_str = entry.get('path', '')
                actual_path = entry.get('actual_path')
                if actual_path and actual_path.exists():
                    zipf.write(actual_path, arcname=path_str)

            zipf.writestr('_manifest_notes.md', '\n'.join(manifest_doc))

    except Exception as e:
        print(f"❌ Failed to generate ZIP archive: {e}")
        sys.exit(1)

    print(f"✅ ZIP successfully bundled into -> {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a ZIP context bundle from a JSON manifest.")
    parser.add_argument("--manifest", required=True, type=Path, help="Path to the JSON manifest.")
    parser.add_argument("--bundle", required=True, type=Path, help="Output path for the .zip file.")
    args = parser.parse_args()
    generate_zip_bundle(args.manifest, args.bundle)
