#!/usr/bin/env python
"""
bundle_zip.py (CLI)
=====================================

Purpose:
    Reads a JSON manifest file and archives targets into a compressed .zip file.

Layer: Context / Technical Documentation

Usage Examples:
    python bundle_zip.py --manifest manifest.json --bundle output.zip

Supported Object Types:
    Files (binary and text), Directories (recursive)

CLI Arguments:
    --manifest: Path to the JSON manifest file
    --bundle: Output path for the generated ZIP archive

Input Files:
    - JSON manifest specifying files/directories to include
    - .gitignore (for default exclusion logic)

Output:
    - Compressed ZIP file containing all source files
    - _manifest_notes.md (embedded metadata and index)

Key Functions:
    - generate_zip_bundle(): Primary orchestrator for resolution and archiving
    - load_gitignore_patterns(): Parses exclusion rules
    - is_ignored(): Validates files against glob patterns

Script Dependencies:
    - Python 3.8+ Standard Library only (os, sys, json, argparse, zipfile, fnmatch, pathlib)

Consumed by:
    - Context Bundler Plugin
    - Red Team Reviewers
"""


import os
import sys
import json
import argparse
import zipfile
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


MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB safety limit for ZIPs


# Logic: Resolves .gitignore patterns to avoid archiving system junk
def load_gitignore_patterns(project_root: Path) -> list:
    """
    Parses the local .gitignore file and adds common system defaults.
    
    Args:
        project_root: The base directory of the repository.
        
    Returns:
        List of glob patterns to ignore.
    """

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


# Logic: Determines if a file should be excluded from the archive
def is_ignored(file_path: Path, project_root: Path, patterns: list) -> bool:
    """
    Checks a file path against a list of ignore patterns.
    
    Args:
        file_path: Absolute path to the file.
        project_root: Root directory for relative path calculation.
        patterns: List of fnmatch-compatible patterns.
        
    Returns:
        True if the file matches any ignore pattern.
    """

    try:
        rel_path = str(file_path.relative_to(project_root)).replace('\\', '/')
    except ValueError:
        return False

    ignored = False
    for pattern in patterns:
        negate = pattern.startswith('!')
        clean_pattern = pattern.lstrip('!').strip('/')
        if (fnmatch.fnmatch(rel_path, clean_pattern) or
                fnmatch.fnmatch(rel_path, f"{clean_pattern}/*") or
                fnmatch.fnmatch(rel_path, f"*/{clean_pattern}/*") or
                fnmatch.fnmatch(rel_path, f"*/{clean_pattern}")):
            ignored = not negate
    return ignored


def _load_manifest(manifest_path: Path) -> dict:
    """Load and parse the JSON manifest file; exits with code 1 on failure."""
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading manifest '{manifest_path}': {e}")
        sys.exit(1)


def _process_resolved_file(file_path: Path, reported_path: str, note: str,
                            dir_source_path: str | None,
                            project_root: Path, seen_real_paths: dict) -> dict:
    """Process one resolved file for archiving: dedup by real path, size check, token estimate, symlink note.

    dir_source_path is set for directory-walk entries (adds "(from <path>)" to the
    note) and None for direct manifest file entries (note passed through as-is).
    Binary files (UnicodeDecodeError) still get archived — only 'tokens' stays None.
    """
    real_path = os.path.realpath(file_path)
    is_symlink = file_path.is_symlink()

    # Deduplication: record as symlink reference, do not archive again
    if real_path in seen_real_paths:
        return {'path': reported_path, 'note': note, 'symlink_to': seen_real_paths[real_path]}

    seen_real_paths[real_path] = reported_path

    if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
        return {'path': reported_path, 'note': note, 'too_large': True}

    tokens = None
    try:
        with open(file_path, 'r', encoding='utf-8') as peek:
            tokens = len(peek.read()) // 4
    except UnicodeDecodeError:
        pass

    if dir_source_path is not None:
        file_note = f"{note} (from {dir_source_path})" if note else f"from {dir_source_path}"
        if is_symlink:
            real_rel = str(Path(real_path).relative_to(project_root)).replace('\\', '/') \
                if Path(real_path).is_relative_to(project_root) else real_path
            file_note = f"{file_note} [symlink → {real_rel}]"
    else:
        file_note = note
        if is_symlink:
            real_rel = str(Path(real_path).relative_to(project_root)).replace('\\', '/') \
                if Path(real_path).is_relative_to(project_root) else real_path
            file_note = f"{note} [symlink → {real_rel}]" if note else f"[symlink → {real_rel}]"

    return {'path': reported_path, 'actual_path': file_path, 'note': file_note, 'tokens': tokens}


def _resolve_directory_entry(actual_path: Path, path_str: str, note: str, project_root: Path,
                              ignore_patterns: list, seen_real_paths: dict) -> list:
    """Walk a directory manifest entry and process each contained file. Returns list of entry dicts."""
    results = []
    for file_path in sorted(actual_path.rglob('*')):
        if not file_path.is_file():
            continue
        if is_ignored(file_path, project_root, ignore_patterns):
            continue

        rel_path = str(file_path.relative_to(project_root)).replace('\\', '/') \
            if file_path.is_relative_to(project_root) else str(file_path).replace('\\', '/')

        results.append(_process_resolved_file(file_path, rel_path, note, path_str, project_root, seen_real_paths))
    return results


def _resolve_single_file_entry(actual_path: Path, path_str: str, note: str,
                                project_root: Path, seen_real_paths: dict) -> dict:
    """Process a direct (non-directory) manifest file entry. Explicit entries always bypass gitignore."""
    return _process_resolved_file(actual_path, path_str, note, None, project_root, seen_real_paths)


def _resolve_all_files(manifest: dict, project_root: Path) -> tuple:
    """Resolve every manifest file/directory entry for archiving.

    Returns (resolved_files, total_tokens, valid_file_count). valid_file_count
    includes binary files (they're still archived); total_tokens only sums
    entries with a non-None token estimate.
    """
    files = manifest.get('files', [])

    ignore_patterns = load_gitignore_patterns(project_root)
    ignore_patterns.extend(manifest.get('excludes', []))

    resolved_files = []
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
            resolved_files.extend(
                _resolve_directory_entry(actual_path, path_str, note, project_root, ignore_patterns, seen_real_paths)
            )
        elif not actual_path.exists():
            resolved_files.append({'path': path_str, 'note': note, 'missing': True})
        else:
            resolved_files.append(
                _resolve_single_file_entry(actual_path, path_str, note, project_root, seen_real_paths)
            )

    total_tokens = sum(e['tokens'] for e in resolved_files if e.get('tokens') is not None)
    valid_file_count = sum(1 for e in resolved_files if 'actual_path' in e)
    return resolved_files, total_tokens, valid_file_count


def _build_manifest_doc(title: str, description: str, valid_file_count: int,
                         total_tokens: int, resolved_files: list) -> list:
    """Build the _manifest_notes.md lines: header, metadata, and index."""
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
    return manifest_doc


def _write_zip_archive(output_path: Path, resolved_files: list, manifest_doc: list) -> None:
    """Write the resolved files and the manifest notes into a ZIP archive; exits on failure."""
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


# Logic: Primary orchestration of the archiving process
def generate_zip_bundle(manifest_path: Path, output_path: Path) -> None:
    """
    Reads the manifest, resolves files (handling symlinks), and creates a ZIP archive.

    Args:
        manifest_path: Path to the JSON manifest.
        output_path: Destination path for the .zip archive.
    """
    manifest = _load_manifest(manifest_path)

    title = manifest.get('title', 'Context Bundle')
    description = manifest.get('description', '')
    project_root = Path.cwd()

    resolved_files, total_tokens, valid_file_count = _resolve_all_files(manifest, project_root)

    manifest_doc = _build_manifest_doc(title, description, valid_file_count, total_tokens, resolved_files)

    _write_zip_archive(output_path, resolved_files, manifest_doc)

    print(f"✅ ZIP successfully bundled into -> {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a ZIP context bundle from a JSON manifest.")
    parser.add_argument("--manifest", required=True, type=Path, help="Path to the JSON manifest.")
    parser.add_argument("--bundle", required=True, type=Path, help="Output path for the .zip file.")
    args = parser.parse_args()
    generate_zip_bundle(args.manifest, args.bundle)
