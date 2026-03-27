#!/usr/bin/env python3
"""
organize_screenshots.py (CLI)
=====================================

Purpose:
    Organizes legacy Oracle screenshots into form-specific subdirectories.

Layer: Curate / Utilities

Usage Examples:
    python plugins/screenshot-manager/scripts/organize_screenshots.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    (None detected)

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import re
import shutil

from pathlib import Path

_SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in _SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

REPO_ROOT = _find_project_root()

BASE_DIR = REPO_ROOT / 'docs/screenshots/LegacyOracle'
moved_count = 0

if not os.path.exists(BASE_DIR):
    print(f"Directory not found: {BASE_DIR}")
    exit(1)

files = os.listdir(BASE_DIR)
print(f"Scanning {len(files)} items in {BASE_DIR}...")

# Regex to match Form IDs like FORM0000, FORM0000, FORM0000
# Also handles suffixes like -1, _menu, etc.
# Match start of string: [A-Z]{4}[A-Z0-9]{4}  (e.g., FORM0000, FORM0000)
# Note: Some IDs might be 7 chars? Oracle usually 8.
# Pattern: 4 letters + 4 digits (or E+digits)
ID_PATTERN = re.compile(r'^([A-Z]{4}[A-Z0-9]{4})')

for filename in files:
    file_path = os.path.join(BASE_DIR, filename)
    
    # Skip directories
    if os.path.isdir(file_path):
        continue
        
    # Match ID
    match = ID_PATTERN.match(filename)
    if match:
        form_id = match.group(1)
        target_dir = os.path.join(BASE_DIR, form_id)
        
        # Create dir if not exists
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"Created directory: {form_id}")
            
        # Move file
        try:
            shutil.move(file_path, os.path.join(target_dir, filename))
            moved_count += 1
            # print(f"Moved {filename} -> {form_id}/")
        except Exception as e:
            print(f"Error moving {filename}: {e}")
    else:
        # Handle cases like 'Oracle-Legacy-FORM0000.png'
        # secondary pattern search
        secondary_match = re.search(r'([A-Z]{4}[A-Z0-9]{4})', filename)
        if secondary_match:
            form_id = secondary_match.group(1)
            target_dir = os.path.join(BASE_DIR, form_id)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            try:
                shutil.move(file_path, os.path.join(target_dir, filename))
                moved_count += 1
                # print(f"Moved {filename} -> {form_id}/")
            except Exception as e:
                print(f"Error moving {filename}: {e}")
        else:
            print(f"Skipping (No ID found): {filename}")

print(f"Organization Complete. Moved {moved_count} files.")
