#!/usr/bin/env python3
"""
[SKILL_ROOT]/scripts/generate_missing_overviews.py (CLI)
=====================================

Purpose:
    Creates placeholder overviews from templates.

Layer: Curate / Documentation

Usage Examples:
    python [SKILL_ROOT]/scripts/generate_missing_overviews.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - load_template(): No description.
    - load_json(): No description.
    - generate_reports(): No description.
    - generate_libraries(): No description.
    - generate_menus(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import json
import shutil
from datetime import datetime
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

TEMPLATES_DIR = SCRIPT_DIR.parent / 'assets' / 'templates'
INVENTORIES_DIR = BASE_DIR / 'legacy-system' / 'reference-data' / 'inventories'
OVERVIEWS_DIR = BASE_DIR / 'legacy-system' / 'oracle-forms-overviews'

# Templates
REPORT_TEMPLATE_PATH = TEMPLATES_DIR / 'report-overview-template.md'
LIBRARY_TEMPLATE_PATH = TEMPLATES_DIR / 'library-overview-template.md'
MENU_TEMPLATE_PATH = TEMPLATES_DIR / 'menu-overview-template.md'

# Output Directories
REPORTS_DIR = OVERVIEWS_DIR / 'reports'
LIBRARIES_DIR = OVERVIEWS_DIR / 'libraries'
MENUS_DIR = OVERVIEWS_DIR / 'menus'

# Ensure directories exist
for d in [REPORTS_DIR, LIBRARIES_DIR, MENUS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def load_template(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_reports():
    print("Generating Report Overviews...")
    template = load_template(REPORT_TEMPLATE_PATH)
    inventory = load_json(INVENTORIES_DIR / 'reports_inventory.json')
    
    count = 0
    for report_id, data in inventory.items():
        # Determine target file
        filename = f"{report_id}-Report-Overview.md"
        target_path = REPORTS_DIR / filename
        
        if target_path.exists():
            continue
            
        print(f"  Creating {filename}")
        
        # Prepare template params
        # Use replace() instead of format() to avoid issues with braces in description text
        content = template
        content = content.replace('{REPORT_NAME}', report_id)
        content = content.replace('{REPORT_ID}', report_id)
        
        source_file = data.get('SourceFile')
        filename_val = source_file.replace('.xml', '').lower() if source_file else 'tbd'
        content = content.replace('{filename}', filename_val)
        
        content = content.replace('{APPLICATION}', 'TBD')
        content = content.replace('{DATE}', datetime.now().strftime('%Y-%m-%d'))
        content = content.replace('{TABLE_NAME}', 'TBD')
        content = content.replace('{PURPOSE}', 'TBD')
        content = content.replace('{JOIN}', 'TBD')
        content = content.replace('{PARAM_NAME}', 'TBD')
        content = content.replace('{TYPE}', 'TBD')
        content = content.replace('{DESCRIPTION}', 'TBD')
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1
    print(f"Created {count} report placeholders.")

def generate_libraries():
    print("\nGenerating Library Overviews...")
    template = load_template(LIBRARY_TEMPLATE_PATH)
    inventory = load_json(INVENTORIES_DIR / 'pll_inventory.json')
    
    count = 0
    for lib_id, data in inventory.items():
        # Determine target file
        filename = f"{lib_id}-Library-Overview.md"
        target_path = LIBRARIES_DIR / filename
        
        if target_path.exists():
            continue
            
        print(f"  Creating {filename}")
        
        # Prepare template params
        # Use replace() instead of format()
        content = template
        content = content.replace('{LIBRARY_NAME}', lib_id)
        content = content.replace('{LIBRARY_ID}', lib_id)
        
        source_file = data.get('file')
        filename_val = source_file.replace('.txt', '').lower() if source_file else 'tbd'
        content = content.replace('{filename}', filename_val)
        
        content = content.replace('{DATE}', datetime.now().strftime('%Y-%m-%d'))
        content = content.replace('{UNIT_NAME}', 'TBD')
        content = content.replace('{DESCRIPTION}', 'TBD')
        content = content.replace('{VAR_NAME}', 'TBD')
        content = content.replace('{PURPOSE}', 'TBD')
        content = content.replace('{FORM_NAME}', 'TBD')
        content = content.replace('{USAGE_DESCRIPTION}', 'TBD')
        content = content.replace('{OBJECT_NAME}', 'TBD')
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1
    print(f"Created {count} library placeholders.")

def generate_menus():
    print("\nGenerating Menu Overviews...")
    template = load_template(MENU_TEMPLATE_PATH)
    inventory = load_json(INVENTORIES_DIR / 'menus_inventory.json')
    
    count = 0
    for menu_id, data in inventory.items():
        # Determine target file
        filename = f"{menu_id}-Menu-Overview.md"
        target_path = MENUS_DIR / filename
        
        if target_path.exists():
            continue
            
        print(f"  Creating {filename}")
        
        # Prepare template params
        # Format expects keys: MENU_NAME, MENU_ID, filename, APPLICATION, DATE, MENU_ITEM_1, SUB_ITEM_1, SUB_ITEM_2, MENU_ITEM_2, MENU_ITEM_3, ITEM_NAME, LABEL, TARGET, CONDITION, ROLE_NAME, ITEMS_LIST, MAIN_FORM, LIBRARIES
        # Some of these are for the structure diagram which might raise KeyError if not provided
        # I need to use replace() or safe_substitute if using string.Template, but here I am using format()
        # I must provide all keys or format() will fail.
        
        # Let's check the template again to see exact placeholders.
        # {MENU_NAME}, {MENU_ID}, {filename}, {APPLICATION}, {DATE}
        # {MENU_ITEM_1}, {SUB_ITEM_1}, {SUB_ITEM_2}, {MENU_ITEM_2}, {MENU_ITEM_3}
        # {ITEM_NAME}, {LABEL}, {TARGET}, {CONDITION}
        # {ROLE_NAME}, {ITEMS_LIST}
        # {MAIN_FORM}, {LIBRARIES}
        
        content = template
        content = content.replace('{MENU_NAME}', menu_id)
        content = content.replace('{MENU_ID}', menu_id)
        
        source_file = data.get('file')
        filename_val = source_file.replace('_mmb.xml', '').lower() if source_file else 'tbd'
        content = content.replace('{filename}', filename_val)
        
        content = content.replace('{APPLICATION}', 'TBD')
        content = content.replace('{DATE}', datetime.now().strftime('%Y-%m-%d'))
        
        # Diagram placeholders
        content = content.replace('{MENU_ITEM_1}', 'File')
        content = content.replace('{SUB_ITEM_1}', 'Exit')
        content = content.replace('{SUB_ITEM_2}', 'Save')
        content = content.replace('{MENU_ITEM_2}', 'Edit')
        content = content.replace('{MENU_ITEM_3}', 'Help')
        
        # Table placeholders
        content = content.replace('{ITEM_NAME}', 'FILE_EXIT')
        content = content.replace('{LABEL}', 'Exit Application')
        content = content.replace('{TARGET}', 'Exit_Form')
        content = content.replace('{CONDITION}', 'Always Enabled')
        content = content.replace('{ROLE_NAME}', 'ALL_USERS')
        content = content.replace('{ITEMS_LIST}', 'Unrestricted')
        
        content = content.replace('{MAIN_FORM}', 'TBD')
        content = content.replace('{LIBRARIES}', 'TBD')
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1
    print(f"Created {count} menu placeholders.")

if __name__ == "__main__":
    generate_reports()
    generate_libraries()
    generate_menus()
