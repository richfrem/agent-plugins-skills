#!/usr/bin/env python
"""
Plugin Inventory Generator
==========================

Purpose:
    Scans a plugins directory and generates a detailed JSON inventory of available plugins.
    Uses a multi-tier metadata extraction strategy (Manifest -> SKILL.md -> README.md).

Layer: Plugin Manager / Inventory

Usage Examples:
    python plugins/plugin-manager/scripts/plugin_inventory.py [--root <project_root>] [--output <file.json>]
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path

# --- Configuration ---
SKIP_DIRS = frozenset({"node_modules", "venv", "env", ".venv", "__pycache__", ".git"})

def extract_metadata(plugin_dir: Path) -> dict:
    """
    Extracts name and description from a plugin directory using a waterfall approach.
    
    Args:
        plugin_dir: Path to the specific plugin folder.
        
    Returns:
        Dictionary containing 'name', 'description', 'version', and 'path'.
    """
    metadata = {
        "name": plugin_dir.name,
        "description": "",
        "version": "",
        "path": str(plugin_dir.resolve()).replace("\\", "/") # Unix style absolute paths
    }

    # 1. Try manifest files (Standard source)
    for manifest_rel in [".claude-plugin/plugin.json", "plugin.json"]:
        manifest = plugin_dir / manifest_rel
        if manifest.exists():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                metadata["name"] = data.get("name", metadata["name"])
                desc = data.get("description", "")
                # Clean HTML tags and collapse whitespace
                desc = re.sub(r'<[^>]+>', '', desc).strip()
                metadata["description"] = desc
                metadata["version"] = data.get("version", "")
                if metadata["description"]:
                    return metadata
            except Exception:
                pass

    # 2. Try SKILL.md frontmatter (Common in this repo)
    skills_dir = plugin_dir / "skills"
    if skills_dir.exists() and skills_dir.is_dir():
        for skill_item in skills_dir.iterdir():
            if skill_item.is_dir():
                skill_file = skill_item / "SKILL.md"
                if skill_file.exists():
                    try:
                        content = skill_file.read_text(encoding='utf-8')
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 3:
                                # Simple regex-based extraction to avoid PyYAML dependency
                                match = re.search(r'description:\s*(.*)', parts[1])
                                if match:
                                    desc = match.group(1).strip().strip('"').strip("'")
                                    metadata["description"] = desc
                                    return metadata
                    except Exception:
                        pass
        
        # Fallback description if skills exist but no description found
        n = len([d for d in skills_dir.iterdir() if d.is_dir()])
        metadata["description"] = f"{n} skill{'s' if n != 1 else ''}"

    # 3. Try README.md (Last resort)
    readme = plugin_dir / "README.md"
    if readme.exists():
        try:
            lines = readme.read_text(encoding='utf-8').splitlines()
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    metadata["description"] = line
                    return metadata
        except Exception:
            pass
                
    return metadata

def scan_plugins(root: Path) -> list[dict]:
    """
    Scans the plugins/ directory for available plugins and extracts metadata.
    
    Args:
        root: The project root directory.
        
    Returns:
        List of plugin metadata dictionaries.
    """
    plugins_dir = root / "plugins"
    if not plugins_dir.exists():
        print(f"Error: Plugins directory not found at {plugins_dir}", file=sys.stderr)
        return []

    inventory = []
    
    # Sort for deterministic output
    for item in sorted(plugins_dir.iterdir()):
        if item.is_dir() and not item.name.startswith((".", "__")):
            if item.name in SKIP_DIRS:
                continue
            meta = extract_metadata(item)
            inventory.append(meta)
            
    return inventory

def main() -> None:
    """
    Main entry point for generating the plugin inventory.
    """
    parser = argparse.ArgumentParser(description="Generate plugin inventory.")
    parser.add_argument("--root", default=".", help="Project root directory containing plugins/")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    inventory = scan_plugins(root)

    json_output = json.dumps(inventory, indent=2)

    if args.output:
        try:
            output_path = Path(args.output).resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json_output, encoding='utf-8')
            print(f"Inventory saved to {args.output} ({len(inventory)} plugins)")
        except Exception as e:
            print(f"Error saving inventory to {args.output}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(json_output)

if __name__ == "__main__":
    main()

