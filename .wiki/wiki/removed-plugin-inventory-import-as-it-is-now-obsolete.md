---
concept: removed-plugin-inventory-import-as-it-is-now-obsolete
source: plugin-code
source_file: plugin-manager/scripts/sync_with_inventory.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.030300+00:00
cluster: plugin-code
content_hash: 785ced79dbc6a89c
---

# Removed plugin_inventory import as it is now obsolete.

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

"""
Sync Plugins with Inventory
===========================

Purpose:
    Synchronizes the agent environments with the local `plugins/` directory.
    Uses `plugin-sources.json` as the authoritative registry of installed plugins
    to safely identify and clean up deleted/removed plugins.

Layer: Plugin Manager / Synchronization

Usage Examples:
    python plugins/plugin-manager/scripts/sync_with_inventory.py [--dry-run]

Supported Object Types:
    - None (Synchronization)

CLI Arguments:
    --dry-run: Simulate cleanup without deleting.
    --cleanup-only: Run cleanup analysis only, skip installation.

Input Files:
    - plugin-sources.json (canonical install registry)
    - plugin_installer.py (subprocess installation engine)

Output:
    - Cleans or installs plugin artifacts on agent targets.

Key Functions:
    clean_plugin_artifacts(): Removes artifacts for a specific plugin.
    run_plugin_installer(): Runs plugin_installer for a plugin.
    get_installed_plugin_names(): Returns set of plugin names from plugin-sources.json.

Script Dependencies:
    os, sys, json, shutil, argparse, subprocess, pathlib

Consumed by:
    - None (Standalone script)
Related:
    - scripts/plugin_inventory.py
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path

# Removed plugin_inventory import as it is now obsolete.

# --- Configuration ---

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]  # scripts→plugin-manager→plugins→ROOT
PLUGIN_INSTALLER = PROJECT_ROOT / "plugins" / "plugin-manager" / "scripts" / "plugin_installer.py"

AGENT_DIRS = {
    "antigravity": {
        "dirs": [".agents/workflows", ".agents/skills", ".agents/rules"],
    },
    "github": {
        "dirs": [".github/prompts", ".github/skills", ".github/rules"],
    },
    "gemini": {
        "dirs": [".gemini/commands", ".gemini/skills", ".gemini/rules"],
    },
    "claude": {
        "dirs": [".claude/commands", ".claude/skills", ".claude/rules"],
    }
}

def clean_plugin_artifacts(plugin_name: str, root: Path, dry_run: bool) -> None:
    """Removes artifacts for a specific plugin from all agent directories."""
    print(f"  [CLEAN] Removing artifacts for '{plugin_name}'...")
    
    for agent, config in AGENT_DIRS.items():
        for dir_path_str in config["dirs"]:
            target_dir = root / dir_path_str
            if not target_dir.exists():
                continue
                
            # Pattern A: Directory match (skills/rules) -> delete folder {plugin_name}
            # Pattern B: File match (workflows/prompts) -> delete files starting with {plugin_name}_
            
            if dir_path_str.endswith("skills") or dir_path_str.endswith("rules"):
                target_subdir = target_dir / plugin_name
                if target_subdir.exists() and target_subdir.is_dir():
                    print(f"    - Deleting dir: {target_subdir}")
                    if not dry_run:
                        shutil.rmtree(target_subdir)
            else:
                # File cleanup
                for f in target_dir.iterdir():
                    if f.is_file() and f.name.startswith(f"{plugin_name}_"):
                        print(f"    - Deleting file: {f}")
                        if not dry_run:
                            f.unlink()

def run_plugin_installer(plugin_path: Path) -> None:
    """Runs plugin_installer.py for a specific plugin."""
    cmd = [sys.executable, str(PLUGIN_INSTALLER), "--plugin", str(plugin_path)]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"  [INSTALL] Success: {plugin_path.name}")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Failed to install {plugin_path.name}: {e.stderr.decode()}")


def get_installed_plugin_names(root: Path) -> set:
    """Returns the set of plugin names tracked in plugin-sources.json.

    Supports both the new schema (

*(content truncated)*

## See Also

- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[plugin-files-and-symlinks-inventory]]
- [[strip-yaml-frontmatter-from-skillmd-before-using-it-as-an-agent-prompt]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]
- [[add-the-scripts-directory-so-we-can-import-rlm-config]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `plugin-manager/scripts/sync_with_inventory.py`
- **Indexed:** 2026-04-27T05:21:04.030300+00:00
