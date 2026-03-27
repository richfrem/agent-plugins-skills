#!/usr/bin/env python3
"""
fix_invalid_role_links.py (CLI)
=====================================

Purpose:
    Fixes broken role links in documentation files.

Layer: Curate / Utilities

Usage Examples:
    python plugins/legacy-system-roles/scripts/fix_invalid_role_links.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - load_role_inventory(): Load the roles inventory JSON.
    - fix_invalid_role_links(): Fix invalid role links in a markdown file.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import re
import json
from pathlib import Path

# Base paths
_SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in _SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

CWD = _find_project_root()
OVERVIEWS_DIR = CWD / "legacy-system" / "oracle-forms-overviews"
ROLES_INVENTORY_PATH = CWD / "legacy-system" / "project-roles" / "roles_inventory.json"


def load_role_inventory():
    """Load the roles inventory JSON."""
    if not ROLES_INVENTORY_PATH.exists():
        print(f"Error: Roles inventory not found at {ROLES_INVENTORY_PATH}")
        return {}
    with open(ROLES_INVENTORY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def fix_invalid_role_links(file_path: Path, valid_roles: set) -> bool:
    """
    Fix invalid role links in a markdown file.
    Returns True if file was modified.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Pattern: [ROLE_NAME](../../project-roles/ROLE_NAME.md)
    # Captures role name and full link
    role_link_pattern = re.compile(r'\[([A-Z]{3,}_[A-Z0-9_]+)\]\(([^)]*project-roles[^)]*)\)')
    
    def replace_invalid_role(match):
        role_name = match.group(1)
        link_path = match.group(2)
        
        if role_name in valid_roles:
            # Valid role - keep the link
            return match.group(0)
        else:
            # Invalid role - remove the link, keep plain text
            print(f"  Removing link for: {role_name}")
            return role_name
    
    content = role_link_pattern.sub(replace_invalid_role, content)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False


def main():
    print("Loading roles inventory...")
    inventory = load_role_inventory()
    valid_roles = set(inventory.keys())
    print(f"Found {len(valid_roles)} valid roles in inventory.")
    
    modified_count = 0
    
    # Process all subdirectories
    for subdir in ['forms', 'reports', 'archived']:
        dir_path = OVERVIEWS_DIR / subdir
        if not dir_path.exists():
            continue
        
        print(f"\nScanning: {subdir}/")
        for md_file in sorted(dir_path.glob('*-Overview.md')):
            if fix_invalid_role_links(md_file, valid_roles):
                print(f"Fixed: {md_file.name}")
                modified_count += 1
    
    print(f"\n✓ Complete. Modified {modified_count} files.")


if __name__ == "__main__":
    main()
