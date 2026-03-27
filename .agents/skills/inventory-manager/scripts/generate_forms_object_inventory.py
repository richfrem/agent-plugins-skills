#!/usr/bin/env python3
"""
generate_forms_object_inventory.py (CLI)
=====================================

Purpose:
    Scans XML directory for Menus (.mmb) and Object Libraries (.olb) to build their inventories.

Layer: Curate / Inventories

Usage Examples:
    python plugins/inventory-manager/scripts/generate_forms_object_inventory.py --help

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
import re

# Paths are relative to project root - run this script from the project root directory.
XML_DIR = os.path.join('.', 'legacy-system', 'oracle-forms', 'XML')
OUT_DIR = os.path.join('.', 'legacy-system', 'reference-data', 'inventories')

if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR, exist_ok=True)

MENU_OUT = os.path.join(OUT_DIR, "menus_inventory.json")
OLB_OUT = os.path.join(OUT_DIR, "olb_inventory.json")

def main():
    if not os.path.exists(XML_DIR):
        print(f"Error: XML directory not found: {XML_DIR}")
        return

    menus = {}
    olbs = {}

    print(f"Scanning {XML_DIR} for Menus and Object Libraries...")
    
    for filename in os.listdir(XML_DIR):
        lower_name = filename.lower()
        
        # Check for Menus (_mmb.xml)
        if lower_name.endswith("_mmb.xml"):
            # JASON MENU -> ID: JASON_MENU (Upper)
            # Filename: jason_menu_mmb.xml -> JASON_MENU
            obj_name = filename[:-8].upper() # Remove _mmb.xml
            menus[obj_name] = {
                "name": obj_name,
                "file": filename,
                "artifacts": {
                    "xml": f"legacy-system/oracle-forms/XML/{filename}"
                }
            }
        
        # Check for Object Libraries (_olb.xml)
        elif lower_name.endswith("_olb.xml"):
            obj_name = filename[:-8].upper() # Remove _olb.xml
            olbs[obj_name] = {
                "name": obj_name,
                "file": filename,
                "artifacts": {
                    "xml": f"legacy-system/oracle-forms/XML/{filename}"
                }
            }

    # Write Menus
    with open(MENU_OUT, 'w', encoding='utf-8') as f:
        json.dump(menus, f, indent=2)
    print(f"Menus Inventory: {len(menus)} objects -> {MENU_OUT}")

    # Write OLBs
    with open(OLB_OUT, 'w', encoding='utf-8') as f:
        json.dump(olbs, f, indent=2)
    print(f"OLB Inventory: {len(olbs)} objects -> {OLB_OUT}")

if __name__ == "__main__":
    main()
