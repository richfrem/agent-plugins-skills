#!/usr/bin/env python3
"""
MMB Structure Extractor - Layer 1 (Foundation)
===============================================

Purpose:
    Parses the Oracle Forms Menu Module Binary (MMB) XML export to extract
    the physical menu structure - what menus exist and what they do.

Input:
    - legacy-system/oracle-forms/XML/EXAMPLE_LIB_mmb.xml (MMB XML export)

Output:
    - legacy-system/reference-data/inventories/mmb_structure.json
      Contains:
      - raw_menus: Dict mapping menu_name -> list of menu items
      - main_menu_tree: Hierarchical tree starting from MAIN_MENU

Data Extracted per MenuItem:
    - id: Item identifier (e.g., "FORM0000")
    - label: Display label (e.g., "&User Preferences")
    - type: MenuItem, Submenu, or Separator
    - commandType: PL/SQL, Menu, Null
    - command: The actual PL/SQL code/command
    - submenu_ref: Reference to child menu (for Submenus)

Known Issues:
    - Separators: Items with MenuItemType="Separator" may not be correctly typed
    - <New_Item> labels: These are placeholders that should be filtered in UI
    - Built-in items: "Save", "Close", "Exit" are NOT in shared MMB, they're
      in individual FMB forms or Oracle Forms built-in menus

Usage:
    python extract_mmb_structure.py

Related:
    - ADR-0002: Menu Configuration as Code
    - menu_builder.py: Merges this with MenuConfig rules (Layer 2)
"""

import os
import json
import xml.etree.ElementTree as ET

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../"))

XML_PATH = os.path.join(REPO_ROOT, "legacy-system/oracle-forms/XML/EXAMPLE_LIB_mmb.xml")
OUTPUT_PATH = os.path.join(REPO_ROOT, "legacy-system/reference-data/inventories/mmb_structure.json")

def parse_mmb(xml_path):
    if not os.path.exists(xml_path):
        print(f"Error: {xml_path} not found.")
        return None

    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Forms XML usually has a specific structure. namespace might be involved.
    # Namespace handling is tricky in ET. We'll strip it or handle it generically.
    # We are looking for 'Menu' and 'MenuItem' elements strictly.
    
    # We'll traverse looking for 'MenuModule' -> 'Menu' -> 'MenuItem'
    # Actually, MMB XMLs often flatten 'Menu' elements under the root or module.
    
    # Strategy: Find all 'Menu' elements first, then map them by Name.
    # Then build tree starting from known roots (like MAIN_MENU or MODULE_MENU).
    
    menus = {} # Name -> { items: [], label: ... }
    
    # Find all Menu elements (case insensitive tag search via iter)
    for menu_node in root.iter():
        if menu_node.tag.endswith('Menu'): # e.g. <Menu Name="ACTION_MENU">
            menu_name = menu_node.get('Name')
            if not menu_name: continue
            
            menu_items = []
            
            # Iterate direct children formatted as MenuItem
            for child in menu_node:
                if child.tag.endswith('MenuItem'):
                    # It's a leaf or action item
                    item_name = child.get('Name')
                    label = child.get('Label')
                    cmd_type = child.get('CommandType')
                    cmd_text = child.get('MenuItemCode') # The actual PL/SQL or macro (e.g. CALL_FORM)
                    menu_item_type = child.get('MenuItemType')  # Plain, Separator, Magic

                    # Check if it has a sub-menu attached? 
                    # In Forms, Submenu is defined by 'SubMenuName' attribute usually.
                    submenu_ref = child.get('SubMenuName')
                    
                    # FILTER: Skip separators
                    if menu_item_type == 'Separator':
                        continue
                    
                    # FILTER: Skip placeholder items
                    if label in ['<New_Item>', None, '']:
                        # Keep if it's a submenu reference
                        if not submenu_ref:
                            continue
                    
                    # FILTER: Skip SEPARATOR-named items
                    if item_name and item_name.upper().startswith('SEPARATOR'):
                        continue
                    
                    # Clean label: Remove accelerator ampersands
                    clean_label = label.replace('&', '') if label else item_name
                    
                    item_def = {
                        "id": item_name,
                        "label": clean_label,
                        "type": "MenuItem" if menu_item_type != 'Magic' else "Magic",
                        "commandType": cmd_type,
                        "command": cmd_text
                    }
                    if submenu_ref:
                        item_def["type"] = "Submenu"
                        item_def["submenu_ref"] = submenu_ref
                        
                    menu_items.append(item_def)
                    
            menus[menu_name] = menu_items

    return menus

def build_hierarchy(menus, start_menu_name, visited=None):
    if visited is None: visited = set()
    
    if start_menu_name in visited:
        return {"id": start_menu_name, "error": "Circular Reference"}
    
    visited.add(start_menu_name)
    
    menu_def = menus.get(start_menu_name)
    if not menu_def:
        return {"id": start_menu_name, "error": "Menu Not Found"}
    
    items = []
    for item in menu_def:
        node = {
            "id": item["id"],
            "label": item["label"],
            "type": item["type"]
        }
        
        if item["type"] == "Submenu":
             # Recurse
             ref = item["submenu_ref"]
             # We create a 'children' property
             child_structure = build_hierarchy(menus, ref, visited.copy())
             # If valid, we might want to flatten or nest? 
             # Usually nesting:
             if "items" in child_structure:
                 node["children"] = child_structure["items"]
             else:
                 node["children"] = [] # Empty or error
                 
        items.append(node)
        
    return {"id": start_menu_name, "items": items}

# Helper removed - MMB contains these items naturally


def main():
    print(f"Parsing MMB: {XML_PATH}")
    menus_raw = parse_mmb(XML_PATH)
    
    if not menus_raw:
        print("Failed to parse menus.")
        return

    print(f"Found {len(menus_raw)} Menu definitions.")
    
    # Usually the entry point is 'MAIN_MENU' or specific module menus.
    # Common entry points in EXAMPLE_LIB: 'MAIN_MENU', 'MODULE_MENU'

    
    main_menu = build_hierarchy(menus_raw, 'MAIN_MENU')
    
    # Export the full raw map AND the built main menu.
    output = {
        "raw_menus": menus_raw,
        "main_menu_tree": main_menu
    }
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
        
    print(f"Structure extracted to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()

