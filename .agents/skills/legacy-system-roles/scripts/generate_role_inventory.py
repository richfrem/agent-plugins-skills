#!/usr/bin/env python3
"""
generate_role_inventory.py (CLI)
=====================================

Purpose:
    Scans project-roles directory and builds roles_inventory.json.

Layer: Curate / Inventories

Usage Examples:
    python plugins/legacy-system-roles/scripts/generate_role_inventory.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import json

ROLES_DIR = os.path.join(os.getcwd(), 'legacy-system', 'project-roles')
INVENTORY_FILE = os.path.join(os.getcwd(), 'legacy-system', 'reference-data', 'roles_inventory.json')

def main():
    if not os.path.exists(ROLES_DIR):
        print(f"Directory not found: {ROLES_DIR}")
        return

    # Load existing to preserve status if possible, or just rebuild?
    # User feedback implies we should "sanitize". Rebuilding from current files (after deletion of bad ones) 
    # is the safest way to ensure inventory matches reality.
    # However, we want to know if they were active or deprecated.
    # We can infer: if it's in the generated list from split_roles (Active) vs created by script (Deprecated).
    # Since we deleted the bad files, we can just scan the folder again.
    
    # But wait, how do we distinguish "Active" vs "Deprecated" just from files?
    # We can check the file content.
    
    inventory = {}
    for filename in os.listdir(ROLES_DIR):
        if filename.endswith('.md'):
            role_name = os.path.splitext(filename)[0]
            file_path = os.path.join(ROLES_DIR, filename)
            
            status = "Active" # Default
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "**Status**: Deprecated" in content:
                        status = "Deprecated"
            except:
                pass

            inventory[role_name] = {
                "file": filename,
                "status": status
            }

    with open(INVENTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2)
    
    print(f"Sanitized inventory with {len(inventory)} roles at {INVENTORY_FILE}")

if __name__ == "__main__":
    main()
