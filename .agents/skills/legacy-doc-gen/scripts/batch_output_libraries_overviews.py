#!/usr/bin/env python3
"""
[SKILL_ROOT]/scripts/batch_output_libraries_overviews.py (CLI)
=====================================

Purpose:
    Orchestrates PllMiner to generate library overview documentation.

Layer: Curate / Documentation

Usage Examples:
    python [SKILL_ROOT]/scripts/batch_output_libraries_overviews.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - generate_row(): No description.
    - generate_global_row(): No description.
    - process_libs(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import json
import os
import importlib.util
from pathlib import Path

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

# Tooling Dependencies (co-located in same folder)
MINER_PATH = SCRIPT_DIR / 'pll_miner.py'

spec = importlib.util.spec_from_file_location("pll_miner", str(MINER_PATH))
pll_miner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pll_miner)
PllMiner = pll_miner.PllMiner

MANIFEST_PATH = BASE_DIR / 'reference-data' / 'legacy_object_manifest.json'
PLL_DIR = BASE_DIR / 'oracle-forms' / 'pll'

TEMPLATE_PATH = SCRIPT_DIR.parent / 'assets' / 'templates' / 'library-overview-template.md'

def get_template():
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")
    return TEMPLATE_PATH.read_text(encoding='utf-8')

def generate_row(lib_name, item):
    name = item['Name']
    type_ = item['Type']
    # Construct link: ../../oracle-forms-markdown/pll/[lib].md#[type]-[name]
    # Anchor format: procedure-my_proc (lowercase)
    anchor = f"{type_.lower()}-{name.lower()}"
    link = f"[{name}](../../oracle-forms-markdown/pll/{lib_name.lower()}.md#{anchor})"
    return f"| {link} | {type_} | TBD |"

def generate_global_row(item):
    return f"| `{item['Variable']}` | {item['Usage']} | TBD |"

def process_libs():
    if not MANIFEST_PATH.exists():
        print(f"Manifest not found: {MANIFEST_PATH}")
        return

    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    # Auto-Discovery: Scan PLL directory
    print(f"Scanning {PLL_DIR} for Libraries (*.txt)...")
    found_files = list(Path(PLL_DIR).glob('*.txt'))
    manifest_updated = False
    
    for txt_file in found_files:
        # derive ID from filename (e.g. fis_calendar.txt -> FIS_CALENDAR)
        obj_id = txt_file.stem.upper()
             
        # Check if exists
        exists = any(x['ObjectID'] == obj_id for x in manifest)
        if not exists:
            print(f"  Discovered new Library: {obj_id} ({txt_file.name})")
            new_entry = {
                "ObjectID": obj_id,
                "ObjectName": f"{obj_id} (Discovered)",
                "Application": "APP", 
                "Type": "PLL",
                "DocumentationStatus": "Missing",
                "SourceAvailable": True
            }
            manifest.append(new_entry)
            manifest_updated = True

    if manifest_updated:
        print("Syncing manifest with discovered libraries...")
        with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
    
    # Filter for Type='LIBRARY' or 'PLL' (case-insensitive)
    target_items = [item for item in manifest if item.get('Type', '').upper() in ['LIBRARY', 'PLL']]
    
    if not target_items:
        print("No items of Type 'LIBRARY' or 'PLL' found in manifest scan.")
        return

    print(f"Found {len(target_items)} libraries to process.")
    updated_count = 0
    
    # Output dir
    output_dir = os.path.join(PROJECT_ROOT, 'legacy-system', 'oracle-forms-overviews', 'libraries')
    os.makedirs(output_dir, exist_ok=True)

    for item in target_items:
        lib = item['ObjectID']
        print(f"Processing {lib}...")
        lib_lower = lib.lower()
        
        # Check source exists
        source_path = PLL_DIR / f"{lib_lower}.txt"
        if not source_path.exists():
             print(f"  Warning: Source text dump not found at {source_path}. Skipping extraction.")
             # We could still generate a stub? For now, stick to extraction logic.
             continue

        # 1. Run Miner (in-memory)
        miner = PllMiner() 
        try:
            miner.scan_plls(target=source_path, silent=True)
            rules = miner.rules
            
            # 2. Format Data
            api_rows = [generate_row(lib, x) for x in sorted(rules['PublicAPI'], key=lambda k: k['Name'])]
            if not api_rows:
                api_rows = ["| None Detected | - | - |"]
                
            global_rows = [generate_global_row(x) for x in sorted(rules['GlobalStateUsage'], key=lambda k: k['Variable'])]
            if not global_rows:
                global_rows = ["| None Detected | - | - |"]

            external_rows = []
            if rules['ExternalCalls']:
                for call in rules['ExternalCalls']:
                    external_rows.append(f"*   **{call['Target']}** ({call['CallType']})")
            else:
                external_rows = ["None Detected."]

            validation_rows = []
            if rules['ValidationLogic']:
                count = rules['ValidationLogic'][0]['Count']
                validation_rows = [f"*   **Validation Blocker**: Contains {count} checks raising `FORM_TRIGGER_FAILURE`."]
            else:
                validation_rows = ["None Detected."]

            # 3. Write File
            template = get_template()
            content = template.format(
                LIBRARY_NAME=lib,
                LIBRARY_ID=lib,
                filename=lib_lower,
                DATE=datetime.now().strftime("%Y-%m-%d")
            )
            
            # Save to disk
            out_dir = BASE_DIR / "oracle-forms-overviews" / "libraries"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{lib}-Library-Overview.md"
            
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Generated {out_path}")
            
            # Update Status
            item['DocumentationStatus'] = 'Draft'
            updated_count += 1
            
        except Exception as e:
            print(f"  Error processing {lib}: {e}")

    if updated_count > 0:
        print("Updating manifest documentation status...")
        try:
             with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
                 json.dump(manifest, f, indent=2)
             print(f"Manifest updated: {MANIFEST_PATH}")
        except Exception as e:
             print(f"Error updating manifest: {e}")

if __name__ == "__main__":
    process_libs()
