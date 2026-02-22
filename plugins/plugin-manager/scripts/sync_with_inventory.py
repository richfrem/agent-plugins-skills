#!/usr/bin/env python3
"""
Sync Plugins with Inventory
===========================

Synchronizes the agent environments with the local `plugins/` directory.
Implements a "Dual Inventory" approach to safely identify and clean up deleted plugins.

Process:
1.  **Scan Vendor**: Generates/Reads inventory from `.vendor/agent-plugins-skills`.
2.  **Scan Local**: Generates local inventory from `plugins/`.
3.  **Cleanup**: Identifies plugins present in Vendor but missing from Local (User Deleted).
    -   Removes their artifacts from .agent, .github, .gemini, .claude.
4.  **Install**: Re-installs/Updates all plugins present in Local.

Usage:
  python3 scripts/sync_with_inventory.py [--dry-run]
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
# Bridge installer is provided by plugin-mapper (canonical, supports 30+ targets)
# plugin-manager/scripts/bridge_installer.py has been removed — use this path instead.
PROJECT_ROOT = SCRIPT_DIR.parents[2]  # scripts→plugin-manager→plugins→ROOT
BRIDGE_INSTALLER = PROJECT_ROOT / "plugins/plugin-mapper/skills/agent-bridge/scripts/bridge_installer.py"

AGENT_DIRS = {
    "antigravity": {
        "dirs": [".agent/workflows", ".agent/skills", ".agent/rules"],
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

def clean_plugin_artifacts(plugin_name: str, root: Path, dry_run: bool):
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

def run_bridge_installer(plugin_path: Path):
    """Runs the bridge installer for a specific plugin."""
    cmd = [sys.executable, str(BRIDGE_INSTALLER), "--plugin", str(plugin_path), "--target", "auto"]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"  [INSTALL] Success: {plugin_path.name}")
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Failed to install {plugin_path.name}: {e.stderr.decode()}")

def get_inventory_names(root: Path) -> set:
    """Helper to get just the set of plugin names from a root."""
    try:
        inventory = plugin_inventory.scan_plugins(root)
        return {item["name"] for item in inventory}
    except Exception as e:
        print(f"Error scanning {root}: {e}")
        return set()

def main():
    parser = argparse.ArgumentParser(description="Sync plugins using dual-inventory.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate cleanup without deleting.")
    parser.add_argument("--cleanup-only", action="store_true", help="Run cleanup analysis only, skip installation.")
    args = parser.parse_args()
    
    root = Path.cwd()
    
    # 1. Get Vendor Inventory (What we COULD have)
    print("--- 1. Scanning Vendor Inventory ---")
    
    vendor_set = set()
    
    if VENDOR_ROOT.exists():
        # Iterate all subdirectories in .vendor/ to support multiple sources (Repo 1, Repo 2, etc.)
        for vendor_repo in VENDOR_ROOT.iterdir():
            if not vendor_repo.is_dir() or vendor_repo.name.startswith("."):
                continue
            
            print(f"  Scanning vendor: {vendor_repo.name}...")
            
            # 1a. Check for official inventory file
            inventory_file = vendor_repo / "vendor-plugins-inventory.json"
            if inventory_file.exists():
                try:
                    data = json.loads(inventory_file.read_text(encoding='utf-8'))
                    names = {str(item["name"]) for item in data}
                    vendor_set.update(names)
                    print(f"    - Loaded {len(names)} plugins from inventory file.")
                except Exception as e:
                    print(f"    - Error reading inventory file: {e}")
            
            # 1b. Check for flat plugins directory (fallback or alongside)
            vendor_plugins_dir = vendor_repo / "plugins"
            if vendor_plugins_dir.exists():
                results = get_inventory_names(vendor_plugins_dir)
                if results:
                    vendor_set.update({str(name) for name in results})
                    print(f"    - Found {len(results)} plugins in directory.")
    else:
        print(f"Warning: Vendor root {VENDOR_ROOT} not found. Skipping cleanup logic.")
    
    print(f"Total Vendor Plugins discovered for sync: {len(vendor_set)}")
    
    # 2. Get Local Inventory (What we DO have)
    print("\n--- 2. Scanning Local Inventory ---")
    if plugin_inventory:
        local_inventory = plugin_inventory.scan_plugins(root)
        local_set = {str(item["name"]) for item in local_inventory}
    else:
        print("❌ Error: plugin_inventory module not found. Sync aborted.")
        sys.exit(1)
    
    # Save Local Inventory (Rich) for the user to reference
    local_inventory_path = root / "local-plugins-inventory.json"
    local_inventory_path.write_text(json.dumps(local_inventory, indent=2), encoding='utf-8')
    print(f"Found {len(local_set)} plugins in Local. Saved to {local_inventory_path}")
    
    # 3. Cleanup Logic (Review)
    # Plugins that are in VENDOR but NOT in LOCAL means the user deleted them.
    to_clean = vendor_set - local_set
    
    print(f"\n--- 3. Cleanup Analysis ---")
    print(f"Vendor Only (Deleted by User): {len(to_clean)}")
    print(f"Local Only (Project Specific): {len(local_set - vendor_set)} (Protected)")
    
    if to_clean:
        print("\nCleaning up artifacts for deleted plugins:")
        for plugin in sorted(to_clean):
            clean_plugin_artifacts(plugin, root, args.dry_run)
    else:
        print("No deleted vendor plugins found. Cleanup skipped.")
        
    # 4. Install Logic
    if not args.cleanup_only:
        print(f"\n--- 4. Updating Agent Artifacts (Bridge) ---")
        if args.dry_run:
            print("Dry run enabled. Skipping installation.")
        else:
            # We iterate local_set to ensure we only install what we have
            # We need the path. Since scan_plugins assumes standard layout:
            for plugin_name in sorted(local_set):
                # Assumption: Directory name matches plugin name for simplicity
                # plugin_inventory uses directory name as default name
                if plugin_name not in vendor_set:
                     # This might be custom, still install it? Yes.
                     pass
                     
                plugin_path = root / "plugins" / plugin_name
                if plugin_path.exists():
                    run_bridge_installer(plugin_path)
    else:
        print("\nSkipping installation (--cleanup-only enabled).")

    print("\nSync Complete.")

if __name__ == "__main__":
    main()
