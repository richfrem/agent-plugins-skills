---
concept: only-check-files-in-pluginsskills
source: plugin-code
source_file: agent-scaffolders/scripts/fix_inside_plugin_symlinks.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.303751+00:00
cluster: path
content_hash: 2a8449871b32038f
---

# Only check files in plugins/*/skills/*

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/fix_inside_plugin_symlinks.py -->
#!/usr/bin/env python
"""
fix_inside_plugin_symlinks.py
=====================================

Purpose:
    Creates local relative symlinks for files that skills reference inside 
    their parent plugin to preserve distribution containment guarantees.

Layer: Investigate / Repair

Usage Examples:
    python scripts/fix_inside_plugin_symlinks.py temp/inventory.json --project . --dry-run
    python scripts/fix_inside_plugin_symlinks.py temp/inventory.json --project . --apply

Supported Object Types:
    Skill file references.

CLI Arguments:
    inventory: Path to inventory.json (Required)
    --project: Project root (default: .)
    --dry-run: Preview changes only (default: True if no action supplied)
    --apply: Apply fixes on disk

Input Files:
    - inventory.json

Output:
    Console logs listing SYMLINKS and UPDATES applied.

Key Functions:
    - InsidePluginSymlinkFixer.load_inventory()
    - InsidePluginSymlinkFixer.get_plugin_root()
    - InsidePluginSymlinkFixer.analyze()
    - InsidePluginSymlinkFixer.propose_fix()
    - InsidePluginSymlinkFixer.apply_fixes()

Script Dependencies:
    - json
    - sys
    - argparse
    - os
    - subprocess
    - platform
    - Path (pathlib)

Consumed by:
    Static auditor repair workflows.
"""

import json
import sys
import argparse
import os
import subprocess
import platform
from pathlib import Path
from collections import defaultdict

class InsidePluginSymlinkFixer:
    def __init__(self, inventory_file: str | Path, project_root: str | Path) -> None:
        self.inventory_file = Path(inventory_file)
        self.project_root = Path(project_root).resolve()
        self.violations = []
        self.fixes = []
        self.skipped = []

    def load_inventory(self) -> dict:
        """Load inventory.json"""
        with open(self.inventory_file, 'r') as f:
            return json.load(f)

    def get_plugin_root(self, file_path: str) -> tuple[Path | None, str | None]:
        """Extract plugin root from path like plugins/adr-manager/skills/adr-management/file.md"""
        parts = Path(file_path).parts
        if 'plugins' in parts:
            idx = parts.index('plugins')
            if idx + 1 < len(parts):
                plugin_name = parts[idx + 1]
                return Path(*parts[:idx+2]), plugin_name
        return None, None

    def analyze(self) -> None:
        """Find all inside-plugin violations"""
        inventory = self.load_inventory()

        for ref_entry in inventory['references']:
            source_file = ref_entry['source_file']
            reference = ref_entry['reference']
            status = ref_entry.get('status', {})

            # Only check files in plugins/*/skills/*
            if 'plugins' not in source_file or ('/skills/' not in source_file and '\\skills\\' not in source_file):
                continue

            plugin_root, plugin_name = self.get_plugin_root(source_file)
            if not plugin_root or not plugin_name:
                continue

            resolved = status.get('resolved_path')
            if not resolved:
                continue

            resolved_path = Path(resolved)
            plugin_path = self.project_root / plugin_root

            # Check if resolved path is inside the plugin
            try:
                resolved_path.relative_to(plugin_path)
                is_inside = True
            except ValueError:
                is_inside = False

            if is_inside:
                source_full = self.project_root / source_file
                source_dir = source_full.parent

                self.violations.append({
                    'source_file': source_file,
                    'source_full': source_full,
                    'source_dir': source_dir,
                    'plugin_root': plugin_path,
                    'plugin_name': plugin_name,
                    'reference': reference,
                    'resolved_path': resolved_path,
                    'resolved_rel_to_plugin': resolved_path.r

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/path-reference-auditor/scripts/fix_inside_plugin_symlinks.py -->
#!/usr/bin/env python3
"""
fix_inside_plugin_symlinks.py
=====================================

Purpose:
    Creates local relative symlinks for files that skills reference inside 
    their parent plugin to preserve distribution containment guarantees.

Layer: Investigate / Repair

Usage Examples:
    python scripts/fix_inside_plugin_symlinks.py temp/inventory.json --project . --dry-run
    python scripts/fix_inside_plugin_symlinks.py temp/inventory.json --project . --apply

Supported Object Types:
    Skill file references.

CLI Arguments:
    inventory: Path to inventory.json (Required)
    --project: Project root (default: .)
    --dry-run: Preview changes only (default: True if no action supplied)
    --apply: Apply fixes on disk

Input Files:
    - in

*(combined content truncated)*

## See Also

- [[check-all-text-files-in-skill-for-regex-py-mentions]]
- [[only-include-those-appearing-in-2-of-the-last-n-traces]]
- [[only-process-plugin-root-level-files-not-skill-files]]
- [[1-check-env]]
- [[1-check-root-structure]]
- [[1-initialize-a-custom-manifest-in-a-temp-folder]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/fix_inside_plugin_symlinks.py`
- **Indexed:** 2026-04-27T05:21:04.303751+00:00
