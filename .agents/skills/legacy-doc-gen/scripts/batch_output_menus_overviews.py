#!/usr/bin/env python3
"""
[SKILL_ROOT]/scripts/batch_output_menus_overviews.py (CLI)
=====================================

Purpose:
    Orchestrates MenuMiner for batch menu documentation.

Layer: Curate / Documentation

Usage Examples:
    python [SKILL_ROOT]/scripts/batch_output_menus_overviews.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - generate_hierarchy(): No description.
    - generate_commands(): No description.
    - generate_dependencies(): No description.
    - generate_modernization_section(): No description.
    - process(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import sys
import importlib.util
import re
import json
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

XML_DIR = PROJECT_ROOT / 'legacy-system' / 'oracle-forms' / 'XML'
OUTPUT_DIR = PROJECT_ROOT / 'legacy-system' / 'oracle-forms-overviews' / 'menus'

# Tooling Dependencies
# NOTE: MINER_PATH is a cross-skill reference — verify path is correct for your install
MINER_PATH = SCRIPT_DIR / 'menu_miner.py'

MANIFEST_PATH = PROJECT_ROOT / 'legacy-system' / 'reference-data' / 'legacy_object_manifest.json'

# Import Miner
spec = importlib.util.spec_from_file_location("menu_miner", str(MINER_PATH))
menu_miner = importlib.util.module_from_spec(spec)
sys.modules["menu_miner"] = menu_miner
spec.loader.exec_module(menu_miner)
MenuMiner = menu_miner.MenuMiner


TEMPLATE = """# {id} - Menu Overview

## Menu Information
**Name**: {name}

## Roles
{roles_section}

## Menu Hierarchy
{hierarchy_section}

## Logic & Commands
{commands_section}

## Dependencies
{dependencies_section}
"""

def generate_hierarchy(menus):
    sections = []
    # Identify Main Menu if possible, but flat list is safer for complete coverage
    for menu in menus:
        sections.append(f"### Menu: {menu['Name']}")
        for item in menu['Items']:
            label = item.get('Label') or item.get('Name', '')
            
            # Strip Oracle keyboard accelerator marker (&)
            label = label.replace('&', '')
            
            # Skip placeholders
            if label == "<New_Item>" or label == "":
                continue

            # Check for Separator
            if 'SEPARATOR' in label.upper() or 'SEPARATOR' in item.get('Name', '').upper():
                sections.append("\n---\n") 
                continue

            extra = []
            
            if item.get('SubMenu'):
                extra.append(f"-> {item.get('SubMenu')}")
            
            # Target (Form/Report) - NEW
            target = item.get('Target')
            if target:
                extra.append(f"Opens: [{target.upper()}]")
            
            # Roles
            roles = item.get('Roles')
            if roles and roles != ['NOGROUP']:
                extra.append(f"Roles: {', '.join(roles)}")
            
            if item.get('CommandType') and item.get('CommandType') not in ['Null', 'Menu']:
                extra.append(f"[{item.get('CommandType')}]")
            
            # If no target but code exists, show hint
            code = item.get('CommandText')
            if code and not target and not item.get('SubMenu'):
                 # Decode entities first
                 code_clean = code.replace('&#10;', ' ').replace('&amp;', '&').strip()
                 
                 # Clean specific common patterns (Make regex robust)
                 # Handle Menubar.ItemClick, ItemClick, etc
                 m_trig = re.search(r"(?:Menubar\.)?ItemClick\s*\(\s*'([^']+)'", code_clean, re.IGNORECASE)
                 if m_trig:
                     code_clean = f"Trigger: {m_trig.group(1)}"
                 
                 m_key = re.search(r"do_key\s*\(\s*'([^']+)'", code_clean, re.IGNORECASE)
                 if m_key:
                     code_clean = f"Action: {m_key.group(1)}"

                 # If still raw code, wrap it
                 if len(code_clean) < 60:
                     extra.append(f"`{code_clean}`")
                 else:
                     extra.append("Custom Logic")

            line = f"*   **{label}**"
            if extra:
                line += f" ({'; '.join(extra)})"
            sections.append(line)
        sections.append("")
    return "\n".join(sections)

def generate_commands(menus, program_units):
    sections = []
    
    # Program Units
    if program_units:
        sections.append("### Program Units")
        for pu in program_units:
            text = pu.get('Text', '')
            # Decode Oracle XML entities
            text = text.replace('&#10;', '\n').replace('&amp;', '&').replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>')
            sections.append(f"#### {pu['Name']} ({pu['Type']})\n```sql\n{text}\n```")

    # Menu Item Logic (if explicit PL/SQL)
    for menu in menus:
        for item in menu['Items']:
            cmd = item.get('CommandText')
            if cmd and item.get('CommandType') == 'PL/SQL':
                 cmd = cmd.replace('&#10;', '\n').replace('&amp;', '&').replace('&quot;', '"').replace('&lt;', '<').replace('&gt;', '>')
                 sections.append(f"#### Item: {menu['Name']}.{item['Name']}\n```sql\n{cmd}\n```")
                 
    if not sections:
        return "None Detected."
    return "\n".join(sections)

def generate_dependencies(libs):
    if not libs:
        return "None Detected."
    return "\n".join([f"*   [{lib.upper()}]" for lib in libs])

def generate_modernization_section(data):
    insights = []
    
    # Analyze Program Units for dynamic behavior
    has_dynamic_visibility = any(pu['Name'] == 'HIDEMODULEITEMS' for pu in data['ProgramUnits'])
    if has_dynamic_visibility:
        insights.append("*   **Dynamic Visibility**: This menu uses `HIDEMODULEITEMS` to toggle visibility based on context (likely Global Variables). In React, manage this via a Context Provider or State Store (Redux/Zustand).")
        
    # Roles
    if data['Roles']:
       insights.append(f"*   **RBAC**: Defined roles ({', '.join(data['Roles'])}) must be mapped to the new Identity Provider.")
       
    # Navigation Analysis
    targets = 0
    for m in data['Menus']:
        for i in m['Items']:
            if i.get('Target'): targets += 1
            
    if targets > 10:
        insights.append(f"*   **Navigation Complexity**: High volume of navigation targets ({targets}). Consider a Mega-Menu or searchable Command Palette (Ctrl+K).")
    
    # Check for Dialog/Modal calls
    has_modals = any("open_form" in (i.get('CommandText') or '').lower() for m in data['Menus'] for i in m['Items'])
    if has_modals:
        insights.append("*   **Modals**: Uses `OPEN_FORM` which may imply opening new windows/sessions. In modern web apps, use true routable Modals or separate browser tabs.")

    if not insights:
        return "Standard Static Navigation."
        
    return "\n".join(insights)

def process():
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not MANIFEST_PATH.exists():
        print(f"Manifest not found: {MANIFEST_PATH}")
        return

    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    # Auto-Discovery: Scan XML directory for Menus
    found_files = list(XML_DIR.glob('*_mmb.xml'))
    manifest_updated = False
    
    for xml_file in found_files:
        # derive ID
        filename = xml_file.name
        # fism0001_mmb.xml -> FISM0001_MMB
        stem = xml_file.stem
        obj_id = stem.upper()
             
        # Check if exists
        exists = any(x['ObjectID'] == obj_id for x in manifest)
        if not exists:
            print(f"  Discovered new Menu: {obj_id} ({filename})")
            new_entry = {
                "ObjectID": obj_id,
                "ObjectName": f"{obj_id} (Discovered)",
                "Application": "APP", 
                "Type": "MENU",
                "DocumentationStatus": "Missing",
                "SourceAvailable": True
            }
            manifest.append(new_entry)
            manifest_updated = True

    if manifest_updated:
        print("Syncing manifest with discovered menus...")
        with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
    
    # Filter for Type='MENU' (case-insensitive)
    target_items = [item for item in manifest if item.get('Type', '').upper() == 'MENU']
    
    if not target_items:
        print("No items of Type 'MENU' found in manifest.")
        return
        
    print(f"Found {len(target_items)} menus to process.")
    updated_count = 0

    for item in target_items:
        target = item['ObjectID']
        
        # Check for lowercase _mmb.xml
        fpath = XML_DIR / f"{target.lower()}_mmb.xml"
        if not fpath.exists():
            # Try just .xml
            fpath = XML_DIR / f"{target.lower()}.xml"
            
        if not fpath.exists():
            print(f"Skipping {target}: Source file not found.")
            continue
            
        print(f"Processing {target}...")
        try:
            miner = MenuMiner()
            miner.analyze(fpath)
            data = miner.metadata
            
            # Use manifest name if available, else miner name
            display_name = item.get('ObjectName') or data['Name']

            content = TEMPLATE.format(
                id=data['ID'],
                name=display_name,
                roles_section=", ".join(data['Roles']) if data['Roles'] else "None",
                hierarchy_section=generate_hierarchy(data['Menus']),
                commands_section=generate_commands(data['Menus'], data['ProgramUnits']),
                dependencies_section=generate_dependencies(data['AttachedLibraries'])
            ) + f"\n## Modernization Insights\n{generate_modernization_section(data)}\n"
            
            out_path = OUTPUT_DIR / f"{data['ID']}-Menu-Overview.md"
            with open(out_path, 'w', encoding='utf-8') as out:
                out.write(content)
            
            # Update Status
            item['DocumentationStatus'] = 'Draft'
            updated_count += 1
            
        except Exception as e:
            print(f"Error processing {target}: {e}")

    # Save Manifest if changes were made
    if updated_count > 0:
        print("Updating manifest documentation status...")
        try:
             with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
                 json.dump(manifest, f, indent=2)
             print(f"Manifest updated: {MANIFEST_PATH}")
        except Exception as e:
             print(f"Error updating manifest: {e}")

if __name__ == "__main__":
    process()
