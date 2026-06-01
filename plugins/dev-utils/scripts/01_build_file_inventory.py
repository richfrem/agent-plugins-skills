#!/usr/bin/env python
"""
01_build_file_inventory.py (CLI)
=====================================

Purpose:
    Mapper: Indexes the entire repository to create a file inventory for link fixing.
    This is Phase 1 of the Link Checker pipeline.

Usage:
    python01_build_file_inventory.py --root .

Output:
    - file_inventory.json: Mapping of filename -> [list of relative paths]
"""
import os
import json
import argparse
from typing import Dict, List

def generate_file_map(root_dir: str, extra_excludes: List[str] = None) -> Dict[str, List[str]]:
    """
    Scans the directory structure and maps filenames to their relative paths.
    """
    file_map = {}
    
    # Default excludes
    excludes = {'.git', 'node_modules', '.venv', '.next', 'bin', 'obj', '.agents', '.gemini', '__pycache__'}
    if extra_excludes:
        excludes.update(extra_excludes)
    
    print(f"Mapping files in: {os.path.abspath(root_dir)}")
    
    for root, dirs, files in os.walk(root_dir):
        # Prune excludes in place
        dirs[:] = [d for d in dirs if d not in excludes]
        
        for filename in files:
            # Skip common noise files
            if filename in {'.DS_Store', 'Thumbs.db'}:
                continue
                
            try:
                if filename not in file_map:
                    file_map[filename] = []
                
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, root_dir).replace('\\', '/')
                file_map[filename].append(rel_path)
            except Exception as e:
                print(f"  Error mapping {filename}: {e}")
                continue
            
    return file_map

def main() -> None:
    parser = argparse.ArgumentParser(description="Step 1: Build repository file inventory.")
    parser.add_argument("--root", default=".", help="Root directory to scan (default: current)")
    parser.add_argument("--output", default="file_inventory.json", help="Output JSON file name")
    args = parser.parse_args()

    root_dir = args.root
    file_map = generate_file_map(root_dir)
    
    # Save in current directory
    output_path = args.output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(file_map, f, indent=2)
        
    print(f"✅ Inventory saved to {output_path}. Mapped {len(file_map)} unique filenames.")

if __name__ == "__main__":
    main()
