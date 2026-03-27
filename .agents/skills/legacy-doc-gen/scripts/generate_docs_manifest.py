#!/usr/bin/env python3
"""
[SKILL_ROOT]/scripts/generate_docs_manifest.py (CLI)
=====================================

Purpose:
    Generates manifest tracking documentation status for in-scope forms vs master sheet.

Layer: Curate / Inventories

Usage Examples:
    python [SKILL_ROOT]/scripts/generate_docs_manifest.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - get_confirmed_ids(): No description.
    - get_in_scope_objects(): No description.
    - check_documentation_status(): No description.
    - check_source_availability(): No description.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import csv
import json
import os
import re
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()
BASE_DIR = PROJECT_ROOT

MASTER_SHEET = BASE_DIR / 'legacy-system' / 'reference-data' / 'collections' / 'jam-mastersheet' / 'JAM-SharePoint-MasterSheet.csv'
OVERVIEWS_DIR = BASE_DIR / 'legacy-system' / 'oracle-forms-overviews'
FORMS_DIR = OVERVIEWS_DIR / 'forms'
REPORTS_DIR = OVERVIEWS_DIR / 'reports'
ARCHIVED_DIR = OVERVIEWS_DIR / 'archived'
XML_MARKDOWN_DIR = BASE_DIR / 'legacy-system' / 'oracle-forms-markdown' / 'XML'
MANIFEST_PATH = BASE_DIR / 'legacy-system' / 'reference-data' / 'oracle_forms_manifest.json'

IN_SCOPE_IDS_FILE = BASE_DIR / 'archive' / 'scripts' / 'documentation' / 'in_scope_ids.txt'

def get_confirmed_ids():
    if not IN_SCOPE_IDS_FILE.exists():
        return []
    with open(IN_SCOPE_IDS_FILE, 'r') as f:
        return [line.strip().upper() for line in f if line.strip()]

def get_in_scope_objects():
    confirmed_ids = get_confirmed_ids()
    objects = []
    
    # Map for quick lookup from master sheet
    master_data = {}
    if MASTER_SHEET.exists():
        with open(MASTER_SHEET, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                obj_id = row.get('Oracle ID', '').strip().upper()
                if obj_id:
                    master_data[obj_id] = {
                        'ObjectName': row.get('Object Name', '').strip(),
                        'Application': row.get('App', '').strip(),
                        'Type': row.get('Type', '').strip()
                    }

    for obj_id in confirmed_ids:
        data = master_data.get(obj_id, {'ObjectName': 'Unknown', 'Application': 'Unknown', 'Type': 'Unknown'})
        # Special case for PCR reports which are forms in some contexts but reports in others
        if (REPORTS_DIR / f"{obj_id}-Overview.md").exists():
            doc_type = 'REPORT'
        elif obj_id.startswith('PCR') or 'R' in obj_id[2:4]: # Heuristic
            doc_type = 'REPORT'
        else:
            doc_type = data.get('Type', 'FORM')

        objects.append({
            'ObjectID': obj_id,
            'ObjectName': data['ObjectName'],
            'Application': data['Application'],
            'Type': doc_type
        })
    return objects

def check_documentation_status(obj_id, obj_type):
    filename = f"{obj_id}-Overview.md"
    
    # Check forms, reports, or archived
    paths_to_check = [
        FORMS_DIR / filename,
        REPORTS_DIR / filename,
        ARCHIVED_DIR / filename
    ]
    
    found_path = None
    for p in paths_to_check:
        if p.exists():
            found_path = p
            break
            
    if not found_path:
        return "Missing", None
    
    with open(found_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Heuristic: if it has "STUB" or "TBD" flags, it's definitely a stub.
        # Also check length - enriched files are typically > 1000 characters.
        is_stub_content = "STUB" in content.upper() or "TBD" in content.upper()
        if is_stub_content or len(content) < 800:
            return "Stub", found_path
        return "Enriched", found_path

def check_source_availability(obj_id):
    # XML Markdown conversion check
    # Many are named lowercase in the XML directory
    xml_md_file = XML_MARKDOWN_DIR / f"{obj_id.lower()}-FormModule.md"
    return xml_md_file.exists()

def main():
    print("Generating Oracle Forms Documentation Manifest...")
    in_scope = get_in_scope_objects()
    manifest = []
    
    for obj in in_scope:
        status, path = check_documentation_status(obj['ObjectID'], obj['Type'])
        source_avail = check_source_availability(obj['ObjectID'])
        
        manifest.append({
            'ObjectID': obj['ObjectID'],
            'ObjectName': obj['ObjectName'],
            'Application': obj['Application'],
            'Type': obj['Type'],
            'DocumentationStatus': status,
            'SourceAvailable': source_avail,
            'RelativePath': os.path.relpath(path, BASE_DIR) if path else None
        })
    
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Manifest generated with {len(manifest)} objects at {MANIFEST_PATH}")
    
    # Summary
    stats = {
        'Total': len(manifest),
        'Enriched': len([x for x in manifest if x['DocumentationStatus'] == 'Enriched']),
        'Stub': len([x for x in manifest if x['DocumentationStatus'] == 'Stub']),
        'Missing': len([x for x in manifest if x['DocumentationStatus'] == 'Missing']),
        'SourceAvailable': len([x for x in manifest if x['SourceAvailable']])
    }
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
