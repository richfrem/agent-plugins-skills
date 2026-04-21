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

    Supports both the new schema ({"source": ..., "plugins": [...]}) and
    legacy schema ({"local"/"github"/"name": ..., "plugins": [...]}).
    """
    sources_file = root / "plugin-sources.json"
    if not sources_file.exists():
        return set()
    try:
        data = json.loads(sources_file.read_text(encoding="utf-8"))
        names = set()
        for s in data.get("sources", []):
            plugs = s.get("plugins", [])
            if isinstance(plugs, list):
                names.update(plugs)
        return names
    except Exception as e:
        print(f"  Warning: Failed reading plugin-sources.json: {e}")
        return set()


# plugin_inventory dependencies removed

def sync_source(source_key: str, plugins: list, root: Path, dry_run: bool) -> None:
    """Re-installs all plugins for a given source by calling plugin_add.py."""
    if not plugins:
        return
    plugin_add = root / "plugins" / "plugin-manager" / "scripts" / "plugin_add.py"
    if not plugin_add.exists():
        print(f"  [ERROR] plugin_add.py not found at {plugin_add}")
        return

    plugins_arg = ",".join(plugins)
    cmd = [sys.executable, str(plugin_add), source_key, "--plugins", plugins_arg, "--yes"]
    if dry_run:
        print(f"  [DRY RUN] Would run: {' '.join(cmd)}")
        return
    try:
        subprocess.run(cmd, check=True)
        print(f"  [SYNC] OK: {source_key} → {plugins}")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Failed syncing source '{source_key}': {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync all plugins from plugin-sources.json registry.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without modifying files.")
    parser.add_argument("--cleanup-only", action="store_true", help="Run cleanup only, skip reinstall.")
    args = parser.parse_args()

    root = Path.cwd()

    # 1. Read plugin-sources.json — authoritative registry of ALL installed plugins
    print("--- 1. Reading plugin-sources.json Registry ---")
    registered_set = get_installed_plugin_names(root)
    sources_file = root / "plugin-sources.json"
    sources_data = []
    if sources_file.exists():
        try:
            raw = json.loads(sources_file.read_text(encoding="utf-8"))
            for s in raw.get("sources", []):
                # Support both new (source) and legacy (local/github/name) schema
                src = s.get("source") or s.get("github") or s.get("local") or s.get("name", "")
                plugs = s.get("plugins", [])
                if src and isinstance(plugs, list) and plugs:
                    sources_data.append({"source": src, "plugins": plugs})
        except Exception as e:
            print(f"  Error reading plugin-sources.json: {e}")

    print(f"  {len(registered_set)} registered plugins across {len(sources_data)} sources:")
    for s in sources_data:
        print(f"    [{s['source']}] → {', '.join(s['plugins'])}")

# plugin_inventory dependency removed

    # 3. Cleanup: plugins in registry that no longer have a local source dir
    #    (only applies to locally-sourced plugins where the dir was deleted)
    print("\n--- 3. Cleanup Analysis ---")
    # Detect locally-sourced plugins whose source dir is gone
    stale = set()
    for s in sources_data:
        src = s["source"]
        # Only check stale for local paths (not GitHub slugs)
        if src.startswith("/") or src.startswith("./") or src.startswith("plugins/"):
            src_path = Path(src) if src.startswith("/") else root / src
            if not src_path.exists():
                stale.update(s["plugins"])
                print(f"  Stale source (path gone): {src} → {s['plugins']}")

    if stale:
        print(f"  Cleaning {len(stale)} stale plugin(s)...")
        for plugin in sorted(stale):
            clean_plugin_artifacts(plugin, root, args.dry_run)
    else:
        print("  No stale local sources detected.")

    # 4. Reinstall — call plugin_add.py per source entry so all plugins are redeployed
    if not args.cleanup_only:
        print(f"\n--- 4. Syncing All Registered Plugins ---")
        if not sources_data:
            print("  No sources registered in plugin-sources.json. Nothing to sync.")
            print("  Run plugin_add.py to register and install plugins first.")
        else:
            for s in sources_data:
                if s["plugins"]:
                    src = s["source"]
                    print(f"\n  Source: {src}")
                    sync_source(src, s["plugins"], root, args.dry_run)
    else:
        print("\nSkipping reinstall (--cleanup-only).")

    print("\nSync Complete.")


if __name__ == "__main__":
    main()
