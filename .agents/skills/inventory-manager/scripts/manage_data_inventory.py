#!/usr/bin/env python3
"""
plugins/inventory-manager/scripts/manage_data_inventory.py
==================================================

Purpose: 
    Comprehensive manager for Data Inventories (Legacy System Reference Data).
    Manages the meta-inventory that tracks all JSON inventories in 
    legacy-system/reference-data/inventories/.

Arguments:
    --inventory <path>     Path to the manifest JSON (Default: legacy-system/reference-data/inventories/inventory_manifest.json)
    
Subcommands:
    list        List all registered inventories
    add         Add a new inventory to the manifest
    update      Update an inventory's metadata
    remove      Remove an inventory from the manifest
    search      Search inventories by keyword
    audit       Find JSON files not in manifest
    generate    Generate Markdown summary

Usage Examples:
    # List all inventories
    python plugins/inventory-manager/scripts/manage_data_inventory.py list

    # Search for role-related inventories
    python plugins/inventory-manager/scripts/manage_data_inventory.py search roles

    # Add a new inventory
    python plugins/inventory-manager/scripts/manage_data_inventory.py add --path legacy-system/reference-data/inventories/new_inventory.json --desc "Description" --script tools/curate/inventories/generate_new.py

    # Audit for untracked JSON files
    python plugins/inventory-manager/scripts/manage_data_inventory.py audit
"""
import os
import re
import json
import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

DEFAULT_MANIFEST_PATH = "legacy-system/reference-data/data_manifest.json"
REFERENCE_DATA_DIR = "legacy-system/reference-data"
SUPPORTED_EXTENSIONS = [".json", ".csv", ".ts"]
EXCLUDED_FILES = ["data_manifest.json", "inventory_manifest.json"]

CATEGORY_EMOJIS = {
    'forms': '📋',
    'reports': '📊',
    'tables': '🗃️',
    'views': '👁️',
    'roles': '🔐',
    'procedures': '⚙️',
    'functions': '🔧',
    'packages': '📦',
    'triggers': '⚡',
    'types': '🏷️',
    'menus': '🍽️',
    'libraries': '📚',
    'business_rules': '📜',
    'workflows': '🔄',
    'dependencies': '🔗',
    'default': '📁',
}

# -----------------------------------------------------------------------------
# Core Classes
# -----------------------------------------------------------------------------

class DataInventoryManager:
    def __init__(self, manifest_path: Path):
        self.manifest_path = manifest_path.resolve()
        self.root_dir = self._determine_root()
        self.data = self._load()

    def _determine_root(self) -> Path:
        """Find repo root (parent of legacy-system/)."""
        current = self.manifest_path.parent
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        # Fallback: assume 4 levels up from inventories folder
        return self.manifest_path.parent.parent.parent.parent

    def _load(self) -> Dict[str, Any]:
        """Load manifest JSON data."""
        if not self.manifest_path.exists():
            print(f"📝 Manifest not found. Creating new at {self.manifest_path}")
            return {
                "metadata": {
                    "description": "Meta-inventory of all data inventories in legacy-system/reference-data/",
                    "created": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                },
                "inventories": []
            }
        
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save(self):
        """Save manifest JSON data."""
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # Ensure parent directory exists
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved manifest to {self.manifest_path}")

    def add_inventory(self, inv_path: str, description: str = None, maintenance_script: str = None):
        """Register an inventory in the manifest."""
        full_path = self.root_dir / inv_path
        
        # Check if already exists
        exists = any(inv['path'] == inv_path for inv in self.data.get("inventories", []))
        if exists:
            print(f"⚠️ Inventory {inv_path} already registered.")
            return

        # Auto-detect name from filename
        name = Path(inv_path).stem
        
        # Try to get item count if file exists
        item_count = None
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                # Heuristic: count top-level array or 'objects' key
                if isinstance(content, list):
                    item_count = len(content)
                elif isinstance(content, dict):
                    for key in ['objects', 'items', 'data', 'entries']:
                        if key in content and isinstance(content[key], (list, dict)):
                            item_count = len(content[key])
                            break
            except:
                pass

        new_entry = {
            "name": name,
            "path": inv_path,
            "description": description or f"Inventory of {name.replace('_', ' ')}",
            "maintenance_script": maintenance_script or "Unknown",
            "item_count": item_count,
            "last_verified": datetime.now().isoformat() if full_path.exists() else None
        }

        if "inventories" not in self.data:
            self.data["inventories"] = []
        
        self.data["inventories"].append(new_entry)
        self.data["inventories"].sort(key=lambda x: x['name'])
        
        self.save()
        print(f"✅ Added {name} to manifest")

    def list_inventories(self):
        """Print all registered inventories."""
        print(f"\n📂 Manifest: {self.manifest_path}")
        print(f"   Last Updated: {self.data.get('metadata', {}).get('last_updated', 'N/A')}\n")

        inventories = self.data.get("inventories", [])
        if not inventories:
            print("   (No inventories registered)")
            return
        
        for inv in inventories:
            name = inv.get('name', 'Unknown')
            emoji = self._get_emoji(name)
            count = inv.get('item_count', '?')
            script = inv.get('maintenance_script', 'Unknown')
            print(f"  {emoji} {name}")
            print(f"     Path: {inv.get('path', 'N/A')}")
            print(f"     Items: {count}")
            print(f"     Script: {script}")
            print()
        
        print(f"Total Inventories: {len(inventories)}")

    def _get_emoji(self, name: str) -> str:
        """Get emoji based on inventory name."""
        name_lower = name.lower()
        for key, emoji in CATEGORY_EMOJIS.items():
            if key in name_lower:
                return emoji
        return CATEGORY_EMOJIS['default']

    def search(self, keyword: str):
        """Search inventories by keyword."""
        keyword_lower = keyword.lower()
        results = []
        
        for inv in self.data.get("inventories", []):
            name = inv.get('name', '').lower()
            path = inv.get('path', '').lower()
            desc = inv.get('description', '').lower()
            
            if keyword_lower in name or keyword_lower in path or keyword_lower in desc:
                results.append(inv)
        
        if not results:
            print(f"❌ No inventories found matching '{keyword}'")
            return
        
        print(f"\n🔍 Found {len(results)} inventory(ies) matching '{keyword}':\n")
        for r in results:
            emoji = self._get_emoji(r.get('name', ''))
            print(f"  {emoji} {r['name']}")
            print(f"     Path: {r['path']}")
            print(f"     Description: {r.get('description', 'N/A')[:80]}")
            print(f"     Script: {r.get('maintenance_script', 'Unknown')}")
            print()

    def update_inventory(self, inv_path: str, new_desc: str = None, new_script: str = None):
        """Update an inventory's metadata."""
        found = False
        for inv in self.data.get("inventories", []):
            if inv['path'] == inv_path or inv['name'] == inv_path:
                if new_desc:
                    inv['description'] = new_desc
                    print(f"✅ Updated description for {inv['name']}")
                if new_script:
                    inv['maintenance_script'] = new_script
                    print(f"✅ Updated maintenance_script for {inv['name']}")
                inv['last_verified'] = datetime.now().isoformat()
                found = True
                break
        
        if not found:
            print(f"❌ Inventory '{inv_path}' not found in manifest.")
            return
        
        self.save()

    def remove_inventory(self, inv_path: str):
        """Remove an inventory from the manifest."""
        inventories = self.data.get("inventories", [])
        for i, inv in enumerate(inventories):
            if inv['path'] == inv_path or inv['name'] == inv_path:
                removed = inventories.pop(i)
                print(f"✅ Removed {removed['name']} from manifest")
                self.save()
                return
        
        print(f"❌ Inventory '{inv_path}' not found in manifest.")

    def audit(self):
        """Find data files not in manifest and missing files."""
        print(f"🔍 Auditing data files against filesystem...")
        
        ref_dir = self.root_dir / REFERENCE_DATA_DIR
        if not ref_dir.exists():
            print(f"❌ Directory {ref_dir} does not exist")
            return
        
        # Get registered paths
        registered_paths = {inv['path'] for inv in self.data.get("inventories", [])}
        
        # Find all data files recursively
        all_files = []
        for ext in SUPPORTED_EXTENSIONS:
            for f in ref_dir.rglob(f"*{ext}"):
                if f.name not in EXCLUDED_FILES:
                    rel = f.relative_to(self.root_dir)
                    all_files.append(str(rel).replace("\\", "/"))
        
        # Check for untracked
        untracked = [p for p in all_files if p not in registered_paths]
        
        # Check for missing
        missing = []
        for inv in self.data.get("inventories", []):
            full = self.root_dir / inv['path']
            if not full.exists():
                missing.append(inv['path'])
        
        if untracked:
            print(f"\n⚠️ UNTRACKED FILES ({len(untracked)}):")
            for u in untracked[:20]:
                print(f"   - {u}")
            if len(untracked) > 20:
                print(f"   ... and {len(untracked) - 20} more")
        else:
            print("\n✅ No untracked files.")
        
        if missing:
            print(f"\n❌ MISSING FILES ({len(missing)}):")
            for m in missing:
                print(f"   - {m}")
        else:
            print("✅ All registered files exist.")
        
        return untracked, missing

    def auto_discover(self):
        """Automatically discover and register all data files in reference-data/."""
        print(f"🔍 Auto-discovering data files in {REFERENCE_DATA_DIR}...")
        
        ref_dir = self.root_dir / REFERENCE_DATA_DIR
        if not ref_dir.exists():
            print(f"❌ Directory does not exist")
            return
        
        registered_paths = {inv['path'] for inv in self.data.get("inventories", [])}
        added = 0
        
        # Scan recursively for all supported file types
        for ext in SUPPORTED_EXTENSIONS:
            for f in sorted(ref_dir.rglob(f"*{ext}")):
                if f.name in EXCLUDED_FILES:
                    continue
                
                rel_path = str(f.relative_to(self.root_dir)).replace("\\", "/")
                
                if rel_path not in registered_paths:
                    # Try to infer maintenance script
                    script = self._infer_script(f.stem)
                    # Infer category from parent folder
                    parent = f.parent.name if f.parent != ref_dir else "root"
                    self.add_inventory(rel_path, maintenance_script=script)
                    added += 1
        
        print(f"\n✅ Auto-discovery complete. Added {added} new data files.")

    def _infer_script(self, name: str) -> str:
        """Try to infer the maintenance script from inventory name."""
        # Common patterns
        script_base = f"tools/curate/inventories/generate_{name}.py"
        if (self.root_dir / script_base).exists():
            return script_base
        
        # Check for build_* pattern
        script_base = f"tools/curate/inventories/build_{name}.py"
        if (self.root_dir / script_base).exists():
            return script_base
        
        return "Unknown - needs verification"

    def find_scripts(self):
        """Search codebase for references to each inventory file and update maintenance_script."""
        import subprocess
        
        print("🔍 Searching codebase for inventory creation scripts...")
        print("   (This may take a moment...)\n")
        
        found = []
        not_found = []
        
        for inv in self.data.get("inventories", []):
            name = inv.get('name', '')
            filename = Path(inv.get('path', '')).name
            
            # Skip if already has a known script
            if inv.get('maintenance_script', '').startswith('tools/'):
                found.append((name, inv['maintenance_script']))
                continue
            
            # Search for references to this filename in Python/JS files
            try:
                result = subprocess.run(
                    ['git', 'grep', '-l', filename, '--', '*.py', '*.js'],
                    cwd=self.root_dir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                matches = [m for m in result.stdout.strip().split('\n') if m and 'test' not in m.lower()]
                
                if matches:
                    # Prefer scripts in tools/curate/inventories
                    best_match = None
                    for m in matches:
                        if 'curate/inventories' in m or 'generate_' in m or 'build_' in m:
                            best_match = m
                            break
                    if not best_match:
                        best_match = matches[0]
                    
                    inv['maintenance_script'] = best_match
                    found.append((name, best_match))
                else:
                    not_found.append(name)
                    
            except Exception as e:
                not_found.append(f"{name} (error: {e})")
        
        # Save updates
        self.save()
        
        # Report
        print(f"✅ FOUND SCRIPTS ({len(found)}):")
        for name, script in found[:15]:
            print(f"   - {name}: {script}")
        if len(found) > 15:
            print(f"   ... and {len(found) - 15} more")
        
        print(f"\n❓ UNKNOWN ORIGIN ({len(not_found)}):")
        for name in not_found:
            print(f"   - {name}")
        
        print(f"\n💡 TIP: For unknown items, check if they are:")
        print("   - Manually created/curated")
        print("   - Generated by external tools")
        print("   - Legacy data that needs documentation")


# -----------------------------------------------------------------------------
# Documentation Generator
# -----------------------------------------------------------------------------

def generate_markdown(manager: DataInventoryManager, output_path: Path):
    """Generate Markdown summary of all inventories with links."""
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    lines = [
        "# Data Inventory Manifest",
        "",
        f"> **Auto-generated:** {timestamp}",
        f"> **Source:** [`data_manifest.json`](data_manifest.json)",
        f"> **Regenerate:** `python plugins/inventory-manager/scripts/manage_data_inventory.py generate`",
        "",
        "This manifest tracks all data files (JSON, CSV, TS) in `legacy-system/reference-data/`.",
        "",
        "---",
        "",
        "## Registered Data Files",
        "",
        "| Name | Description | Items | Maintenance Script |",
        "| :--- | :--- | :---: | :--- |",
    ]

    for inv in manager.data.get("inventories", []):
        path = inv.get('path', '')
        # Use full filename with extension
        display_name = Path(path).name if path else inv.get('name', 'Unknown')
        desc = inv.get('description', 'N/A')[:60]
        count = inv.get('item_count', '?')
        script = inv.get('maintenance_script', 'Unknown')
        
        # Make name a link to the file (relative from reference-data/)
        if path:
            rel_path = path.replace("legacy-system/reference-data/", "")
            name_link = f"[**{display_name}**]({rel_path})"
        else:
            name_link = f"**{display_name}**"
        
        # Make script a link if it exists
        if script and script not in ["Unknown", "Unknown - needs verification", "Manual curation"]:
            script_link = f"[`{Path(script).name}`](../../../{script})"
        else:
            script_link = script if script else "Unknown"
        
        lines.append(f"| {name_link} | {desc} | {count} | {script_link} |")

    lines.extend([
        "",
        "---",
        "",
        f"**Total Data Files:** {len(manager.data.get('inventories', []))}",
    ])

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Generated Markdown: {output_path}")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Manage Data Inventories (Legacy System Reference Data)")
    
    parser.add_argument("--inventory", default=DEFAULT_MANIFEST_PATH, help="Path to manifest JSON")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    subparsers.add_parser("list", help="List all registered inventories")
    subparsers.add_parser("audit", help="Find untracked/missing data files")
    subparsers.add_parser("discover", help="Auto-discover and register all data files")
    subparsers.add_parser("find-scripts", help="Search codebase for scripts that create each inventory")
    
    add_parser = subparsers.add_parser("add", help="Add an inventory to manifest")
    add_parser.add_argument("--path", required=True, help="Relative path to JSON file")
    add_parser.add_argument("--desc", help="Description")
    add_parser.add_argument("--script", help="Path to maintenance script")

    search_parser = subparsers.add_parser("search", help="Search inventories by keyword")
    search_parser.add_argument("keyword", help="Keyword to search")

    update_parser = subparsers.add_parser("update", help="Update inventory metadata")
    update_parser.add_argument("--path", required=True, help="Path or name of inventory")
    update_parser.add_argument("--desc", help="New description")
    update_parser.add_argument("--script", help="New maintenance script")

    remove_parser = subparsers.add_parser("remove", help="Remove inventory from manifest")
    remove_parser.add_argument("--path", required=True, help="Path or name to remove")

    gen_parser = subparsers.add_parser("generate", help="Generate Markdown summary")
    gen_parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    # Load
    inv_path = Path(args.inventory)
    manager = DataInventoryManager(inv_path)

    # Dispatch
    if args.command == "list":
        manager.list_inventories()
    
    elif args.command == "add":
        manager.add_inventory(args.path, args.desc, args.script)
    
    elif args.command == "search":
        manager.search(args.keyword)
    
    elif args.command == "update":
        manager.update_inventory(args.path, args.desc, args.script)
    
    elif args.command == "remove":
        manager.remove_inventory(args.path)
    
    elif args.command == "audit":
        manager.audit()
    
    elif args.command == "discover":
        manager.auto_discover()
    
    elif args.command == "generate":
        if args.output:
            out_path = Path(args.output)
        else:
            out_path = inv_path.parent / "DATA_MANIFEST.md"
        generate_markdown(manager, out_path)
    
    elif args.command == "find-scripts":
        manager.find_scripts()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
