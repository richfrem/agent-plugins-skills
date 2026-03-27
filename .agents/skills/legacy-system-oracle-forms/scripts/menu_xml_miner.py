#!/usr/bin/env python3
"""
menu_xml_miner.py (CLI)
=====================================

Purpose:
    Parses Oracle Forms Menu XML files to extract definitions, items, and hierarchy for static analysis.

Layer: Curate / Miners

Usage Examples:
    python plugins/legacy-system-oracle-forms/scripts/menu_xml_miner.py --help
    python plugins/legacy-system-oracle-forms/scripts/menu_xml_miner.py --json
    python plugins/legacy-system-oracle-forms/scripts/menu_xml_miner.py --json > menus.json

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - clean_label(): No description.
    - parse_menu_module(): No description.
    - build_hierarchy(): Reverse map: SubMenuName -> ParentMenuName
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import json
import glob
import xml.etree.ElementTree as ET
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
XML_DIR = PROJECT_ROOT / "legacy-system" / "oracle-forms" / "XML"
OUTPUT_JSON = PROJECT_ROOT / "legacy-system" / "reference-data" / "inventories" / "menu_static_definitions.json"

def clean_label(label):
    if not label:
        return ""
    # Remove accelerator ampersands (e.g. "&File" -> "File")
    return label.replace("&", "")

def parse_menu_module(file_path):
    try:
        # Calculate relative path
        try:
             rel_path = os.path.relpath(str(file_path), str(PROJECT_ROOT))
        except ValueError:
             rel_path = str(file_path)

        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Handle namespaces if present (Oracle Forms XML usually has them)
        # But often we can just search by tag name ignoring namespace if we're careful,
        # or handle the namespace map.
        # Let's try raw tag names first, or strip namespaces.
        
        ns = {'f': 'http://xmlns.oracle.com/Forms'}
        
        menu_module = root.find('f:MenuModule', ns)
        if menu_module is None:
            # Try without namespace if that fails (some old exports might differ)
            menu_module = root.find('MenuModule')
            
        if menu_module is None:
            print(f"⚠️  No MenuModule found in {file_path.name}")
            return None

        module_name = menu_module.get('Name')
        main_menu_name = menu_module.get('MainMenu')
        
        menus = {}
        
        # Find all Menu elements
        for menu in menu_module.findall('f:Menu', ns):
            menu_name = menu.get('Name')
            items = []
            
            for item in menu.findall('f:MenuItem', ns):
                item_name = item.get('Name')
                label = item.get('Label')
                sub_menu = item.get('SubMenuName')
                command_type = item.get('CommandType')
                # Some items might not have a label (separators)
                item_type = item.get('MenuItemType') # Plain, Separator, Magic
                
                items.append({
                    "name": item_name,
                    "label": clean_label(label),
                    "subMenu": sub_menu,
                    "type": item_type,
                    "commandType": command_type
                })
            
            menus[menu_name] = items
            
        return {
            "moduleName": module_name,
            "filePath": rel_path,
            "mainMenu": main_menu_name,
            "menus": menus
        }

    except Exception as e:
        print(f"❌ Error parsing {file_path.name}: {e}")
        return None

def build_hierarchy(menus_dict):
    """
    Reverse map: SubMenuName -> ParentMenuName
    """
    parent_map = {}
    
    for menu_name, items in menus_dict.items():
        for item in items:
            if item.get('subMenu'):
                sub = item.get('subMenu')
                # We assume a submenu has primarily one parent in a standard hierarchy,
                # though technically reused submenus are possible.
                if sub not in parent_map:
                    parent_map[sub] = []
                parent_map[sub].append(menu_name)
                
    return parent_map

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Menu XML Static Miner")
    parser.add_argument("--json", action="store_true", help="Output raw JSON to stdout (suppress logs)")
    args = parser.parse_args()

    if not args.json:
        print(f"🔍 Scanning {XML_DIR} for *_mmb.xml...")
    
    files = list(XML_DIR.glob("*_mmb.xml"))
    if not files:
        if not args.json:
             print("❌ No menu XML files found.")
        return

    full_definitions = {}
    
    # We primarily care about EXAMPLE_LIB as it seems to be the core,
    # but we'll parse all.
    
    for xml_file in files:
        if not args.json:
            print(f"   Sidebar: Parsing {xml_file.name}...")
        result = parse_menu_module(xml_file)
        if result:
            full_definitions[result['moduleName']] = result

    # Flatten logic to create a global lookup
    # Because MenuConfig CSV doesn't specify which Library the menu comes from (it implies app context),
    # we might need to merge them or check order. EXAMPLE_LIB is likely the base.
    
    # Let's create a "merged" lookup of Menu -> Items
    # If duplicates exist (e.g. MAIN_MENU in multiple files), EXAMPLE_LIB takes precedence?
    
    merged_menus = {}
    # Sort so EXAMPLE_LIB is processed last? Or first?
    # Let's just process all and see.
    
    ordered_modules = ['EXAMPLE_LIB2', 'AGNOMENU', 'POSMENU', 'EXAMPLE_LIB'] # EXAMPLE_LIB last to override?
    
    for mod_name in ordered_modules:
        if mod_name in full_definitions:
            data = full_definitions[mod_name]
            for menu_name, items in data['menus'].items():
                merged_menus[menu_name] = items

    # Build hierarchy on merged menus
    parent_map = build_hierarchy(merged_menus)
    
    output_data = {
        "modules": full_definitions,
        "mergedMenus": merged_menus,
        "parentMap": parent_map
    }
    
    if args.json:
        print(json.dumps(output_data, indent=2))
        return

    os.makedirs(OUTPUT_JSON.parent, exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
        
    print(f"✅ Saved static menu definitions to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
