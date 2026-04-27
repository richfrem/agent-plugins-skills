---
concept: skip-git-and-other-hidden-dirs
source: plugin-code
source_file: obsidian-wiki-engine/scripts/init_vault.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.264601+00:00
cluster: obsidian
content_hash: 2c0487cdcf263053
---

# Skip .git and other hidden dirs

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/obsidian-wiki-engine/scripts/init_vault.py -->
"""
init_vault.py (CLI)
=====================================

Purpose:
    Bootstrap any project directory as an Obsidian Vault.
    Creates .obsidian/app.json with sensible exclusion filters for developer repos.

Layer: Core Operations

Usage Examples:
    pythoninit_vault.py --vault-root /path/to/vault
    pythoninit_vault.py --vault-root /path/to/vault --validate-only

Supported Object Types:
    - .obsidian/app.json

CLI Arguments:
    --vault-root: Root directory for the vault.
    --exclude: Additional exclusion patterns.
    --validate-only: Check without making changes.

Input Files:
    - Project directories containing .md files.

Output:
    - JSON results indicating initialization status.

Key Functions:
    init_vault(): Initialize an Obsidian Vault.
    count_markdown_files(): Count .md files in the vault.

Script Dependencies:
    os, sys, json, argparse, pathlib

Consumed by:
    - obsidian-init skill
"""
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any

DEFAULT_EXCLUSIONS = [
    "node_modules/",
    ".worktrees/",
    ".vector_data/",
    ".git/",
    "venv/",
    "__pycache__/",
    "*.json",
    "*.jsonl",
    "learning_package_snapshot.md",
    "bootstrap_packet.md",
    "learning_debrief.md",
    "*_packet.md",
    "*_digest.md",
    "dataset_package/",
    "rlm_summary_cache*",
    "rlm_tool_cache*"
]


def count_markdown_files(vault_root: Path) -> int:
    """Count .md files in the vault (non-recursive top-level scan for speed)."""
    count = 0
    for root, dirs, files in os.walk(vault_root):
        # Skip .git and other hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if f.endswith('.md'):
                count += 1
    return count


def init_vault(vault_root: Path, extra_exclusions: Optional[List[str]] = None, validate_only: bool = False) -> Dict[str, Any]:
    """Initialize an Obsidian Vault at the given root."""
    vault_root = vault_root.resolve()

    if not vault_root.exists():
        return {"error": f"Directory does not exist: {vault_root}"}

    if not vault_root.is_dir():
        return {"error": f"Not a directory: {vault_root}"}

    # Count markdown files
    md_count = count_markdown_files(vault_root)
    if md_count == 0:
        return {"error": f"No .md files found in {vault_root}. Is this the right directory?"}

    obsidian_dir = vault_root / ".obsidian"
    app_json = obsidian_dir / "app.json"

    result = {
        "vault_root": str(vault_root),
        "markdown_files_found": md_count,
        "obsidian_dir_exists": obsidian_dir.exists(),
        "app_json_exists": app_json.exists(),
    }

    if validate_only:
        result["mode"] = "validate_only"
        if obsidian_dir.exists():
            result["status"] = "vault_already_initialized"
        else:
            result["status"] = "ready_to_initialize"
        return result

    # Build exclusion list
    exclusions = list(DEFAULT_EXCLUSIONS)
    if extra_exclusions:
        exclusions.extend(extra_exclusions)

    # Create .obsidian directory
    obsidian_dir.mkdir(exist_ok=True)

    # Write or update app.json
    app_config = {}
    if app_json.exists():
        try:
            app_config = json.loads(app_json.read_text())
        except json.JSONDecodeError:
            pass

    app_config["userIgnoreFilters"] = exclusions

    app_json.write_text(json.dumps(app_config, indent=2) + "\n")

    # Add .obsidian to .gitignore if not already there
    gitignore = vault_root / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".obsidian/" not in content:
            with open(gitignore, 'a') as f:
                f.write("\n# Obsidian local config (user-specific)\n.obsidian/\n")
            result["gitignore_updated"] = True
    else:
        gitignore.write_text("# Obsidian local config (user-specific)\n.obsidian/\n")
        result["gitignore_creat

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/obsidian-init/scripts/init_vault.py -->
"""
init_vault.py (CLI)
=====================================

Purpose:
    Bootstrap any project directory as an Obsidian Vault.
    Creates .obsidian/app.json with sensible exclusion filters for developer repos.

Layer: Core Operations

Usage Examples:
    python3 init_vault.py --vault-root /path/to/vault
    python3 init_vault.py --vault-root /path/to/vault --validate-only

Supported Object Types:
    - .obsidian/app.json

CLI Arguments:
    --vault-root: Root directory for the vault.
    --exclude: Additional exclusion patterns.
    --validate-only: Check without making changes.

Input Files:
    - Project directories containing .md files.

Output:
    - JSON results indicating initialization status.

Key Functions:
    init_vault(): Initialize an Obsidian Vault.
    count_markdown_files():

*(combined content truncated)*

## See Also

- [[skip-hidden-files]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]
- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[commands-that-are-unconditionally-safe-and-bypass-further-checks]]
- [[configuration-artifact-types-and-their-locationspatterns]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/scripts/init_vault.py`
- **Indexed:** 2026-04-27T05:21:04.264601+00:00
