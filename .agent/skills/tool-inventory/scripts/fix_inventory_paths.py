#!/usr/bin/env python3
"""
Fix Inventory Paths
===================

Updates tool_inventory.json to reflect the new plugin structure:
plugins/<plugin>/scripts/X -> plugins/<plugin>/skills/<skill>/scripts/X

Usage:
    python3 plugins/plugin-manager/skills/plugin-manager/scripts/fix_inventory_paths.py [--apply]
"""

import json
import sys
import argparse
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent.parent
INVENTORY_PATH = PROJECT_ROOT / "tools" / "tool_inventory.json"

SKILL_MAPPINGS = {
    "rlm-factory": "rlm-curator",
    "context-bundler": "bundler-agent",
    "spec-kitty": "spec-kitty-agent",
    "task-manager": "task-agent",
    "vector-db": "vector-db-agent",
    "workflow-inventory": "workflow-inventory-agent",
    "adr-manager": "adr-agent",
    "chronicle-manager": "chronicle-agent",
    "protocol-manager": "protocol-agent",
    "link-checker": "link-checker-agent",
    "mermaid-export": "diagram-agent",
    "code-snapshot": "snapshot-agent",
    "json-hygiene": "json-hygiene-agent",
    "agent-orchestrator": "orchestrator-agent",
}

def get_new_path(old_path: Path) -> Path:
    # Expected format: plugins/<plugin>/scripts/<file>
    parts = old_path.parts
    
    # Check if it starts with plugins/
    try:
        if parts[0] != "plugins":
            return old_path
        
        plugin_name = parts[1]
        
        # Check if it was in scripts/
        if len(parts) > 2 and parts[2] == "scripts":
            file_name = parts[3]
            
            # Determine skill name
            skill_name = SKILL_MAPPINGS.get(plugin_name, plugin_name)
            
            # Construct new path: plugins/<plugin>/skills/<skill>/scripts/<file>
            new_path = Path("plugins") / plugin_name / "skills" / skill_name / "scripts" / file_name
            return new_path
            
    except IndexError:
        return old_path
        
    return old_path

def main():
    parser = argparse.ArgumentParser(description="Fix Inventory Paths")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    args = parser.parse_args()

    print(f"DEBUG: PROJECT_ROOT = {PROJECT_ROOT}")

    if not INVENTORY_PATH.exists():
        print(f"❌ Inventory not found: {INVENTORY_PATH}")
        sys.exit(1)

    with open(INVENTORY_PATH, "r") as f:
        data = json.load(f)

    updated_count = 0
    
    # Iterate through categories (python, javascript, etc.)
    for lang in ["python", "javascript"]:
        if lang not in data: continue
        
        tools_dict = data[lang].get("tools", {})
        
        for tool_list in tools_dict.values():
            if not isinstance(tool_list, list): continue
            
            for tool in tool_list:
                current_path_str = tool.get("path")
                if not current_path_str: continue
                
                current_path = Path(current_path_str)
                full_current_path = PROJECT_ROOT / current_path
                
                if not full_current_path.exists():
                    # Attempt to fix
                    new_path = get_new_path(current_path)
                    full_new_path = PROJECT_ROOT / new_path
                    
                    if full_new_path.exists():
                        print(f"✅ Found moved file: {current_path} -> {new_path}")
                        if args.apply:
                            tool["path"] = str(new_path)
                            updated_count += 1
                    else:
                        print(f"❌ File missing: {current_path}")
                        print(f"   Tried: {new_path}")
                        print(f"   Full Checked: {full_new_path}")
                        if not full_new_path.parent.exists():
                             print(f"   Parent dir missing: {full_new_path.parent}")
                        else:
                             print(f"   Parent dir exists: {full_new_path.parent}")
                             # List parent dir
                             try:
                                 files = list(full_new_path.parent.glob("*"))
                                 print(f"   Files in parent: {[f.name for f in files]}")
                             except Exception as e:
                                 print(f"   Error listing parent: {e}")

    if args.apply:
        with open(INVENTORY_PATH, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\n💾 Updated {updated_count} valid paths in inventory.")
    else:
        print(f"\n🔍 Dry Run: Found {updated_count} paths to update. Use --apply to save.")

if __name__ == "__main__":
    main()
