#!/usr/bin/env python3
"""
Update From Vendor Script
=========================

This script synchronizes the local `plugins/` directory with the `.vendor/agent-plugins-skills` source.
It only updates plugins that are ALREADY installed locally. It does NOT install new plugins automatically.

Usage:
  python3 scripts/update_from_vendor.py
"""

import os
import shutil
from pathlib import Path
import sys

def main():
    # 1. Identify Roots
    script_dir = Path(__file__).parent.resolve()
    # Assume script is in plugins/plugin-manager/scripts/
    project_root = script_dir.parents[2] 
    
    local_plugins_dir = project_root / "plugins"
    vendor_plugins_dir = project_root / ".vendor" / "agent-plugins-skills" / "plugins"

    # print(f"Project Root: {project_root}")
    # print(f"Local Plugins: {local_plugins_dir}")
    # print(f"Vendor Source: {vendor_plugins_dir}")

    if not vendor_plugins_dir.exists():
        print(f"Error: Vendor plugins directory not found at {vendor_plugins_dir}")
        print("Please ensure the vendor repo is cloned: git clone ... .vendor/agent-plugins-skills")
        sys.exit(1)

    if not local_plugins_dir.exists():
        print(f"Warning: Local plugins directory not found at {local_plugins_dir}")
        return

    print("--- Starting Plugin Update ---")

    # 2. Iterate Local Plugins
    updated_count = 0
    skipped_count = 0

    for item in local_plugins_dir.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            plugin_name = item.name
            vendor_src = vendor_plugins_dir / plugin_name
            
            # 3. Check Vendor Existence
            if vendor_src.exists():
                print(f"  [UPDATE] found update for '{plugin_name}'")
                try:
                    # dirs_exist_ok=True allows overwriting existing files
                    shutil.copytree(vendor_src, item, dirs_exist_ok=True)
                    updated_count += 1
                except Exception as e:
                    print(f"    Error updating {plugin_name}: {e}")
            else:
                # This is a custom plugin or renamed vendor plugin
                # print(f"  [SKIP] '{plugin_name}' not found in vendor (Project Specific)")
                skipped_count += 1

    print("-" * 30)
    print(f"Update Complete.")
    print(f"Updated: {updated_count}")
    print(f"Skipped: {skipped_count} (Custom/Local-only)")

if __name__ == "__main__":
    main()
