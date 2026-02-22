#!/usr/bin/env python3
"""
rebuild_inventory.py
====================
Scans the plugins directory and rebuilds tool_inventory.json from scratch.
"""
import sys
import os
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Import InventoryManager
try:
    from plugins.tool_inventory.scripts.manage_tool_inventory import InventoryManager
except ImportError:
    # Try relative import if package structure fails
    sys.path.append(str(SCRIPT_DIR))
    from manage_tool_inventory import InventoryManager

def rebuild():
    inventory_path = PROJECT_ROOT / "tools" / "tool_inventory.json"
    
    # Backup existing if it exists
    if inventory_path.exists():
        backup_path = inventory_path.with_suffix(".json.bak")
        print(f"📦 Backing up existing inventory to {backup_path}")
        try:
            inventory_path.rename(backup_path)
        except OSError as e:
            print(f"⚠️ Could not backup: {e}")

    # Initialize new manager (creates empty file)
    manager = InventoryManager(inventory_path)
    # FIX: Explicitly set root_dir to project root because heuristic fails for new inventory location
    manager.root_dir = PROJECT_ROOT
    
    # FIX: Disable RLM distillation for speed
    manager._trigger_distillation = lambda tool_path: print(f"   (Skipping distillation for {tool_path})")
    
    # Scan plugins directory
    plugins_dir = PROJECT_ROOT / "plugins"
    print(f"🔍 Scanning {plugins_dir}...")
    
    count = 0
    for file_path in plugins_dir.rglob("*.py"):
        # Filters
        if file_path.name == "__init__.py": continue
        if "tests" in file_path.parts: continue
        if "node_modules" in file_path.parts: continue
        if ".venv" in file_path.parts: continue
        
        # Calculate relative path from PROJECT_ROOT
        try:
            rel_path = file_path.relative_to(PROJECT_ROOT)
        except ValueError:
            continue
            
        # Determine Category from plugin name
        # plugins/<plugin-name>/scripts/...
        parts = rel_path.parts
        if len(parts) > 1:
            category = parts[1] # plugin name
        else:
            category = "uncategorized"
            
        print(f"Registering: {rel_path} ({category})")
        manager.add_tool(str(rel_path), category=category)
        count += 1

    print(f"\n✅ Rebuild Complete. Registered {count} tools.")

if __name__ == "__main__":
    rebuild()
