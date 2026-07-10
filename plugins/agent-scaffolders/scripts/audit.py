#!/usr/bin/env python
"""
audit.py (CLI)
=====================================

Purpose:
    Audit plugins against the Agent Skills Open Standard to ensure architectural and resource compliance.

Layer: Meta-Execution

Usage Examples:
    python audit.py --path <plugin-directory>

Supported Object Types:
    - .claude-plugin formatted directories
    - Agent Skills

CLI Arguments:
    --path: The absolute or relative path to the plugin directory to audit.

Input Files:
    - ./plugin.json
    - ././SKILL.md files
    - .mcp.json and hooks.json structures

Output:
    - Terminal stdout (Success/Fail metrics)
    - Warnings for minor structural deviations

Key Functions:
    - audit_plugin(): Recursively checks directory presence and constraints.

Script Dependencies:
    None

Consumed by:
    - User (CLI)
    - ecosystem-standards (Agent Skill)
"""
import argparse
import os
import json
import glob
import sys

# Ensure Unicode output works on Windows terminals that default to cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def audit_plugin(plugin_path: str) -> bool:
    print(f"Auditing Plugin at: {plugin_path}")
    plugin_name = os.path.basename(os.path.normpath(plugin_path))
    errors = []
    warnings = []

    # 0. Detect deprecated stub plugins (no skills/ directory + README marked DEPRECATED)
    skills_dir_check = os.path.join(plugin_path, "skills")
    readme_check = os.path.join(plugin_path, "README.md")
    if not os.path.isdir(skills_dir_check):
        is_deprecated = False
        if os.path.isfile(readme_check):
            with open(readme_check, "r", encoding="utf-8") as f:
                if "DEPRECATED" in f.read():
                    is_deprecated = True
        if is_deprecated:
            print(f"\n✅ AUDIT PASSED - Deprecated stub (no skills, README marked DEPRECATED) ✅")
            print(f"\nInfo: '{plugin_name}' is a deprecated stub and was skipped for full compliance checks.")
            return True

    # 1. Check Root Structure
    claude_plugin_dir = os.path.join(plugin_path, ".claude-plugin")
    if not os.path.isdir(claude_plugin_dir):
        errors.append("Missing `.claude-plugin/` directory.")
    else:
        manifest_path = os.path.join(claude_plugin_dir, "plugin.json")
        if not os.path.isfile(manifest_path):
            errors.append("Missing `plugin.json` inside `.claude-plugin/`.")

    # 1.2. Check standard file layout
    if os.path.isfile(os.path.join(plugin_path, "mcp.json")):
        errors.append("Found `mcp.json` at root. The officially supported standard is `.mcp.json`.")
    if os.path.isfile(os.path.join(plugin_path, "hooks.json")):
        errors.append("Found `hooks.json` at root. The officially supported standard requires `hooks/hooks.json`.")

    # 1.5. Check for README
    readme_path = os.path.join(plugin_path, "README.md")
    if not os.path.isfile(readme_path):
        warnings.append("Missing root `README.md`.")
    else:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "├──" not in content and "└──" not in content:
                warnings.append("The `README.md` is missing a file tree structure. It is highly recommended to include one.")

    # 2. Check Skills
    skills_dir = os.path.join(plugin_path, "skills")
    if os.path.isdir(skills_dir):
        for skill_name in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, skill_name)
            if not os.path.isdir(skill_path):
                continue
            
            skill_md = os.path.realpath(os.path.join(skill_path, "././SKILL.md"))

            if not os.path.isfile(skill_md):
                errors.append(f"Skill '{skill_name}' is missing `././SKILL.md`.")
            else:
                with open(skill_md, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if len(lines) > 500:
                        warnings.append(f"Skill '{skill_name}' ././SKILL.md exceeds 500 lines ({len(lines)} lines). Extract logic to scripts.")
            
            # Check for Microsoft Progressive Disclosure & Testing standard
            references_dir = os.path.realpath(os.path.join(skill_path, "references"))
            if not os.path.isdir(references_dir):
                warnings.append(f"Skill '{skill_name}' is missing a `references/` directory. Progressive Disclosure is highly recommended.")
            else:
                acceptance_file = os.path.realpath(os.path.join(references_dir, "acceptance-criteria.md"))
                if not os.path.isfile(acceptance_file):
                    errors.append(f"Skill '{skill_name}' is missing `./acceptance-criteria.md`. All skills must have test criteria.")
                    
            # Check for illegal root directories inside skill (enforce agentskills.io Optional Directories)
            allowed_skill_dirs = {".history", "scripts", "references", "assets", "examples", "templates", "evals", "tests"}
            for item in os.listdir(skill_path):
                full_item_path = os.path.join(skill_path, item)
                if os.path.isdir(full_item_path) and item not in allowed_skill_dirs and not item.startswith("."):
                    errors.append(f"Skill '{skill_name}' contains illegal root directory '{item}/'. Only ['scripts', 'references', 'assets', 'examples', 'templates', 'evals', 'tests'] and specific scaffolds are allowed.")

    if errors:
        print("\n❌ AUDIT FAILED ❌")
        for e in errors:
            print(f"  - {e}")
    else:
        print("\n✅ AUDIT PASSED - Fully Open Standard Compliant ✅")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")

    return len(errors) == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit a plugin for agent ecosystem standard compliance.")
    parser.add_argument("--path", required=True, help="Path to the plugin directory to audit")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.path):
        print(f"Error: Path '{args.path}' does not exist or is not a directory.")
        exit(1)
        
    success = audit_plugin(args.path)
    if not success:
        exit(1)
