#!/usr/bin/env python3
"""
olb_miner.py (CLI)
=====================================

Purpose:
    Parses Oracle Forms Object Library (.olb) XML files to extract reusable UI components like SmartClasses, Object Groups, Visual Attributes, and Windows for analysis and inventory.

Layer: Curate / Miners

Usage Examples:
    python plugins/legacy-system-oracle-forms/scripts/olb_miner.py --help
    python plugins/legacy-system-oracle-forms/scripts/olb_miner.py --file legacy-system/oracle-forms/XML/APP2_olb.xml
    python plugins/legacy-system-oracle-forms/scripts/olb_miner.py --search "APP2_ETRY" --json

Supported Object Types:
    - Generic

CLI Arguments:
    --file          : Path to OLB XML file
    --search        : Keyword to search across OLBs
    --output        : Output format (text|json)
    --json          : Shortcut for --output json

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - parse_olb_xml(): Parse an OLB XML file and extract component definitions.
    - extract_item(): Extract item (SmartClass) information.
    - extract_object_group(): Extract ObjectGroup and its children.
    - format_text_output(): Format the extracted data as human-readable text.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import argparse
import json
import sys
import os
import glob
from pathlib import Path
from xml.etree import ElementTree as ET

# Constants
SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()
OLB_XML_DIR = PROJECT_ROOT / "legacy-system" / "oracle-forms" / "XML"

# Oracle Forms XML namespace
NS = {'forms': 'http://xmlns.oracle.com/Forms'}


def parse_olb_xml(file_path: str) -> dict:
    """Parse an OLB XML file and extract component definitions."""
    
    result = {
        "library_name": "",
        "filePath": "",
        "object_count": 0,
        "tabs": [],
        "items": [],
        "visual_attributes": [],
        "object_groups": [],
        "triggers": [],
        "program_units": [],
        "alerts": [],
        "canvases": [],
        "windows": [],
        "blocks": [],
        "lovs": [],
        "module_parameters": [],
        "graphics": [],
        "radio_buttons": []
    }
    
    try:
        # Calculate relative path
        try:
             repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
             result["filePath"] = os.path.relpath(file_path, repo_root)
        except ValueError:
             result["filePath"] = str(file_path)

        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}", file=sys.stderr)
        return result
    
    # Find ObjectLibrary element
    olb = root.find('.//forms:ObjectLibrary', NS)
    if olb is None:
        # Try without namespace
        olb = root.find('.//ObjectLibrary')
    
    if olb is None:
        print("No ObjectLibrary element found", file=sys.stderr)
        return result
    
    result["library_name"] = olb.get("Name", "UNKNOWN")
    result["object_count"] = int(olb.get("ObjectCount", 0))
    
    # Process ObjectLibraryTabs
    for tab in olb.findall('.//forms:ObjectLibraryTab', NS) or olb.findall('.//ObjectLibraryTab'):
        tab_info = {
            "name": tab.get("Name", ""),
            "label": tab.get("Label", ""),
            "object_count": int(tab.get("ObjectCount", 0)),
            "items": []
        }
        
        # Items within tab (SmartClasses)
        for item in tab.findall('forms:Item', NS) or tab.findall('Item'):
            item_info = extract_item(item)
            tab_info["items"].append(item_info)
            result["items"].append(item_info)
        
        # Radio buttons within tab
        for rb in tab.findall('forms:RadioButton', NS) or tab.findall('RadioButton'):
            rb_info = {
                "name": rb.get("Name", ""),
                "smart_class": rb.get("SmartClass", "false") == "true",
                "visual_attribute": rb.get("VisualAttributeName", "")
            }
            result["radio_buttons"].append(rb_info)
        
        # Blocks within tab
        for block in tab.findall('forms:Block', NS) or tab.findall('Block'):
            block_info = {
                "name": block.get("Name", ""),
                "smart_class": block.get("SmartClass", "false") == "true",
                "records_display_count": block.get("RecordsDisplayCount", ""),
                "database_block": block.get("DatabaseBlock", "true"),
                "navigation_style": block.get("NavigationStyle", "")
            }
            result["blocks"].append(block_info)
        
        # Canvases within tab
        for canvas in tab.findall('forms:Canvas', NS) or tab.findall('Canvas'):
            canvas_info = {
                "name": canvas.get("Name", ""),
                "smart_class": canvas.get("SmartClass", "false") == "true",
                "canvas_type": canvas.get("CanvasType", "Content"),
                "back_color": canvas.get("BackColor", "")
            }
            result["canvases"].append(canvas_info)
        
        # Windows within tab
        for window in tab.findall('forms:Window', NS) or tab.findall('Window'):
            window_info = {
                "name": window.get("Name", ""),
                "smart_class": window.get("SmartClass", "false") == "true",
                "window_style": window.get("WindowStyle", ""),
                "modal": window.get("Modal", "false") == "true",
                "title": window.get("Title", "")
            }
            result["windows"].append(window_info)
        
        # ObjectGroups within tab
        for og in tab.findall('forms:ObjectGroup', NS) or tab.findall('ObjectGroup'):
            og_info = extract_object_group(og)
            result["object_groups"].append(og_info)
        
        # LOVs within tab
        for lov in tab.findall('forms:LOV', NS) or tab.findall('LOV'):
            lov_info = {
                "name": lov.get("Name", ""),
                "smart_class": lov.get("SmartClass", "false") == "true",
                "auto_refresh": lov.get("AutoRefresh", "false") == "true"
            }
            result["lovs"].append(lov_info)
        
        # Graphics (Frames) within tab
        for gfx in tab.findall('forms:Graphics', NS) or tab.findall('Graphics'):
            gfx_info = {
                "name": gfx.get("Name", ""),
                "smart_class": gfx.get("SmartClass", "false") == "true",
                "graphics_type": gfx.get("GraphicsType", "")
            }
            result["graphics"].append(gfx_info)
        
        result["tabs"].append(tab_info)
    
    # Top-level elements (outside tabs)
    for trigger in olb.findall('forms:Trigger', NS) or olb.findall('Trigger'):
        trigger_info = {
            "name": trigger.get("Name", ""),
            "text_preview": trigger.get("TriggerText", "")[:100] + "..." if len(trigger.get("TriggerText", "")) > 100 else trigger.get("TriggerText", "")
        }
        result["triggers"].append(trigger_info)
    
    for pu in olb.findall('forms:ProgramUnit', NS) or olb.findall('ProgramUnit'):
        pu_info = {
            "name": pu.get("Name", ""),
            "type": pu.get("ProgramUnitType", "Procedure")
        }
        result["program_units"].append(pu_info)
    
    for alert in olb.findall('forms:Alert', NS) or olb.findall('Alert'):
        alert_info = {
            "name": alert.get("Name", ""),
            "style": alert.get("AlertStyle", "Note"),
            "title": alert.get("Title", ""),
            "button1": alert.get("Button1Label", ""),
            "button2": alert.get("Button2Label", ""),
            "button3": alert.get("Button3Label", "")
        }
        result["alerts"].append(alert_info)
    
    for va in olb.findall('forms:VisualAttribute', NS) or olb.findall('VisualAttribute'):
        va_info = {
            "name": va.get("Name", ""),
            "back_color": va.get("BackColor", ""),
            "fore_color": va.get("ForegroundColor", ""),
            "font_name": va.get("FontName", ""),
            "font_size": va.get("FontSize", ""),
            "font_weight": va.get("FontWeight", "")
        }
        result["visual_attributes"].append(va_info)
    
    for mp in olb.findall('forms:ModuleParameter', NS) or olb.findall('ModuleParameter'):
        mp_info = {
            "name": mp.get("Name", ""),
            "data_type": mp.get("ParameterDataType", "Char"),
            "initial_value": mp.get("ParameterInitializeValue", ""),
            "comment": mp.get("Comment", "")
        }
        result["module_parameters"].append(mp_info)
    
    return result


def extract_item(item) -> dict:
    """Extract item (SmartClass) information."""
    return {
        "name": item.get("Name", ""),
        "item_type": item.get("ItemType", "Text Item"),
        "smart_class": item.get("SmartClass", "false") == "true",
        "visual_attribute": item.get("VisualAttributeName", ""),
        "insert_allowed": item.get("InsertAllowed", "true") == "true",
        "update_allowed": item.get("UpdateAllowed", "true") == "true",
        "keyboard_navigable": item.get("KeyboardNavigable", "true") == "true",
        "data_type": item.get("DataType", ""),
        "format_mask": item.get("FormatMask", ""),
        "max_length": item.get("MaximumLength", "")
    }


def extract_object_group(og) -> dict:
    """Extract ObjectGroup and its children."""
    children = []
    for child in og.findall('forms:ObjectGroupChild', NS) or og.findall('ObjectGroupChild'):
        children.append({
            "name": child.get("Name", ""),
            "type": child.get("Type", ""),
            "program_unit_type": child.get("ProgramUnitType", "")
        })
    
    return {
        "name": og.get("Name", ""),
        "object_group_type": og.get("ObjectGroupType", ""),
        "children": children
    }

def search_olb_content(data: dict, term: str) -> list:
    """Search extracted OLB data for term."""
    term = term.lower()
    matches = []
    
    # Simple recursive search
    if term in data["library_name"].lower():
        matches.append("LibraryName")
        
    for item in data["items"]:
        if term in item["name"].lower():
             matches.append(f"Item:{item['name']}")
    
    for og in data["object_groups"]:
        if term in og["name"].lower():
             matches.append(f"ObjectGroup:{og['name']}")
        for child in og["children"]:
             if term in child["name"].lower():
                  matches.append(f"ObjectGroupChild:{child['name']}")
                  
    return matches


def format_text_output(data: dict) -> str:
    """Format the extracted data as human-readable text."""
    lines = []
    lines.append(f"=" * 60)
    lines.append(f"OLB MINER OUTPUT: {data['library_name']}")
    lines.append(f"Total Objects: {data['object_count']}")
    lines.append(f"=" * 60)
    
    # Tabs
    if data["tabs"]:
        lines.append(f"\n## LIBRARY TABS ({len(data['tabs'])})")
        for tab in data["tabs"]:
            lines.append(f"  - {tab['name']} ({tab['label']}): {tab['object_count']} objects")
    
    # SmartClass Items
    smart_classes = [i for i in data["items"] if i.get("smart_class")]
    if smart_classes:
        lines.append(f"\n## SMART CLASSES ({len(smart_classes)})")
        for item in smart_classes:
            lines.append(f"  - {item['name']} [{item['item_type']}]")
            if item.get("visual_attribute"):
                lines.append(f"      Visual: {item['visual_attribute']}")
    
    # Visual Attributes
    if data["visual_attributes"]:
        lines.append(f"\n## VISUAL ATTRIBUTES ({len(data['visual_attributes'])})")
        for va in data["visual_attributes"]:
            lines.append(f"  - {va['name']}: bg={va['back_color']}, fg={va['fore_color']}")
    
    # Object Groups
    if data["object_groups"]:
        lines.append(f"\n## OBJECT GROUPS ({len(data['object_groups'])})")
        for og in data["object_groups"]:
            lines.append(f"  - {og['name']} ({len(og['children'])} children)")
            for child in og["children"][:5]:  # Show first 5
                lines.append(f"      → {child['name']} [{child['type']}]")
            if len(og["children"]) > 5:
                lines.append(f"      ... and {len(og['children']) - 5} more")
    
    # Triggers
    if data["triggers"]:
        lines.append(f"\n## TRIGGERS ({len(data['triggers'])})")
        for t in data["triggers"]:
            lines.append(f"  - {t['name']}")
    
    # Program Units
    if data["program_units"]:
        lines.append(f"\n## PROGRAM UNITS ({len(data['program_units'])})")
        for pu in data["program_units"]:
            lines.append(f"  - {pu['name']} [{pu['type']}]")
    
    # Alerts
    if data["alerts"]:
        lines.append(f"\n## ALERTS ({len(data['alerts'])})")
        for a in data["alerts"]:
            lines.append(f"  - {a['name']} [{a['style']}]: {a['title']}")
    
    # Blocks
    if data["blocks"]:
        lines.append(f"\n## BLOCKS ({len(data['blocks'])})")
        for b in data["blocks"]:
            db = "DB" if b["database_block"] != "false" else "Control"
            lines.append(f"  - {b['name']} [{db}]")
    
    # Canvases
    if data["canvases"]:
        lines.append(f"\n## CANVASES ({len(data['canvases'])})")
        for c in data["canvases"]:
            lines.append(f"  - {c['name']} [{c['canvas_type']}]")
    
    # Windows
    if data["windows"]:
        lines.append(f"\n## WINDOWS ({len(data['windows'])})")
        for w in data["windows"]:
            modal = "Modal" if w["modal"] else "Modeless"
            lines.append(f"  - {w['name']} [{w['window_style']}, {modal}]")
    
    # Module Parameters
    if data["module_parameters"]:
        lines.append(f"\n## MODULE PARAMETERS ({len(data['module_parameters'])})")
        for mp in data["module_parameters"]:
            lines.append(f"  - {mp['name']} [{mp['data_type']}]")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="OLB (Object Library) Miner")
    parser.add_argument("--file", help="Path to OLB XML file")
    parser.add_argument("--search", help="Keyword to search across OLBs")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--json", action="store_true", help="Shortcut for --output json")
    
    args = parser.parse_args()
    
    if args.json:
        args.output = "json"
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)
        
        data = parse_olb_xml(str(file_path))
        
        if args.output == "json":
            print(json.dumps(data, indent=2))
        else:
            print(format_text_output(data))
        return

    # Bulk Mode
    files = list(OLB_XML_DIR.glob("*_olb.xml")) # Convention? Or just all XML and check root?
    # Let's trust *_olb.xml convention or just try parsing.
    # Actually just globbing *_olb.xml is safer to avoid parsing thousands of forms.
    
    if args.output != "json":
        print(f"Scanning {len(files)} OLBs in {OLB_XML_DIR}...")
    
    results = []
    for f in files:
        data = parse_olb_xml(str(f))
        
        if args.search:
            matches = search_olb_content(data, args.search)
            if matches:
                 if args.output == "json":
                     results.append({
                         "Library": data["library_name"],
                         "FilePath": data["filePath"],
                         "Matches": matches
                     })
                 else:
                     print(f"[{data['library_name']}] Found match: {', '.join(matches[:5])}")
        else:
             if args.output == "json":
                 results.append(data)
             else:
                 print(f"Processed {data['library_name']}")

    if args.output == "json":
        print(json.dumps(sorted(list(set(r["FilePath"] for r in results))), indent=2))


if __name__ == "__main__":
    main()
