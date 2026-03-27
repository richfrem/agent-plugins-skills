#!/usr/bin/env python3
"""
split_sql_dump.py (CLI)
=====================================

Purpose:
    Parses raw SQL scripts (dumps or distinct files) and extracts distinct Oracle Database objects 
    (Procedures, Functions, Packages, Views, Triggers, Types) into their canonical 
    'legacy-system/oracle-database/{Type}' folders.

    This is critical for "bootstrapping" raw DB dumps into the granulated structure required 
    by the Granular Analysis Agent.

Layer: Curate / Utils

Usage Examples:
    python plugins/legacy-system-database/scripts/split_sql_dump.py --source legacy-system/oracle-database/rawscripts
    python plugins/legacy-system-database/scripts/split_sql_dump.py --source legacy-system/oracle-database/rawscripts --out legacy-system/oracle-database

CLI Arguments:
    --source        : Path to raw SQL file or directory containing .sql files (Required)
    --out           : Base output directory (Default: legacy-system/oracle-database)
    --dry-run       : If set, identifies objects but does not write files.

Supported Object Types:
    - PROCEDURE     -> Procedures/
    - FUNCTION      -> Functions/
    - PACKAGE       -> Packages/
    - PACKAGE BODY  -> Packages/
    - TRIGGER       -> Triggers/
    - VIEW          -> Views/
    - TYPE          -> Types/
    - TABLE         -> Tables/ (DDL)
    - SEQUENCE      -> Sequences/

Output:
    - Individual .sql files named by object (e.g. `MY_PROC.sql`) in categorized folders.
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

# Mapping Oracle Object Types to Folder Names
TYPE_TO_FOLDER = {
    'PROCEDURE': 'Procedures',
    'FUNCTION': 'Functions',
    'PACKAGE': 'Packages',
    'PACKAGE BODY': 'Packages',
    'TRIGGER': 'Triggers',
    'VIEW': 'Views',
    'TYPE': 'Types',
    'TYPE BODY': 'Types',
    'TABLE': 'Tables',
    'SEQUENCE': 'Sequences',
    'INDEX': 'Indexes',
    'CONSTRAINT': 'Constraints'
}

def setup_args():
    parser = argparse.ArgumentParser(description="Split raw SQL dumps into granular object files.")
    parser.add_argument('--source', required=True, help="Input file or directory")
    parser.add_argument('--out', default='legacy-system/oracle-database', help="Output base directory")
    parser.add_argument('--dry-run', action='store_true', help="Preview mode")
    return parser.parse_args()

def extract_objects(sql_content: str) -> List[Tuple[str, str, str]]:
    """
    Splits SQL content into objects based on '/' terminator and CREATE statement patterns.
    Returns list of (ObjectType, ObjectName, FullContent).
    """
    objects = []
    
    # Heuristic: Oracle dumps often separate objects with '/' on a new line.
    # We first split by that, then regex match the CREATE header.
    # If no '/', we assume the file IS the object (if distinct) or try pattern matching.
    
    # Normalize line endings
    content = sql_content.replace('\r\n', '\n')
    
    # Split by slash terminator if present in abundance (>1)
    chunks = []
    if content.count('\n/\n') > 0 or content.endswith('\n/'):
         chunks = re.split(r'\n/\s*\n', content)
    else:
         # Fallback for single object files or missing terminators: 
         # Try global match for CREATE OR REPLACE ...
         # This is harder for nested PL/SQL, so strictly we prefer terminator splitting.
         # For now, treat whole file as one chunk if no slash.
         chunks = [content]

    # Regex to identify object type and name
    # Matches: CREATE [OR REPLACE] [EDITIONABLE] <TYPE> [SCHEMA.]<NAME>
    header_pattern = re.compile(
        r'CREATE\s+'
        r'(?:OR\s+REPLACE\s+)?'
        r'(?:(?:FORCE|NOFORCE)\s+)?'
        r'(?:(?:EDITIONABLE|NONEDITIONABLE)\s+)?'
        r'(PROCEDURE|FUNCTION|PACKAGE(?:\s+BODY)?|TRIGGER|VIEW|TYPE(?:\s+BODY)?|TABLE|SEQUENCE|INDEX)\s+'
        r'(?:(?:"?[\w$]+"?)?\.)?"?([\w$]+)"?', 
        re.IGNORECASE | re.DOTALL
    )

    for chunk in chunks:
        clean_chunk = chunk.strip()
        if not clean_chunk: 
            continue
            
        # Skip SQL*Plus commands (SET DEFINE OFF, PROMPT, etc) at start
        # but keep them if part of logic? usually stripped.
        # heuristic: match the first CREATE
        match = header_pattern.search(clean_chunk)
        if match:
            obj_type = match.group(1).upper()
            obj_name = match.group(2) # Base name from CREATE

            # Refinement: Prioritize casing from the END tag for Packages and Types
            # This captures developer intent (e.g., fis_activities_pkg) vs quoted CREATE case.
            if 'PACKAGE' in obj_type or 'TYPE' in obj_type:
                # Look for "END <name>;" at the very end of the chunk
                # Allowing for optional terminator / and any amount of trailing whitespace/newlines
                end_match = re.search(r'\bEND\s+([a-zA-Z0-9_$]+)\s*;?\s*(?:/\s*)?\s*\Z', clean_chunk, re.IGNORECASE)
                if end_match:
                    end_name = end_match.group(1)
                    if end_name.upper() == obj_name.upper():
                        obj_name = end_name
            
            # Normalize TYPE BODY to TYPE for folder mapping, but simplify logic:
            # We keep distinct TYPES in logic, map in folder.
            
            objects.append((obj_type, obj_name, clean_chunk + "\n/\n"))
        else:
            pass # Skipping unknown chunks or anon blocks
            
    return objects

class ProcessReport:
    def __init__(self):
        self.entries = []

    def add(self, source_file, status, detail):
        self.entries.append({
            'source_file': source_file,
            'status': status,
            'detail': detail
        })

    def save_csv(self, output_path: Path):
        import csv
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['source_file', 'status', 'detail'])
            writer.writeheader()
            writer.writerows(self.entries)
        print(f"\\n📄 Report saved to {output_path}")

def process_file(file_path: Path, out_base: Path, dry_run: bool, report: ProcessReport):
    print(f"Processing {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            
        found_objects = extract_objects(content)
        
        if not found_objects:
            print(f"  ⚠️  [SKIPPED] No identifiable definition (CREATE...) found in {file_path.name}")
            report.add(file_path.name, 'SKIPPED', 'No CREATE statement found')
            return

        extracted_names = []
        for obj_type, obj_name, code in found_objects:
            # Normalize type for folder (e.g. PACKAGE BODY -> Packages)
            folder_key = obj_type
            if 'BODY' in obj_type:
                # e.g. PACKAGE BODY -> PACKAGE -> Packages
                # e.g. TYPE BODY -> TYPE -> Types
                folder_key = obj_type.replace(' BODY', '') 
            
            folder_name = TYPE_TO_FOLDER.get(folder_key, 'Misc')
            dest_dir = out_base / folder_name
            
            file_suffix = ".sql"
            if 'BODY' in obj_type:
                file_suffix = "_body.sql"
            
            dest_file = dest_dir / f"{obj_name}{file_suffix}"
            
            if dry_run:
                print(f"  [Dry Run] Would write {obj_type} {obj_name} -> {dest_file}")
            else:
                dest_dir.mkdir(parents=True, exist_ok=True)
                with open(dest_file, 'w', encoding='utf-8') as out_f:
                    out_f.write(code)
                print(f"  ✓ Extracted {obj_type} {obj_name}")
            
            extracted_names.append(f"{obj_type} {obj_name}")

        report.add(file_path.name, 'SUCCESS', f"Extracted: {', '.join(extracted_names)}")

    except Exception as e:
        print(f"  ❌ Error processing file: {e}")
        report.add(file_path.name, 'ERROR', str(e))

def main():
    args = setup_args()
    
    source = Path(args.source)
    out_base = Path(args.out)
    report = ProcessReport()
    
    print(f"Splitting SQL from: {source}")
    print(f"Target Output:    {out_base}")
    if args.dry_run:
        print("MODE: DRY RUN (No changes)")
    print("-" * 50)
    
    if source.is_file():
        process_file(source, out_base, args.dry_run, report)
    elif source.is_dir():
        for f in source.rglob('*.sql'):
            process_file(f, out_base, args.dry_run, report)
    else:
        print(f"Source {source} not found!")
        exit(1)

    print("\\nDone.")
    report.save_csv(out_base / "splitting_report.csv")

if __name__ == "__main__":
    main()
