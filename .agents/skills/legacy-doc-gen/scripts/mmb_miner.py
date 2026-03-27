#!/usr/bin/env python3
"""
mmb_miner.py (CLI)
=====================================

Purpose:
    Extracts raw structure from MMB XML files.

Layer: Curate / Miners

Usage Examples:
    python plugins/legacy-system-oracle-forms/scripts/mmb_miner.py --help
    python plugins/legacy-system-oracle-forms/scripts/mmb_miner.py --build
    python plugins/legacy-system-oracle-forms/scripts/mmb_miner.py --build --json
    python plugins/legacy-system-oracle-forms/scripts/mmb_miner.py --lookup ADMIN_MENU.FORM0000
    python plugins/legacy-system-oracle-forms/scripts/mmb_miner.py --lookup FORM0000 --json
    python plugins/legacy-system-oracle-forms/scripts/mmb_miner.py --search "Security" --json

Supported Object Types:
    - Generic

CLI Arguments:
    --build         : Build MMB menu map
    --lookup        : Lookup label for an item ID
    --search        : Keyword to search across MMB files
    --json          : Output raw JSON to stdout (suppress logs)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - parse_mmb_xml(): Parse an MMB XML file to extract menu structure.
    - build_mmb_menu_map(): Build a comprehensive menu map from all MMB files.
    - get_label_for_item(): Look up a human-readable label for an MenuConfig item ID.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import json
import os
import re
from pathlib import Path
from xml.etree import ElementTree as ET

SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()

MMB_DIR = PROJECT_ROOT / "legacy-system" / "oracle-forms" / "XML"
OUTPUT_PATH = PROJECT_ROOT / "legacy-system" / "reference-data" / "inventories" / "mmb_menu_map.json"


def parse_mmb_xml(xml_path: Path) -> dict:
    """
    Parse an MMB XML file to extract menu structure.
    
    Returns:
        Dictionary with menu items, labels, and actions
    """
    result = {
        "source": xml_path.name,
        "filePath": "",
        "menus": {},
        "items": {}
    }
    
    try:
        # Read raw content (MMB XML can be malformed)
        try:
             result["filePath"] = str(xml_path.relative_to(PROJECT_ROOT))
        except ValueError:
             result["filePath"] = str(xml_path)

        content = xml_path.read_text(encoding='utf-8', errors='ignore')
        
        # Extract MenuItem elements using regex (more robust than XML parsing)
        pattern = r'<MenuItem[^>]*Name="([^"]*)"[^>]*(?:Label="([^"]*)")?[^>]*(?:MenuItemCode="([^"]*)")?[^/]*/?>'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            name = match.group(1) or ""
            label = match.group(2) or name
            code = match.group(3) or ""
            
            # Decode HTML entities
            label = label.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
            label = re.sub(r'&[a-z]+;', '', label)  # Remove remaining entities
            
            # Extract form call from MenuItemCode
            form_match = re.search(r"GoForm\.do\('([^']+)'", code) or \
                         re.search(r"CallForm\.do\('([^']+)'", code) or \
                         re.search(r"CALL_FORM\s*\(\s*'([^']+)'", code, re.IGNORECASE)
            
            target_form = form_match.group(1).upper() if form_match else None
            
            result["items"][name.upper()] = {
                "name": name,
                "label": label.strip(),
                "targetForm": target_form,
                "hasCode": len(code) > 10
            }
        
        # Also extract Menu elements for hierarchy
        menu_pattern = r'<Menu[^>]*Name="([^"]*)"'
        for match in re.finditer(menu_pattern, content):
            menu_name = match.group(1)
            result["menus"][menu_name.upper()] = {"name": menu_name}
            
    except Exception as e:
        result["error"] = str(e)
    
    return result


def build_mmb_menu_map(json_output=False):
    """
    Build a comprehensive menu map from all MMB files.
    """
    all_items = {}
    sources = []
    
    # Find all MMB files
    mmb_files = list(MMB_DIR.glob("*_mmb.xml"))
    
    for mmb_path in mmb_files:
        if not json_output:
            print(f"🔍 Parsing {mmb_path.name}...")
        parsed = parse_mmb_xml(mmb_path)
        
        sources.append({
            "file": mmb_path.name,
            "filePath": parsed.get("filePath", ""),
            "itemCount": len(parsed.get("items", {})),
            "menuCount": len(parsed.get("menus", {}))
        })
        
        # Merge items (prefix with source to avoid conflicts)
        source_prefix = mmb_path.stem.upper().replace("_MMB", "")
        for item_name, item_data in parsed.get("items", {}).items():
            key = f"{source_prefix}.{item_name}" if source_prefix else item_name
            all_items[key] = {
                **item_data,
                "source": mmb_path.name,
                "filePath": parsed.get("filePath", "")
            }
    
    # Build output
    output = {
        "meta": {
            "generatedAt": __import__("datetime").datetime.utcnow().isoformat() + "Z",
            "sources": sources,
            "totalItems": len(all_items)
        },
        "items": all_items
    }
    
    # Save
    os.makedirs(OUTPUT_PATH.parent, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    if json_output:
        print(json.dumps(output, indent=2))
        return output

    print(f"\n✅ Saved MMB menu map: {OUTPUT_PATH}")
    print(f"   Total items: {len(all_items)}")
    
    return output


def get_label_for_item(item_id: str, mmb_map: dict = None) -> str:
    """
    Look up a human-readable label for an MenuConfig item ID.
    
    Args:
        item_id: e.g., "ADMIN_MENU.FORM0000"
    
    Returns:
        Human-readable label or the original ID if not found
    """
    if mmb_map is None:
        if OUTPUT_PATH.exists():
            with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
                mmb_map = json.load(f)
        else:
            return item_id


def get_item_data(item_id: str, mmb_map: dict = None) -> dict:
    """
    Look up full item data for an MenuConfig item ID.
    
    Returns:
        Dict with label, source, etc. or None if not found.
    """
    if mmb_map is None:
        if OUTPUT_PATH.exists():
            with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
                mmb_map = json.load(f)
        else:
            return None
    
    items = mmb_map.get("items", {})
    
    # Try exact match
    if item_id.upper() in items:
        return items[item_id.upper()]
    
    # Try suffix match
    parts = item_id.split(".")
    if len(parts) > 1:
        suffix = parts[-1].upper()
        for key, data in items.items():
            if key.endswith(suffix):
                return data
    
    # Try exact match on just the last part if unrelated to previous check
    # e.g. user passes just "FORM0000" but key is "ADMIN_MENU.FORM0000"
    suffix = item_id.upper()
    for key, data in items.items():
        if key.endswith(suffix):
            return data

    return None

def search_mmb_files(term: str) -> list:
    """Search all MMB MMB files for term."""
    term = term.lower()
    matches = []
    
    files = list(MMB_DIR.glob("*_mmb.xml"))
    for f in files:
        data = parse_mmb_xml(f)
        # Search in menus and items
        file_matches = []
        
        # Check source filename
        if term in data["source"].lower():
             file_matches.append(f"FileName:{data['source']}")
             
        for key, item in data["items"].items():
             if term in item.get("label", "").lower() or term in item.get("command", "").lower():
                  file_matches.append(f"Item:{item.get('name')}")
        
        # Check menus keys?
        for menu_name in data["menus"]:
             if term in menu_name.lower():
                  file_matches.append(f"Menu:{menu_name}")
                  
        if file_matches:
             matches.append({
                 "Menu": data["source"],
                 "FilePath": data["filePath"],
                 "Matches": file_matches
             })
             
    return matches


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MMB Menu Miner")
    parser.add_argument("--build", action="store_true", help="Build MMB menu map")
    parser.add_argument("--lookup", help="Item ID to lookup (e.g., ADMIN_MENU.FORM0000)")
    parser.add_argument("--search", help="Keyword to search across MMB files")
    parser.add_argument("--json", action="store_true", help="Output raw JSON to stdout (suppress logs)")
    
    args = parser.parse_args()
    
    if args.build:
        build_mmb_menu_map(json_output=args.json)
    elif args.lookup:
        if args.json:
            data = get_item_data(args.lookup)
            if data:
                print(json.dumps(data, indent=2))
            else:
                print(json.dumps({"error": "Item not found", "lookup": args.lookup}, indent=2))
        else:
            label = get_label_for_item(args.lookup)
            print(f"{args.lookup} → {label}")
    elif args.search:
        if not args.json:
            print(f"Scanning MMB files in {MMB_DIR} for '{args.search}'...")
            
        results = search_mmb_files(args.search)
        
        if args.json:
            # Unique file paths
            unique = sorted(list(set(r["FilePath"] for r in results)))
            print(json.dumps(unique, indent=2))
        else:
            for r in results:
                print(f"[{r['Menu']}] Found {len(r['Matches'])} matches: {', '.join(r['Matches'][:5])}...")
    else:
        parser.print_help()

