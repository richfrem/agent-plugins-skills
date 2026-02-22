#!/usr/bin/env python3
"""
sync_inventory_descriptions.py
==============================

Purpose:
    One-time (or periodic) hygiene script to backfill Tool Inventory descriptions 
    using the high-quality 'purpose' fields from the RLM Cache.
    
    This effectively "hydrates" the manual inventory with LLM-generated insights.

Usage:
    python plugins/tool-inventory/scripts/sync_inventory_descriptions.py

Dependencies:
    - plugins/tool-inventory/scripts/manage_tool_inventory.py
    - .agent/learning/rlm_tool_cache.json
"""

import sys
import json
from pathlib import Path

# Add project root to sys.path
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Import from local script in same plugin directory
try:
    from manage_tool_inventory import InventoryManager
except ImportError:
    # Fallback to absolute path if running from project root
    from plugins.tool_inventory.scripts.manage_tool_inventory import InventoryManager

def main():
    # Cache and Inventory paths
    cache_path = PROJECT_ROOT / ".agent/learning/rlm_tool_cache.json"
    inventory_path = PROJECT_ROOT / "tools/tool_inventory.json"

    
    if not cache_path.exists():
        print(f"❌ Cache not found at {cache_path}")
        return

    print("Loading RLM Cache...")
    with open(cache_path, "r", encoding="utf-8") as f:
        cache = json.load(f)

    print("Loading Inventory Manager...")
    mgr = InventoryManager(inventory_path)
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"Processing {len(cache)} cache entries...")
    
    for relative_path, data in cache.items():
        try:
            summary_json_str = data.get("summary", "{}")
            # distillation failure check
            if summary_json_str == "[DISTILLATION FAILED]":
                skipped_count += 1
                continue
                
            summary_data = json.loads(summary_json_str)
            purpose = summary_data.get("purpose", "").strip()
            
            if not purpose:
                skipped_count += 1
                continue
                
            # Call Update w/ Suppression to avoid infinite loop
            # The manager's update_tool prints its own success messages
            # We assume if tool not found, manager prints error and returns
            
            # Check if description distinct enough? 
            # Actually manager overwrites. That is desired behavior (RLM is source of truth for desc)
            
            mgr.update_tool(
                tool_path=relative_path,
                new_desc=purpose,
                suppress_distillation=True
            )
            updated_count += 1
            
        except json.JSONDecodeError:
            print(f"⚠️  JSON Parse Error for {relative_path}")
            error_count += 1
        except Exception as e:
            print(f"⚠️  Error processing {relative_path}: {e}")
            error_count += 1
            
    print("-" * 50)
    print("Sync Complete!")
    print(f"   Processed: {updated_count}")
    print(f"   Skipped:   {skipped_count}")
    print(f"   Errors:    {error_count}")

if __name__ == "__main__":
    main()
