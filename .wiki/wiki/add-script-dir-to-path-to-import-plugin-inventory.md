---
concept: add-script-dir-to-path-to-import-plugin-inventory
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/maintain-plugins/scripts/sync_with_inventory.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.250936+00:00
cluster: plugin-code
content_hash: 9b31c3f42570a425
---

# Add script dir to path to import plugin_inventory

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

"""
Sync Plugins with Inventory
===========================

Purpose:
    Synchronizes the agent environments with the local `plugins/` directory.
    Implements a "Dual Inventory" approach to safely identify and clean up deleted plugins.

Layer: Plugin Manager / Synchronization

Usage Examples:
    python3 plugins/plugin-manager/scripts/sync_with_inventory.py [--dry-run]

Supported Object Types:
    - None (Synchronization)

CLI Arguments:
    --dry-run: Simulate cleanup without deleting.
    --cleanup-only: Run cleanup analysis only, skip installation.

Input Files:
    - vendor-plugins-inventory.json (Vendor manifest)
    - plugin_installer.py (Subprocess script)

Output:
    - Cleans or installs plugin artifacts on agent targets.

Key Functions:
    clean_plugin_artifacts(): Removes artifacts for a specific plugin.
    run_bridge_installer(): Runs bridge installer for a plugin.
    get_inventory_names(): Returns set of plugin names.

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

# Add script dir to path to import plugin_inventory
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.append(str(SCRIPT_DIR))

try:
    import plugin_inventory
except ImportError:
    # Fallback if running from root without package structure
    pass

# --- Configuration ---

VENDOR_ROOT = Path(".vendor")
# Fallback for simple setups or legacy references
DEFAULT_VENDOR_DIR = VENDOR_ROOT / "agent-plugins-skills"
LOCAL_ROOT = Path(".")
# Bridge installer is provided by plugin-manager
PROJECT_ROOT = SCRIPT_DIR.parents[2]  # scripts→plugin-manager→plugins→ROOT
BRIDGE_INSTALLER = PROJECT_ROOT / "plugins" / "plugin-manager" / "scripts" / "plugin_installer.py"

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

def run_bridge_installer(plugin_path: Path) -> None:
    """Runs the bridge installer for a specific plugin."""
    cmd = [sys.executable, str(BRIDGE_INSTALLER), "--plugin", str(plugin_path)]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"  [INSTALL] Success: {plugin_path.name}")
    except subprocess.Ca

*(content truncated)*

## See Also

- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]
- [[removed-plugin-inventory-import-as-it-is-now-obsolete]]
- [[absolute-path-prefixes-that-should-never-be-written-to]]
- [[add-project-root-to-syspath]]
- [[add-the-scripts-directory-so-we-can-import-rlm-config]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/maintain-plugins/scripts/sync_with_inventory.py`
- **Indexed:** 2026-04-27T05:21:04.250936+00:00
