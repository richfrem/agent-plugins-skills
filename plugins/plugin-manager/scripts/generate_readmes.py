#!/usr/bin/env python3
"""
Generate Plugin READMEs
=======================

Generates a standardized README.md for plugins that are missing one.
Extracts description from .claude-plugin/plugin.json or SKILL.md.

Usage:
    python3 plugins/plugin-manager/skills/plugin-manager/scripts/generate_readmes.py [--apply]
"""

import sys
import json
import argparse
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent  # repo-root/plugins/plugin-manager/scripts/ → 3 levels up
PLUGINS_DIR = PROJECT_ROOT / "plugins"

def get_plugin_description(plugin_path: Path) -> str:
    # 1. Check plugin.json
    plugin_json = plugin_path / ".claude-plugin" / "plugin.json"
    if plugin_json.exists():
        try:
            data = json.loads(plugin_json.read_text())
            return data.get("description", "No description provided.")
        except:
            pass
            
    # 2. Check SKILL.md
    # Try to find SKILL.md in skills/*/SKILL.md
    skills_dir = plugin_path / "skills"
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir(): continue
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                # Extract description from frontmatter
                content = skill_md.read_text()
                for line in content.splitlines():
                    if line.startswith("description:"):
                        return line.replace("description:", "").strip()
                        
    return "No description provided."

def generate_readme(plugin_path: Path, description: str, apply: bool):
    readme_path = plugin_path / "README.md"
    
    if readme_path.exists():
        return # Skip if exists
        
    print(f"📄 Generating README for {plugin_path.name}")
    print(f"   Description: {description}")
    
    content = f"""# {plugin_path.name.title().replace('-', ' ')} Plugin

{description}

## Overview
This plugin provides capabilities for the **{plugin_path.name}** domain.
It follows the standard Project Sanctuary plugin architecture.

## Structure
- `skills/`: Contains the agent skills instructions (`SKILL.md`) and executable scripts.
- `.claude-plugin/`: Plugin manifest and configuration.

## Usage
This plugin is automatically loaded by the Agent Environment.
"""
    
    if apply:
        readme_path.write_text(content)
        print(f"   ✅ Created: {readme_path}")
    else:
        print("   (Dry run - use --apply to create)")

def main():
    parser = argparse.ArgumentParser(description="Generate Plugin READMEs")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    args = parser.parse_args()
    
    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
            continue
            
        if (plugin_dir / "README.md").exists():
            continue
            
        description = get_plugin_description(plugin_dir)
        generate_readme(plugin_dir, description, args.apply)

if __name__ == "__main__":
    main()
