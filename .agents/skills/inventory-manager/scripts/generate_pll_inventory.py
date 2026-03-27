#!/usr/bin/env python3
"""
generate_pll_inventory.py (CLI)
=====================================

Purpose:
    Parses PLL text dumps to build JSON inventory of packages and procedures.

Layer: Curate / Inventories

Usage Examples:
    python plugins/inventory-manager/scripts/generate_pll_inventory.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - parse_pll_file(): Parses a PLL text dump to extract Package names and their Procedures/Functions.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import re
import json

# Configuration
PLL_DIR = r'legacy-system/oracle-forms/pll'
OUTPUT_FILE = r'legacy-system/reference-data/inventories/pll_inventory.json'

def parse_pll_file(file_path):
    """
    Parses a PLL text dump to extract Package names and their Procedures/Functions.
    """
    inventory = {}
    current_package = None
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    # Regex patterns
    # PACKAGE name IS
    pkg_pattern = re.compile(r'^\s*PACKAGE\s+([\w$]+)\s+IS', re.IGNORECASE)
    # PROCEDURE name (...)
    proc_pattern = re.compile(r'^\s*PROCEDURE\s+([\w$]+)', re.IGNORECASE)
    # FUNCTION name (...) RETURN ...
    func_pattern = re.compile(r'^\s*FUNCTION\s+([\w$]+)', re.IGNORECASE)
    # PACKAGE BODY - stop processing spec
    body_pattern = re.compile(r'^\s*PACKAGE BODY', re.IGNORECASE)

    for line in lines:
        if body_pattern.search(line):
            # We mostly care about the spec for linking
            continue
            
        pkg_match = pkg_pattern.search(line)
        if pkg_match:
            current_package = pkg_match.group(1).upper()
            inventory[current_package] = {
                'procedures': [],
                'functions': []
            }
            continue
            
        if current_package:
            proc_match = proc_pattern.search(line)
            if proc_match:
                proc_name = proc_match.group(1).upper()
                if proc_name not in inventory[current_package]['procedures']:
                    inventory[current_package]['procedures'].append(proc_name)
                    
            func_match = func_pattern.search(line)
            if func_match:
                func_name = func_match.group(1).upper()
                if func_name not in inventory[current_package]['functions']:
                    inventory[current_package]['functions'].append(func_name)

    return inventory

def main():
    if not os.path.exists(os.path.dirname(OUTPUT_FILE)):
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    master_inventory = {}

    print(f"Scanning {PLL_DIR}...")
    for filename in os.listdir(PLL_DIR):
        if filename.lower().endswith('.txt') or filename.lower().endswith('.pld'):
            file_path = os.path.join(PLL_DIR, filename)
            print(f"  Parsing {filename}...")
            
            pll_data = parse_pll_file(file_path)
            
            # Key by PLL File Name (Base)
            base_name = os.path.splitext(filename)[0].upper()
            master_inventory[base_name] = {
                'file': filename,
                'packages': pll_data
            }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(master_inventory, f, indent=2)

    print(f"PLL Inventory generated at {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
