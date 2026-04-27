---
concept: run-bulk-md-to-docx
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/markdown-to-msword-converter/scripts/run_bulk_md_to_docx.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.253216+00:00
cluster: path
content_hash: eea59436c4b9bc46
---

# Run Bulk Md To Docx

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

"""
run_bulk_md_to_docx.py (CLI)
=====================================

Purpose:
    Bulk Converter: Convert all Markdown files under a root folder by calling md_to_docx.py.

Layer: Cli_Entry_Points

Usage Examples:
    python3 run_bulk_md_to_docx.py --root . --config folders_to_convert.json

Supported Object Types:
    - Generic

CLI Arguments:
    --root: Root path to scan for .md files.
    --config: Path to folders JSON config file.
    --overwrite: Overwrite existing .docx files.
    --dry-run: Show planned conversions only.
    --exclude: Additional folder names to exclude.
    --python-exe: Python executable used for converter calls.

Input Files:
    - folders_to_convert.json containing scope configuration.
    - Markdown files (.md).

Output:
    - Word documents (.docx) generated via md_to_docx.py.

Key Functions:
    find_repo_root(): Locate the repository root.
    should_skip(): Check if a path should be skipped.
    find_markdown_files(): Find markdown files recursively.
    load_folder_config(): Load bulk conversion scope config from JSON.
    find_markdown_files_from_config(): Find markdown files according to config.

Script Dependencies:
    argparse, json, subprocess, sys, pathlib

Consumed by:
    - markdown-to-msword-converter skill
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List


DEFAULT_EXCLUDES = {
    ".git",
    ".github",
    ".vscode",
    ".venv",
    ".venv-1",
    "venv",
    "__pycache__",
    "node_modules",
}


def find_repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def should_skip(path: Path, root: Path, excludes: set[str]) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(part in excludes for part in parts)


def find_markdown_files(root: Path, excludes: set[str]) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        if should_skip(path, root, excludes):
            continue
        files.append(path)
    return sorted(files)


def load_folder_config(config_path: Path) -> Dict[str, Any]:
    """Load bulk conversion scope config from JSON file."""
    if not config_path.exists() or not config_path.is_file():
        raise FileNotFoundError(f"Folder config file not found: {config_path}")

    data = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Config must be a JSON object")

    folders = data.get("folders", [])
    include_root = data.get("include_root_markdown", True)

    if not isinstance(folders, list) or not all(isinstance(item, str) for item in folders):
        raise ValueError("Config field 'folders' must be an array of strings")
    if not isinstance(include_root, bool):
        raise ValueError("Config field 'include_root_markdown' must be boolean")

    return {
        "folders": folders,
        "include_root_markdown": include_root,
    }


def find_markdown_files_from_config(repo_root: Path, excludes: set[str], config: Dict[str, Any]) -> List[Path]:
    """Find markdown files only within configured folders and optional repo root."""
    files: set[Path] = set()

    if config.get("include_root_markdown", True):
        for path in repo_root.glob("*.md"):
            if path.is_file() and not should_skip(path, repo_root, excludes):
                files.add(path.resolve())

    for folder in config.get("folders", []):
        folder_path = (repo_root / folder).resolve()
        if not folder_path.exists() or not folder_path.is_dir():
            print(f"WARN    Config folder not found, skipping: {folder_path}")
            continue

        for path in folder_path.rglob("*.md"):
            if path.is_file() and not should_skip(path, repo_root, excludes):
                files.add(path.resolve())

    return sorted(files)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert all Ma

*(content truncated)*

## See Also

- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[absolute-path-prefixes-that-should-never-be-written-to]]
- [[add-project-root-to-syspath]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/markdown-to-msword-converter/scripts/run_bulk_md_to_docx.py`
- **Indexed:** 2026-04-27T05:21:04.253216+00:00
