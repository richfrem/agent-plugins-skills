#!/usr/bin/env python3
"""
[SKILL_ROOT]/scripts/batch_output_olb_overviews.py (CLI)
=====================================

Purpose:
    Orchestrates OlbMiner to generate Object Library (.olb) documentation.

Layer: Curate / Documentation

Usage Examples:
    python [SKILL_ROOT]/scripts/batch_output_olb_overviews.py

Supported Object Types:
    - OLB (Object Library)
"""
import os
import sys
import json
import importlib.util
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

MANIFEST_PATH = PROJECT_ROOT / 'legacy-system' / 'reference-data' / 'legacy_object_manifest.json'
XML_DIR = PROJECT_ROOT / 'legacy-system' / 'oracle-forms' / 'XML'
OUTPUT_DIR = PROJECT_ROOT / 'legacy-system' / 'oracle-forms-overviews' / 'olb'

# Tooling Dependencies
# NOTE: MINER_PATH is a cross-skill reference — verify path is correct for your install
MINER_PATH = SCRIPT_DIR / 'olb_miner.py'

spec = importlib.util.spec_from_file_location("olb_miner", str(MINER_PATH))
olb_miner = importlib.util.module_from_spec(spec)
sys.modules["olb_miner"] = olb_miner
spec.loader.exec_module(olb_miner)

parse_olb_xml = olb_miner.parse_olb_xml
format_text_output = olb_miner.format_text_output

TEMPLATE = """# {id} - Object Library Overview

## Library Information
| Property | Value |
|---|---|
| **Library ID** | `{id}` |
| **Source File** | `legacy-system/oracle-forms/XML/{source_file}` |
| **Type** | Object Library (OLB) |
| **Status** | Active |
| **Object Count** | {object_count} |

## Subclassing Strategy
Describes the reusable components provided by this library.

## Subclass Inventory

### Smart Classes
{smart_classes}

### Object Groups
{object_groups}

### Visual Attributes
{visual_attributes}

## Technical Details
{tech_details}

## Modernization Notes
*   **Smart Classes**: Map to React Components or CSS Classes.
*   **Object Groups**: Map to functional modules or hooks.
"""

def generate_smart_classes(items):
    lines = []
    smart_classes = [i for i in items if i.get("smart_class")]
    if not smart_classes:
        return "None Detected."
        
    for item in smart_classes:
        lines.append(f"*   **{item['name']}** ({item['item_type']})")
        if item.get("visual_attribute"):
             lines.append(f"    *   Visual: `{item['visual_attribute']}`")
             
    return "\n".join(lines)

def generate_object_groups(groups):
    lines = []
    if not groups:
        return "None Detected."
        
    for g in groups:
        lines.append(f"*   **{g['name']}**")
        for child in g.get('children', []):
            lines.append(f"    *   {child['name']} ({child['type']})")
            
    return "\n".join(lines)

def generate_visual_attributes(vas):
    lines = []
    if not vas:
        return "None Detected."
        
    for va in vas:
        lines.append(f"*   **{va['name']}**: FG={va['fore_color']}, BG={va['back_color']}, Font={va['font_name']}")
        
    return "\n".join(lines)

def generate_tech_details(data):
    lines = []
    
    # Windows
    if data.get('windows'):
        lines.append("### Windows")
        for w in data['windows']:
             lines.append(f"*   {w['name']} (Modal: {w['modal']})")
        lines.append("")

    # Canvases
    if data.get('canvases'):
        lines.append("### Canvases")
        for c in data['canvases']:
             lines.append(f"*   {c['name']} ({c['canvas_type']})")
        lines.append("")
        
    return "\n".join(lines) if lines else "No additional technical details extracted."

def process():
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not MANIFEST_PATH.exists():
        print(f"Manifest not found: {MANIFEST_PATH}")
        return

    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
        
    print(f"Scanning {XML_DIR} for Object Libraries (*_olb.xml)...")
    found_files = list(XML_DIR.glob('*_olb.xml'))
    manifest_updated = False
    
    for xml_file in found_files:
        # derive ID
        stem = xml_file.stem # fiso_olb
        if stem.lower().endswith('_olb'):
            obj_id = stem[:-4].upper()
        else:
             obj_id = stem.upper()
             
        # Check if exists
        exists = any(x['ObjectID'] == obj_id for x in manifest)
        if not exists:
            print(f"  Discovered new OLB: {obj_id} ({xml_file.name})")
            new_entry = {
                "ObjectID": obj_id,
                "ObjectName": f"{obj_id} (Discovered)",
                "Application": "APP", 
                "Type": "OLB",
                "DocumentationStatus": "Missing",
                "SourceAvailable": True
            }
            manifest.append(new_entry)
            manifest_updated = True

    if manifest_updated:
        print("Syncing manifest with discovered OLBs...")
        with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
    
    # Filter for Type='OLB' or 'OBJLIB'
    target_items = [item for item in manifest if item.get('Type', '').upper() in ['OLB', 'OBJLIB']]
    
    if not target_items:
        print("No items of Type 'OLB' found in manifest scan.")
        return
        
    print(f"Found {len(target_items)} Object Libraries to process.")
    updated_count = 0

    for item in target_items:
        target = item['ObjectID']
        
        # Check files: target.lower() + "_olb.xml"
        fpath = XML_DIR / f"{target.lower()}_olb.xml"
        
        if not fpath.exists():
             # Try just .xml
             fpath = XML_DIR / f"{target.lower()}.xml"
            
        if not fpath.exists():
            print(f"Skipping {target}: Source file not found at {fpath}")
            continue
            
        print(f"Processing {target}...")
        try:
            # Parse
            data = parse_olb_xml(str(fpath))
            
            # Format
            content = TEMPLATE.format(
                id=target,
                source_file=fpath.name,
                object_count=data['object_count'],
                smart_classes=generate_smart_classes(data['items']),
                object_groups=generate_object_groups(data['object_groups']),
                visual_attributes=generate_visual_attributes(data['visual_attributes']),
                tech_details=generate_tech_details(data)
            )
            
            out_path = OUTPUT_DIR / f"{target}-OLB-Overview.md"
            with open(out_path, 'w', encoding='utf-8') as out:
                out.write(content)
            print(f"  Generated {out_path}")
            
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
