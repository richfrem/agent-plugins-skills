#!/usr/bin/env python3
"""
map_repository_files.py (CLI)
=====================================

Purpose:
    Mapper: Indexes the entire repository to create a file inventory for link fixing.

Layer: Curate / Cli_Entry_Points

Usage Examples:
    python plugins/link-checker/scripts/map_repository_files.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - generate_file_map(): Scans the directory structure and maps filenames to their relative paths.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import json
from typing import Dict, List

def generate_file_map(root_dir: str) -> Dict[str, List[str]]:
    """
    Scans the directory structure and maps filenames to their relative paths.

    Args:
        root_dir: The root directory to start scanning.

    Returns:
        Dictionary where keys are filenames and values are lists of relative paths.
    """
    file_map = {}
    
    #Dirs to exclude
    excludes = {'.git', 'node_modules', '.venv', '.next', 'bin', 'obj'}
    
    print(f"Mapping files in {root_dir}...")
    
    for root, dirs, files in os.walk(root_dir):
        # Prune excludes in place
        dirs[:] = [d for d in dirs if d not in excludes]
        
        for filename in files:
            try:
                # Map filename to list of full paths (handling duplicates)
                if filename not in file_map:
                    file_map[filename] = []
                
                full_path = os.path.join(root, filename)
                # Store relative path from root to keep it clean
                rel_path = os.path.relpath(full_path, root_dir).replace('\\', '/')
                file_map[filename].append(rel_path)
            except Exception as e:
                print(f"Error mapping {filename}: {e}")
                continue
            
    return file_map

def main():
    root_dir = os.getcwd()
    file_map = generate_file_map(root_dir)
    
    output_file = os.path.join(os.path.dirname(__file__), 'file_inventory.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(file_map, f, indent=2)
        
    print(f"Inventory saved the {output_file}. Mapped {len(file_map)} unique filenames.")

if __name__ == "__main__":
    main()
