#!/usr/bin/env python3
"""
smart_fix_links.py (CLI)
=====================================

Purpose:
    Fixer: Auto-corrects broken links using fuzzy matching against the file inventory.

Layer: Curate / Cli_Entry_Points

Usage Examples:
    python plugins/link-checker/scripts/smart_fix_links.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - load_inventory(): Loads the file inventory JSON.
    - calculate_relative_path(): Calculates relative path between two files.
    - fix_links_in_file(): Scans a file for broken links and attempts to fix them using the inventory.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import json
import re
from urllib.parse import unquote
from typing import Dict, List, Any

def load_inventory(inventory_path: str) -> Dict[str, List[str]]:
    """Loads the file inventory JSON."""
    with open(inventory_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_relative_path(start_file: str, target_path: str) -> str:
    """Calculates relative path between two files."""
    start_dir = os.path.dirname(start_file)
    return os.path.relpath(target_path, start_dir).replace('\\', '/')

def fix_links_in_file(file_path: str, inventory: Dict[str, List[str]], root_dir: str) -> bool:
    """
    Scans a file for broken links and attempts to fix them using the inventory.

    Args:
        file_path: Path to the markdown file.
        inventory: Dictionary of filename -> valid paths.
        root_dir: Root directory of the repository (for absolute path calc).

    Returns:
        True if the file was modified, False otherwise.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping binary/unreadable: {file_path}")
        return False

    original_content = content
    
    # Regex for standard markdown links [label](path)
    # Group 1: Label, Group 2: Path
    link_pattern = re.compile(r'(\[.*?\])\((.*?)\)')
    
    def replace_link(match):
        label = match.group(1)
        original_link_path = match.group(2)
        
        # Skip web links/anchors
        if original_link_path.startswith(('http', 'mailto:', '#')):
            return match.group(0)
            
        clean_link = original_link_path.split('#')[0]
        anchor = '#' + original_link_path.split('#')[1] if '#' in original_link_path else ''
        
        # Verify if currently valid
        # Construct absolute path from current file loc
        file_dir = os.path.dirname(file_path)
        current_abs_target = os.path.join(file_dir, unquote(clean_link))
        
        if os.path.exists(current_abs_target):
            return match.group(0) # It's valid, don't touch
            
        # It's broken. Let's find the basename.
        basename = os.path.basename(unquote(clean_link))
        
        # Skip README.md - too many in repo, always ambiguous
        if basename.lower() == 'readme.md':
            return match.group(0)
        
        # Lookup in inventory
        candidates = inventory.get(basename)
        
        if not candidates:
             # Try case-insensitive lookup
            lower_basename = basename.lower()
            # This is O(N) scan of inventory matching, bit slow but fine for fallback
            # optimize by creating a lower-case map?
            # Let's just iterate keys for now, inventory is small (4k)
            matches = [k for k in inventory.keys() if k.lower() == lower_basename]
            if matches:
                candidates = inventory[matches[0]]
            
            # Try kebab to camel? valid-project-roles.ts -> validRoles.ts
            # If still no candidates, try removing hyphens?
            if not candidates:
                no_hyph = basename.replace('-', '').lower()
                matches_hyph = [k for k in inventory.keys() if k.replace('-', '').lower() == no_hyph]
                if matches_hyph:
                    candidates = inventory[matches_hyph[0]]

        if not candidates:
            # File truly missing
            # heuristic: if it contains "modernization/archive", mark as archived
            if "modernization/archive" in original_link_path:
                 return f"{label} (Archived)"
            return f"{label} (Reference Missing: {basename})"
            
        if len(candidates) == 1:
            # Unique match! Fix it.
            new_target = os.path.join(root_dir, candidates[0])
            new_rel_path = calculate_relative_path(file_path, new_target)
            print(f"  Fixed: {basename} -> {new_rel_path}")
            return f"{label}({new_rel_path}{anchor})"
            
        # Ambiguous (multiple files with same name)
        # simplistic heuristic: pick the one that shares the most path components? 
        # Or just skip warning.
        # For now, let's skip ambiguity to be safe, but print warning
        print(f"  Ambiguous match for {basename}: {candidates}")
        return match.group(0) # Leave it for manual review

    new_content = link_pattern.sub(replace_link, content)
    
    if new_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

def main():
    root_dir = os.getcwd()
    inventory_path = os.path.join(os.path.dirname(__file__), 'file_inventory.json')
    
    if not os.path.exists(inventory_path):
        print("Inventory not found. Run map_repository_files.py first.")
        return

    inventory = load_inventory(inventory_path)
    
    # We will exclude the same dirs as the mapper to avoid scanning node_modules etc
    excludes = {'.git', 'node_modules', '.venv', '.next', 'bin', 'obj'}
    
    print("Fixing links...")
    count = 0
    files_scanned = 0
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in excludes]
        
        for filename in files:
            # Skip temp files
            if filename.startswith('temp_') or filename.startswith('temp-'):
                continue
            if filename.endswith('.md'):
                file_path = os.path.join(root, filename)
                files_scanned += 1
                if files_scanned % 100 == 0:
                    print(f"  Scanned {files_scanned} files...", flush=True)
                if fix_links_in_file(file_path, inventory, root_dir):
                    print(f"Updated: {os.path.relpath(file_path, root_dir)}")
                    count += 1
                    
    print(f"Finished. Modified {count} files.")

if __name__ == "__main__":
    main()
