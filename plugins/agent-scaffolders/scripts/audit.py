#!/usr/bin/env python3
"""
audit.py (CLI)
=====================================

Purpose:
    Audit plugins against the Agent Skills Open Standard to ensure architectural and resource compliance.

Layer: Meta-Execution

Usage Examples:
    python3 audit.py --path <plugin-directory>

Supported Object Types:
    - .claude-plugin formatted directories
    - Agent Skills

CLI Arguments:
    --path: The absolute or relative path to the plugin directory to audit.

Input Files:
    - plugin.json
    - SKILL.md files
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

def audit_plugin(plugin_path):
    print(f"Auditing Plugin at: {plugin_path}")
    errors = []
    warnings = []

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
            
            skill_md = os.path.join(skill_path, "SKILL.md")
            if not os.path.isfile(skill_md):
                errors.append(f"Skill '{skill_name}' is missing `SKILL.md`.")
            else:
                with open(skill_md, "r") as f:
                    lines = f.readlines()
                    if len(lines) > 500:
                        warnings.append(f"Skill '{skill_name}' SKILL.md exceeds 500 lines ({len(lines)} lines). Extract logic to scripts.")
            
            # Check for illegal bash/powershell scripts
            scripts_dir = os.path.join(skill_path, "scripts")
            if os.path.isdir(scripts_dir):
                for script_file in os.listdir(scripts_dir):
                    if script_file.endswith(".sh") or script_file.endswith(".ps1"):
                        errors.append(f"Skill '{skill_name}' contains illegal script '{script_file}'. Only Python (.py) is allowed.")
                        
            # Check for Microsoft Progressive Disclosure & Testing standard
            references_dir = os.path.join(skill_path, "references")
            if not os.path.isdir(references_dir):
                warnings.append(f"Skill '{skill_name}' is missing a `references/` directory. Progressive Disclosure is highly recommended.")
            else:
                acceptance_file = os.path.join(references_dir, "acceptance-criteria.md")
                if not os.path.isfile(acceptance_file):
                    errors.append(f"Skill '{skill_name}' is missing `references/acceptance-criteria.md`. All skills must have test criteria.")

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
