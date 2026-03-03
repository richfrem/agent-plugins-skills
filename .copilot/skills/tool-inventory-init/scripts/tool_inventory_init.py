#!/usr/bin/env python3
"""
Tool Inventory Setup (Librarian Bootstrapper)
=============================================

Purpose:
    Provides an automated, non-interactive wrapper around the `rlm-init` logic,
    expressly tailoring a semantic cache profile specifically for "tools". This script
    acts as the first-run configuration generator, creating the necessary manifests
    and profile entries without requiring QA prompt loops.

Layer: Curate / Inventories

Usage:
    python3 plugins/tool-inventory/skills/tool-inventory-init/scripts/tool_inventory_init.py
"""

import sys
import json
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent.parent
LEARNING_DIR = PROJECT_ROOT / ".agent" / "learning"
PROFILES_PATH = LEARNING_DIR / "rlm_profiles.json"
MANIFEST_PATH = LEARNING_DIR / "rlm_tools_manifest.json"
CACHE_PATH = LEARNING_DIR / "rlm_tool_cache.json"

TOOLS_PROFILE_NAME = "tools"

def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error parsing {path}: {e}")
        return {}

def save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
def configure_profile():
    print(f"🔍 Configuring RLM Tools Profile in {PROFILES_PATH}...")
    
    profiles_data = load_json(PROFILES_PATH)
    
    # Initialize base schema if empty
    if "version" not in profiles_data:
        profiles_data["version"] = 1
    if "profiles" not in profiles_data:
        profiles_data["profiles"] = {}
        
    # Check for existing tools profile
    if TOOLS_PROFILE_NAME in profiles_data["profiles"]:
        print(f"ℹ️  Profile '{TOOLS_PROFILE_NAME}' already exists. Skipping profile creation.")
    else:
        # Inject the custom tools profile
        profiles_data["profiles"][TOOLS_PROFILE_NAME] = {
            "description": "Semantic Registry of Project Tools and Executable Code logic.",
            "manifest": ".agent/learning/rlm_tools_manifest.json",
            "cache": ".agent/learning/rlm_tool_cache.json",
            "extensions": [".py", ".js", ".ts", ".sh"]
        }
        
        # Optionally set default profile if it's the only one
        if "default_profile" not in profiles_data:
            profiles_data["default_profile"] = TOOLS_PROFILE_NAME
            
        save_json(PROFILES_PATH, profiles_data)
        print(f"✅ Created profile '{TOOLS_PROFILE_NAME}' in {PROFILES_PATH}.")

def configure_manifest():
    print(f"🔍 Generating Inventory Manifest at {MANIFEST_PATH}...")
    
    if MANIFEST_PATH.exists():
         print(f"ℹ️  Manifest already exists at {MANIFEST_PATH}. Skipping manifest creation.")
    else:
        manifest_data = {
            "description": "Globs tracking tool and plugin behavior scripts across the repository.",
            "include": [
                "plugins/",
                "plugins/"
            ],
            "exclude": [
                ".git/",
                "node_modules/",
                ".venv/",
                "__pycache__/",
                ".pytest_cache/",
                "tests/"
            ],
            "recursive": True
        }
        save_json(MANIFEST_PATH, manifest_data)
        print(f"✅ Created explicit tools manifest at {MANIFEST_PATH}.")

def initialize_cache():
    print(f"🔍 Ensuring empty cache exists at {CACHE_PATH}...")
    
    if CACHE_PATH.exists():
        print(f"ℹ️  Cache file already exists at {CACHE_PATH}. Leaving untouched.")
    else:
        save_json(CACHE_PATH, {})
        print(f"✅ Created baseline cache file at {CACHE_PATH}.")
        
def main():
    print("====================================")
    print(" LIBRARIAN TOOL-INVENTORY BOOTSTRAP")
    print("====================================")
    
    # Ensure directory framework exists
    LEARNING_DIR.mkdir(parents=True, exist_ok=True)
    
    configure_profile()
    configure_manifest()
    initialize_cache()
    
    print("\n✅ Initialization complete. The ledger and schemas are scaffolded.")
    print("\nNext Steps for Agent:\n  1. Run the RLM auditor to identify missing scripts: \n     python3 plugins/rlm-factory/skills/rlm-curator/scripts/inventory.py --profile tools")
    print("  2. Perform initial distillation on those missing tools.")
    
if __name__ == "__main__":
    main()
