#!/usr/bin/env python3
"""
split_roles.py (CLI)
=====================================

Purpose:
    Splits Role_Descriptions.md into individual role files.

Layer: Curate / Utilities

Usage Examples:
    python plugins/legacy-system-roles/scripts/split_roles.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - main(): No description.
    - save_role(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import re

# Paths
CWD = os.getcwd()
SOURCE_FILE = os.path.join(CWD, 'legacy-system', 'previous-analysis-of-forms-and-business-rules', 'business-rules', 'overview', 'Role_Descriptions.md')
DEST_DIR = os.path.join(CWD, 'legacy-system', 'project-roles')

def main():
    if not os.path.exists(SOURCE_FILE):
        print(f"Error: Source file not found: {SOURCE_FILE}")
        return

    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
        print(f"Created directory: {DEST_DIR}")

    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_role = None
    role_content = []
    
    # Iterate through lines
    for line in lines:
        # Check for Role Header (### ROLE_NAME)
        # Regex to match ### ROLE_NAME (allowing for potential extra whitespace)
        match = re.match(r'^###\s+([A-Z0-9_]+)\s*$', line.strip())
        
        if match:
            # If we were processing a role, save it
            if current_role:
                save_role(current_role, role_content)
            
            # Start new role
            current_role = match.group(1)
            role_content = [f"# {current_role}\n"] # Start with H1 title
        
        elif current_role:
            # Add line to current role content
            # Skip the first empty line if it matches
            if len(role_content) == 1 and line.strip() == "":
                continue
            role_content.append(line)
            
    # Save the last role
    if current_role:
        save_role(current_role, role_content)

    print("Role splitting complete.")

def save_role(role_name, content_lines):
    filename = f"{role_name}.md"
    file_path = os.path.join(DEST_DIR, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(content_lines)
    print(f"Created: {filename}")

if __name__ == "__main__":
    main()
