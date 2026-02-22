#!/usr/bin/env python3
"""
Spec Kitty Configuration Sync
=============================

Synchronizes fresh artifacts from the local workspace back into the plugin's
source of truth directories for distribution via the Bridge.

Artifacts:
1. Workflows (.windsurf/workflows -> plugins/spec-kitty/commands)
2. Rules (.kittify/memory -> plugins/spec-kitty/rules)

Assumptions:
1. User has installed the 'spec-kitty' CLI: `pip install --upgrade spec-kitty-cli`
2. User has initialized the repository: `spec-kitty init . --ai windsurf`
3. Run this script to propagate updates into the plugin system.

Usage:
    python3 plugins/spec-kitty/skills/spec-kitty-agent/scripts/sync_configuration.py
"""

import shutil
import os
from pathlib import Path
from typing import NoReturn

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
ROOT = PROJECT_ROOT

# Sources
WORKFLOWS_SOURCE_DIR = ROOT / ".windsurf/workflows"
RULES_SOURCE_DIR = ROOT / ".kittify/memory"

# Destinations
WORKFLOWS_DEST_DIR = ROOT / "plugins/spec-kitty/commands"
RULES_DEST_DIR = ROOT / "plugins/spec-kitty/rules"

# Legacy Cleanup
LEGACY_WORKFLOWS_DIR = ROOT / "plugins/spec-kitty/workflows"

def sync_workflows() -> None:
    """Syncs workflow files from Windsurf source to plugin commands."""
    if not WORKFLOWS_SOURCE_DIR.exists():
        print(f"⚠️  Workflows source not found: {WORKFLOWS_SOURCE_DIR}")
        return

    print(f"🔄 Syncing workflows from {WORKFLOWS_SOURCE_DIR} to {WORKFLOWS_DEST_DIR}...")
    WORKFLOWS_DEST_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for src_file in WORKFLOWS_SOURCE_DIR.glob("*.md"):
        new_name = src_file.name
        # Remove prefix if present to avoid double prefix in Bridge
        if new_name.startswith("spec-kitty."):
             new_name = new_name.replace("spec-kitty.", "")
             
        dest_file = WORKFLOWS_DEST_DIR / new_name
        shutil.copy2(src_file, dest_file)
        count += 1

    print(f"   ✅ Synced {count} workflows.")

    if LEGACY_WORKFLOWS_DIR.exists():
        print(f"🗑️  Removing legacy workflows dir: {LEGACY_WORKFLOWS_DIR}")
        shutil.rmtree(LEGACY_WORKFLOWS_DIR)

def sync_rules() -> None:
    """Syncs rule files from Kittify memory source to plugin rules."""
    if not RULES_SOURCE_DIR.exists():
        print(f"⚠️  Rules source not found: {RULES_SOURCE_DIR}")
        return

    print(f"🔄 Syncing rules from {RULES_SOURCE_DIR} to {RULES_DEST_DIR}...")
    RULES_DEST_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for src_file in RULES_SOURCE_DIR.glob("*.md"):
        dest_file = RULES_DEST_DIR / src_file.name
        shutil.copy2(src_file, dest_file)
        count += 1

    print(f"   ✅ Synced {count} rules.")

def main() -> None:
    print("🚀 Synchronizing Spec-Kitty configurations...")
    sync_workflows()
    sync_rules()
    
    print("\n⚠️  NEXT STEP: Propagate to Agents")
    print("   Run: python plugins/plugin-mapper/skills/agent-bridge/scripts/bridge_installer.py --plugin plugins/spec-kitty --target <your_ide>")

if __name__ == "__main__":
    main()
