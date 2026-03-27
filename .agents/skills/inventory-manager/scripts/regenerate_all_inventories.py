#!/usr/bin/env python3
"""
regenerate_all_inventories.py (CLI)
=====================================

Purpose:
    Orchestrates regeneration of all inventory files.

Layer: Curate / Inventories

Usage Examples:
    python plugins/inventory-manager/scripts/regenerate_all_inventories.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - run_script(): No description.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

def _find_project_root():
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in Path(SCRIPTS_DIR).parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return str(parent)
    raise RuntimeError(f"Could not find project root from {__file__}")

REPO_ROOT = _find_project_root()

def run_script(script_name, args=[]):
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    print(f"\n>>> Running {script_name}...")
    cmd = [sys.executable, script_path] + args
    try:
        subprocess.check_call(cmd, cwd=REPO_ROOT)
        print(">>> Success.")
    except subprocess.CalledProcessError as e:
        print(f">>> Error running {script_name}: {e}")
        sys.exit(1)

def main():
    print("=== Legacy Inventory Regeneration ===")
    
    # 1. DB Schema (Granular Scan)
    run_script("generate_db_schema_inventory.py")
    
    # 2. PLL Inventory
    run_script("generate_pll_inventory.py")
    
    # 3. Reports Inventory
    run_script("generate_reports_inventory.py")
    
    # 4. Forms Objects (Menus, OLBs)
    run_script("generate_forms_object_inventory.py")
    
    # 5. Master Collection
    print("\n>>> Building Master Object Collection (Full)...")
    run_script("build_master_collection.py", ["--full"])
    
    print("\n=== All Inventories Regenerated ===")

if __name__ == "__main__":
    main()
