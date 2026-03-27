#!/usr/bin/env python3
"""
audit_scope_zombies.py (CLI)
=====================================

Purpose:
    Identifies zombie forms - documented but not in master scope CSV.

Layer: Curate / Inventories

Usage Examples:
    python plugins/inventory-manager/scripts/audit_scope_zombies.py --help

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
import csv
import os

# 1. Load Master Scope (CSV)
master_scope = set()
try:
    with open('legacy-system/reference-data/collections/jam-mastersheet/APP-MasterScope.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row:
                for val in row.values():
                    if val and (val.startswith('APP') or val.startswith('FORM')): 
                         master_scope.add(val.upper())
                         break
except Exception as e:
    print(f"CSV Error: {e}")

# If heuristic failed, let's look at the raw keys in the next step.

# 2. Load File Scope
file_scope = set()
try:
    files = os.listdir('legacy-system/oracle-forms-overviews/forms')
    for f in files:
        if f.endswith('.md'):
            form_id = f.split('-')[0].upper()
            file_scope.add(form_id)
except Exception as e:
    print(f"File Error: {e}")

# 3. Compare
# Files that are NOT in Master Scope (Potential Zombies)
zombies = file_scope - master_scope

print(f"Master CSV Count (Heuristic): {len(master_scope)}")
print(f"Overview File Count:          {len(file_scope)}")
print(f"Potential 'Zombie' Forms (Documented but not in Master): {len(zombies)}")

if zombies:
    print(f"Sample Zombies: {sorted(list(zombies))[:10]}")

# Debug: Print CSV headers if count is low (heuristic check)
if len(master_scope) < 10:
    try:
        with open('legacy-system/reference-data/collections/jam-mastersheet/APP-MasterScope.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            headers = next(reader)
            print(f"CSV Headers: {headers}")
    except:
        pass
