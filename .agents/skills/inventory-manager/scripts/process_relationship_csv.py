#!/usr/bin/env python3
"""
process_relationship_csv.py (CLI)
=====================================

Purpose:
    Processes CSV files containing form relationships.

Layer: Curate / Inventories

Usage Examples:
    python plugins/inventory-manager/scripts/process_relationship_csv.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input:
    - `legacy-system/reference-data/collections/code-detected/form_relationships.csv` (Mapped Source/Target pairs)
    - `legacy-system/reference-data/master_object_collection.json` (Used for type resolution)

Output:
    - `legacy-system/reference-data/inventories/relationship_graph.json` (JSON graph consumed by `generate_dependency_map.py`)

Key Functions:
    - infer_type(): Resolve object type using direct lookup or pattern matching (Generic).
    - process_csv(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import csv
import json
import os
import re

# Paths
CWD = os.getcwd()
# Default to the output of our new Python miner
CSV_PATH = os.path.join(CWD, 'legacy-system', 'reference-data', 'collections', 'code-detected', 'form_relationships.csv')
OUTPUT_JSON_PATH = os.path.join(CWD, 'legacy-system', 'reference-data', 'inventories', 'relationship_graph.json')
MASTER_COLLECTION_PATH = os.path.join(CWD, 'legacy-system', 'reference-data', 'master_object_collection.json')

# Load the Master Collection for type resolution
MASTER_COLLECTION = {}

if os.path.exists(MASTER_COLLECTION_PATH):
    try:
        with open(MASTER_COLLECTION_PATH, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
            # Support both new nested format and legacy flat format
            MASTER_COLLECTION = full_data.get('objects', full_data)
        print(f"Loaded {len(MASTER_COLLECTION)} objects from Master Collection.")
    except Exception as e:
        print(f"Warning: Could not load Master Collection: {e}")

# Minimum heuristic patterns for prefix matching if inventory lookup fails
HEURISTIC_PATTERNS = [
    (r'^[A-Z]{3,4}R\d+', 'REPORT'),
    (r'^[A-Z]{3,4}[FME]\d+', 'FORM'),
    (r'^[A-Z]{3,}LIB$', 'PLL')
]

def infer_type(name):
    """Resolve object type using direct lookup or pattern matching (Generic)."""
    name_upper = name.upper()
    
    # 1. Direct Lookup
    if name_upper in MASTER_COLLECTION:
        return MASTER_COLLECTION[name_upper].get('type', 'UNKNOWN').upper()
    
    # 2. Key-based Heuristic (Handling common suffixes like _FMB, _PLL)
    # Strip common suffixes and double check inventory
    base_name = re.sub(r'_(FMB|MMB|PLL|XML|RDF|TXT|PLD)$', '', name_upper)
    if base_name in MASTER_COLLECTION:
        return MASTER_COLLECTION[base_name].get('type', 'UNKNOWN').upper()

    # 3. Pattern-based Fallback
    for pattern, obj_type in HEURISTIC_PATTERNS:
        if re.match(pattern, name_upper):
            return obj_type
        
    return 'UNKNOWN'

def process_csv():
    print(f"Reading CSV: {CSV_PATH}")
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        return

    relationships = []
    
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # Handle various header formats (Source/Target, Parent/Child, etc.)
                parent = (row.get('Source') or row.get('PARENT') or row.get('parent') or '').strip().upper()
                child = (row.get('Target') or row.get('CHILD') or row.get('child') or '').strip().upper()
                
                if parent and child:
                    relationships.append({
                        "Source": parent,
                        "Target": child,
                        "SourceType": infer_type(parent),
                        "TargetType": infer_type(child),
                        "SourceOrigin": "Mined-From-Code" # Descriptive Origin
                    })
                    count += 1
            
        print(f"Processed {count} relationships.")
        
        # Write JSON
        os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
        with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(relationships, f, indent=2)
            
        print(f"JSON Output generated at: {OUTPUT_JSON_PATH}")

    except Exception as e:
        print(f"Error processing CSV: {e}")

if __name__ == "__main__":
    process_csv()
