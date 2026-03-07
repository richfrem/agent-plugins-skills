#!/usr/bin/env python3
"""
Plugin Inventory Generator
==========================

Scans a plugins directory and generates a detailed JSON inventory of available plugins.
Extracts metadata from:
1. .claude-plugin/plugin.json (Best source)
2. SKILL.md frontmatter (Fallback)
3. README.md (Last resort)

Usage:
  python3 plugin_inventory.py [--root <project_root>] [--output <file.json>]
"""

import os
import sys
import json
import yaml  # Requires PyYAML or simple parsing
import argparse
from pathlib import Path

def parse_frontmatter(file_path):
    """Simple YAML frontmatter parser to avoid external dependencies if possible."""
    try:
        content = file_path.read_text(encoding='utf-8')
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                # Part 0 is empty, Part 1 is YAML
                yaml_text = parts[1]
                # Simple parsing for 'description: ...'
                for line in yaml_text.splitlines():
                    if line.strip().startswith('description:'):
                        return line.split(':', 1)[1].strip()
    except Exception:
        pass
    return None

def extract_metadata(plugin_dir: Path) -> dict:
    """Extracts name and description from a plugin directory."""
    metadata = {
        "name": plugin_dir.name,
        "description": "No description available.",
        "path": str(plugin_dir).replace("\\", "/") # Unix style paths
    }

    # 1. Try plugin.json (Standard)
    manifest = plugin_dir / ".claude-plugin" / "plugin.json"
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text(encoding='utf-8'))
            if "name" in data: metadata["name"] = data["name"]
            if "description" in data: metadata["description"] = data["description"]
            if "version" in data: metadata["version"] = data["version"]
            return metadata
        except Exception as e:
            # print(f"Warn: Bad json in {plugin_dir.name}: {e}")
            pass

    # 2. Try SKILL.md (Common in this repo)
    # Search for any SKILL.md in subdirs
    # Start with skills/
    skills_dir = plugin_dir / "skills"
    if skills_dir.exists():
        for skill_item in skills_dir.iterdir():
            if skill_item.is_dir():
                skill_file = skill_item / "SKILL.md"
                if skill_file.exists():
                    desc = parse_frontmatter(skill_file)
                    if desc:
                        metadata["description"] = desc
                        return metadata

    # 3. Try README.md
    readme = plugin_dir / "README.md"
    if readme.exists():
        lines = readme.read_text(encoding='utf-8').splitlines()
        # Find first non-header line
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                metadata["description"] = line
                return metadata
                
    return metadata

def scan_plugins(root: Path) -> list:
    plugins_dir = root / "plugins"
    if not plugins_dir.exists():
        print(f"Error: Plugins directory not found at {plugins_dir}", file=sys.stderr)
        return []

    inventory = []
    
    # Sort for stability
    for item in sorted(plugins_dir.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            # Exclude non-plugin dirs if strictly verifying? 
            # For now, assume folders in plugins/ are plugins.
            meta = extract_metadata(item)
            inventory.append(meta)
            
    return inventory

def main():
    parser = argparse.ArgumentParser(description="Generate plugin inventory.")
    parser.add_argument("--root", default=".", help="Project root directory containing plugins/")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    inventory = scan_plugins(root)

    json_output = json.dumps(inventory, indent=2)

    if args.output:
        Path(args.output).write_text(json_output, encoding='utf-8')
        print(f"Inventory saved to {args.output} ({len(inventory)} plugins)")
    else:
        print(json_output)

if __name__ == "__main__":
    main()
