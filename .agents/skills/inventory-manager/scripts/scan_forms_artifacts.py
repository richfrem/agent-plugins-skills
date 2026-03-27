#!/usr/bin/env python3
"""
scan_forms_artifacts.py (CLI)
=====================================

Purpose:
    Scans the XML directory for specific Oracle Forms artifacts (FMB, MMB, OLB)
    and generates distinct JSON inventories for each type. 
    This replaces disparate legacy scripts with a single unified scanner.

Layer: Curate / Inventories

Usage Examples:
    python plugins/inventory-manager/scripts/scan_forms_artifacts.py

Output:
    - legacy-system/reference-data/inventories/forms_inventory.json
    - legacy-system/reference-data/inventories/menus_inventory.json
    - legacy-system/reference-data/inventories/olbs_inventory.json

Key Functions:
    - scan_directory(): Generic scanner for XML files based on suffix.
    - extract_metadata(): Reads minimal metadata from XML (Name, Title).
"""

import os
import json
import re
import glob
from pathlib import Path

# Paths are relative to project root — run this script from the project root directory.
XML_DIR = Path('./legacy-system/oracle-forms/XML')
OUT_DIR = Path('./legacy-system/reference-data/inventories')

# File Suffixes
SUFFIX_MAP = {
    'FORM':  ('_fmb.xml', 'forms_inventory.json'),
    'MENU':  ('_mmb.xml', 'menus_inventory.json'),
    'OLB':   ('_olb.xml', 'olb_inventory.json')
}

import xml.etree.ElementTree as ET

def extract_metadata(xml_path: Path, artifact_type: str) -> dict:
    """Extracts metadata using XML parser for accuracy."""
    metadata = {
        'id': None,
        'title': None, # Form Title
        'path': str(xml_path).replace('\\', '/'),
        'filename': xml_path.name,
        'size_bytes': xml_path.stat().st_size
    }
    
    try:
        # iterparse is memory efficient; we only need the root element
        for event, elem in ET.iterparse(str(xml_path), events=('start',)):
            # Handle potential namespaces like {http://xmlns.oracle.com/Forms}FormModule
            tag_clean = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            target_tags = {
                'FORM': 'FormModule',
                'MENU': 'MenuModule',
                'OLB': 'ObjectLibrary'
            }
            
            expected = target_tags.get(artifact_type, 'Module')
            
            if tag_clean == expected:
                metadata['id'] = elem.get('Name')
                metadata['title'] = elem.get('Title')
                
                # Comprehensive Metadata Extraction
                metadata['console_window'] = elem.get('ConsoleWindow')
                metadata['menu_module'] = elem.get('MenuModule')
                metadata['parent_module'] = elem.get('ParentModule')
                metadata['parent_filename'] = elem.get('ParentFilename')
                metadata['parent_type'] = elem.get('ParentType')
                metadata['validation_unit'] = elem.get('ValidationUnit')
                metadata['interaction_mode'] = elem.get('InteractionMode')
                metadata['coordinate_system'] = elem.get('CoordinateSystem')
                
                # Dimensions
                w = elem.get('Width')
                h = elem.get('Height')
                if w and w.isdigit(): metadata['width'] = int(w)
                if h and h.isdigit(): metadata['height'] = int(h)

                # Cleanup and break as we found the root
                elem.clear()
                break
                
    except Exception as e:
        print(f"Error parsing {xml_path.name}: {e}")
    
    # Fallback to filename if XML parsing failed to yield ID
    if not metadata['id']:
         # e.g. FORM001_fmb.xml -> FORM001
         clean_name = xml_path.name.lower().replace(SUFFIX_MAP[artifact_type][0], '')
         metadata['id'] = clean_name.upper()

    return metadata

def scan_artifacts():
    print(f"Scanning {XML_DIR}...")
    
    if not XML_DIR.exists():
        print(f"Error: XML Directory not found: {XML_DIR}")
        return

    # Ensure output exists
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for art_type, (suffix, out_file) in SUFFIX_MAP.items():
        print(f"  Processing {art_type} ({suffix})...")
        inventory = {}
        
        # Glob for *suffix
        # Note: glob is case-sensitive on Linux, standard on Windows.
        # We assume files are generated with standard suffixes (_fmb.xml).
        files = list(XML_DIR.glob(f"*{suffix}"))
        
        if not files:
             # Try case-insensitive fallback logic if needed, but glob is simple
             pass
             
        for f in files:
            meta = extract_metadata(f, art_type)
            obj_id = meta['id']
            if obj_id:
                inventory[obj_id] = meta
        
        # Write JSON
        out_path = OUT_DIR / out_file
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(inventory, f, indent=2)
            
        print(f"    -> Generated {out_path.name} ({len(inventory)} items)")

if __name__ == "__main__":
    scan_artifacts()
