
import sys
import os
from pathlib import Path

# POC Fix: Ensure we can import manage_tool_inventory
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from manage_tool_inventory import InventoryManager

def main():
    # Resolve inventory path relative to project root
    # Assuming this script is running from project root
    project_root = Path.cwd()
    inventory_path = project_root / "tools/tool_inventory.json"
    
    if not inventory_path.exists():
        print(f"❌ Inventory not found at {inventory_path}")
        return

    print(f"Loading inventory from {inventory_path}...")
    mgr = InventoryManager(inventory_path)
    
    to_remove = []
    
    # Inspect data structure to find targets
    # Dynamically find all 'tools' dictionaries across all top-level keys
    sources_list = []
    
    # Iterate all top-level keys (python, javascript, etc.)
    for stack_key, stack_val in mgr.data.items():
        if isinstance(stack_val, dict):
            # Check for 'tools' sub-key (common pattern)
            if "tools" in stack_val and isinstance(stack_val["tools"], dict):
                sources_list.append(stack_val["tools"])
            # Or if it's a direct list of tools (like 'scripts' might be in some versions)
            elif isinstance(stack_val, list):
                 pass # usually lists are leaf nodes in categories, handled by parent dict iteration if we went deeper
                 
    # Also handle flat lists if 'scripts' is top level
    if "scripts" in mgr.data and isinstance(mgr.data["scripts"], dict):
        sources_list.append(mgr.data["scripts"])
        
    for sources in sources_list:
        for category, tools in sources.items():
            for tool in tools:
                path = tool.get('path', '')
                # normalize path separators
                norm_path = path.replace('\\', '/')
                if norm_path.startswith("modernization/"):
                    to_remove.append(path)
    
    if not to_remove:
        print("✅ No modernization tools found in inventory.")
        return

    print(f"found {len(to_remove)} tools to remove.")
    
    # Use the Manager API to ensure cache cleanup happens
    for path in to_remove:
        mgr.remove_tool(path)
        
    print(f"✅ Cleanup complete.")

if __name__ == "__main__":
    main()
