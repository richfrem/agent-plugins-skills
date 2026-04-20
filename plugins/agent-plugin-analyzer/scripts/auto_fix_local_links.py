#!/usr/bin/env python
"""
auto_fix_local_links.py
=====================================

Purpose:
    Safely rewrites hardcoded plugin execution paths in Markdown files.
    Converts full repository absolute paths into relative ones so commands
    remain functional when a skill is installed via legacy methods.

Layer: Investigate / Repair / Documentation

Usage Examples:
    pythonauto_fix_local_links.py

Supported Object Types:
    Markdown files (.md, .mmd).

CLI Arguments:
    None.

Input Files:
    - Recursively discovers Markdown files inside plugins/

Output:
    - Console updates detailing rewritten counts by file.

Key Functions:
    - resolve_project_root()
    - fix_file()

Script Dependencies:
    - os
    - re
    - pathlib

Consumed by:
    Static auditor workflows and pre-flight validation hooks.
"""

import os
import re
from pathlib import Path

# Match pythonexecution paths that are hardcoded to the repo root plugins/ folder
# Group 1: The command (python, python
# Group 2: The plugins prefix (plugins/plugin-name/...)
# Group 3: The actual script path starting with 'scripts/' or similar target
EXEC_RX = re.compile(r'(python|bash) (plugins/[a-zA-Z0-9_\-]+/(?:skills/[a-zA-Z0-9_\-]+/)?)([^ ]+)')

def resolve_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".git").exists() or current.name == "agent-plugins-skills":
            return current
        current = current.parent
    return Path.cwd()


def fix_file(file_path: Path) -> int:
    """Reads a markdown file, replaces hardcoded bash execution paths, and writes back if changed."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return 0
        
    lines = content.splitlines()
    lines = content.splitlines()
    fixed_lines = []
    state = {'replacements': 0}
    
    for line in lines:
        # Skip installation commands and specific hardcoded markers
        if "skills add" in line or "#" in line and "Hardcoded" in line:
            fixed_lines.append(line)
            continue
            
        def replacer(match: re.Match) -> str:
            cmd = match.group(1)
            target = match.group(3)
            state['replacements'] += 1
            
            # Check if it was executing a script directly in the plugin root instead of a skill
            if not target.startswith("scripts/"):
                # if the original string was plugins/agent-plugin-analyzer/scripts/foo.py
                # group 3 would be "scripts/foo.py". 
                if target.startswith("scripts/"):
                    return f"{cmd} ../../{target}"
                return f"{cmd} ./{target}"
            
            return f"{cmd} ./{target}"
            
        new_line = EXEC_RX.sub(replacer, line)
        if new_line != line:
            state['replacements'] += 1
        fixed_lines.append(new_line)
        
    if state['replacements'] > 0:
        file_path.write_text("\n".join(fixed_lines) + "\n", encoding="utf-8")
    return state['replacements']

def main() -> None:
    root = resolve_project_root()
    plugins_dir = root / "plugins"
    print(f"🔧 Starting auto-fix for hardcoded markdown paths in {plugins_dir}...")
    
    total_fixes = 0
    files_fixed = 0
    
    # We primarily target documentation files where users copy/paste commands
    for ext in ("*.md", "*.mmd"):
        for file_path in plugins_dir.rglob(ext):
            # Skip templates or known files that need absolute paths for context
            if ".venv" in file_path.parts or ".agent" in file_path.parts:
                continue
                
            fixes = fix_file(file_path)
            if fixes > 0:
                print(f"  Fixed {fixes} paths in {file_path.relative_to(root)}")
                files_fixed += 1
                total_fixes += fixes
                
    print(f"\n✅ Auto-fix complete! Replaced {total_fixes} paths across {files_fixed} files.")

if __name__ == "__main__":
    main()
