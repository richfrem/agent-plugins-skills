#!/usr/bin/env python3
"""
button_inventory_generator.py (CLI)
=====================================

Purpose:
    Generates dashboard button groupings for React.

Layer: Curate / Inventories

Usage Examples:
    python plugins/inventory-manager/scripts/button_inventory_generator.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - generate_button_configs(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import sys
import csv
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Setup Path Resolution
current_dir = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in current_dir.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

project_root = _find_project_root()
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from tools.investigate.utils.path_resolver import resolve_path

# Source CSV
CSV_PATH = resolve_path("legacy-system/reference-data/collections/menuconfig/MainModuleButtonVisibilityRulesByRole.csv")
# Output Dir
OUTPUT_DIR = resolve_path("sandbox/ui/public/config")

def generate_button_configs():
    # Structure: configs[form_id][button_id] = { label, action, visible_roles, enabled_roles }
    configs = defaultdict(lambda: defaultdict(lambda: {
        "label": "", 
        "action": "", 
        "visible_roles": set(), 
        "enabled_roles": set(),
        "app_cd": ""
    }))

    print(f"Reading {CSV_PATH}...")
    
    try:
        with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                app_cd = row.get('PROJECT_CD', 'UNK').strip()
                parent_id = row.get('PARENT OBJECT ID', '').strip()
                role = row.get('ROLE', '').strip()
                child_id = row.get('CHILD OBJECT ID', '').strip()
                item_name = row.get('CHILD OBJECT NAME', '').strip() # Using Child Object Name as label
                
                # Check flags
                display_yn = row.get('DISPLAY_YN', 'N').upper()
                enabled_yn = row.get('ENABLED_YN', 'N').upper()
                
                if not parent_id or not child_id:
                    continue

                # Get/Create Button Entry
                btn = configs[parent_id][child_id]
                btn["label"] = item_name
                btn["action"] = child_id
                btn["app_cd"] = app_cd

                # Add Roles
                if display_yn == 'Y':
                    btn["visible_roles"].add(role)
                
                if enabled_yn == 'Y':
                    btn["enabled_roles"].add(role)

    except FileNotFoundError:
        print(f"Error: Could not find {CSV_PATH}")
        return

    # Generate JSON attributes
    print(f"Generating configs for {len(configs)} forms...")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for form_id, buttons in configs.items():
        # Determine App Code (take from first button)
        first_btn = next(iter(buttons.values()))
        app_cd = first_btn["app_cd"]

        # Build Items List
        items_list = []
        for btn_id, data in buttons.items():
            items_list.append({
                "id": btn_id,
                "label": data["label"],
                "action": data["action"],
                "roles": {
                    "visible": sorted(list(data["visible_roles"])),
                    "enabled": sorted(list(data["enabled_roles"]))
                }
            })
        
        # Sort items by label
        items_list.sort(key=lambda x: x["label"])

        # Create Config Structure
        config = {
            "meta": {
                "formId": form_id,
                "application": app_cd,
                "generatedAt": datetime.now().isoformat()
            },
            "groups": [
                {
                    "id": "MAIN",
                    "label": "Main Options",
                    "items": items_list
                }
            ]
        }

        # Write to file
        filename = f"{form_id}_buttons.json"
        
        out_path = os.path.join(OUTPUT_DIR, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
            
        print(f"  -> Generated {out_path}")

if __name__ == "__main__":
    generate_button_configs()
