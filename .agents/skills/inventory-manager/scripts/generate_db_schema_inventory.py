#!/usr/bin/env python3
"""
generate_db_schema_inventory.py (CLI)
=====================================

Purpose:
    Generates database schema inventory from SQL files.

Layer: Curate / Inventories

Usage Examples:
    python plugins/inventory-manager/scripts/generate_db_schema_inventory.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - scan_directory(): Returns a dict of {NAME: filename} for all .sql files in directory.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import json

# Paths are relative to project root — run this script from the project root directory.
DB_ROOT = os.path.join('.', 'legacy-system', 'oracle-database')

DIRS = {
    'tables': os.path.join(DB_ROOT, 'Tables'),
    'views': os.path.join(DB_ROOT, 'Views'),
    'constraints': os.path.join(DB_ROOT, 'Constraints'),
    'indexes': os.path.join(DB_ROOT, 'Indexes'),
    'sequences': os.path.join(DB_ROOT, 'Sequences'),
    'functions': os.path.join(DB_ROOT, 'Functions'),
    'procedures': os.path.join(DB_ROOT, 'Procedures'),
    'types': os.path.join(DB_ROOT, 'Types'),
    'packages': os.path.join(DB_ROOT, 'Packages'),
    'triggers': os.path.join(DB_ROOT, 'Triggers')
}

INVENTORIES_DIR = os.path.join('.', 'legacy-system', 'reference-data', 'inventories')

def scan_directory(path):
    """Returns a dict of {NAME: filename} for all .sql files in directory."""
    result = {}
    if not os.path.exists(path):
        print(f"Warning: Directory not found: {path}")
        return result

    print(f"Scanning {path}...")
    for filename in os.listdir(path):
        if filename.lower().endswith('.sql'):
            # For Granular files, name usually IS the filename without extension (except Packages)
            # Packages/Funcs: PKG.NAME.sql
            name = filename[:-4].upper()
            result[name] = filename
    return result

def main():
    if not os.path.exists(INVENTORIES_DIR):
        os.makedirs(INVENTORIES_DIR, exist_ok=True)

    inventory = {}

    for key, path in DIRS.items():
        inventory[key] = scan_directory(path)

    # Write separate inventories
    configs = [
        ('tables', 'tables_inventory.json'),
        ('views', 'views_inventory.json'),
        ('functions', 'functions_inventory.json'),
        ('procedures', 'procedures_inventory.json'),
        ('types', 'types_inventory.json'),
        ('constraints', 'constraints_inventory.json'),
        ('indexes', 'indexes_inventory.json'),
        ('sequences', 'sequences_inventory.json'),
        ('packages', 'packages_inventory.json'),
        ('triggers', 'triggers_inventory.json')
    ]

    for section, file_suffix in configs:
        out_path = os.path.join(INVENTORIES_DIR, file_suffix)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(inventory.get(section, {}), f, indent=2)
        print(f"Generated {out_path} ({len(inventory.get(section, {}))} items)")

if __name__ == "__main__":
    main()
