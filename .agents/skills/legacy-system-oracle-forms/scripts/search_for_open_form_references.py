#!/usr/bin/env python3
"""
Search for Open Form References (Python Port)
=============================================

Purpose:
    Scans Oracle Forms source code (XML, Markdown, PLL text) to identify parent-child form dependencies.
    Builds a Form Dependency Tree by finding calls like CALL_FORM, OPEN_FORM, RUN_REPORT_OBJECT, etc.
    Scans input files (Forms, Menus, PLLs, OLBs) for OPEN_FORM, CALL_FORM, NEW_FORM.
    Outputs a CSV of dependencies.

Behavior:
    1.  **Recursive Scan**: Iterates through all directories provided via `--input`.
    2.  **Supported Formats**: Processes .md, .xml, .txt, .pld files.
    3.  **Parent Detection**: Derives the Source Form ID from the filename.
    4.  **Relationship Detection**: Uses regex patterns to extract Target IDs from code calls.
    5.  **Target Validation**:
        - Source (Parent): Can be any analyzed module (Form, Menu, PLL, OLB).
        - Target (Child): Validated against the Master Object Collection (Strictly Forms).
    6.  **Deduplication**: Ensures unique (Source, Target, Type) rows.
    7.  **Fallback Logic**: Records GENERIC_REFERENCE only if no specific pattern matched.

Usage:
    python plugins/legacy-system-oracle-forms/scripts/search_for_open_form_references.py \
        --input legacy-system/oracle-forms/XML \
        --input legacy-system/oracle-forms/pll \
        --output legacy-system/reference-data/collections/code-detected/form_relationships.csv \
        --verbose

Input Files (Metadata):
    - `legacy-system/reference-data/master_object_collection.json` (via `valid_form_ids.py`)

Output:
    - `legacy-system/reference-data/collections/code-detected/form_relationships.csv`

Dependencies:
    - `valid_form_ids.py`: Logic for validating ID targets against the Master Object Collection.
    - `python_regex/`: Library of regex patterns ported from JS.
"""

import sys
import argparse
import csv
import re
import html
from pathlib import Path
from typing import List, Dict

# Add script directory to sys.path so local modules (python_regex, valid_form_ids) resolve.
# Run this script from the project root directory.
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Add project root for any project-level imports
project_root = Path.cwd()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from python_regex import matchers
from valid_form_ids import is_valid_id, is_valid_source_id

def extract_parent_id(file_path: Path) -> str:
    """
    Extracts Parent ID from filename.
    Legacy JS logic: Takes filename, strips extension, converts to uppercase.
    Example: FORM0001-FormModule.md -> FORM0002
             MyLib.md -> MYLIB
    """
    stem = file_path.stem
    # If filename ends with _fmb, _mmb, _olb (XML dump pattern), strip it
    for suffix in ['_fmb', '_mmb', '_olb', '_pll']:
        if stem.lower().endswith(suffix):
            stem = stem[:-4] # Remove suffix
            break
            
    if '-' in stem:
        parts = stem.split('-')
        return parts[0].upper()
    return stem.upper()



def scan_file(file_path: Path) -> List[Dict[str, str]]:
    """Reads file and runs all matchers."""
    parent_id = extract_parent_id(file_path)
    
    # 1. Validate Source (Parent) - Check if known, but DO NOT SKIP if unknown (just warn)
    # This prevents incomplete inventory from blocking analysis.
    if not is_valid_source_id(parent_id):
        print(f"[WARN] Source {file_path.name} (ID {parent_id}) not in Master Collection. Processing anyway.")
        # return [] # DISABLED STRICT SOURCE VALIDATION to ensure output

    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        print(f"[WARN] Failed to read {file_path}: {e}")
        return []

    # Strip SQL comments
    def strip_comments(text):
        # Strip multi-line /* */
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        # Strip single line --
        text = re.sub(r'--.*', '', text)
        return text

    # UNESCAPE XML ENTITIES (Mandatory for trigger parsing)
    # Turns &amp;#10; into \n, &amp;gt; into >, etc.
    content = html.unescape(content)
    # Also handle specific encoded entities that html.unescape might miss depending on version/context
    content = content.replace('&#10;', '\n').replace('&amp;', '&').replace('&#x9;', '\t')

    content = strip_comments(content)

    all_refs = []

    # List of matcher functions to run
    # We could iterate dynamically, but explicit list is safer/clearer
    mining_funcs = [
        matchers.match_call_form,
        matchers.match_open_form,
        matchers.match_new_form,
        matchers.match_run_product,
        matchers.match_execute_trigger,
        matchers.match_add_list_element,
        matchers.match_add_param,
        matchers.match_call_help_topic,
        matchers.match_call_prefix,
        matchers.match_get_menu_item_property,
        matchers.match_get_param_list,
        matchers.match_go_form_do,
        matchers.match_menubar_enable_item,
        matchers.match_menubar_hide_item,
        matchers.match_menubar_item_is_enabled,
        matchers.match_open_form_do,
        matchers.match_pr_call_form,
        matchers.match_pr_open_form,
        matchers.match_p_formmodule_name,
        matchers.match_xml_menu_module,
        matchers.match_xml_attached_lib,
        matchers.match_xml_parent_module,
        matchers.match_attr_all_ids,
        matchers.match_generic_references,
    ]

    for func in mining_funcs:
        results = func(content, parent_id)
        if results:
            print(f"  DEBUG: {func.__name__} found {len(results)} references")
        all_refs.extend(results)

    return all_refs

def main():
    parser = argparse.ArgumentParser(description="Scan Forms/Reports for dependencies.")
    parser.add_argument("--input", "-i", required=True, action='append', help="Input directory (recursive scan). Can be specified multiple times.")
    parser.add_argument("--output", "-o", required=True, type=Path, help="Output CSV path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--skip-validation", action="store_true", help="Include IDs not found in inventory")
    args = parser.parse_args()

    # Convert strings to Paths
    input_dirs = [Path(p) for p in args.input]
    output_path = args.output

    for d in input_dirs:
        if not d.exists():
            print(f"Error: Input directory {d} does not exist.")
            sys.exit(1)

    # Ensure output dir exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Scanning directories: {[str(d) for d in input_dirs]}")
    print(f"Output to: {output_path}")

    files = []
    for d in input_dirs:
        # Recursive scan for .md, .xml, and .txt files
        if d.is_file():
             # If user passes specific file, just add it if checks pass
             if d.suffix.lower() in ['.md', '.xml', '.txt', '.pld']:
                 files.append(d)
        else:
            files.extend(list(d.rglob("*.md")) + list(d.rglob("*.xml")) + list(d.rglob("*.txt")) + list(d.rglob("*.pld")))
    
    print(f"Found {len(files)} files to scan.")

    all_relationships = []
    seen_relationships = set()
    seen_specific_pairs = set() # Track (parent, child) found via specific methods

    for f in files:
        parent_id = extract_parent_id(f)
        print(f"DEBUG: File={f.name} -> Extracted_ID={parent_id}")
        
        refs = scan_file(f)
        
        # Sort so specific methods are processed before GENERIC_REFERENCE
        # GENERIC_REFERENCE starts with 'G', but we want it last.
        refs.sort(key=lambda x: 1 if x['method'] == 'GENERIC_REFERENCE' else 0)
        
        for ref in refs:
            parent = ref['parent']
            child = ref['child']
            method = ref['method']
            file_name = f.name

            # Determine if validation is required based on Method Type
            # Static calls should be trusted to capture all explicit form-to-form calls
            is_static_call = method in ['CALL_FORM', 'OPEN_FORM', 'NEW_FORM', 'RUN_PRODUCT', 'CALL_REPORT']
            
            # Filter Logic:
            # 1. Skip Validation enabled? -> Keep All
            # 2. Valid ID (Target is in the 76 Form IDs list)? -> Keep
            # 3. Not a self-reference? -> Keep
            # 4. Fallback Logic: Generic only if no specific method found for this pair.
            if (args.skip_validation or is_valid_id(child)) and parent != child:
                
                # Deduplication logic:
                pair_key = f"{parent}|{child}"
                
                if method == 'GENERIC_REFERENCE' and pair_key in seen_specific_pairs:
                    continue # Already found via a specific pattern
                
                rel_key = f"{parent}|{child}|{method}"
                if rel_key not in seen_relationships:
                    all_relationships.append({
                        'Source': parent,
                        'Target': child,
                        'Type': method,
                        'File': file_name
                    })
                    seen_relationships.add(rel_key)
                    if method != 'GENERIC_REFERENCE':
                        seen_specific_pairs.add(pair_key)
            elif args.verbose:
                 print(f"Filtered invalid ID: {child} (from {parent}) using method {method}")

    # Sort results
    all_relationships.sort(key=lambda x: (x['Source'], x['Target'], x['Type']))

    # Write CSV
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Source', 'Target', 'Type', 'File']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for row in all_relationships:
                writer.writerow(row)
        
        print(f"Successfully wrote {len(all_relationships)} relationships to {output_path}")

    except Exception as e:
        print(f"Error writing CSV: {e}")
        sys.exit(1)

    # DEBUG: Output valid_form_ids collection
    #from tools.investigate.miners import valid_form_ids
    #print(f"\nDEBUG: Loaded {len(valid_form_ids.valid_form_ids)} Valid Target IDs (FORMs):")
    #print(sorted(list(valid_form_ids.valid_form_ids)))

if __name__ == "__main__":
    main()
