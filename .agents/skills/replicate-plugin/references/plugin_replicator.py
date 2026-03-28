#!/usr/bin/env python3
"""
plugin_replicator.py
=====================================
Purpose: Safely installs or updates a plugin in a target repository.
[v2.0] Implements a Local Ledger to track and prune orphaned files (ghost artifacts) during updates.

Replicates a plugin from a source directory to a destination directory.
Supports additive-update mode (default) and clean-sync mode (--clean).

Usage:
    plugin_replicator.py --source <src-plugin-dir> --dest <dest-dir> [--link] [--clean] [--dry-run]

Arguments:
    --source    Path to the source plugin folder (e.g., plugins/rlm-factory)
    --dest      Path to the destination folder (e.g., /path/to/other-project/plugins/rlm-factory)
    --link      Create a symlink instead of copying (best for active development)
    --clean     Remove files/dirs in dest that no longer exist in source (default: additive only)
    --dry-run   Preview changes without making them

Modes:
    Default     Copies new/updated files. Does NOT delete anything from dest.
    --clean     Copies new/updated files AND removes dest files missing from source.
    --link      Creates a symlink. Implies always up-to-date (no --clean needed).

Examples:
    # Additive update: replicate rlm-factory to Project Sanctuary
    python3 plugin_replicator.py \\
        --source plugins/rlm-factory \\
        --dest /Users/richardfremmerlid/Projects/Project_Sanctuary/plugins/rlm-factory

    # Clean sync: remove deleted skills/files too
    python3 plugin_replicator.py \\
        --source plugins/rlm-factory \\
        --dest /Users/richardfremmerlid/Projects/Project_Sanctuary/plugins/rlm-factory \\
        --clean

    # Dev symlink (always live)
    python3 plugin_replicator.py \\
        --source plugins/rlm-factory \\
        --dest /Users/richardfremmerlid/Projects/Project_Sanctuary/plugins/rlm-factory \\
        --link
"""
import os
import sys
import json
import shutil
import argparse
from pathlib import Path

LEDGER_FILENAME = "plugin_ledger.json"

def load_ledger(agents_dir: Path) -> dict:
    """Loads the installation ledger tracking which files belong to which plugin."""
    ledger_path = agents_dir / LEDGER_FILENAME
    if ledger_path.exists():
        try:
            with open(ledger_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Warning: Could not read ledger at {ledger_path}: {e}")
    return {}

def save_ledger(agents_dir: Path, ledger_data: dict) -> None:
    """Saves the updated installation ledger."""
    ledger_path = agents_dir / LEDGER_FILENAME
    agents_dir.mkdir(parents=True, exist_ok=True)
    with open(ledger_path, 'w', encoding='utf-8') as f:
        json.dump(ledger_data, f, indent=2)

def safely_remove_path(target_path: Path):
    """Deletes a file or directory if it exists."""
    if not target_path.exists():
        return
    try:
        if target_path.is_symlink() or target_path.is_file():
            target_path.unlink()
        elif target_path.is_dir():
            shutil.rmtree(target_path)
        print(f"  🧹 Pruned orphaned artifact: {target_path.name}")
    except Exception as e:
        print(f"  ❌ Failed to remove {target_path}: {e}")

def replicate_plugin(plugin_name: str, source_dir: Path, target_repo: Path):
    print(f"\n🚀 Starting installation for: {plugin_name}")
    
    # 1. Define standard paths
    target_agents_dir = target_repo / ".agents"
    target_plugins_dir = target_agents_dir / "plugins" / plugin_name
    target_skills_dir = target_agents_dir / "skills"
    
    # Ensure target directories exist
    target_plugins_dir.mkdir(parents=True, exist_ok=True)
    target_skills_dir.mkdir(parents=True, exist_ok=True)

    # 2. Load the Ledger
    ledger = load_ledger(target_agents_dir)
    plugin_state = ledger.get(plugin_name, {"folders": [], "skills": []})
    
    # 3. Analyze the incoming payload to see what WE are about to install
    incoming_skills = []
    source_skills_dir = source_dir / "skills"
    if source_skills_dir.exists():
        incoming_skills = [d.name for d in source_skills_dir.iterdir() if d.is_dir()]

    # 4. Prune Ghost Artifacts (The Cleanup Phase)
    print("🔍 Checking for orphaned files from previous installations...")
    old_skills = plugin_state.get("skills", [])
    
    for old_skill in old_skills:
        if old_skill not in incoming_skills:
            # The skill existed in the old version, but isn't in the new version. KILL IT.
            orphan_path = target_skills_dir / old_skill
            safely_remove_path(orphan_path)

    # 5. Install the new payload
    print(f"📦 Copying plugin core to {target_plugins_dir}...")
    
    # Wipe the core plugin directory to ensure a clean slate there
    if target_plugins_dir.exists():
        shutil.rmtree(target_plugins_dir)
    shutil.copytree(source_dir, target_plugins_dir, ignore=shutil.ignore_patterns('.git', 'node_modules', '__pycache__'))

    # Hard-copy skills into the global .agents/skills/ directory
    if incoming_skills:
        print(f"🔗 Deploying {len(incoming_skills)} skills...")
        for skill_name in incoming_skills:
            src_skill = source_skills_dir / skill_name
            dest_skill = target_skills_dir / skill_name
            
            # Wipe existing skill if updating
            if dest_skill.exists():
                shutil.rmtree(dest_skill)
            
            shutil.copytree(src_skill, dest_skill)
            print(f"  ✅ Installed skill: {skill_name}")

    # 6. Update and Save the Ledger
    ledger[plugin_name] = {
        "installed_at": datetime.now().isoformat(),
        "skills": incoming_skills
    }
    save_ledger(target_agents_dir, ledger)
    
    print(f"🎉 Successfully installed/updated '{plugin_name}' and updated the ledger!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replicate a plugin to a target repository with ledger tracking.")
    parser.add_argument("--plugin-name", required=True, help="Name of the plugin being installed.")
    parser.add_argument("--source-dir", required=True, type=Path, help="Path to the source plugin directory.")
    parser.add_argument("--target-repo", required=True, type=Path, help="Path to the target repository root.")
    
    args = parser.parse_args()
    
    from datetime import datetime # Imported here for the ledger timestamp
    replicate_plugin(args.plugin_name, args.source_dir, args.target_repo)