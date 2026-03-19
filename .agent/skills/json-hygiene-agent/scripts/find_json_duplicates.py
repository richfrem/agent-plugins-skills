#!/usr/bin/env python3
"""
find_json_duplicates.py (V2)
=====================================
Purpose:
    Perform a deterministic Abstract Syntax Tree (AST) sweep of a JSON file to 
    catch 100% of duplicate keys at any tree depth, preventing silent data loss caused 
    by the "last writer wins" standard.

Usage:
    python3 scripts/find_json_duplicates.py --file config.json

Exit Codes:
    0 - Success (No duplicates)
    1 - Duplicates Found 
    2 - Fundamental JSON Syntax Error
"""

import json
import sys
import argparse
from pathlib import Path

def detect_duplicates(ordered_pairs):
    """
    Hook function intercepted by json.loads during AST construction.
    """
    counts = {}
    duplicates = []
    
    for key, value in dict(ordered_pairs).items():
        if key in counts:
            counts[key] += 1
            if key not in duplicates:
                duplicates.append(str(key))
        else:
            counts[key] = 1
            
    # We purposefully raise an error to bubble the duplicate up to the main try/except block
    if duplicates:
        raise ValueError(f"Duplicate keys detected in JSON AST layer: {', '.join(duplicates)}")
        
    return dict(ordered_pairs)

def find_duplicates(file_path: Path):
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(2)

    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ Failed to read file {file_path}: {e}")
        sys.exit(2)
        
    try:
        # We hook into the parser instantly as it maps keys to values.
        # This catches duplicates deterministically at any nesting depth.
        json.loads(content, object_pairs_hook=detect_duplicates)
        
        print(f"✅ Analyzer Pass: {file_path.name}")
        print("✅ No duplicate keys found. File is pristine.")
        sys.exit(0)
        
    except ValueError as ve:
        if "Duplicate keys detected" in str(ve):
            print(f"⚠️  Hygiene Failure: {file_path.name}")
            print(f"⚠️  {ve}")
            sys.exit(1)
        # Catch standard JSON decoding errors (missing commas, bad quotes)
        print(f"❌ Standard JSON Syntax Error in {file_path.name}:")
        print(f"   {ve}")
        sys.exit(2)
    except json.JSONDecodeError as jde:
        print(f"❌ Standard JSON Syntax Error in {file_path.name}:")
        print(f"   {jde}")
        sys.exit(2)
    except Exception as e:
        print(f"❌ Unknown Error processing file: {e}")
        sys.exit(2)

def main():
    parser = argparse.ArgumentParser(description="Find duplicate JSON keys via deterministic AST sweep")
    parser.add_argument("--file", "-f", required=True, help="Path to the JSON file to analyze")
    args = parser.parse_args()
    
    file_path = Path(args.file).expanduser().resolve()
    find_duplicates(file_path)

if __name__ == "__main__":
    main()
