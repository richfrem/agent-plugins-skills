#!/usr/bin/env python3
"""
manage_tool_inventory.py (CLI)
=====================================

Purpose:
    Comprehensive manager for Tool Inventories. Supports list, add, update, remove, search, audit, and generate operations.

Layer: Curate / Curate

Usage Examples:
    python plugins/tool-inventory/scripts/manage_tool_inventory.py --help
    python plugins/tool-inventory/scripts/manage_tool_inventory.py list
    python plugins/tool-inventory/scripts/manage_tool_inventory.py search "keyword"
    python plugins/tool-inventory/scripts/manage_tool_inventory.py remove --path "path/to/tool.py"
    python plugins/tool-inventory/scripts/manage_tool_inventory.py update --path "tool.py" --desc "New description"
    python plugins/tool-inventory/scripts/manage_tool_inventory.py discover --auto-stub
    python plugins/tool-inventory/scripts/manage_tool_inventory.py summarize-missing
    python plugins/tool-inventory/scripts/manage_tool_inventory.py sync-from-cache
    python plugins/tool-inventory/scripts/manage_tool_inventory.py reset-from-cache
    python plugins/tool-inventory/scripts/manage_tool_inventory.py clear-inventory

Supported Object Types:
    - Generic

CLI Arguments:
    --inventory     : Path to JSON inventory
    --path          : Relative path to tool
    --category      : Category (e.g. curate/inventories)
    --desc          : Description (Optional, auto-extracted if empty)
    --output        : Output file path (Default: adjacent TOOL_INVENTORY.md)
    keyword         : Keyword to search in name/path/description
    --status        : Filter by compliance status
    --path          : Current path or name of the tool
    --desc          : New description
    --new-path      : New path
    --mark-compliant: Mark as compliant
    --path          : Path or name of tool to remove
    --auto-stub     : Automatically create stub entries
    --include-json  : Include JSON config files
    --json          : Output as JSON
    --path          : Single script path
    --batch         : Process all 'stub' tools
    --dry-run       : Preview changes only

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - generate_markdown(): Generate Markdown documentation from the Inventory Manager data.
    - extract_docstring(): Read file and extract PyDoc or JSDoc.
    - main(): No description.

Script Dependencies:
    - plugins/tool-inventory/scripts/distiller.py (Cyclical: Triggers distillation on update)
    - plugins/tool-inventory/scripts/cleanup_cache.py (Atomic cleanup on removal)

Consumed by:
    - plugins/tool-inventory/scripts/distiller.py (Invokes update_tool for RLM-driven enrichment)
"""
import os
import sys
from pathlib import Path

# Add project root to sys.path to ensure we can import tools package
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
import re
import json
import argparse
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import ast
import re

# Compliance status values

# Compliance status values
COMPLIANCE_STATUS = ['compliant', 'partial', 'needs_review', 'stub']
HEADER_STYLES = ['extended', 'basic', 'minimal', 'none']

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

CATEGORY_EMOJIS = {
    'miners': '⛏️',
    'search': '🔍',
    'bundler': '📦',
    'rlm': '🧠',
    'vector': '🗄️',
    'code-gen': '⚙️',
    'documentation': '📝',
    'inventories': '📊',
    'menu': '🍽️',
    'link-checker': '🔗',
    'utils': '🛠️',
    'tracking': '📋',
    'processors': '🔧',
    'elements': '📦',
    'tools': '🔨',
    'src': '📁',
    'root': '🚀',
}

# -----------------------------------------------------------------------------
# Core Classes
# -----------------------------------------------------------------------------

class InventoryManager:
    def __init__(self, inventory_path: Path):
        self.inventory_path = inventory_path.resolve()
        self.root_dir = self._determine_root()
        self.data = self._load()

    def _determine_root(self) -> Path:
        """Heuristic to find the 'root' relative to the inventory location."""
        # If global inventory, root is repo root
        if self.inventory_path.name == 'tool_inventory.json' and self.inventory_path.parent.name == 'reference-data':
            return self.inventory_path.parent.parent.parent
        # If local inventory (e.g. inside xml-to-markdown), root is that tool's dir
        return self.inventory_path.parent

    def _load(self) -> Dict[str, Any]:
        """Load JSON data."""
        if not self.inventory_path.exists():
            print(f"Inventory not found at {self.inventory_path}. Creating new.")
            return {"metadata": {}, "scripts": {}}
        
        with open(self.inventory_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save(self):
        """Save JSON data."""
        # Update metadata
        if "metadata" not in self.data:
            self.data["metadata"] = {}
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        with open(self.inventory_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved inventory to {self.inventory_path}")

    def _trigger_distillation(self, tool_path: str):
        """
        Triggers the RLM Distiller for a specific tool.
        This ensures the RLM Cache (rlm_tool_cache.json) is always in sync with the Inventory.
        """
        distiller_script = self.root_dir / "plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py"
        if not distiller_script.exists():
            print(f"⚠️  Distiller not found at {distiller_script}. Skipping sync.")
            return

        print(f"🔄 Triggering RLM Distillation for {tool_path}...")
        try:
            # Run distiller in 'tool' mode for this specific file
            # --cleanup ensures if we renamed something, old keys might get cleaned up (though per-file cleanup is tricky)
            # Actually, per-file mode + cleanup might be aggressive, but safest is just to distill the file.
            cmd = [
                sys.executable,
                str(distiller_script),
                "--type", "tool",
                "--file", tool_path
            ]
            
            # Using Popen to run in background or run_and_wait?
            # User likely wants immediate consistency, so wait.
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ Distillation successful.")
            else:
                print(f"   ❌ Distillation failed:")
                print(result.stderr)
        except Exception as e:
            print(f"   ❌ Error running distiller: {e}")

    def add_tool(self, tool_path: str, category: str = None, description: str = None):
        """Register a tool in the inventory."""
        full_path = self.root_dir / tool_path
        if not full_path.exists():
            print(f"❌ Error: File {tool_path} does not exist.")
            return

        # GUARDRAIL: Do not allow modernization/ tracks
        # We normalize to forward slash for check just in case
        norm_path = tool_path.replace('\\', '/')
        if norm_path.startswith("modernization/") or "modernization" in Path(tool_path).parts:
             print(f"❌ Error: 'modernization/' paths are application code, not tools. Exclusion enforced.")
             return

        # Auto-detect category if missing
        if not category:
            parts = Path(tool_path).parts
            if "tools" in parts:
                idx = parts.index("tools")
                if idx + 1 < len(parts) - 1:
                    category = parts[idx + 1] # e.g. 'curate'
                else:
                    category = 'root'
            else:
                category = 'root'
        
        # Structure compatibility: check if 'python' key exists (Legacy Global format)
        target_dict = self.data.get("python", {}).get("tools", {})
        is_legacy_global = "python" in self.data
        
        if not is_legacy_global:
            # Local inventory format (simpler)
            if "scripts" not in self.data:
                self.data["scripts"] = {}
            target_dict = self.data["scripts"]

        if category not in target_dict:
            target_dict[category] = []
        
        # Check if already exists
        exists = any(t['path'] == tool_path for t in target_dict[category])
        if exists:
            print(f"⚠️ Tool {tool_path} already registered in category '{category}'.")
            return

        # Extract description if not provided
        if not description:
            description = extract_docstring(full_path)

        # Detect header style
        header_style = self._detect_header_style(full_path)
        
        new_entry = {
            "name": Path(tool_path).name,
            "path": tool_path,
            "description": description,
            "last_updated": datetime.now().isoformat(),
            "compliance_status": "compliant" if header_style == "extended" else "needs_review",
            "header_style": header_style
        }

        target_dict[category].append(new_entry)
        
        # Sort
        target_dict[category].sort(key=lambda x: x['name'])
        
        
        self.save()
        print(f"✅ Added {tool_path} to category '{category}' (status: {new_entry['compliance_status']})")
        
        # Trigger RLM Update
        self._trigger_distillation(tool_path)

    def list_tools(self):
        """Print all tools."""
        print(f"\n📂 Inventory: {self.inventory_path}")
        
        # Handle both formats
        if "python" in self.data:
            # Global format
            sources = self.data["python"].get("tools", {})
        else:
            # Local format
            sources = self.data.get("scripts", {})

        count = 0
        for category, tools in sources.items():
            print(f"\n🔹 Category: {category}")
            for tool in tools:
                print(f"   - {tool['name']} ({tool['path']})")
                count += 1
        print(f"\nTotal Tools: {count}")

    def audit(self):
        """Check for missing files and untracked scripts."""
        print(f"🔍 Auditing inventory against filesystem root: {self.root_dir}")
        
        # 1. Check Missing
        missing = []
        tracked_paths = set()
        
        sources = self.data.get("python", {}).get("tools", {}) if "python" in self.data else self.data.get("scripts", {})
        
        for category, tools in sources.items():
            for tool in tools:
                p = self.root_dir / tool['path']
                tracked_paths.add(str(p.resolve()))
                if not p.exists():
                    missing.append(tool['path'])
        
        if missing:
            print("\n❌ MISSING FILES (In JSON, not on Disk):")
            for m in missing:
                print(f"   - {m}")
        else:
            print("\n✅ No missing files.")

        # 2. Check Untracked (Simple scan of tools dir)
        print("\n🔍 Scanning for untracked .py scripts (basic scan)...")
        # heuristic: only scan 'tools' or current dir
        scan_dir = self.root_dir / 'tools'
        if not scan_dir.exists():
            scan_dir = self.root_dir # For local bundles

        untracked = []
        for f in scan_dir.rglob("*.py"):
            if "env" in str(f) or "tests" in str(f): continue
            if str(f.resolve()) not in tracked_paths:
                rel = f.relative_to(self.root_dir)
                untracked.append(str(rel))
        
        if untracked:
            print("⚠️ UNTRACKED FILES (On Disk, not in JSON):")
            for u in untracked[:10]: # Limit output
                print(f"   - {u}")
            if len(untracked) > 10: print(f"   ... and {len(untracked)-10} more.")
        else:
            print("✅ No untracked files found.")

    def search(self, keyword: str):
        """Search for tools by keyword in name, path, or description."""
        keyword_lower = keyword.lower()
        results = []
        
        # Generic Multi-Stack Search
        sources_list = []
        for stack_key, stack_val in self.data.items():
            if stack_key == 'metadata': continue
            if isinstance(stack_val, dict):
                if "tools" in stack_val:
                    sources_list.append((stack_key, stack_val["tools"]))
                else: 
                     # Check if the dict itself is a category map (like scripts)
                     # Heuristic: does it contain lists of dicts?
                     is_category_map = True
                     for k,v in stack_val.items():
                         if not isinstance(v, list): is_category_map = False; break
                     if is_category_map:
                         sources_list.append((stack_key, stack_val))
            elif isinstance(stack_val, list):
                 # Top level list? Unlikely but possible
                 pass

        for stack_name, categories in sources_list:
            for category, tools in categories.items():
                for tool in tools:
                    name = tool.get('name', '').lower()
                    path = tool.get('path', '').lower()
                    desc = tool.get('description', '').lower()
                    
                    if keyword_lower in name or keyword_lower in path or keyword_lower in desc:
                        results.append({**tool, 'category': f"{stack_name}/{category}"})
        
        if not results:
            print(f"❌ No tools found matching '{keyword}'")
            return
        
        print(f"\n🔍 Found {len(results)} tool(s) matching '{keyword}':\n")
        for r in results:
            print(f"  📦 {r['name']}")
            print(f"     Path: {r['path']}")
            print(f"     Category: {r['category']}")
            print(f"     Description: {r.get('description', 'N/A')[:100]}")
            print()

    def update_tool(self, tool_path: str, new_desc: str = None, new_path: str = None, mark_compliant: bool = False, suppress_distillation: bool = False):
        """Update description or path of an existing tool."""
        
        # Generic Multi-Stack Traversal
        sources_list = []
        for stack_key, stack_val in self.data.items():
            if stack_key == 'metadata': continue
            if isinstance(stack_val, dict):
                if "tools" in stack_val:
                    sources_list.append((stack_key, stack_val["tools"]))
                else: 
                     # Check if the dict itself is a category map
                     is_category_map = True
                     for k,v in stack_val.items():
                         if not isinstance(v, list): is_category_map = False; break
                     if is_category_map:
                         sources_list.append((stack_key, stack_val))

        found = False
        target_posix = tool_path.replace('\\', '/').lower() # normalize for comparison
        
        for stack_name, categories in sources_list:
            for category, tools in categories.items():
                for tool in tools:
                    current_path = tool['path'].replace('\\', '/').lower()
                    if current_path == target_posix or tool['name'] == tool_path:
                        if new_desc:
                            tool['description'] = new_desc
                            print(f"✅ Updated description for {tool['name']}")
                        if new_path:
                            tool['path'] = new_path
                            print(f"✅ Updated path for {tool['name']} -> {new_path}")
                        if mark_compliant:
                            tool['compliance_status'] = 'compliant'
                            print(f"✅ Marked {tool['name']} as compliant")
                        
                        tool['last_updated'] = datetime.now().isoformat()
                        found = True
                        break
                if found: break
            if found: break
        
        if not found:
            print(f"❌ Tool '{tool_path}' not found in inventory.")
            return
        
        self.save()

        # Trigger RLM Distillation (Unless suppressed)
        if not suppress_distillation:
             target_path = new_path if new_path else tool_path
             if hasattr(self, '_trigger_distillation') and callable(self._trigger_distillation):
                 self._trigger_distillation(target_path)
             else:
                 print(f"ℹ️  Skipped distillation (no handler registered).")
        else:
             print(f"ℹ️  Skipped distillation (suppressed).")
        


    def remove_tool(self, tool_path: str):
        """Remove a tool from the inventory."""
        
        # Generic Multi-Stack Traversal
        sources_list = []
        for stack_key, stack_val in self.data.items():
            if stack_key == 'metadata': continue
            if isinstance(stack_val, dict):
                if "tools" in stack_val:
                    sources_list.append((stack_key, stack_val["tools"]))
                else: 
                     # Check if the dict itself is a category map
                     is_category_map = True
                     for k,v in stack_val.items():
                         if not isinstance(v, list): is_category_map = False; break
                     if is_category_map:
                         sources_list.append((stack_key, stack_val))
            # Handle direct lists if ever encountered (unlikely based on current schema)

        found = False
        target_posix = tool_path.replace('\\', '/').lower() # normalize for comparison

        for stack_name, categories in sources_list:
            for category, tools in categories.items():
                for i, tool in enumerate(tools):
                    current_path = tool['path'].replace('\\', '/').lower()
                    if current_path == target_posix or tool['name'] == tool_path:
                        removed = tools.pop(i)
                        print(f"✅ Removed {removed['name']} from category '{stack_name}/{category}'")
                        found = True
                        break
                if found: break
            if found: break
        
        if not found:
            print(f"❌ Tool '{tool_path}' not found in inventory.")
            return
        
        self.save()

        # Trigger Cache Removal
        self._remove_from_cache(tool_path)

    def _remove_from_cache(self, tool_path: str):
        """Removes the tool from the RLM Tool Cache using rlm-factory cleanup_cache.py."""
        cleanup_script = self.root_dir / "plugins/rlm-factory/skills/rlm-curator/scripts/cleanup_cache.py"
        if not cleanup_script.exists():
            print(f"⚠️  Cleanup script not found at {cleanup_script}. RLM Cache may be out of sync.")
            return

        try:
            cmd = [
                sys.executable,
                str(cleanup_script),
                "--type", "tool",
                "--apply"  # Apply will likely need logic to target a specific file if supported, else this is generic
            ]
            
            # Note: rlm-factory cleanup_cache.py is designed to purge *all* missing files inherently by scanning.
            # So just running it with --apply is enough to sync the ledger with the deletion.
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Synced removal with RLM Cache via Janitor scan.")
            else:
                print(f"⚠️  Error syncing with cache: {result.stderr}")
                
        except Exception as e:
            print(f"⚠️  Error executing cache cleanup: {e}")

    def _detect_header_style(self, file_path: Path) -> str:
        """Detect the documentation header style of a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(3000)
        except:
            return 'none'
        
        if file_path.suffix != '.py':
            return 'none'
        
        # Check for extended style (has Purpose:, Usage:, Key Functions:, etc.)
        has_purpose = 'Purpose:' in content or 'PURPOSE:' in content
        has_usage = 'Usage' in content and ('Examples:' in content or 'python' in content.lower())
        has_key_functions = 'Key Functions:' in content or 'Functions:' in content
        has_layer = 'Layer:' in content
        
        if has_purpose and has_usage and has_key_functions:
            return 'extended'
        elif has_purpose and has_usage:
            return 'basic'
        elif has_purpose or '"""' in content[:500]:
            return 'minimal'
        else:
            return 'none'

    def discover_gaps(self, include_json: bool = False) -> Dict[str, List]:
        """
        Scans plugins/ directory for untracked scripts.
        
        Args:
            include_json: If True, also scan for .json config files
            
        Returns:
            Dict with keys: 'with_docstring', 'without_docstring', 'json_configs'
        """
        print(f"🔎 Discovering untracked scripts in {self.root_dir / 'tools'}...")
        
        # Build set of tracked paths
        tracked_paths = set()
        sources = self.data.get("python", {}).get("tools", {}) if "python" in self.data else self.data.get("scripts", {})
        
        for category, tools in sources.items():
            for tool in tools:
                p = self.root_dir / tool['path']
                tracked_paths.add(str(p.resolve()))
        
        # Scan for untracked
        results = {
            'with_docstring': [],
            'without_docstring': [],
            'json_configs': []
        }
        
        # Recursive scan of tools ONLY (plugins are sources) per user instruction
        scan_dirs = [self.root_dir / 'tools', self.root_dir / 'plugins']
        found_files = set()
        
        for d in scan_dirs:
            if d.exists():
                for f in d.rglob("*.py"):
                    found_files.add(f)
                # Keep JS scanning if present in tools
                for f in d.rglob("*.js"):
                    found_files.add(f)

        for f in found_files:
             # Blacklist: __init__.py
             if f.name == "__init__.py":
                 continue

             # Blacklist: logical folders
             ignore_parts = {'node_modules', 'venv', '.venv', 'env', '.git', '__pycache__', '.agent'}
             if any(p in f.parts for p in ignore_parts):
                 continue
             
             # Special Case: investment-screener
             # Ignore plugins/investment-screener UNLESS it is in backend/py_services
             try:
                 rel = str(f.relative_to(self.root_dir))
                 if rel.startswith("plugins/investment-screener"):
                     if not rel.startswith("plugins/investment-screener/backend/py_services"):
                         continue
             except ValueError:
                 continue
             
             if str(f.resolve()) not in tracked_paths:
                 try:
                     docstring = extract_docstring(f)
                     
                     if docstring and docstring != 'TBD':
                         results['with_docstring'].append((rel, docstring))
                     else:
                         results['without_docstring'].append(rel)
                 except Exception as e:
                     print(f"⚠️ Error processing {f}: {e}")
                     continue
        
        # Optionally scan JSON files
        if include_json:
            for f in scan_dir.rglob("*.json"):
                skip_patterns = ['node_modules', '.git', 'package-lock']
                if any(p in str(f) for p in skip_patterns):
                    continue
                if str(f.resolve()) not in tracked_paths:
                    rel = str(f.relative_to(self.root_dir))
                    results['json_configs'].append(rel)
        
        return results

    def create_stub(self, path: str, extracted_desc: str = None, category: str = None) -> bool:
        """
        Creates a stub inventory entry for a discovered script.
        Sets compliance_status='stub', last_updated=now().
        
        Args:
            path: Relative path to the script
            extracted_desc: Pre-extracted description (or None for TBD)
            category: Category override (auto-detected if None)
        
        Returns:
            True if stub was created, False if already exists
        """
        full_path = self.root_dir / path
        if not full_path.exists():
            print(f"⚠️ File not found: {path}")
            return False
        
        # Auto-detect category
        if not category:
            parts = Path(path).parts
            if "tools" in parts:
                idx = parts.index("tools")
                if idx + 1 < len(parts) - 1:
                    category = parts[idx + 1]
                else:
                    category = 'root'
            else:
                category = 'root'
        
        # Get or create category
        sources = self.data.get("python", {}).get("tools", {}) if "python" in self.data else self.data.get("scripts", {})
        is_legacy_global = "python" in self.data
        
        if not is_legacy_global:
            if "scripts" not in self.data:
                self.data["scripts"] = {}
            sources = self.data["scripts"]
        
        if category not in sources:
            sources[category] = []
        
        # Check if already exists
        exists = any(t['path'] == path for t in sources[category])
        if exists:
            return False
        
        # Detect header style
        header_style = self._detect_header_style(full_path)
        
        new_entry = {
            "name": Path(path).name,
            "path": path,
            "description": extracted_desc if extracted_desc else "TBD",
            "last_updated": datetime.now().isoformat(),
            "compliance_status": "stub",
            "header_style": header_style
        }
        
        sources[category].append(new_entry)
        sources[category].sort(key=lambda x: x['name'])
        
        return True

    def search_by_status(self, status: str) -> List[Dict]:
        """
        Returns all tools matching the given compliance_status.
        
        Args:
            status: One of 'compliant', 'partial', 'needs_review', 'stub'
        
        Returns:
            List of tool dicts with matching status
        """
        results = []
        sources = self.data.get("python", {}).get("tools", {}) if "python" in self.data else self.data.get("scripts", {})
        
        for category, tools in sources.items():
            for tool in tools:
                tool_status = tool.get('compliance_status', 'needs_review')
                if tool_status == status:
                    results.append({**tool, 'category': category})
        
        return results

    def mark_compliant(self, path: str) -> bool:
        """
        Updates compliance_status to 'compliant' and refreshes last_updated.
        
        Args:
            path: Path or name of the tool
            
        Returns:
            True if updated, False if not found
        """
        self.update_tool(path, mark_compliant=True)
        return True

    
    def _parse_js_metadata(self, source_code: str) -> Dict[str, Any]:
        """
        Roughly extracts metadata from JS/Node scripts using regex.
        """
        cli_args = []
        functions = []
        
        # 1. args extraction (very rough, looking for yargs/commander patterns)
        # matches .option('--flag', 'desc')
        option_pattern = re.compile(r"\.option\(\s*['\"](-{1,2}[\w-]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]")
        for match in option_pattern.finditer(source_code):
            cli_args.append(f"    {match.group(1):<16}: {match.group(2)}")
            
        # matches simple const args = process.argv
        if "process.argv" in source_code and not cli_args:
            cli_args.append("    (Process.argv usage detected)")

        # 2. function extraction
        # function name(
        func_pattern = re.compile(r"function\s+(\w+)\s*\(")
        for match in func_pattern.finditer(source_code):
            functions.append(f"    - {match.group(1)}()")
            
        # const name = (
        arrow_pattern = re.compile(r"(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(.*?\)\s*=>")
        for match in arrow_pattern.finditer(source_code):
             functions.append(f"    - {match.group(1)}()")

        return {
            "cli_args": cli_args,
            "functions": functions
        }

    def standardize_header(self, tool_path: str, dry_run: bool = False) -> bool:
        """
        Generates and applies a standardized header to a python script.
        Uses inventory data + AST parsing.
        
        Args:
            tool_path: Relative path to the script
            dry_run: If True, prints header but doesn't write
            
        Returns:
            True if successful
        """
        full_path = self.root_dir / tool_path
        if not full_path.exists():
            print(f"❌ File not found: {tool_path}")
            return False
            
        # 1. Get Inventory Data (Source of Truth for Description)
        tool_data = None
        sources = self.data.get("python", {}).get("tools", {}) if "python" in self.data else self.data.get("scripts", {})
        
        for cat, tools in sources.items():
            for tool in tools:
                if tool['path'] == tool_path:
                    tool_data = tool
                    tool_data['category'] = cat
                    break
            if tool_data: break
            
        if not tool_data:
            print(f"❌ Tool not in inventory: {tool_path}")
            return False

        # Detect File Type
        is_js = tool_path.endswith('.js')
        
        cli_args = []
        functions = []
        template_name = "python-tool-header-template.py" if not is_js else "js-tool-header-template.js"

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
                
            if is_js:
                meta = self._parse_js_metadata(source_code)
                cli_args = meta['cli_args']
                functions = meta['functions']
            else:
                # Python AST parsing
                tree = ast.parse(source_code)
                # Extract CLI Args
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and hasattr(node.func, 'attr') and node.func.attr == 'add_argument':
                        # rough extraction of args
                        arg_name = "arg"
                        help_text = "N/A"
                        if node.args:
                            arg_name = getattr(node.args[0], 'value', 'arg')
                        
                        for kw in node.keywords:
                            if kw.arg == 'help':
                                help_text = getattr(kw.value, 'value', 'N/A')
                        
                        cli_args.append(f"    {arg_name:<16}: {help_text}")

                # Extract Functions
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef):
                        if not node.name.startswith('_'):
                            doc = ast.get_docstring(node) or "No description."
                            doc_summary = doc.split('\n')[0]
                            functions.append(f"    - {node.name}(): {doc_summary}")

        except Exception as e:
            print(f"❌ Failed to parse {tool_path}: {e}")
            return False

        # 3. Render Template
        # Load template
        template_path = self.root_dir / ".agent/templates" / template_name
        if not template_path.exists():
            # Fallback inline template
            template = '''#!/usr/bin/env python3
"""
{{script_name}} (CLI)
=====================================

Purpose:
    {{description}}

Layer: {{layer}}

Usage Examples:
    python {{script_path}} --help

CLI Arguments:
{{cli_arguments}}

Key Functions:
{{key_functions}}
"""
'''
        else:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()

        # Context
        context = {
            "script_name": Path(tool_path).name,
            "script_path": tool_path,
            "description": tool_data.get('description', 'TBD').replace('\n', '\n    '),
            "layer": f"Curate / {tool_data.get('category', 'Tools').title()}",
            "usage_examples": f"    python {tool_path} --help" if not is_js else f"    node {tool_path} --help",
            "supported_types": "    - Generic",
            "cli_arguments": "\n".join(cli_args) if cli_args else "    (None detected)",
            "input_files": "    - (See code)",
            "output_files": "    - (See code)",
            "key_functions": "\n".join(functions) if functions else "    (None detected)",
            "script_dependencies": "    (None detected)",
            "consumed_by": "    (Unknown)"
        }

        # Render
        header = template
        for k, v in context.items():
            header = header.replace(f"{{{{{k}}}}}", str(v))

        if dry_run:
            print(f"\n--- Preview Header for {tool_path} ---")
            print(header)
            print("---------------------------------------")
            return True

        # 4. Apply to File
        # Remove existing header (everything before imports or first code)
        lines = source_code.split('\n')
        start_idx = 0
        
        # Heuristic: Find first import or definition
        for i, line in enumerate(lines):
            line_strip = line.strip()
            if not line_strip: continue
            
            # Skip shebangs and comments at top
            if line_strip.startswith('#') or line_strip.startswith('//') or line_strip.startswith('/*') or line_strip.startswith('*'):
                continue
                
            if is_js:
                if line_strip.startswith('const ') or line_strip.startswith('let ') or line_strip.startswith('var ') or line_strip.startswith('import ') or line_strip.startswith('require(') or line_strip.startswith('function '):
                    start_idx = i
                    break
            else:
                if line_strip.startswith('import ') or line_strip.startswith('from ') or line_strip.startswith('def ') or line_strip.startswith('class '):
                    start_idx = i
                    break
        
        # Keep shebang if present
        # ... logic kept same ...
        
        remaining_code = '\n'.join(lines[start_idx:])
            
        new_content = header.strip() + "\n\n" + remaining_code.lstrip()
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"✅ Applied standardized header to {tool_path}")
        
        # 5. Mark Compliant
        self.mark_compliant(tool_path)
        return True

    def reset_compliance(self):
        """
        Resets compliance status for ALL tools in the inventory.
        Sets status='needs_review' and clears last_updated.
        Also re-detects header style.
        """
        sources = self.data.get("python", {}).get("tools", {}) if "python" in self.data else self.data.get("scripts", {})
        count = 0
        
        print("🔄 Resetting compliance status for all tools...")
        
        for category, tools in sources.items():
            for tool in tools:
                full_path = self.root_dir / tool['path']
                
                # Detect header style
                header_style = self._detect_header_style(full_path)
                
                tool['header_style'] = header_style
                tool['last_updated'] = "" # Reset
                
                if header_style == 'extended':
                    tool['compliance_status'] = 'compliant'
                elif header_style == 'basic':
                    tool['compliance_status'] = 'partial'
                else:
                    tool['compliance_status'] = 'needs_review'
                
                count += 1
        
        self.save()
        print(f"✅ Reset status for {count} tools.")


    
    def cleanup_by_extension(self, extensions: List[str]) -> None:
        """
        Removes all tools with the specified extensions from the inventory.
        """
        extensions = [e.lower() if e.startswith('.') else f".{e.lower()}" for e in extensions]
        to_remove = []
        
        print(f"🔍 Searching for tools with extensions: {extensions}")
        
        # Collect paths to remove
        all_sources = []
        if "python" in self.data:
            all_sources.append(self.data["python"].get("tools", {}))
        if "javascript" in self.data:
            all_sources.append(self.data["javascript"].get("tools", {}))
        if "scripts" in self.data:
            all_sources.append(self.data["scripts"])
            
        for sources in all_sources:
            for cat, tools in sources.items():
                for tool in tools:
                    path = tool['path']
                    if any(path.lower().endswith(ext) for ext in extensions):
                        to_remove.append(path)
        
        if not to_remove:
            print("✅ No tools found to remove.")
            return
            
        print(f"🗑️ Found {len(to_remove)} tools to remove.")
        for path in to_remove:
            self.remove_tool(path)
            
        print(f"✅ Removed {len(to_remove)} tools.")

    def cleanup_by_path(self, pattern: str) -> None:
        """
        Removes all tools whose path contains the given pattern.
        """
        pattern = pattern.lower()
        to_remove = []
        
        print(f"🔍 Searching for tools with path containing: '{pattern}'")
        
        # Collect paths to remove
        all_sources = []
        if "python" in self.data:
            all_sources.append(self.data["python"].get("tools", {}))
        if "javascript" in self.data:
            all_sources.append(self.data["javascript"].get("tools", {}))
        if "scripts" in self.data:
            all_sources.append(self.data["scripts"])
            
        for sources in all_sources:
            for cat, tools in sources.items():
                for tool in tools:
                    path = tool['path']
                    if pattern in path.lower():
                        to_remove.append(path)
        
        if not to_remove:
            print("✅ No tools found to remove.")
            return
            
        print(f"🗑️ Found {len(to_remove)} tools to remove.")
        for path in to_remove:
            self.remove_tool(path)
            
        print(f"✅ Removed {len(to_remove)} tools.")

    def reset_inventory(self):
        """
        Clears all script entries from the inventory while keeping metadata.
        """
        print("🗑️ Resetting tool inventory (clearing all script registrations)...")
        if "python" in self.data:
            self.data["python"]["tools"] = {}
        if "javascript" in self.data:
            self.data["javascript"]["tools"] = {}
        if "scripts" in self.data:
            self.data["scripts"] = {}
        
        self.save()
        print("✅ Inventory reset successfully.")

    def sync_from_cache(self, cache_path: str = ".agent/learning/rlm_tool_cache.json"):
        """
        Populates tool descriptions from the RLM tool cache.
        """
        cache_file = self.root_dir / cache_path
        if not cache_file.exists():
            print(f"❌ Cache not found at {cache_file}")
            return

        with open(cache_file, 'r') as f:
            cache = json.load(f)

        updated_count = 0
        
        def process_node(node):
            nonlocal updated_count
            if isinstance(node, list):
                for entry in node:
                    if isinstance(entry, dict) and 'path' in entry:
                        path = entry['path']
                        if path in cache:
                            cached_data = cache[path]
                            if 'summary' in cached_data:
                                try:
                                    summary_json = json.loads(cached_data['summary'])
                                    purpose = summary_json.get('purpose', 'TBD')
                                    if purpose and purpose != 'TBD':
                                        entry['description'] = purpose
                                        updated_count += 1
                                        print(f"✅ Updated {path}")
                                except json.JSONDecodeError:
                                    entry['description'] = cached_data['summary']
                                    updated_count += 1
                                    print(f"✅ Updated {path} (plain string)")
            elif isinstance(node, dict):
                for v in node.values():
                    process_node(v)

        print(f"🔄 Syncing descriptions from {cache_path}...")
        if "python" in self.data:
            process_node(self.data["python"].get("tools", {}))
        if "javascript" in self.data:
            process_node(self.data["javascript"].get("tools", {}))
        if "scripts" in self.data:
            process_node(self.data["scripts"])

        if updated_count > 0:
            self.save()
            print(f"✨ Successfully enriched {updated_count} tool descriptions.")
        else:
            print("ℹ️ No matching tools found in cache to enrich.")

    def summarize_missing(self, cache_path: str = ".agent/learning/rlm_tool_cache.json"):
        """
        Identify tools missing from cache and trigger RLM distillation.
        """
        cache_file = self.root_dir / cache_path
        cache = {}
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                cache = json.load(f)
        
        missing_paths = []
        
        def collect_missing(node):
            if isinstance(node, list):
                for entry in node:
                    if isinstance(entry, dict) and 'path' in entry:
                        path = entry['path']
                        # Only summarize code files
                        if path.endswith(('.py', '.js')) and path not in cache:
                            missing_paths.append(path)
            elif isinstance(node, dict):
                for v in node.values():
                    collect_missing(v)

        if "python" in self.data:
            collect_missing(self.data["python"].get("tools", {}))
        if "javascript" in self.data:
            collect_missing(self.data["javascript"].get("tools", {}))
        if "scripts" in self.data:
            collect_missing(self.data["scripts"])

        if not missing_paths:
            print("✅ All inventory tools are already summarized in cache.")
            return

        print(f"🔎 Found {len(missing_paths)} tools missing from cache.")
        for i, path in enumerate(missing_paths, 1):
            print(f"[{i}/{len(missing_paths)}] ", end="")
            self._trigger_distillation(path)
        
        print(f"✨ Finished summarizing {len(missing_paths)} tools.")
        print("💡 Tip: Run 'sync-from-cache' now to update descriptions in inventory.")

# -----------------------------------------------------------------------------
# Documentation Generator (The "View" Layer)
# -----------------------------------------------------------------------------

def generate_markdown(manager: InventoryManager, output_path: Path):
    """Generate Markdown documentation from the Inventory Manager data."""
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    inv_rel_path = manager.inventory_path.relative_to(manager.root_dir) if manager.inventory_path.is_relative_to(manager.root_dir) else manager.inventory_path.name
    
    lines = [
        f"# Tool Inventory",
        "",
        f"> **Auto-generated:** {timestamp}",
        f"> **Source:** [`{inv_rel_path}`]({inv_rel_path})",
        f"> **Regenerate:** `python plugins/tool-inventory/scripts/manage_tool_inventory.py generate --inventory {inv_rel_path}`",
        "",
        "---",
        ""
    ]

    # Normalize data structure
    if "python" in manager.data:
        sources = manager.data["python"].get("tools", {})
    else:
        sources = manager.data.get("scripts", {})

    # Sort categories
    for category in sorted(sources.keys()):
        tools = sources[category]
        if not tools: continue

        emoji = CATEGORY_EMOJIS.get(category.lower().split('/')[-1], '📁')
        display_name = category.replace('/', ' / ').replace('_', ' ').title()
        
        lines.append(f"## {emoji} {display_name}")
        lines.append("")
        lines.append("| Script | Description |")
        lines.append("| :--- | :--- |")
        
        for tool in sorted(tools, key=lambda x: x['name']):
            name = tool['name']
            path = tool['path']
            desc = tool.get('description', 'TBD').replace('\n', ' ')
            lines.append(f"| [`{name}`]({path}) | {desc} |")
        
        lines.append("")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Generated Markdown: {output_path}")


# -----------------------------------------------------------------------------
# Utils
# -----------------------------------------------------------------------------

def extract_docstring(file_path: Path) -> str:
    """Read file and extract PyDoc or JSDoc."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(2000)
    except:
        return "TBD"

    # Python Docstring
    if file_path.suffix == '.py':
        # Search for docstring (non-anchored to allow shebangs/imports)
        match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if match:
            # Get first non-empty line
            lines = [l.strip() for l in match.group(1).split('\n') if l.strip()]
            for line in lines:
                if not line.startswith('plugins/') and not line.startswith('='):
                   return line
            return lines[0] if lines else "TBD"

    # JS Docstring
    if file_path.suffix == '.js':
        match = re.search(r'/\*\*(.*?)\*/', content, re.DOTALL)
        if match:
             # Look for Purpose:
            purpose = re.search(r'Purpose:\s*(.*?)(?:\n|\*)', match.group(1), re.IGNORECASE)
            if purpose:
                return purpose.group(1).strip()
    
    return "TBD"

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Manage Tool Inventories (Global & Local)")
    
    # Global args
    parser.add_argument("--inventory", default="legacy-system/reference-data/tool_inventory.json", help="Path to JSON inventory")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Subcommands
    subparsers.add_parser("list", help="List all tools")
    subparsers.add_parser("audit", help="Check for missing/untracked files")
    
    add_parser = subparsers.add_parser("add", help="Add a tool to inventory")
    add_parser.add_argument("--path", required=True, help="Relative path to tool")
    add_parser.add_argument("--category", help="Category (e.g. curate/inventories)")
    add_parser.add_argument("--desc", help="Description (Optional, auto-extracted if empty)")

    gen_parser = subparsers.add_parser("generate", help="Generate Markdown documentation")
    gen_parser.add_argument("--output", help="Output file path (Default: adjacent TOOL_INVENTORY.md)")

    search_parser = subparsers.add_parser("search", help="Search for tools by keyword")
    search_parser.add_argument("keyword", nargs='?', help="Keyword to search in name/path/description")
    search_parser.add_argument("--status", choices=COMPLIANCE_STATUS, help="Filter by compliance status")

    update_parser = subparsers.add_parser("update", help="Update a tool's description or path")
    update_parser.add_argument("--path", required=True, help="Current path or name of the tool")
    update_parser.add_argument("--desc", help="New description")
    update_parser.add_argument("--new-path", help="New path")
    update_parser.add_argument("--mark-compliant", action="store_true", help="Mark as compliant")

    remove_parser = subparsers.add_parser("remove", help="Remove a tool from inventory")
    remove_parser.add_argument("--path", required=True, help="Path or name of tool to remove")

    discover_parser = subparsers.add_parser("discover", help="Find untracked scripts and create stubs")
    discover_parser.add_argument("--auto-stub", action="store_true", help="Automatically create stub entries")
    discover_parser.add_argument("--include-json", action="store_true", help="Include JSON config files")
    discover_parser.add_argument("--json", action="store_true", help="Output as JSON")

    std_parser = subparsers.add_parser("standardize", help="Apply standardized header to scripts")
    std_parser.add_argument("--path", help="Single script path")
    std_parser.add_argument("--batch", action="store_true", help="Process all 'stub' tools")
    std_parser.add_argument("--dry-run", action="store_true", help="Preview changes only")

    subparsers.add_parser("reset-compliance", help="Reset compliance status for all tools")
    
    subparsers.add_parser("clear-inventory", help="Clear all registered tools from inventory")
    
    sync_parser = subparsers.add_parser("sync-from-cache", help="Sync tool descriptions from RLM cache")
    sync_parser.add_argument("--cache", default=".agent/learning/rlm_tool_cache.json", help="Path to RLM tool cache")

    subparsers.add_parser("reset-from-cache", help="Full reset: Clear, Discover, and Sync from Cache")

    subparsers.add_parser("summarize-missing", help="Trigger RLM distillation for tools missing from cache")

    clean_ext_parser = subparsers.add_parser("cleanup-types", help="Remove tools by extension")
    clean_ext_parser.add_argument("--ext", nargs="+", required=True, help="Extensions to remove (e.g. .ts .tsx)")

    clean_path_parser = subparsers.add_parser("cleanup-path", help="Remove tools by path pattern")
    clean_path_parser.add_argument("--pattern", required=True, help="Substring match for path removal")

    args = parser.parse_args()

    # Load
    inv_path = Path(args.inventory)
    manager = InventoryManager(inv_path)

    # Dispatch
    if args.command == "list":
        manager.list_tools()
    
    elif args.command == "add":
        manager.add_tool(args.path, args.category, args.desc)
    
    elif args.command == "audit":
        manager.audit()
    
    elif args.command == "generate":
        # Determine output
        if args.output:
            out_path = Path(args.output)
        else:
            out_path = inv_path.parent / "TOOL_INVENTORY.md"
        
        generate_markdown(manager, out_path)
    
    elif args.command == "search":
        if args.status:
            # Search by status
            results = manager.search_by_status(args.status)
            if not results:
                print(f"❌ No tools found with status '{args.status}'")
            else:
                print(f"\n🔍 Found {len(results)} tool(s) with status '{args.status}':\n")
                for r in results:
                    print(f"  📦 {r['name']}")
                    print(f"     Path: {r['path']}")
                    print(f"     Category: {r['category']}")
                    print(f"     Header Style: {r.get('header_style', 'unknown')}")
                    print()
        elif args.keyword:
            manager.search(args.keyword)
        else:
            print("❌ Please provide a keyword or --status flag")
    
    elif args.command == "update":
        manager.update_tool(args.path, args.desc, getattr(args, 'new_path', None), getattr(args, 'mark_compliant', False))
    
    elif args.command == "discover":
        gaps = manager.discover_gaps(include_json=args.include_json)
        
        total_py = len(gaps['with_docstring']) + len(gaps['without_docstring'])
        total_json = len(gaps['json_configs'])
        
        if args.json:
            import json as json_mod
            output = {
                'with_docstring': [{'path': p, 'description': d} for p, d in gaps['with_docstring']],
                'without_docstring': gaps['without_docstring'],
                'json_configs': gaps['json_configs'],
                'summary': {
                    'total_python': total_py,
                    'with_docstring': len(gaps['with_docstring']),
                    'without_docstring': len(gaps['without_docstring']),
                    'json_configs': total_json
                }
            }
            print(json_mod.dumps(output, indent=2))
        else:
            print(f"\n🔎 Gap Discovery Report")
            print("=" * 50)
            print(f"Found {total_py} untracked Python scripts\n")
            
            if gaps['with_docstring']:
                print("[WITH DOCSTRING] (auto-extracted):")
                for path, desc in gaps['with_docstring'][:10]:
                    print(f"  ✅ {path}")
                    print(f"     → {desc[:80]}..." if len(desc) > 80 else f"     → {desc}")
                if len(gaps['with_docstring']) > 10:
                    print(f"  ... and {len(gaps['with_docstring']) - 10} more")
                print()
            
            if gaps['without_docstring']:
                print("[NO DOCSTRING] (needs header):")
                for path in gaps['without_docstring'][:10]:
                    print(f"  ⚠️ {path}")
                if len(gaps['without_docstring']) > 10:
                    print(f"  ... and {len(gaps['without_docstring']) - 10} more")
                print()
            
            if gaps['json_configs']:
                print(f"[JSON CONFIGS]: {len(gaps['json_configs'])} files")
                for path in gaps['json_configs'][:5]:
                    print(f"  📄 {path}")
                print()
            
            print(f"\nSummary:")
            print(f"  - {len(gaps['with_docstring'])} scripts with docstrings (auto-extractable)")
            print(f"  - {len(gaps['without_docstring'])} scripts without docstrings (need headers)")
            if args.include_json:
                print(f"  - {len(gaps['json_configs'])} JSON config files")
        
        # Auto-stub if requested
        if args.auto_stub:
            print(f"\n📝 Creating stub entries...")
            created = 0
            
            # Create stubs for scripts with docstrings first
            for path, desc in gaps['with_docstring']:
                if manager.create_stub(path, extracted_desc=desc):
                    created += 1
            
            # Create stubs for scripts without docstrings
            for path in gaps['without_docstring']:
                if manager.create_stub(path):
                    created += 1
            
            if created > 0:
                manager.save()
                print(f"✅ Created {created} stub entries")
            else:
                print("ℹ️ No new stubs created (all scripts already tracked)")
    
    elif args.command == "remove":
        manager.remove_tool(args.path)
    
    elif args.command == "standardize":
        if args.path:
            manager.standardize_header(args.path, dry_run=args.dry_run)
        elif args.batch:
            stubs = manager.search_by_status("stub")
            if not stubs:
                print("✅ No stubs found to standardize.")
            else:
                print(f"🚀 Standardizing {len(stubs)} scripts...")
                for tool in stubs:
                    manager.standardize_header(tool['path'], dry_run=args.dry_run)
        else:
            print("❌ Please specify --path or --batch")
    
    elif args.command == "reset-compliance":
        manager.reset_compliance()
    
    elif args.command == "clear-inventory":
        manager.reset_inventory()
    
    elif args.command == "sync-from-cache":
        manager.sync_from_cache(args.cache)
    
    elif args.command == "reset-from-cache":
        print("🚀 Performing full tool inventory reset from cache...")
        manager.reset_inventory()
        gaps = manager.discover_gaps(include_json=True)
        
        # Auto-stub
        print(f"📝 Creating stubs for {len(gaps['with_docstring']) + len(gaps['without_docstring'])} scripts...")
        for path, desc in gaps['with_docstring']:
            manager.create_stub(path, extracted_desc=desc)
        for path in gaps['without_docstring']:
            manager.create_stub(path)
        manager.save()
        
        # Sync
        manager.sync_from_cache()
        
        # Generate
        inv_path = Path(args.inventory)
        out_path = inv_path.parent / "TOOL_INVENTORY.md"
        generate_markdown(manager, out_path)
        print("✅ Full reset from cache complete.")

    elif args.command == "summarize-missing":
        manager.summarize_missing()

    elif args.command == "cleanup-types":
        manager.cleanup_by_extension(args.ext)

    elif args.command == "cleanup-path":
        manager.cleanup_by_path(args.pattern)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()

