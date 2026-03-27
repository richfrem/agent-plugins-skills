
import json
import os
from pathlib import Path

# valid_form_ids.py
# Purpose: Validates Form/Report IDs against Master Object Collection.

# Project Root - use CWD (must be run from project root)
project_root = Path.cwd()

# Path to Master Collection
MASTER_COLLECTION_PATH = project_root / "legacy-system/reference-data/master_object_collection.json"

valid_form_ids = set()
valid_source_ids = set() # Parents: Form, Report, Menu, OLB, PLL
inventory_loaded = False

def load_inventory():
    global valid_form_ids, valid_source_ids, inventory_loaded
    if inventory_loaded:
        return

    if not MASTER_COLLECTION_PATH.exists():
        print(f"Error: Master Object Collection not found at {MASTER_COLLECTION_PATH}")
        return

    try:
        with open(MASTER_COLLECTION_PATH, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
            
            # Master Collection has "objects" key containing the actual inventory
            objects_map = full_data.get('objects', {})
            
            for obj_id, metadata in objects_map.items():
                # Handle case sensitivity of 'type' key (usually lowercase 'type')
                obj_type = metadata.get('type', metadata.get('Type', '')).upper()
                obj_id_upper = obj_id.upper()
                
                # Filter for Valid Sources (Parents)
                # We analyze Forms, Reports, Menus, OLBs, PLLs for dependencies
                # Included LIBRARY alias just in case
                if obj_type in ['FORM', 'REPORT', 'MENU', 'OLB', 'PLL', 'LIBRARY']:
                     valid_source_ids.add(obj_id_upper)
                
                # Filter for Valid Targets (Children)
                # Strictly Forms (the 76 valid IDs)
                if obj_type == 'FORM':
                    valid_form_ids.add(obj_id_upper)
                    # print(f"  DEBUG: Added valid target FORM: {obj_id_upper}")
                    
    except Exception as e:
        print(f"Error loading master_object_collection.json: {e}")
    
    inventory_loaded = True

def is_valid_target_id(child_id):
    """
    Checks if the child_id is a valid FORM ID (Strict Target).
    """
    if not child_id:
        return False
    if not inventory_loaded:
        load_inventory()
    
    return child_id.upper() in valid_form_ids

def is_valid_source_id(parent_id):
    """
    Checks if the parent_id is a valid Object ID suitable for source scanning.
    """
    if not parent_id:
        return False
    if not inventory_loaded:
        load_inventory()
        
    return parent_id.upper() in valid_source_ids

# Alias
is_valid_id = is_valid_target_id

if __name__ == "__main__":
    load_inventory()
    print(f"Valid Source IDs: {len(valid_source_ids)}")
    print(f"Valid Target IDs (Forms): {len(valid_form_ids)}")
