#!/usr/bin/env python3
"""
find_json_duplicates.py
=======================

Purpose:
    Finds duplicate keys in JSON files (e.g., in a dictionary/map structure)
    that standard JSON parsers might silently overwrite (last winner wins).

Usage:
    python3 plugins/json-hygiene/scripts/find_json_duplicates.py --file path/to/file.json

Dependencies:
    None (Standard Library)
"""
import re
import collections
import os
import argparse
from pathlib import Path

def find_duplicates(file_path):
    path = Path(file_path).resolve()
    if not path.exists():
        print(f"❌ File not found: {path}")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex to capture keys that start an object definition like "KEY": {
        # This captures top-level keys for typical config/manifest files.
        # It's a heuristic, not a full parser (since full parsers dedupe automatically).
        keys = re.findall(r'\"([A-Z0-9_.-]+)\"\s*:\s*\{', content)
        
        counts = collections.Counter(keys)
        duplicates = [k for k, v in counts.items() if v > 1]
        
        print(f"🔍 Analyzing: {path.name}")
        if duplicates:
            print(f"⚠️  Found {len(duplicates)} duplicate keys:")
            for k in sorted(duplicates):
                print(f"   - {k} (x{counts[k]})")
        else:
            print("✅ No duplicate keys found (heuristic scan).")
            
    except Exception as e:
        print(f"❌ Error processing file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Find duplicate JSON keys via regex heuristic")
    parser.add_argument("--file", "-f", required=True, help="Path to the JSON file to analyze")
    args = parser.parse_args()
    
    find_duplicates(args.file)

if __name__ == "__main__":
    main()
