#!/usr/bin/env python3
"""
validate_counts.py (CLI)
=====================================

Purpose:
    Counts and validates legacy system artifacts (Forms, Reports, Menus, OLBs, PLLs, DB packages, etc.) across all source directories. Excludes AG* prefixed files and outputs a summary table showing found, valid, and ignored counts per type.

Layer: Curate / Curate

Usage Examples:
    python tools\curate\inventories\validate_counts.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - should_ignore(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import glob
from pathlib import Path

CWD = os.getcwd()

EXCLUDED_PREFIXES = (
    'AGE', 'AGM', 'AGT', 'APPLE', 'AGLOGON', 'AGMSG', 
    'AGNOMENU', 'AGOBJECTS', 'APPLJ', 'APPLQ'
)

def should_ignore(name):
    return name.upper().startswith(EXCLUDED_PREFIXES)

DIRECTORIES = {
    'FORM': (os.path.join(CWD, 'legacy-system', 'oracle-forms-markdown', 'XML'), '*.md', '_fmb'), # Adjust ID extraction
    'REPORT': (os.path.join(CWD, 'legacy-system', 'oracle-forms', 'Reports'), '*.xml', ''),
    'MENU': (os.path.join(CWD, 'legacy-system', 'oracle-forms', 'XML'), '*_mmb.xml', '_mmb'),
    'OLB': (os.path.join(CWD, 'legacy-system', 'oracle-forms', 'XML'), '*_olb.xml', '_olb'),
    'PLL': (os.path.join(CWD, 'legacy-system', 'oracle-forms', 'pll'), '*.txt', ''),
    'DB_PKG': (os.path.join(CWD, 'legacy-system', 'oracle-database', 'source', 'Packages'), '*.sql', ''),
    'DB_PROC': (os.path.join(CWD, 'legacy-system', 'oracle-database', 'Procedures'), '*.sql', ''),
    'DB_FUNC': (os.path.join(CWD, 'legacy-system', 'oracle-database', 'Functions'), '*.sql', ''),
    'DB_VIEW': (os.path.join(CWD, 'legacy-system', 'oracle-database', 'Views'), '*.sql', ''),
    'DB_TABLE': (os.path.join(CWD, 'legacy-system', 'oracle-database', 'Tables'), '*.sql', ''),
    'DB_TRIG': (os.path.join(CWD, 'legacy-system', 'oracle-database', 'Triggers'), '*.sql', ''),
    'DB_TYPE': (os.path.join(CWD, 'legacy-system', 'oracle-database', 'Types'), '*.sql', ''),
    'DB_SEQ': (os.path.join(CWD, 'legacy-system', 'oracle-database', 'Sequences'), '*.sql', ''),
    'DB_IND': (os.path.join(CWD, 'legacy-system', 'oracle-database', 'Indexes'), '*.sql', ''),
    'DB_CONST': (os.path.join(CWD, 'legacy-system', 'oracle-database', 'Constraints'), '*.sql', ''),
}

print(f"{'TYPE':<12} | {'FOUND':<6} | {'VALID':<6} | {'IGNORED':<8}")
print("-" * 40)

total_valid = 0

for key, (path, pattern, suffix) in DIRECTORIES.items():
    if not os.path.exists(path):
        print(f"{key:<12} | - | - | - (Dir Missing: {path})")
        continue
        
    found = 0
    valid = 0
    ignored = 0
    
    # Use glob or listdir
    # glob is case sensitive on some OS, but Windows is usually forgiving.
    # We will use listdir + endswith for safety matching the script logic
    ext = pattern.replace('*', '') # .xml, .sql, etc
    
    # Special handling for patterns with prefix like *_mmb.xml not handled perfectly by simple ext replace
    # But for count, simple glob is close enough or use explicit listdir logic
    
    files = []
    if '*' in pattern:
        # manual glob logic
        suffix_pat = pattern.replace('*.', '.').replace('*', '') # _mmb.xml
        files = [f for f in os.listdir(path) if f.lower().endswith(suffix_pat.lower())]
    else:
        files = os.listdir(path)
        
    found = len(files)
    
    for f in files:
        # Extract ID
        f_lower = f.lower()
        id_str = f
        if suffix:
            # Handle .xml.txt case or simple extension
            # The script uses replace(suffix + ext, '') logic roughly
            # e.g. replace('_mmb.xml', '')
            
            # Remove extension first?
            # The pattern passed in DIRECTORIES for suffix is mostly the part to strip e.g. '_mmb'
            # But script does replace('_mmb.xml', '')
            
            # Dirty ID extraction for check
            clean_name = f_lower.replace('.xml','').replace('.sql','').replace('.txt','').replace('.md','')
            if suffix.startswith('_'):
                 clean_name = clean_name.replace(suffix, '')
            
            obj_id = clean_name.upper()
        else:
             obj_id = os.path.splitext(f)[0].upper()
             
        if should_ignore(obj_id):
            ignored += 1
        else:
            valid += 1
            
    print(f"{key:<12} | {found:<6} | {valid:<6} | {ignored:<8}")
    total_valid += valid

print("-" * 40)
print(f"TOTAL VALID SYSTEM OBJECTS: {total_valid}")
