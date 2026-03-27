#!/usr/bin/env python3
"""
generate_reports_inventory.py (CLI)
=====================================

Purpose:
    Scans report files to build reports_inventory.json.

Layer: Curate / Inventories

Usage Examples:
    python plugins/inventory-manager/scripts/generate_reports_inventory.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - get_reports_from_overviews(): No description.
    - get_reports_from_source(): No description.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import json

# Paths
CWD = os.getcwd()
REPORTS_OVERVIEWS_DIR = os.path.join(CWD, 'legacy-system', 'oracle-forms-overviews', 'reports')
REPORTS_XML_DIR = os.path.join(CWD, 'legacy-system', 'oracle-forms', 'Reports')
MANIFEST_PATH = os.path.join(CWD, 'legacy-system', 'reference-data', 'inventories', 'reports_inventory.json')

def get_reports_from_overviews():
    reports = {}
    if not os.path.exists(REPORTS_OVERVIEWS_DIR):
        print(f"Warning: Overviews directory not found: {REPORTS_OVERVIEWS_DIR}")
        return reports

    for filename in os.listdir(REPORTS_OVERVIEWS_DIR):
        if filename.endswith('.md'):
            # Filename format: [ID]-Overview.md or similar
            # Extract ID
            if '-' in filename:
                obj_id = filename.split('-')[0].upper()
            else:
                obj_id = os.path.splitext(filename)[0].upper()

            reports[obj_id] = {
                'OverviewFile': filename,
                'SourceFile': None,
                'Status': 'Review Pending' # Default
            }
    return reports

def get_reports_from_source(reports):
    if not os.path.exists(REPORTS_XML_DIR):
        print(f"Warning: Source directory not found: {REPORTS_XML_DIR}")
        return reports

    for filename in os.listdir(REPORTS_XML_DIR):
        if filename.lower().endswith('.xml'):
            # Filename format: [id].xml usually lowercase
            obj_id = os.path.splitext(filename)[0].upper()
            
            if obj_id in reports:
                reports[obj_id]['SourceFile'] = filename
            else:
                # Found report source with no overview
                reports[obj_id] = {
                    'OverviewFile': None,
                    'SourceFile': filename,
                    'Status': 'Missing Documentation'
                }
    return reports

def main():
    print("Generating Reports Inventory...")
    
    # 1. Scan Overviews
    reports = get_reports_from_overviews()
    print(f"Found {len(reports)} reports with overviews.")
    
    # 2. Scan Source
    reports = get_reports_from_source(reports)
    print(f"Total reports found (Source + Overview): {len(reports)}")
    
    # 3. Output
    # Convert dict to list or keep as dict? User asked for "inventory like this [manifest/roles]"
    # Roles is Dict: "Key": { ... }
    # Manifest is List: [ { ... } ]
    # Let's use Dict keyed by ID for O(1) lookups in enrichment
    
    # Sort by ID
    sorted_reports = dict(sorted(reports.items()))
    
    directory = os.path.dirname(MANIFEST_PATH)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(sorted_reports, f, indent=2)
        
    print(f"Reports Inventory generated at {MANIFEST_PATH}")

if __name__ == "__main__":
    main()
