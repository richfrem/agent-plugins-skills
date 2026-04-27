---
concept: setup-paths
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/tool-inventory/scripts/audit_plugins.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.371432+00:00
cluster: inventory
content_hash: 7973cbf0a9d3033e
---

# Setup paths

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/tool-inventory/scripts/audit_plugins.py -->
"""
Audit Plugin Inventory
======================

Purpose:
    Audits the `tools/tool_inventory.json` against the actual file system to ensure all
    scripts in `plugins/` are registered.

Layer: Plugin / Tool-Inventory / Audit

Usage Examples:
    python3 plugins/tool-inventory/scripts/audit_plugins.py

Supported Object Types:
    - None (Audit report)

CLI Arguments:
    None.

Input Files:
    - tools/tool_inventory.json (Registration source)
    - .agent/learning/rlm_tool_cache.json (RLM Sync source)

Output:
    - Prints audit metrics to stdout. Exit 1 on issues.

Key Functions:
    main(): Orchestrates directory scan and set calculations.

Script Dependencies:
    sys, json, os, pathlib

Consumed by:
    - None (Standalone script)
Related:
    - None
"""

import sys
import json
import os
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent.parent
INVENTORY_PATH = PROJECT_ROOT / "tools" / "tool_inventory.json"
RLM_CACHE_PATH = PROJECT_ROOT / ".agent" / "learning" / "rlm_tool_cache.json"

def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def main() -> None:
    print(f"🔍 Auditing Plugin Inventory...")
    print(f"   Project Root: {PROJECT_ROOT}")
    print(f"   Inventory:    {INVENTORY_PATH}")
    if not INVENTORY_PATH.exists():
        print(f"❌ Error: Inventory file not found at {INVENTORY_PATH}")
        sys.exit(1)
        
    inventory = load_json(INVENTORY_PATH)
    rlm_cache = load_json(RLM_CACHE_PATH)
    
    # 1. Map Inventory
    inventory_paths = set()
    
    # Handle structured inventory (python/javascript/scripts -> tools/categories)
    for lang in ["python", "javascript", "scripts"]:
        # If flat "scripts" dict:
        if lang == "scripts":
            tools_section = inventory.get("scripts", {})
        else:
            lang_section = inventory.get(lang, {})
            tools_section = lang_section.get("tools", {})
            
        for category, tools in tools_section.items():
            if isinstance(tools, list):
                for tool in tools:
                    path = tool.get("path")
                    if path:
                        inventory_paths.add(path)
            
    print(f"   Loaded Inventory: {len(inventory_paths)} unique paths") # Debug
        
    # 2. Map File System (Plugins only)
    plugins_dir = PROJECT_ROOT / "plugins"
    args_files = set()
    
    print(f"   Scanning {plugins_dir}...")
    for file_path in plugins_dir.rglob("**/scripts/*.py"):
        # Filters
        if file_path.name == "__init__.py": continue
        if "tests" in file_path.parts: continue
        if "node_modules" in file_path.parts: continue
        if ".venv" in file_path.parts: continue
        if "__pycache__" in file_path.parts: continue
        if "templates" in file_path.parts: continue # Skip templates
        
        try:
            rel_path = str(file_path.relative_to(PROJECT_ROOT))
            args_files.add(rel_path)
        except ValueError:
            continue

    # 3. Analyze
    missing_in_inventory = args_files - inventory_paths
    orphans_in_inventory = {p for p in inventory_paths if p.startswith("plugins/") and p not in args_files} # Only check plugins
    
    # Check RLM Coverage
    rlm_keys = set(rlm_cache.keys())
    missing_in_rlm = {p for p in args_files if p not in rlm_keys}

    print("\n" + "="*50)
    print("📊 Audit Results")
    print("="*50)
    
    print(f"Total Plugin Scripts: {len(args_files)}")
    print(f"Inventory Entries:    {len(inventory_paths)}")
    
    if missing_in_inventory:
        print(f"\n❌ Missing from Inventory ({len(missing_in_inventory)}):")
        for p in sorted(missing_in_inventory):
            print(f"   - {p}")
    else:
        print("\n✅ All scripts registered in inventory.")

    if orphans_in_inventory:
        # Double check if file actual

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/tool-inventory/scripts/fix_inventory_paths.py -->
"""
Fix Inventory Paths
===================

Purpose:
    Updates `tools/tool_inventory.json` to reflect the plugin structure updates:
    `plugins/<plugin>/scripts/X` -> `plugins/<plugin>/skills/<skill>/scripts/X`

Layer: Plugin / Tool-Inventory / Maintenance

Usage Examples:
    python3 plugins/tool-inventory/scripts/fix_inventory_paths.py [--apply]

Supported Object Types:
    - None (JSON modifier)

CLI Arguments:
    --apply: Save changes to disk.

Input Files:
    - tools/tool_inventory.json (Registration source)

Output:
    - Modifies `tools/tool_inventory.json` in-place when `--apply` is set.

Key Functions:
    get_new_path(): Calculates new paths based on SKILL_MAPPINGS.

Script Dependencies:
    json, sys, argparse, pathlib

Consumed by:
    -

*(combined content truncated)*

## See Also

- [[1-configuration-setup-dynamic-from-profile]]
- [[1-handle-absolute-paths-from-repo-root]]
- [[match-pythonexecution-paths-that-are-hardcoded-to-the-repo-root-plugins-folder]]
- [[paths]]
- [[plugin-paths-whitelist]]
- [[project-paths]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/tool-inventory/scripts/audit_plugins.py`
- **Indexed:** 2026-04-27T05:21:04.371432+00:00
