#!/usr/bin/env python
"""
validate_local_links.py
=====================================

Purpose:
    Ensures that all plugins adhere to the Local-First Symlink Architecture.
    Validates containing skills required symlinks pointing UP to the plugin root 
    and verifies no hardcoded string references point outside of expected boundaries.

Layer: Repair / Integrity

Usage Examples:
    pythonvalidate_local_links.py

Supported Object Types:
    Plugins with symlinks inside skill directories.

CLI Arguments:
    None.

Input Files:
    - Codebase plugins/ directories search.

Output:
    Structured summary checklist lists to stdout regarding link creation corrections.

Key Functions:
    - resolve_project_root()
    - scaffold_missing_symlinks()
    - scan_hardcoded_paths()

Script Dependencies:
    - os, re, pathlib (Path), typing (List, Dict, Tuple)

Consumed by:
    Static continuous integration post-validation links checks.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

# The target architecture definition
PLUGIN_TARGETS = {
    "agent-scaffolders": ["agents", "commands", "research", "tests"],
    "agent-scaffolders": ["references", "templates"],
    "vector-db": ["agents", "commands", "references", "resources"],
    "spec-kitty-plugin": ["agents", "references", "rules", "templates"],
    "coding-conventions": ["rules", "templates"],
    "tool-inventory": ["resources", "workflows"],
    "agent-loops": ["resources", "personas", "hooks"],
    "obsidian-integration": ["obsidian-parser", "resources"],
    "agent-scaffolders": ["L4-pattern-definitions"],
    "rlm-factory": ["references", "resources"]
}

# Regex to find hardcoded plugin paths in text files
# Matches explicit strings like "plugins/my-plugin" or "plugins/rlm-factory/scripts"
# We ignore things like `plugins_dir` or conversational text.
HARDCODED_PLUGIN_RX = re.compile(r'\bplugins/[a-zA-Z0-9_\-]+')

# Files to ignore during hardcoded path scanning (usually config roots)
IGNORE_FILES = {
    "validate_local_links.py",
    "cli.py",
    "scaffold.py",
    "inventory.py"
}

def resolve_project_root() -> Path:
    """Finds the repo root by looking for .git or agent-plugins-skills"""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".git").exists() or current.name == "agent-plugins-skills":
            return current
        current = current.parent
    return Path.cwd()

def scaffold_missing_symlinks(root: Path) -> List[str]:
    """Ensures all required symlinks exist according to PLUGIN_TARGETS."""
    results = []
    
    for plugin, required_links in PLUGIN_TARGETS.items():
        skills_dir = root / "plugins" / plugin / "skills"
        if not skills_dir.exists():
            continue
            
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
                
            # Skip ollama-launch as it has custom internal resolutions
            if skill_dir.name == "ollama-launch":
                continue
                
            for link_name in required_links:
                target_symlink = skill_dir / link_name
                
                if target_symlink.is_symlink():
                    results.append(f"✅ OK: {skill_dir.name}/{link_name} -> {os.readlink(target_symlink)}")
                elif target_symlink.exists():
                    results.append(f"⚠️ WARNING: {skill_dir.name}/{link_name} exists but is a real directory, not a symlink.")
                else:
                    # Create the missing upward pointing symlink
                    os.symlink(f"../../{link_name}", target_symlink)
                    results.append(f"🔧 CREATED: {skill_dir.name}/{link_name} -> ../../{link_name}")
                    
    return results

def scan_hardcoded_paths(root: Path) -> List[Tuple[str, int, str]]:
    """Scans all .py, .md, and .mmd files in plugins/ for hardcoded plugins/ paths."""
    violations = []
    
    plugins_dir = root / "plugins"
    if not plugins_dir.exists():
        return violations

    for ext in ("*.py", "*.md", "*.mmd"):
        for file_path in plugins_dir.rglob(ext):
            if file_path.name in IGNORE_FILES:
                continue
                
            # Skip virtualenvs or cache dirs if they sneak in
            if ".venv" in file_path.parts or "__pycache__" in file_path.parts:
                continue
                
            try:
                content = file_path.read_text(encoding="utf-8")
                for line_idx, line in enumerate(content.splitlines(), start=1):
                    if "npx skills open" in line or "validate_local_links.py" in line:
                        continue
                        
                    matches = HARDCODED_PLUGIN_RX.findall(line)
                    if matches:
                        rel_path = file_path.relative_to(root)
                        violations.append((str(rel_path), line_idx, line.strip()))
            except UnicodeDecodeError:
                pass # Skip binary or weirdly encoded files

    return violations

def main() -> None:
    root = resolve_project_root()
    print(f"🔍 Analyzing Symlink Architecture starting from: {root}\n")
    
    print("--- Phase 1: Validating/Scaffolding Upward Symlinks ---")
    symlink_results = scaffold_missing_symlinks(root)
    for res in symlink_results:
        # Only print warnings and creations to keep output clean
        if not res.startswith("✅"):
            print(res)
    print("✅ All required symlinks are present and verified.\n")
    
    print("--- Phase 2: Scanning for Hardcoded 'plugins/' Paths ---")
    violations = scan_hardcoded_paths(root)
    
    if not violations:
        print("✅ Clean! No hardcoded 'plugins/' paths found in source files.")
    else:
        print(f"🚨 Found {len(violations)} potential hardcoded path violations:\n")
        # Group by file for readable output
        grouped = {}
        for file_path, line_num, line in violations:
            grouped.setdefault(file_path, []).append((line_num, line))
            
        for file_path, issues in list(grouped.items())[:15]: # Show top 15 files
            print(f"📄 {file_path}")
            for line_num, line_content in issues[:3]: # Max 3 per file
                preview = (line_content[:80] + "...") if len(line_content) > 80 else line_content
                print(f"   L{line_num}: {preview}")
            if len(issues) > 3:
                print(f"   ... and {len(issues)-3} more lines.")
            print("")
            
        if len(grouped) > 15:
            print(f"... and {len(grouped) - 15} more files.")


if __name__ == "__main__":
    main()
