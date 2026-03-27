#!/usr/bin/env python3
"""
menu_inventory_generator.py (CLI)
=====================================

Purpose:
    Generates master menu inventory from MenuConfig/XML.

Layer: Curate / Inventories

Usage Examples:
    python plugins/inventory-manager/scripts/menu_inventory_generator.py --help

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

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
from pathlib import Path
import sys

# Add script dir to sys.path to ensure local imports work
SCRIPT_DIR = Path(__file__).parent.resolve()
if str(SCRIPT_DIR) not in sys.path:
    sys.path.append(str(SCRIPT_DIR))

from menu_builder import MenuBuilder, save_inventory
# Also define REACT_OUTPUT locally or import if needed
def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()
REACT_OUTPUT = PROJECT_ROOT / "sandbox" / "ui" / "public" / "config" / "menu_inventory.json"

def main():
    mb = MenuBuilder()
    inventory = mb.build_full_inventory()
    
    # Save Master
    saved_path = save_inventory(inventory)
    print(f"💾 Saved master inventory: {saved_path}")
    
    # Save React Copy
    save_inventory(inventory, REACT_OUTPUT)
    print(f"💾 Saved React config: {REACT_OUTPUT}")
    
    total_apps = len(inventory.get("applications", {}))
    print(f"✅ Generated inventory for {total_apps} applications.")

if __name__ == "__main__":
    main()
