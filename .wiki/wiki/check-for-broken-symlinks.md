---
concept: check-for-broken-symlinks
source: plugin-code
source_file: agent-scaffolders/scripts/check_for_broken_symlinks.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.824635+00:00
cluster: name
content_hash: 1b0c7a6b2014a5c7
---

# Check For Broken Symlinks

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
check_for_broken_symlinks.py
=====================================

Purpose:
    Scans all files and symlinks across plugins and builds an inventory database,
    detecting broken symlinks and generating corrective mapping repair scripts.

Layer: Investigate / Codify

Usage:
    pythoncheck_for_broken_symlinks.py
"""

import os
import json
from typing import List, Dict, Tuple, Any

PROJECT_ROOT: str = os.getcwd()
PLUGINS_DIR: str = os.path.join(PROJECT_ROOT, "plugins")

def build_inventory(plugins_dir: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Scans the plugins folder and builds file and symlink inventory lists.

    Args:
        plugins_dir: Absolute path to the plugins directory.

    Returns:
        A tuple containing (inventory, symlinks) lists.
    """
    inventory_list: List[Dict[str, Any]] = []
    symlinks_list: List[Dict[str, Any]] = []

    for root, dirs, files in os.walk(plugins_dir):
        for name in files + dirs:
            if name.startswith("."):
                continue
                
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, PROJECT_ROOT)
            is_link = os.path.islink(full_path)
            
            entry = {
                "name": name,
                "path": rel_path,
                "is_symlink": is_link
            }
            
            if is_link:
                target = os.readlink(full_path)
                entry["target"] = target
                entry["is_broken"] = not os.path.exists(full_path)
                symlinks_list.append(entry)
            
            inventory_list.append(entry)
            
    return inventory_list, symlinks_list

def perform_gap_analysis(
    inventory_list: List[Dict[str, Any]], 
    symlinks_list: List[Dict[str, Any]]
) -> Tuple[List[str], List[str]]:
    """
    Compares broken symlinks against physical file paths to map targets.

    Args:
        inventory_list: List of all files and directories.
        symlinks_list: List of all symbolic links found.

    Returns:
        A tuple containing (report_lines, fix_commands) lists.
    """
    physical_files_by_name: Dict[str, List[str]] = {}
    for item in inventory_list:
        if not item["is_symlink"] and not os.path.isdir(os.path.join(PROJECT_ROOT, item["path"])):
            name = item["name"]
            if name not in physical_files_by_name:
                physical_files_by_name[name] = []
            physical_files_by_name[name].append(item["path"])

    report_lines = [
        "# Broken Symlinks Repair Report",
        "",
        "| Current Symlink Location | Target points to | Correct Target Candidate | Status |",
        "|--------------------------|------------------|--------------------------|--------|",
    ]
    fix_commands = ["#!/bin/bash", "echo 'Repairing symlinks...'"]

    for link in symlinks_list:
        if link.get("is_broken", False):
            name = link["name"]
            loc = link["path"]
            target = link["target"]
            
            candidates = physical_files_by_name.get(name, [])
            mapped = "⚠️  Unknown target"
            fix_cmd = ""

            link_parts = loc.split("/")
            if "skills" in link_parts and "references" in link_parts:
                 skill_name = link_parts[link_parts.index("skills") + 1]
                 for cand in candidates:
                     if f"skills/{skill_name}/{name}" in cand:
                          mapped = f"`../{name}` (Skill Root)"
                          fix_cmd = f"ln -f -s '../{name}' '{loc}'"
                          break

            if fix_cmd == "" and candidates:
                 plugin_name = link_parts[1]
                 for cand in candidates:
                     if cand.startswith(f"plugins/{plugin_name}/references/{name}"):
                          mapped = f"`../../../references/{name}` (Plugin References)"
                          fix_cmd = 

*(content truncated)*

## See Also

- [[broken-symlinks-repair-report]]
- [[check-all-text-files-in-skill-for-regex-py-mentions]]
- [[check-if-we-already-emitted-for-this-completion-avoid-duplicate-events]]
- [[1-check-env]]
- [[1-check-root-structure]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/check_for_broken_symlinks.py`
- **Indexed:** 2026-04-27T05:21:03.824635+00:00
