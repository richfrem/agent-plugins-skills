---
concept: the-target-architecture-definition
source: plugin-code
source_file: agent-scaffolders/scripts/validate_local_links.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.843573+00:00
cluster: plugins
content_hash: c053c9d09afd3323
---

# The target architecture definition

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
    violations = [

*(content truncated)*

## See Also

- [[1-parse-the-hook-payload]]
- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]
- [[add-the-scripts-directory-so-we-can-import-rlm-config]]
- [[all-event-types-recognised-by-the-claude-code-hook-system]]
- [[install-from-the-local-repo-select-plugins-interactively]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/validate_local_links.py`
- **Indexed:** 2026-04-27T05:21:03.843573+00:00
