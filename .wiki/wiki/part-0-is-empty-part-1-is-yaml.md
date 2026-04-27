---
concept: part-0-is-empty-part-1-is-yaml
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/maintain-plugins/scripts/plugin_inventory.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.250361+00:00
cluster: plugin
content_hash: 410adf0918e124be
---

# Part 0 is empty, Part 1 is YAML

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

"""
Plugin Inventory Generator
==========================

Purpose:
    Scans a plugins directory and generates a detailed JSON inventory of available plugins.
    Extracts metadata from:
    1. .claude-plugin/plugin.json (Best source)
    2. SKILL.md frontmatter (Fallback)
    3. README.md (Last resort)

Layer: Plugin Manager / Inventory

Usage Examples:
    python3 plugins/plugin-manager/scripts/plugin_inventory.py [--root <project_root>] [--output <file.json>]

Supported Object Types:
    - json (Inventory output)

CLI Arguments:
    --root: Project root directory containing plugins/.
    --output: Output JSON file path.

Input Files:
    - .claude-plugin/plugin.json (Metadata source)
    - SKILL.md (Fallback)
    - README.md (Fallback)

Output:
    - Writes a JSON array of plugin objects.

Key Functions:
    extract_metadata(): Extracts name and description from plugin directory.
    scan_plugins(): Scans plugins and returns list.

Script Dependencies:
    os, sys, json, yaml, argparse, pathlib

Consumed by:
    - None (Standalone script)
Related:
    - scripts/sync_with_inventory.py
"""

import os
import sys
import json
import yaml  # Requires PyYAML or simple parsing
import argparse
from pathlib import Path

def parse_frontmatter(file_path: Path) -> str | None:
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

def scan_plugins(root: Path) -> list[dict]:
    plugins_dir = root / "plugins"
    if not plugins_dir.exists():
        print(f"Error: Plugins directory not found at {plugins_dir}", file=sys.stderr)
        return []

    inventory = []
    
    # Sort for stability
    

*(content truncated)*

## See Also

- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[default-file-extensions-to-index-if-manifest-is-empty]]
- [[1-basic-summarize-all-documents]]
- [[1-check-env]]
- [[1-check-root-structure]]
- [[1-configuration-setup-dynamic-from-profile]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/maintain-plugins/scripts/plugin_inventory.py`
- **Indexed:** 2026-04-27T05:21:04.250361+00:00
