#!/usr/bin/env python3
"""
audit_inventory.py (CLI)
=====================================

Purpose:
    Compares forms_and_reports_inventory.json against actual Overview files to find gaps.

Layer: Curate / Inventories

Usage Examples:
    python plugins/inventory-manager/scripts/audit_inventory.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    (None detected)

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import json
import os

# 1. Get Inventory IDs
try:
    with open('legacy-system/reference-data/inventories/forms_and_reports_inventory.json', 'r') as f:
        data = json.load(f)
    
    inventory_ids = {
        item.get('OBJECT_ID') 
        for item in data 
        if item.get('APPLICATION', '').upper() == 'Project' and item.get('OBJECT_TYPE', '').upper() == 'FORM'
    }
except Exception as e:
    print(f"Inventory Error: {e}")
    inventory_ids = set()

# 2. Get File IDs
try:
    files = os.listdir('legacy-system/oracle-forms-overviews/forms')
    file_ids = {f.replace('-Overview.md', '') for f in files if f.endswith('.md')}
except Exception as e:
    print(f"File Error: {e}")
    file_ids = set()

# 3. Compare
missing_files = inventory_ids - file_ids
extra_files = file_ids - inventory_ids

print(f"Inventory Count: {len(inventory_ids)}")
print(f"File Count:      {len(file_ids)}")
print(f"Missing Overviews (In Inventory but no MD): {len(missing_files)}")
print(f"Extra Overviews (In MD but not Inventory):   {len(extra_files)}")

if missing_files:
    print(f"Sample Missing: {list(missing_files)[:5]}")
if extra_files:
    print(f"Sample Extra: {list(extra_files)[:5]}")
