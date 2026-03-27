#!/usr/bin/env python3
"""
extract_triggers.py (CLI)
=====================================

Purpose:
    Parses PROJECT_Triggers_clean.sql dump and splits triggers into individual .sql files.

Layer: Curate / Utilities

Usage Examples:
    python plugins/legacy-system-database/scripts/extract_triggers.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - extract_triggers(): Parse the PROJECT_Triggers_clean.sql file and extract CREATE TRIGGER statements.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import re
import os
from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in _SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

def extract_triggers(input_file: str, output_dir: str):
    """
    Parse the PROJECT_Triggers_clean.sql file and extract CREATE TRIGGER statements.
    Each trigger is separated by a '/' on its own line.
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by '/' separator (each trigger ends with 'ALTER TRIGGER ... ENABLE' then '/')
    blocks = content.split('\n/\n')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Pattern to extract trigger name
    trigger_name_pattern = re.compile(
        r'CREATE\s+OR\s+REPLACE\s+(?:EDITIONABLE\s+)?TRIGGER\s+(?:"?\w+"?\.)?"?(\w+)"?',
        re.IGNORECASE
    )
    
    triggers_written = 0
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        match = trigger_name_pattern.search(block)
        if not match:
            continue
        
        trigger_name = match.group(1).upper()
        
        # Clean up and format the DDL
        trigger_ddl = block.strip()
        
        # Remove any leading ALTER TRIGGER statements that might be left over from the previous block
        # due to the way the file is structured (CREATE ... / ALTER ...)
        ddl_lines = trigger_ddl.split('\n')
        cleaned_lines = []
        found_create = False
        for line in ddl_lines:
            if re.search(r'CREATE\s+OR\s+REPLACE', line, re.IGNORECASE):
                found_create = True
            if found_create:
                cleaned_lines.append(line)
        
        if not cleaned_lines:
            continue
            
        trigger_ddl = '\n'.join(cleaned_lines).strip() + '\n/\n'
        
        output_file = Path(output_dir) / f"{trigger_name}.sql"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(trigger_ddl)
        
        triggers_written += 1
    
    print(f"Total triggers extracted: {triggers_written}")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    import sys
    
    # Default paths
    script_dir = _find_project_root()
    input_file = script_dir / "legacy-system/oracle-database/Triggers/FIS_TRIGGERS.sql"
    output_dir = script_dir / "legacy-system/oracle-database/Triggers"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    print(f"Extracting triggers from: {input_file}")
    print(f"Output to: {output_dir}")
    print("-" * 50)
    
    extract_triggers(str(input_file), str(output_dir))
