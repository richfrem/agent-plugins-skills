#!/usr/bin/env python3
"""
batch_output_forms_overviews.py (CLI)
=====================================

Purpose:
    Creates placeholder overview documentation for missing forms
    using the standard project template.

Layer: Curate / Documentation

Usage Examples:
    python plugins/legacy-doc-gen/scripts/batch_output_forms_overviews.py
    python plugins/legacy-doc-gen/scripts/batch_output_forms_overviews.py --file legacy-system/oracle-forms/XML/fisf0005_fmb.xml

Supported Object Types:
    - Forms

CLI Arguments:
    --target: Specific Form ID to generate/update (e.g. JCSM0000)
    --file: Path to a specific XML file to generate overview for (derives ID from filename)
    --overwrite: Overwrite existing files

Input Files:
    - legacy-system/reference-data/legacy_object_manifest.json
    - [SKILL_ROOT]/assets/templates/form-overview-template.md
    - .env (Required for APP_ACRONYM and APP_NAME)
    - [Optional] XML file path provided via --file

Output:
    - legacy-system/oracle-forms-overviews/forms/[ID]-Overview.md
    - legacy-system/reference-data/legacy_object_manifest.json (Updated Status)

Key Functions:
    - load_template(): Load the standard template.
    - generate_overview(): Populate template with manifest data.
    - resolve_object_from_file(): Derive object ID/metadata from filename.
    - main(): Orchestrator.
"""
import json
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

import xml.etree.ElementTree as ET

# Load .env file
load_dotenv()

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()

FORMS_DIR = PROJECT_ROOT / 'legacy-system' / 'oracle-forms-overviews' / 'forms'
REPORTS_DIR = PROJECT_ROOT / 'legacy-system' / 'oracle-forms-overviews' / 'reports'
XML_FORMS_DIR = PROJECT_ROOT / 'legacy-system' / 'oracle-forms' / 'XML'
MANIFEST_PATH = PROJECT_ROOT / 'legacy-system' / 'reference-data' / 'legacy_object_manifest.json'
TEMPLATE_PATH = SCRIPT_DIR.parent / 'assets' / 'templates' / 'form-overview-template.md'

def load_template():
    if not TEMPLATE_PATH.exists():
        print(f"Error: Template not found at {TEMPLATE_PATH}")
        return None
    return TEMPLATE_PATH.read_text(encoding='utf-8')

def generate_overview(obj, template, source_file=None):
    obj_id = obj['ObjectID']
    obj_name = obj['ObjectName']
    obj_app = obj['Application']
    obj_type = obj['Type']
    
    target_dir = REPORTS_DIR if obj_type == 'REPORT' else FORMS_DIR
    target_path = target_dir / f"{obj_id}-Overview.md"
    
    # Pre-calculate derived values
    # Correct relative path: ../../oracle-forms-markdown/XML/[id]-FormModule.md
    xml_link = f"../../oracle-forms-markdown/XML/{obj_id.lower()}-FormModule.md"
    
    # Extract Metadata from XML if available
    form_title = obj_name # Default to object name from manifest
    form_comment = "TBD"
    
    # Determine XML Source Path
    # Prioritize passed source_file, then construct from ID
    xml_source_path = Path(source_file) if source_file else (XML_FORMS_DIR / f"{obj_id.lower()}_fmb.xml")

    if xml_source_path.exists():
        try:
            tree = ET.parse(xml_source_path)
            root = tree.getroot()
            
            # Root is usually <Module>, child is <FormModule>
            # Check if root is FormModule or if it's a child
            form_module = None
            if 'FormModule' in root.tag:
                form_module = root
            else:
                # Search for FormModule element, handling namespaces
                form_module = root.find('{http://xmlns.oracle.com/Forms}FormModule') or root.find('FormModule')
            
            if form_module is not None:
                extracted_title = form_module.get('Title')
                if extracted_title:
                    form_title = extracted_title
                
                extracted_comment = form_module.get('Comment')
                if extracted_comment:
                    form_comment = extracted_comment
                
                # Fallback if comment is same as title or empty
                if form_comment == form_title or not form_comment.strip():
                   form_comment = f"{form_title}. (Extracted from Form Title)"
                   
                # Extract Basic Components (Blocks, Canvases, Windows, Triggers, ProgramUnits)
                # Note: XML tags likely have namespace {http://xmlns.oracle.com/Forms}
                ns = {'f': 'http://xmlns.oracle.com/Forms'}
                
                # Helper to get list of names
                def get_names(element, tag_name):
                    # Try with namespace
                    items = element.findall(f"f:{tag_name}", ns)
                    if not items:
                        # Try without namespace (if namespace striping happened or different parser behavior)
                        items = element.findall(tag_name)
                    return sorted([i.get('Name') for i in items if i.get('Name')])

                blocks = get_names(form_module, 'Block')
                canvases = get_names(form_module, 'Canvas')
                windows = get_names(form_module, 'Window')
                triggers = get_names(form_module, 'Trigger')
                program_units = get_names(form_module, 'ProgramUnit')
                
                # Format for Markdown
                def format_list(items):
                    if not items: return "None Detected"
                    return ", ".join([f"`{i}`" for i in items])
                    
                blocks_str = format_list(blocks)
                canvases_str = format_list(canvases)
                windows_str = format_list(windows)
                triggers_str = format_list(triggers)
                pus_str = format_list(program_units)

        except Exception as e:
            print(f"  Warning: Could not parse XML file '{xml_source_path}' for metadata: {e}")
            blocks_str = canvases_str = windows_str = triggers_str = pus_str = "TBD"
    else:
        # Only warn if a specific file was requested but not found
        if source_file:
            print(f"  Info: XML source file '{xml_source_path}' not found for metadata extraction.")
        blocks_str = canvases_str = windows_str = triggers_str = pus_str = "TBD"

    # Populate Template
    # We use simple string replacement for robustness against template changes
    content = template
    
    # Header & Metadata
    content = content.replace("[ID]", obj_id)
    content = content.replace("[Form Title]", form_title) # Used extracted title
    content = content.replace("[Form ID]", obj_id)
    content = content.replace("[Form ID lower]", obj_id.lower())
    content = content.replace("[Form Type]", obj_type)
    content = content.replace("[Analysis Status]", "Stub (Generated)")
    
    # Application Context
    # Use .env variables if explicit object app code is missing or generic
    env_acronym = os.getenv("APP_ACRONYM", "APP")
    env_name = os.getenv("APP_NAME", "Application")
    
    app_code = obj_app if obj_app and obj_app != "APP" else env_acronym
    content = content.replace("[App Code]", app_code)
    content = content.replace("[APP]", app_code)
    
    # App Name resolution
    content = content.replace("[App Name]", env_name)
    
    # Technical Implementation & Source Links
    content = content.replace("[FORM_NAME]", obj_id)
    content = content.replace("(Reference Missing: path)", xml_link)
    content = content.replace("(Reference Missing: [Form ID lower]-FormModule.md)", xml_link)
    content = content.replace("(Reference Missing: [Form ID lower]_fmb.xml)", f"../../oracle-forms-markdown/XML/{obj_id.lower()}_fmb.xml")
    content = content.replace("(Reference Missing: [ID].png)", f"../../diagrams/screens/{obj_id}.png")
    
    # Clean up other placeholders with TBD/None
    # If we have a comment, override the instructions placeholder
    if form_comment != "TBD":
         content = content.replace("[High-level summary of the form's purpose, primary users, and critical nature. E.g., \"Central Court Inquiry screen used by courts, crown, and RCC staff...\"]", form_comment)
         content = content.replace("[Brief summary of what the form does, who uses it, and its business value.]", form_comment)
    
    content = content.replace("[High-level summary of the form's purpose...]", "Pending analysis.")
    content = content.replace("[Detailed description of functionality...]", "Pending analysis.")
    
    # Technical Components
    # Inject into "Functionality" section since specific placeholders don't exist in the template
    
    tech_summary = f"""
### Recovered Technical Components
*   **Blocks**: {blocks_str}
*   **Canvases**: {canvases_str}
*   **Windows**: {windows_str}
*   **Form Triggers**: {triggers_str}
*   **Program Units**: {pus_str}
"""
    
    if "## Functionality" in content:
        content = content.replace("## Functionality", f"## Functionality\n{tech_summary}")
    else:
        # Fallback: Append to end if header missing
        content += f"\n\n{tech_summary}"

    content = content.replace("[ROLE_NAME]", "TBD")
    content = content.replace("(Reference Missing: role_name.md)", "#")
    content = content.replace("LEGACY_ROLE", "TBD")
    content = content.replace("[Link to Functional Spec if available]", "TBD")
    content = content.replace("[Access Description]", "TBD")
    content = content.replace("[Description]", "TBD")
    content = content.replace("[Condition]", "TBD")
    content = content.replace("[Effect]", "TBD")
    content = content.replace("[Logic]", "TBD")
    content = content.replace("[Source]", "TBD")
    content = content.replace("[List]", "TBD")
    content = content.replace("[Param List Name]", "TBD")
    content = content.replace("[Call_Form Procedure Name]", "TBD")
    content = content.replace("[Menu Path]", "TBD")
    
    # Table Placeholders - Clean up row examples
    content = content.replace("[PARENT_ID] (Reference Missing: PARENT_ID-Overview.md)", "None Detected")
    content = content.replace("[CHILD_ID] (Reference Missing: CHILD_ID-Overview.md)", "None Detected")
    content = content.replace("[LIBNAME] (Reference Missing: LIBNAME-Library-Overview.md)", "None Detected")
    content = content.replace("[PKG_NAME] (Reference Missing: PKG_NAME.md)", "None Detected")
    content = content.replace("[MENU_ITEM]", "TBD")
    content = content.replace("[BUTTON]", "TBD")
    # Clean up any remaining Reference Missing tags that might be generic
    content = content.replace("(Reference Missing: ", "(Missing: ")
    
    # Ensure directory exists
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Force overwrite if target is specified (handled by caller logic usually, but here we just write)
    if target_path.exists():
         pass 

    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return target_path

def resolve_object_from_file(file_path, manifest):
    """Derive Object ID and Metadata from filename."""
    path = Path(file_path)
    filename = path.name
    # Expected formats: ID_fmb.xml, ID_pdf.xml, ID.xml
    
    stem = path.stem # e.g. jcsm0001_fmb
    
    # Remove common suffixes case-insensitively
    suffixes = ['_fmb', '_mmb', '_olb', '_pll']
    clean_stem = stem
    for s in suffixes:
        if clean_stem.lower().endswith(s):
            clean_stem = clean_stem[:-len(s)]
            break
            
    obj_id = clean_stem.upper()
    
    # Try to find in manifest
    matching = [x for x in manifest if x['ObjectID'] == obj_id]
    if matching:
        return matching[0]
    
    # If not in manifest, synthesize a default object
    print(f"Warning: Object ID '{obj_id}' derived from file not found in manifest. Using default metadata.")
    return {
        "ObjectID": obj_id,
        "ObjectName": f"{obj_id} (From File)",
        "Application": os.getenv("APP_ACRONYM", "APP"),
        "Type": "FORM", # Assumption based on XML for form
        "DocumentationStatus": "Missing"
    }

def main():
    parser = argparse.ArgumentParser(description="Batch generate form overviews from template.")
    parser.add_argument("--target", help="Specific Form ID to generate/update (e.g. JCSM0000)")
    parser.add_argument("--file", help="Path to XML file to generate overview for (derives ID from filename)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files (not fully implemented yet, mostly placeholder logic)")
    args = parser.parse_args()

    if not MANIFEST_PATH.exists():
        print(f"Error: Manifest not found at {MANIFEST_PATH}")
        return

    template_content = load_template()
    if not template_content:
        return

    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    to_process = []

    # Priority: File > Target > Missing (Batch)
    # Auto-Discovery: Scan XML directory and update manifest
    print(f"Scanning {XML_FORMS_DIR} for Forms (*_fmb.xml)...")
    found_files = list(XML_FORMS_DIR.glob('*_fmb.xml'))
    manifest_updated = False
    
    for xml_file in found_files:
        # derive ID
        stem = xml_file.stem
        if stem.lower().endswith('_fmb'):
            obj_id = stem[:-4].upper()
        else:
             obj_id = stem.upper()
             
        # Check if exists
        exists = any(x['ObjectID'] == obj_id for x in manifest)
        if not exists:
            print(f"  Discovered new Form: {obj_id} ({xml_file.name})")
            new_entry = {
                "ObjectID": obj_id,
                "ObjectName": f"{obj_id} (Discovered)",
                "Application": os.getenv("APP_ACRONYM", "APP"),
                "Type": "FORM",
                "DocumentationStatus": "Missing",
                "SourceAvailable": True
            }
            manifest.append(new_entry)
            manifest_updated = True

    if manifest_updated:
        print("Syncing manifest with discovered forms...")
        with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)

    to_process = []

    # Priority: File > Target > Missing (Batch)
    if args.file:
        obj = resolve_object_from_file(args.file, manifest)
        if obj:
            # Type check
            if obj.get('Type', '').upper() != 'FORM':
                print(f"Skipping {obj['ObjectID']}: Type is '{obj.get('Type')}', expected 'FORM'.")
            else:
                print(f"Derived target '{obj['ObjectID']}' from file: {args.file}")
                to_process = [obj]
    elif args.target:
        # If target specified, ignore "Missing" status and just process the target
        matching = [x for x in manifest if x['ObjectID'].upper() == args.target.upper()]
        if not matching:
             print(f"Target '{args.target}' not found in manifest.")
             return
        # Filter for FORM type
        to_process = [x for x in matching if x.get('Type', '').upper() == 'FORM']
        if not to_process:
             print(f"Target '{args.target}' found but is not a FORM.")
        else:
             print(f"Generating overview for target: {args.target}...")
    else:
        # Default batch behavior: process all FORMS (Missing or Stub) to ensure coverage
        # We can filter for Missing to be efficient, or just run all. 
        # Let's stick to Missing + Stub to allow updates
        to_process = [x for x in manifest if x.get('Type', '').upper() == 'FORM']
        print(f"Found {len(to_process)} Forms in manifest. Processing...")

    created_count = 0
    for obj in to_process:
        # Safety Check: Do not overwrite if status indicates existing work, unless forced
        current_status = obj.get('DocumentationStatus', 'Missing')
        if current_status != 'Missing' and not args.overwrite:
            print(f"Skipping {obj['ObjectID']} (Status: {current_status}). Use --overwrite to force.")
            continue
            
        path = generate_overview(obj, template_content, source_file=args.file if args.file else None)
        if path:
            created_count += 1
            print(f"Created/Updated: {os.path.basename(path)}")
            # Update manifest status in memory
            obj['DocumentationStatus'] = 'Stub'

    print(f"Generation complete. Processed {created_count} files.")
    
    # Save Manifest if changes were made
    if created_count > 0:
        print("Updating manifest documentation status...")
        try:
             with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
                 json.dump(manifest, f, indent=2)
             print(f"Manifest updated: {MANIFEST_PATH}")
        except Exception as e:
             print(f"Error updating manifest: {e}")

if __name__ == "__main__":
    main()
