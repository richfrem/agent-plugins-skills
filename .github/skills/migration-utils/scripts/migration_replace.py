#!/usr/bin/env python3
"""migration_replace.py — Batch update tool references."""
import json
import os

# Load inventory
try:
    with open("migration_inventory.json") as f:
        inventory = json.load(f)
except FileNotFoundError:
    print("Error: migration_inventory.json not found.")
    exit(1)

# File extensions to scan
SCAN_EXTS = {".py", ".md", ".sh", ".yaml", ".yml", ".json", ".toml"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"} # Allow scanning plugins to fix internal references

def scan_and_replace(root_dir):
    updates_count = 0
    files_checked = 0
    
    for root, dirs, files in os.walk(root_dir):
        # Skip hidden/ignored directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
        
        for file in files:
            file_path = os.path.join(root, file)
            _, ext = os.path.splitext(file)
            
            if ext not in SCAN_EXTS:
                continue
            
            # Skip the inventory file and replacement script itself
            if file in ["migration_inventory.json", "migration_replace.py", "generate_inventory.py"]:
                continue
                
            files_checked += 1
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                original_content = content
                changed = False
                
                # Check for each old path in inventory
                for old_path, info in inventory.items():
                    new_path = info.get("new_path")
                    if not new_path or info.get("status") == "unmapped":
                        continue
                        
                    # Simple string replacement
                    if old_path in content:
                        content = content.replace(old_path, new_path)
                        changed = True
                
                if changed:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated: {file_path}")
                    updates_count += 1
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    print(f"\nScan complete.")
    print(f"Files checked: {files_checked}")
    print(f"Files updated: {updates_count}")

if __name__ == "__main__":
    scan_and_replace(".")
