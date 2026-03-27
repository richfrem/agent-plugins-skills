#!/usr/bin/env python3
"""
batch_process_reports.py (CLI)
=====================================

Purpose:
    Orchestrates ReportMiner for batch report documentation.

Layer: Curate / Documentation

Usage Examples:
    python plugins/legacy-system-oracle-reports/scripts/batch_process_reports.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - load_inventory(): No description.
    - generate_queries_section(): No description.
    - generate_parameters_section(): No description.
    - generate_triggers_section(): No description.
    - generate_libraries_section(): No description.
    - generate_db_objects_section(): No description.
    - process_all(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import glob
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
REPORTS_DIR = str(PROJECT_ROOT / 'legacy-system' / 'oracle-forms' / 'Reports')
OUTPUT_DIR = str(PROJECT_ROOT / 'legacy-system' / 'oracle-forms-overviews' / 'reports')
MINER_PATH = SCRIPT_DIR / 'report_miner.py'
INVENTORY_FILE = str(PROJECT_ROOT / 'legacy-system' / 'reference-data' / 'inventories' / 'forms_and_reports_inventory.json')

# Import Miner
spec = importlib.util.spec_from_file_location("report_miner", MINER_PATH)
report_miner = importlib.util.module_from_spec(spec)
sys.modules["report_miner"] = report_miner
spec.loader.exec_module(report_miner)
ReportMiner = report_miner.ReportMiner

TEMPLATE = """# {id} - Report Overview

## Purpose
**{name}**.

## Data Sources (SQL)
{queries_section}

## Parameters

| Name | Datatype | Width | Label |
|---|---|---|---|
{parameters_section}

## Program Units & Triggers

{triggers_section}

## Dependencies

### Attached Libraries
{libraries_section}

### Database Objects
{db_objects_section}
"""

def load_inventory():
    if not os.path.exists(INVENTORY_FILE):
        print("Warning: Inventory file not found.")
        return {}
    try:
        with open(INVENTORY_FILE, 'r') as f:
            data = json.load(f)
        # Map ID -> Title
        return {item.get('OBJECT_ID'): item.get('OBJECT_TITLE') for item in data if item.get('OBJECT_ID')}
    except Exception as e:
        print(f"Error loading inventory: {e}")
        return {}

def generate_queries_section(queries):
    if not queries:
        return "None Detected."
    
    sections = []
    for q in queries:
        sql = q.get('SQL', '')
        # Basic cleanup - CDATA usually handled by parser but check
        if sql.startswith('<![CDATA['):
            sql = sql.replace('<![CDATA[', '').replace(']]>', '')
        
        sections.append(f"### Query: {q.get('Name')}\n```sql\n{sql}\n```")
    return "\n\n".join(sections)

def generate_parameters_section(params):
    if not params:
        return "| None | - | - | - |"
    
    rows = []
    for p in params:
        rows.append(f"| {p.get('Name')} | {p.get('Datatype')} | {p.get('Width', '-')} | {p.get('Label', '-')} |")
    return "\n".join(rows)

def generate_triggers_section(triggers):
    if not triggers:
        return "None Detected."
    
    sections = []
    
    formulas = [t for t in triggers if 'formula' in (t.get('Name') or '').lower()]
    others = [t for t in triggers if t not in formulas]
    
    if others:
        sections.append("### Triggers")
        for t in others:
            sections.append(f"*   **{t.get('Name')}**: ({t.get('Type')})")
    
    if formulas:
        sections.append("\n### Formulas")
        for f in formulas:
            sections.append(f"*   **{f.get('Name')}**: Formula")

    return "\n".join(sections)

def generate_libraries_section(libs):
    if not libs:
        return "None Detected."
    return "\n".join([f"*   [{lib.upper()}]" for lib in libs])

def generate_db_objects_section(queries):
    # Simple regex extraction for PROJECT_ tables/packages
    all_sql = " ".join([q.get('SQL', '') for q in queries])
    matches = set(re.findall(r'\b(PROJECT_[A-Z0-9_]+)', all_sql.upper()))
    if not matches:
        return "None Detected (or unable to parse from SQL)."
    
    return "\n".join([f"*   [{m}]" for m in sorted(matches)])

def process_all():
    files = sorted(glob.glob(os.path.join(REPORTS_DIR, "*.xml")))
    print(f"Found {len(files)} report files.")
    
    inventory = load_inventory()
    
    for fpath in files:
        fname = os.path.basename(fpath)
        print(f"Processing {fname}...")
        
        try:
            miner = ReportMiner()
            miner.analyze(fpath)
            data = miner.metadata
            
            # Determine Name/Title
            # 1. Inventory
            # 2. Heuristic (from miner)
            # 3. ID
            inv_title = inventory.get(data['ID'])
            heuristic_title = data.get('Name') # Miner sets Name to heuristic if found, else ID
            
            final_title = data['ID']
            if inv_title and inv_title != data['ID']:
                final_title = inv_title
            elif heuristic_title and heuristic_title != data['ID']:
                final_title = heuristic_title
                
            content = TEMPLATE.format(
                id=data['ID'],
                name=final_title,
                queries_section=generate_queries_section(data['Queries']),
                parameters_section=generate_parameters_section(data['Parameters']),
                triggers_section=generate_triggers_section(data['Triggers']),
                libraries_section=generate_libraries_section(data['AttachedLibraries']),
                db_objects_section=generate_db_objects_section(data['Queries'])
            )
            
            out_path = os.path.join(OUTPUT_DIR, f"{data['ID']}-Report-Overview.md")
            with open(out_path, 'w') as out:
                out.write(content)
        except Exception as e:
            print(f"Error processing {fname}: {e}")
            
if __name__ == "__main__":
    process_all()