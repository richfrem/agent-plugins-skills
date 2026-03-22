#!/usr/bin/env python3
"""
check_for_broken_symlinks.py
=====================================

Purpose:
    Scans all files and symlinks across plugins and builds an inventory database,
    detecting broken symlinks and generating corrective mapping repair scripts.

Layer: Investigate / Codify

Usage:
    python3 check_for_broken_symlinks.py
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
                          fix_cmd = f"ln -f -s '../../../references/{name}' '{loc}'"
                          break

            if fix_cmd == "" and candidates:
                 for cand in candidates:
                     if "assets/" in cand:
                          mapped = f"Found elsewhere: {cand}"
                          break

            if fix_cmd != "":
                 report_lines.append(f"| `{loc}` | `{target}` | {mapped} | ✅ Fixable |")
                 fix_commands.append(f"ln -f -s '{mapped.split('`')[1]}' '{loc}'" if mapped.startswith("`") else fix_cmd)
            else:
                 report_lines.append(f"| `{loc}` | `{target}` | {mapped} | ⚠️  Manual Fix |")
                 
    return report_lines, fix_commands

def save_outputs(inventory_list: List[Dict[str, Any]], report_lines: List[str], fix_commands: List[str]) -> None:
    """
    Saves the JSON inventory, Markdown report, and shell script file representations.

    Args:
        inventory_list: List of full filesystem inventory dictionary items.
        report_lines: Formatted markdown strings.
        fix_commands: Corrective bash shell scripts.
    """
    inventory_path = os.path.join(PLUGINS_DIR, "agent-plugin-analyzer/references/plugin_files_and_symlinks_inventory.json")
    os.makedirs(os.path.dirname(inventory_path), exist_ok=True)
    with open(inventory_path, "w") as f:
        json.dump(inventory_list, f, indent=2)

    report_path = os.path.join(PLUGINS_DIR, "agent-plugin-analyzer/references/broken_symlinks_repair_report.md")
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))

    fix_script_path = os.path.join(PLUGINS_DIR, "agent-plugin-analyzer/scripts/apply_symlink_repairs.sh")
    with open(fix_script_path, "w") as f:
        f.write("\n".join(fix_commands))

    print("✅ Analysis Complete.")
    print(f"Report: {report_path}")
    print(f"Fix Script: {fix_script_path}")

def main() -> None:
    """Main execution orchestrator."""
    print("Scanning plugins for all files and symlinks...")
    inv_list, sym_list = build_inventory(PLUGINS_DIR)
    
    rep_lines, fix_cmds = perform_gap_analysis(inv_list, sym_list)
    
    save_outputs(inv_list, rep_lines, fix_cmds)

if __name__ == "__main__":
    main()
