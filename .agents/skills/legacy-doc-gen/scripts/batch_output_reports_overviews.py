#!/usr/bin/env python3
"""
[SKILL_ROOT]/scripts/batch_output_reports_overviews.py (CLI)
=======================================

Purpose:
    Creates placeholder overview documentation for missing reports
    using the standard report template.

Layer: Curate / Documentation

Usage Examples:
    python [SKILL_ROOT]/scripts/batch_output_reports_overviews.py
    python [SKILL_ROOT]/scripts/batch_output_reports_overviews.py --file [PROJECT_ROOT]/legacy-system/oracle-forms/Reports/rccr001.xml

Supported Object Types:
    - Reports

CLI Arguments:
    --target: Specific Report ID to generate/update (e.g. RCC001)
    --file: Path to a specific XML file to generate overview for (derives ID from filename)
    --overwrite: Overwrite existing files

Input Files:
    - [PROJECT_ROOT]/legacy-system/reference-data/legacy_object_manifest.json
    - [SKILL_ROOT]/assets/templates/report-overview-template.md
    - .env (Required for APP_ACRONYM and APP_NAME)
    - [Optional] XML file path provided via --file

Output:
    - legacy-system/oracle-forms-overviews/reports/[ID]-Overview.md
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
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

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
XML_REPORTS_DIR = PROJECT_ROOT / 'legacy-system' / 'oracle-forms' / 'Reports' # Default location
MANIFEST_PATH = PROJECT_ROOT / 'legacy-system' / 'reference-data' / 'legacy_object_manifest.json'
TEMPLATE_PATH = SCRIPT_DIR.parent / 'assets' / 'templates' / 'report-overview-template.md'

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
    
    target_dir = REPORTS_DIR
    target_path = target_dir / f"{obj_id}-Overview.md"
    
    # Extract Metadata from XML if available
    report_title = obj_name
    report_comment = "TBD"
    
    # Component Lists
    queries_str = "TBD"
    groups_str = "TBD"
    params_str = "TBD"
    triggers_str = "TBD"
    pus_str = "TBD"

    # Determine XML Source Path
    xml_sources = []
    if source_file:
        xml_sources.append(Path(source_file))
    else:
        # Try both flat and XML subdir
        xml_sources.append(XML_REPORTS_DIR / f"{obj_id.lower()}.xml")
        xml_sources.append(XML_REPORTS_DIR / f"{obj_id.lower()}_rdf.xml")
        xml_sources.append(XML_REPORTS_DIR / "XML" / f"{obj_id.lower()}.xml")

    xml_source_path = None
    for p in xml_sources:
        if p.exists():
            xml_source_path = p
            break
            
    if xml_source_path:
        try:
            tree = ET.parse(xml_source_path)
            root = tree.getroot()
            
            # Root is usually <Report> or <p:Report>
            # Namespace handling
            # Oracle Reports XML often uses default namespace or 'report'
            # We'll try to be namespace agnostic or define common ones
            # Common: xmlns="http://xmlns.oracle.com/Reports"
            
            ns = {'r': 'http://xmlns.oracle.com/Reports'}
            
            # Helper to find elements/attributes
            def get_attr(element, attr_name):
                 return element.get(attr_name, element.get(attr_name.lower()))

            # Extract Title/Comment from root
            if root.tag.endswith('Report'):
                extracted_title = get_attr(root, 'Title')
                if extracted_title: report_title = extracted_title
                
                extracted_comment = get_attr(root, 'Comment')
                if extracted_comment: report_comment = extracted_comment
            
            # Extract Components
            def get_names(parent, tag_name):
                # Try finding all descendants with tag name, ignoring namespace for simplicity
                # This is a bit rough but works for simple XMLs where tag names are unique enough
                items = []
                for elem in parent.iter():
                    if elem.tag.endswith(tag_name):
                        name = get_attr(elem, 'Name')
                        if name: items.append(name)
                return sorted(list(set(items)))

            queries = get_names(root, 'Query')
            groups = get_names(root, 'Group')
            params = get_names(root, 'Parameter')
            triggers = get_names(root, 'ReportTrigger')
            program_units = get_names(root, 'ProgramUnit')
            
            def format_list(items):
                if not items: return "None Detected"
                return ", ".join([f"`{i}`" for i in items])

            queries_str = format_list(queries)
            groups_str = format_list(groups)
            params_str = format_list(params)
            triggers_str = format_list(triggers)
            pus_str = format_list(program_units)

        except Exception as e:
            print(f"  Warning: Could not parse Report XML '{xml_source_path}': {e}")
    else:
         if source_file:
             print(f"  Info: Report XML '{source_file}' not found.")

    # Populate Template
    content = template
    
    # Application Context
    env_acronym = os.getenv("APP_ACRONYM", "APP")
    app_code = obj_app if obj_app and obj_app != "APP" else env_acronym
    
    # Header & Metadata
    content = content.replace("{REPORT_NAME}", report_title)
    content = content.replace("{REPORT_ID}", obj_id)
    content = content.replace("{filename}", obj_id.lower())
    
    content = content.replace("{APPLICATION}", app_code)
    content = content.replace("{DATE}", datetime.now().strftime('%Y-%m-%d'))
    
    # Purpose
    if report_comment != "TBD":
        content = content.replace("{Brief description of the report's purpose and when it is generated.}", report_comment)
        
    # Inject Technical Summary into Notes or Purpose if not fully replaced
    tech_summary = f"""
### Recovered Technical Components
*   **Queries**: {queries_str}
*   **Groups**: {groups_str}
*   **Parameters**: {params_str}
*   **Triggers**: {triggers_str}
*   **Program Units**: {pus_str}
"""
    # Append to Notes
    if "{Any additional observations or migration considerations.}" in content:
         content = content.replace("{Any additional observations or migration considerations.}", f"Pending analysis.\n{tech_summary}")
    else:
         content += f"\n\n## Technical Inventory\n{tech_summary}"

    # Parameters Table Injection (Partial)
    if params_str != "TBD" and params_str != "None Detected":
        # We can't easily replace the table rows without more complex parsing, 
        # but we can list them in the description column or just leave the TBD row and rely on the summary.
        # Let's replace {PARAM_NAME} with the first param or "See Technical Inventory"
        content = content.replace("{PARAM_NAME}", "See Tech Inventory")
    else:
       content = content.replace("{PARAM_NAME}", "TBD")

    # Clean up other placeholders
    content = content.replace("{TABLE_NAME}", "TBD")
    content = content.replace("{PURPOSE}", "TBD")
    content = content.replace("{JOIN}", "TBD")
    content = content.replace("{TYPE}", "TBD")
    content = content.replace("{DESCRIPTION}", "TBD")
    content = content.replace("{List key columns in the report output}", "TBD")
    content = content.replace("{List any business rules or filters applied during report generation.}", "Pending analysis.")
    content = content.replace("{Roles required to run this report}", "TBD")
    content = content.replace("{Any row-level security applied}", "TBD")
    content = content.replace("{Forms that trigger this report}", "TBD")
    content = content.replace("{DB Packages used for data retrieval}", "TBD")
    content = content.replace("{Brief description of the report's purpose and when it is generated.}", "Pending analysis.")

    # Ensure directory exists
    target_dir.mkdir(parents=True, exist_ok=True)
    
    if target_path.exists():
         pass 

    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return target_path

def resolve_object_from_file(file_path, manifest):
    """Derive Object ID and Metadata from filename."""
    path = Path(file_path)
    filename = path.name
    
    stem = path.stem
    
    # Remove common suffixes case-insensitively
    suffixes = ['_fmb', '_rdf', '.xml', '_rep'] 
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
        "Type": "REPORT",
        "DocumentationStatus": "Missing"
    }

def main():
    parser = argparse.ArgumentParser(description="Batch generate report overviews from template.")
    parser.add_argument("--target", help="Specific Report ID to generate/update (e.g. RCC001)")
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

    # Auto-Discovery: Scan Reports directory
    # We look for .xml files in XML_REPORTS_DIR
    # Typical patterns: ID.xml, ID_rdf.xml, or in specific subfolders
    print(f"Scanning {XML_REPORTS_DIR} for Reports (*.xml)...")
    
    # Simple recursive scan or just top level? Let's check top and one level down 'XML' if exists
    found_files = list(XML_REPORTS_DIR.glob('*.xml'))
    found_files.extend(list(XML_REPORTS_DIR.glob('*_rdf.xml')))
    found_files.extend(list((XML_REPORTS_DIR / 'XML').glob('*.xml')))
    
    # Deduplicate by path
    found_files = list(set(found_files))
    
    manifest_updated = False
    
    for xml_file in found_files:
        # derive ID
        stem = xml_file.stem
        # clean suffixes
        clean_stem = stem
        for s in ['_rdf', '_rep']:
             if clean_stem.lower().endswith(s):
                 clean_stem = clean_stem[:-len(s)]
        
        obj_id = clean_stem.upper()
             
        # Check if exists
        exists = any(x['ObjectID'] == obj_id for x in manifest)
        if not exists:
            print(f"  Discovered new Report: {obj_id} ({xml_file.name})")
            new_entry = {
                "ObjectID": obj_id,
                "ObjectName": f"{obj_id} (Discovered)",
                "Application": os.getenv("APP_ACRONYM", "APP"), 
                "Type": "REPORT",
                "DocumentationStatus": "Missing",
                "SourceAvailable": True
            }
            manifest.append(new_entry)
            manifest_updated = True

    if manifest_updated:
        print("Syncing manifest with discovered reports...")
        with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)

    to_process = []

    # Priority: File > Target > Missing (Batch)
    if args.file:
        obj = resolve_object_from_file(args.file, manifest)
        if obj:
            # Type check
            if obj.get('Type', '').upper() != 'REPORT':
                print(f"Skipping {obj['ObjectID']}: Type is '{obj.get('Type')}', expected 'REPORT'.")
            else:
                print(f"Derived target '{obj['ObjectID']}' from file: {args.file}")
                to_process = [obj]
    elif args.target:
        # If target specified, ignore "Missing" status and just process the target
        matching = [x for x in manifest if x['ObjectID'].upper() == args.target.upper()]
        if not matching:
             print(f"Target '{args.target}' not found in manifest.")
             return
        # Filter for REPORT type
        to_process = [x for x in matching if x.get('Type', '').upper() == 'REPORT']
        if not to_process:
             print(f"Target '{args.target}' found but is not a REPORT.")
        else:
             print(f"Generating overview for target: {args.target}...")
    else:
        # Default batch behavior: process all REPORTS (Missing or Stub)
        to_process = [x for x in manifest if x.get('Type', '').upper() == 'REPORT']
        print(f"Found {len(to_process)} Reports in manifest. Processing...")

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
