"""
[SKILL_ROOT]/scripts/generate_ui_config.py
===========================================

Purpose:
    Generates TypeScript UI configuration files from MenuConfig data.
    Creates Application Menu files and Form-level Rules files with
    role-based visibility and enablement for UI elements.

Input:
    - Menu Inventory JSON
    - Button Rules CSV
    - Roles Inventory JSON

Output:
    - [PROJECT_ROOT]/sandbox/ui/src/rules/{APP}_Menu.ts
    - [PROJECT_ROOT]/sandbox/ui/src/rules/{FORM}_Rules.ts

Usage:
    python [SKILL_ROOT]/scripts/generate_ui_config.py
"""

import json
import csv
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()
BASE_DIR = PROJECT_ROOT / 'legacy-system'

# Centralized Templates
TEMPLATES_DIR = SCRIPT_DIR.parent / 'assets' / 'templates'
APP_MENU_TEMPLATE_PATH = TEMPLATES_DIR / 'app-menu-template.ts'
FORM_RULES_TEMPLATE_PATH = TEMPLATES_DIR / 'form-rules-template.ts'

INVENTORY_PATH = BASE_DIR / 'reference-data' / 'inventories' / 'menu_inventory.json'
BTN_CSV_PATH = BASE_DIR / 'reference-data' / 'collections' / 'menuconfig' / 'MainModuleButtonVisibilityRulesByRole.csv'
OUTPUT_DIR = PROJECT_ROOT / 'sandbox' / 'ui' / 'src' / 'rules'
ROLES_INVENTORY_PATH = BASE_DIR / 'reference-data' / 'inventories' / 'roles_inventory.json'

def generate_unified_rules():
    # Load Valid Roles
    valid_roles = set()
    try:
        with open(ROLES_INVENTORY_PATH, 'r', encoding='utf-8') as f:
            roles_data = json.load(f)
            # Assuming structure is list of role objects or dict of roles
            # Let's handle generic list of strings or objects with 'role' key
            # Based on file naming 'roles_inventory', likely JSON array of objects
            # Or if it's the one I viewed before, it might have structure.
            # I'll create a robust loader.
            if isinstance(roles_data, list):
                for r in roles_data:
                    if isinstance(r, str): valid_roles.add(r)
                    elif isinstance(r, dict) and 'role' in r: valid_roles.add(r['role'])
            elif isinstance(roles_data, dict):
                 # If dict, maybe keys are roles
                 valid_roles.update(roles_data.keys())
    except Exception as e:
        print(f"Warning: Could not load roles inventory: {e}")

    # Helper: Convert empty lists to wildcards (Default Open) AND Filter Invalid Roles
    def normalize_roles(roles_list):
        if not roles_list or len(roles_list) == 0:
            return ["*"]
        
        # Filter Logic: Keep ONLY valid roles (or wildcards if they slip in)
        # If valid_roles is empty (load failed), we don't filter to avoid breaking everything.
        if not valid_roles:
            return sorted(list(set(roles_list)))

        filtered = [r for r in roles_list if r in valid_roles or r == '*' or r == 'ALL']
        
        # If filtering removed all roles, does it mean "No Access"? 
        # Or was it a deprecated feature? 
        # If input list was not empty but output is empty -> No Access (empty list).
        return sorted(list(set(filtered)))
    # app_menus[PROJECT_CODE] = [list of sections]
    app_menus = {} 
    print(f"Reading Menu Inventory from {INVENTORY_PATH}...")
    try:
        with open(INVENTORY_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Structure: { applications: { CODE: { sections: [] } } }
            for app_code, content in data.get("applications", {}).items():
                sections = content.get("sections", [])
                
                # Recursive normalizer and flattener for menu items
                def recursive_normalize(items):
                    normalized_items = []
                    for item in items:
                        new_item = {
                            "id": item.get("id", ""),
                            "label": item.get("label", ""),
                        }
                        
                        # Flatten roles
                        roles = item.get("roles", {})
                        new_item["visible"] = normalize_roles(roles.get("visible", []))
                        new_item["enabled"] = normalize_roles(roles.get("enabled", []))

                        # Optional properties
                        if "action" in item: new_item["action"] = item["action"]
                        if "itemType" in item: new_item["description"] = item["itemType"] # Use description for type? Or add type to interface? 
                        
                        # Recurse for submenus
                        if "items" in item:
                            new_item["items"] = recursive_normalize(item["items"])
                            
                        normalized_items.append(new_item)
                    return normalized_items

                # Normalize all sections
                final_sections = []
                for section in sections:
                    new_section = {
                        "id": section.get("id"),
                        "label": section.get("name") or section.get("label"),
                        "items": []
                    }
                    if "items" in section:
                        new_section["items"] = recursive_normalize(section["items"])
                    final_sections.append(new_section)

                app_menus[app_code] = final_sections
    except Exception as e:
        print(f"Error reading inventory: {e}")

    # 2. Load Button Rules (Form Level - Canvas)
    # form_elements[form_id][element_id] = rule
    form_elements = defaultdict(lambda: defaultdict(lambda: {"visible": set(), "enabled": set(), "label": ""}))
    form_meta = defaultdict(lambda: {"title": "Main Menu", "app": "AppFour"})

    print(f"Reading Button Rules from {BTN_CSV_PATH}...")
    try:
        with open(BTN_CSV_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                form_id = row.get('PARENT OBJECT ID', '').strip()
                child_id = row.get('CHILD OBJECT ID', '').strip()
                name = row.get('CHILD OBJECT NAME', '').strip()
                role = row.get('ROLE', '').strip()
                app_cd = row.get('PROJECT_CD', 'AppFour').strip()
                
                # Check flags
                display = row.get('DISPLAY_YN', 'N').upper()
                enabled = row.get('ENABLED_YN', 'N').upper()

                if not form_id or not child_id: continue

                form_meta[form_id]["app"] = app_cd
                rule = form_elements[form_id][child_id]
                rule["label"] = name
                
                if display == 'Y': rule["visible"].add(role)
                if enabled == 'Y': rule["enabled"].add(role)
    except FileNotFoundError:
        print(f"Error: {BTN_CSV_PATH} not found")
        return
       # ---------------------------------------------------------
    # PART 3: Generate Application Menu Files
    # ---------------------------------------------------------
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    known_apps = ["AppThree", "AppFour", "AppFive", "AppOne", "AppTwo"]
    
    # Pre-calculate normalized menus for apps
    # app_code -> list of sections (normalized)
    normalized_app_menus = {}

    for app_code in known_apps:
        # Get raw sections from inventory (or empty)
        sections = app_menus.get(app_code, [])
        # Fallback for JUS->AppFour mapping if needed, or JUS shared lib
        if not sections and app_code == "AppFour": 
             sections = app_menus.get("JUS", [])

        # Recursive helper inside the loop context? Or use the one from Part 1?
        # We need the one from Part 1. Let's make sure 'recursive_normalize' is available or duplicate logic cleanly.
        # Actually, let's refine the structure.
        
        # Helper logic reused:
        def recursive_normalize(items):
            normalized_items = []
            for item in items:
                new_item = {
                    "id": item.get("id", ""),
                    "label": item.get("label", ""),
                }
                roles = item.get("roles", {})
                new_item["visible"] = normalize_roles(roles.get("visible", []))
                new_item["enabled"] = normalize_roles(roles.get("enabled", []))
                
                if "action" in item: new_item["action"] = item["action"]
                if "itemType" in item: new_item["description"] = item["itemType"]
                if "items" in item: new_item["items"] = recursive_normalize(item["items"])
                normalized_items.append(new_item)
            return normalized_items

        final_sections = []
        for section in sections:
            new_section = {
                "id": section.get("id"),
                "label": section.get("name") or section.get("label"),
                "items": recursive_normalize(section.get("items", []))
            }
            final_sections.append(new_section)
        
        normalized_app_menus[app_code] = final_sections

        # Write App_Menu.ts
        if not APP_MENU_TEMPLATE_PATH.exists():
            print(f"Error: Template not found: {APP_MENU_TEMPLATE_PATH}")
            continue
            
        template = APP_MENU_TEMPLATE_PATH.read_text(encoding='utf-8')
        content = template.replace("{APP_CODE}", app_code).replace("{MENU_JSON}", json.dumps(final_sections, indent=4))
        
        out_path = OUTPUT_DIR / f"{app_code}_Menu.ts"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated App Menu: {out_path}")


    # ---------------------------------------------------------
    # PART 4: Generate All Form Rule Files
    # ---------------------------------------------------------
    # We iterate through form_elements (populated from CSV).
    # This acts as our "Seed List" of forms.
    
    for form_id, elements in form_elements.items():
        app_code = form_meta[form_id]["app"]
        if app_code not in known_apps: app_code = "AppFour" # Default fallback
        
        if not FORM_RULES_TEMPLATE_PATH.exists():
            print(f"Error: Template not found: {FORM_RULES_TEMPLATE_PATH}")
            break
            
        template = FORM_RULES_TEMPLATE_PATH.read_text(encoding='utf-8')
        
        # Build elements JSON block
        elements_lines = []
        sorted_ids = sorted(elements.keys())
        for el_id in sorted_ids:
            data = elements[el_id]
            visible_str = json.dumps(normalize_roles(data["visible"]))
            enabled_str = json.dumps(normalize_roles(data["enabled"]))
            label_safe = json.dumps(data['label'])
            
            elements_lines.append(f"        '{el_id}': {{")
            elements_lines.append(f"            id: '{el_id}',")
            elements_lines.append(f"            label: {label_safe},")
            elements_lines.append(f"            visible: {visible_str},")
            elements_lines.append(f"            enabled: {enabled_str}")
            elements_lines.append(f"        }},")
        
        content = template.replace("{FORM_ID}", form_id).replace("{APP_CODE}", app_code).replace("{ELEMENTS_JSON}", "\n".join(elements_lines))
        
        filename = f"{form_id}_Rules.ts"
        out_path = OUTPUT_DIR / filename
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Generated Form Rules: {out_path}")

if __name__ == "__main__":
    generate_unified_rules()
