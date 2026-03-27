#!/usr/bin/env python3
"""
generate_applications_inventory.py (CLI)
=====================================

Purpose:
    Scans applications directory for Overview markdowns and extracts metadata.

Layer: Curate / Inventories

Usage Examples:
    python plugins/inventory-manager/scripts/generate_applications_inventory.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - extract_metadata_from_file(): Extract metadata from the markdown file content.
    - scan_applications(): Scan applications directory and build inventory.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import json
import re

# Paths
CWD = os.getcwd()
APPLICATIONS_DIR = os.path.join(CWD, 'legacy-system', 'applications')
OUTPUT_PATH = os.path.join(CWD, 'legacy-system', 'reference-data', 'applications_inventory.json')

def extract_metadata_from_file(filepath):
    """Extract metadata from the markdown file content."""
    metadata = {
        'name': None,
        'mainMenu': None,
        'primaryUsers': None
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract title from H1
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['name'] = title_match.group(1).strip()
            
        # Extract Main Menu Form ID (e.g., FORM0000)
        menu_match = re.search(r'\*\*Main Menu Form\*\*[:\s]+\[?([A-Z]{3,4}M\d{4})', content)
        if menu_match:
            metadata['mainMenu'] = menu_match.group(1)
            
        # Extract Primary Users
        users_match = re.search(r'\*\*Primary Users\*\*[:\s]+(.+?)(?:\n|\*\*)', content)
        if users_match:
            metadata['primaryUsers'] = users_match.group(1).strip()
            
    except Exception as e:
        print(f"Warning: Could not parse {filepath}: {e}")
        
    return metadata

def scan_applications():
    """Scan applications directory and build inventory."""
    inventory = {}
    
    if not os.path.exists(APPLICATIONS_DIR):
        print(f"Warning: Applications directory not found: {APPLICATIONS_DIR}")
        return inventory
        
    for filename in os.listdir(APPLICATIONS_DIR):
        if filename.endswith('.md') and 'Overview' in filename:
            # Extract Application Code (e.g., AppFour from AppFour-Application-Overview.md)
            app_code_match = re.match(r'^([A-Z]{2,4})-Application', filename)
            if app_code_match:
                app_code = app_code_match.group(1)
            else:
                app_code = os.path.splitext(filename)[0].upper()
                
            filepath = os.path.join(APPLICATIONS_DIR, filename)
            metadata = extract_metadata_from_file(filepath)
            
            inventory[app_code] = {
                'type': 'APPLICATION',
                'file': filename,
                'name': metadata.get('name') or app_code,
                'mainMenu': metadata.get('mainMenu'),
                'primaryUsers': metadata.get('primaryUsers'),
                'overviewPath': f"legacy-system/applications/{filename}"
            }
            
    return inventory

def main():
    print("Generating Applications Inventory...")
    
    inventory = scan_applications()
    print(f"Found {len(inventory)} applications.")
    
    # Sort by ID
    sorted_inventory = dict(sorted(inventory.items()))
    
    # Write output
    output_dir = os.path.dirname(OUTPUT_PATH)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(sorted_inventory, f, indent=2)
        
    print(f"Applications Inventory generated at {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
