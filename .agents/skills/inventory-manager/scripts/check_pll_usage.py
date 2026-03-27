#!/usr/bin/env python3
"""
check_pll_usage.py (CLI)
=====================================

Purpose:
    Checks if any Forms attach logic from known Backup/Deprecated libraries.

Layer: Curate / Inventories

Usage Examples:
    python plugins/inventory-manager/scripts/check_pll_usage.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - check_usage(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import json
import sys
import os

BACKUP_LIBS = [
    "AGLIB_20019", "AGLIB_20020", "AGLIB_20021", "AGLIB_20022",
    "EXAMPLE_LIB2_20160412", "EXAMPLE_LIB2_20200313", "EXAMPLE_LIB2_20201209"
]

def check_usage():
    map_path = "legacy-system/reference-data/inventories/dependency_map.json"
    
    with open(map_path, 'r') as f:
        data = json.load(f)
        
    found = False
    for form_name, details in data.items():
        attached = details.get("AttachedPLLs", [])
        # Normalize to stored name (upper, no ext)
        attached_clean = [p.replace(".PLL", "").replace(".pll", "").upper() for p in attached]
        
        for lib in BACKUP_LIBS:
            if lib in attached_clean:
                print(f"WARNING: Form {form_name} attaches backup library {lib}")
                found = True
                
    if not found:
        print("Success: No forms reference the backup libraries.")

if __name__ == "__main__":
    check_usage()
