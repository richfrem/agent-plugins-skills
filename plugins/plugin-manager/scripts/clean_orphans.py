#!/usr/bin/env python3
"""
Plugin Orphan Cleaner
=====================

Scans agent directories for artifacts belonging to plugins that no longer exist
in the source `plugins/` directory.

Target Directories:
- .agent/workflows, .agent/skills, .agent/rules
- .github/prompts, .github/skills, .github/rules
- .gemini/commands, .gemini/skills, .gemini/rules
- .claude/commands, .claude/skills, .claude/rules

Usage:
  python3 plugins/plugin-manager/scripts/clean_orphans.py [--dry-run]
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

# --- Configuration ---

# Project-owned files and directories that must NEVER be deleted by the
# orphan cleaner. These are hand-maintained by the project, not generated
# by the bridge installer, so they don't follow the {plugin_name}_ prefix
# convention and would be falsely flagged as orphans.
PROTECTED_NAMES = {
    # Project rules
    "constitution.md",
    "standard-workflow-rules.md",
    # Policy tier directories
    "01_PROCESS",
    "02_OPERATIONS",
    "03_TECHNICAL",
    # Monolithic context files (shouldn't be in scanned dirs, but safety)
    "CLAUDE.md",
    "GEMINI.md",
    "copilot-instructions.md",
}

AGENT_DIRS = {
    "antigravity": [
        ".agent/workflows",
        ".agent/skills",
        ".agent/rules"
    ],
    "github": [
        ".github/prompts",
        ".github/skills",
        ".github/rules"
    ],
    "gemini": [
        ".gemini/commands",
        ".gemini/skills",
        ".gemini/rules"
    ],
    "claude": [
        ".claude/commands",
        ".claude/skills",
        ".claude/rules"
    ]
}

def get_active_plugins(root: Path):
    """Returns a set of active plugin names from the plugins/ directory."""
    plugins_dir = root / "plugins"
    if not plugins_dir.exists():
        print(f"Error: Plugins directory not found at {plugins_dir}")
        sys.exit(1)

    active_plugins = set()
    for item in plugins_dir.iterdir():
        if item.is_dir():
            # Check for manifest name override, otherwise use dir name
            manifest = item / ".claude-plugin" / "plugin.json"
            if manifest.exists():
                try:
                    import json
                    data = json.loads(manifest.read_text(encoding='utf-8'))
                    name = data.get("name", item.name)
                    active_plugins.add(name)
                except Exception:
                    active_plugins.add(item.name)
            else:
                active_plugins.add(item.name)

    return active_plugins

def clean_directory(target_dir: Path, active_plugins: set, dry_run: bool):
    """Scans a directory and removes items not belonging to active plugins.
    Items listed in PROTECTED_NAMES are never deleted."""
    if not target_dir.exists():
        return

    print(f"Scanning {target_dir}...")

    for item in target_dir.iterdir():
        # Skip protected project-owned files and directories
        if item.name in PROTECTED_NAMES:
            continue

        # Directories (Skills/Rules): exact name match to plugin expected.
        if item.is_dir():
            if item.name not in active_plugins:
                print(f"  [ORPHAN DIR]  {item.name}")
                if not dry_run:
                    shutil.rmtree(item)

        # Files (Workflows/Prompts/Toml): {plugin_name}_{command}.* prefix expected.
        elif item.is_file():
            parts = item.name.split('_', 1)
            if len(parts) > 1:
                potential_plugin = parts[0]
                if potential_plugin not in active_plugins:
                    print(f"  [ORPHAN FILE] {item.name}")
                    if not dry_run:
                        item.unlink()

def main():
    parser = argparse.ArgumentParser(description="Clean orphaned plugin artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be deleted without deleting.")
    args = parser.parse_args()

    root = Path.cwd()
    active_plugins = get_active_plugins(root)
    print(f"Detected {len(active_plugins)} active plugins.")

    for agent, dirs in AGENT_DIRS.items():
        for dir_path in dirs:
            target = root / dir_path
            clean_directory(target, active_plugins, args.dry_run)

    print("Cleanup complete.")

if __name__ == "__main__":
    main()
