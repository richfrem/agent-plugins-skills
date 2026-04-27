---
concept: only-process-plugin-root-level-files-not-skill-files
source: plugin-code
source_file: agent-scaffolders/scripts/check_plugin_boundaries.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.302282+00:00
cluster: path
content_hash: fc29e545ac60410d
---

# Only process plugin root level files (not skill files)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/check_plugin_boundaries.py -->
#!/usr/bin/env python
"""
check_plugin_boundaries.py
=====================================

Purpose:
    Flags any inside commands, hooks, or assets that point OUTSIDE their 
    assigned plugin directory to ensure self-containment for distribution.

Layer: Investigate / Codify / Audit

Usage Examples:
    pythonheck_plugin_boundaries.py temp/inventory.json --batch all
    pythonheck_plugin_boundaries.py temp/inventory.json --plugin plugins/adr-manager

Supported Object Types:
    Plugin root file references.

CLI Arguments:
    inventory: Path to inventory.json (Required)
    --project: Project root directory (default: .)
    --plugin: Plugin path or name to check (default: all)
    --batch: Batch mode all or specific plugin (default: all)

Input Files:
    - inventory.json

Output:
    Console logs of BOUNDARY VIOLATIONS.

Key Functions:
    - get_plugin_root()
    - is_reference_inside_plugin()
    - filter_references()

Script Dependencies:
    - json
    - Path (pathlib)

Consumed by:
    Static auditor workflows and path reference audits.
"""

import json
import sys
import argparse
from pathlib import Path

def get_plugin_root(source_file_path: str) -> Path | None:
    """
    Extract the plugin root directory from a source file path.

    Only returns a root if the file is at PLUGIN LEVEL (not skill level).

    Examples (PLUGIN LEVEL - check these):
      plugins/adr-manager/commands/adr-management.md  plugins/adr-manager/
      plugins/plugin-installer/hooks/hooks.json  plugins/plugin-installer/
      plugins/adr-manager/.claude-plugin/plugin.json  plugins/adr-manager/

    Examples (SKILL LEVEL - ignore these):
      plugins/adr-manager/skills/adr-management/SKILL.md  None (skip)
      .agents/skills/plugin-installer/SKILL.md  None (skip)
    """
    parts = Path(source_file_path).parts

    # Only process plugin root level files (not skill files)
    # Plugin root files are in: commands/, hooks/, .mcp.json, etc.
    # NOT in skills/

    if "skills" in parts:
        return None  # This is a skill file, not plugin root

    if "plugins" in parts:
        idx = list(parts).index("plugins")
        if idx + 1 < len(parts):
            return Path(*parts[:idx+2])  # e.g., plugins/adr-manager/

    return None

def is_reference_inside_plugin(source_file: str, reference: str, project_root: str | Path) -> tuple[bool | None, Path | None, Path | None]:
    """
    Check if a reference stays within the plugin directory.

    Returns: (is_inside, resolved_path, plugin_root)
    """
    project_root = Path(project_root)
    source_path = project_root / source_file
    source_dir = source_path.parent
    plugin_root = get_plugin_root(source_file)

    if not plugin_root:
        return None, None, None

    plugin_root_abs = project_root / plugin_root

    # Try to resolve the reference
    try:
        # Resolve relative to source file location
        resolved = (source_dir / reference).resolve()
        plugin_root_resolved = plugin_root_abs.resolve()

        # Check if resolved path is within plugin root
        is_inside = str(resolved).startswith(str(plugin_root_resolved))

        return is_inside, resolved, plugin_root_resolved
    except:
        return False, None, plugin_root_abs

def filter_references(references: list[dict], plugin_filter: str) -> list[dict]:
    """Filter references by plugin path or name."""
    if not plugin_filter or plugin_filter.lower() == 'all':
        return references

    filtered = []
    for ref in references:
        source_file = ref['source_file']
        plugin_root = get_plugin_root(source_file)

        if not plugin_root:
            continue

        # Match by full path or plugin name
        plugin_str = str(plugin_root)
        if plugin_filter in plugin_str or plugin_str.endswith(plugin_filter):
            filtered.append(ref)

    return filtered

def main() -> int:
    parser = argparse.ArgumentParser(description='Plugin Boundary Checker')
    parser.add_argument('invent

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/path-reference-auditor/references/check_plugin_boundaries.py -->
#!/usr/bin/env python3
"""
check_plugin_boundaries.py
=====================================

Purpose:
    Flags any inside commands, hooks, or assets that point OUTSIDE their 
    assigned plugin directory to ensure self-containment for distribution.

Layer: Investigate / Codify / Audit

Usage Examples:
    python3 check_plugin_boundaries.py temp/inventory.json --batch all
    python3 check_plugin_boundaries.py temp/inventory.json --plugin plugins/adr-manager

Supported Object Types:
    Plugin root file references.

CLI Arguments:
    inventory: Path to inventory.json (Required)
    --project: Project root directory (default: .)
    --plugin: Plugin path or name to check (default: all)
    --batch: Batch mode all or specific plugin (default: all)

Input Files

*(combined content truncated)*

## See Also

- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[check-all-text-files-in-skill-for-regex-py-mentions]]
- [[only-check-files-in-pluginsskills]]
- [[plugin-files-and-symlinks-inventory]]
- [[1-check-root-structure]]
- [[1-handle-absolute-paths-from-repo-root]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/check_plugin_boundaries.py`
- **Indexed:** 2026-04-27T05:21:04.302282+00:00
