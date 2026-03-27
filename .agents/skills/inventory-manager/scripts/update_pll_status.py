#!/usr/bin/env python3
"""
update_pll_status.py (CLI)
=====================================

Purpose:
    Updates PLL inventory with analysis status information.

Layer: Curate / Inventories

Usage Examples:
    python plugins/inventory-manager/scripts/update_pll_status.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - update_status(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import json
import os

IGNORED_PATH = "legacy-system/reference-data/ignored_libraries.json"
INVENTORY_PATH = "legacy-system/reference-data/inventories/pll_inventory.json"

def update_status():
    if not os.path.exists(IGNORED_PATH):
        print("Ignored file not found.")
        return

    with open(IGNORED_PATH, 'r') as f:
        ignored_data = json.load(f)
        
    with open(INVENTORY_PATH, 'r') as f:
        inventory = json.load(f)
        
    updated_count = 0
    
    # Process Backup Libraries
    for lib in ignored_data.get("backup_libraries", []):
        # Handle case sensitivity (inventory keys might be upper)
        lib_key = lib.upper()
        if lib_key in inventory:
            inventory[lib_key]["status"] = "Archived"
            inventory[lib_key]["notes"] = "Historical backup version"
            updated_count += 1
            print(f"Marked {lib_key} as Archived")

    # Process Misclassified Files
    for lib in ignored_data.get("misclassified_files", []):
        lib_key = lib.upper().replace(".XML", "").replace(".TXT", "") # Try to match key format
        
        # Also try exact match if key includes extension (rare but possible)
        keys_to_check = [lib_key, lib.upper()]
        
        found = False
        for k in keys_to_check:
            if k in inventory:
                inventory[k]["status"] = "Ignored"
                inventory[k]["notes"] = "Misclassified file (not a valid PLL library)"
                updated_count += 1
                found = True
                print(f"Marked {k} as Ignored")
                break
        
        if not found:
            print(f"Warning: Could not find misclassified item {lib} in inventory")

    # Save
    with open(INVENTORY_PATH, 'w') as f:
        json.dump(inventory, f, indent=2)
        
    print(f"Updated {updated_count} entries in pll_inventory.json")

if __name__ == "__main__":
    update_status()
