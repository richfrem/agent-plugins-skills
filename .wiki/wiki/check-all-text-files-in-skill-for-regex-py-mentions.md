---
concept: check-all-text-files-in-skill-for-regex-py-mentions
source: plugin-code
source_file: agent-scaffolders/scripts/analyze_scripts.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.816858+00:00
cluster: path
content_hash: b0d530fe499f7d62
---

# Check all text files in skill for regex *.py mentions

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
analyze_scripts.py
=====================================

Purpose:
    Analyzer script for the plugin ecosystem. Evaluates Python script usage,
    symlink structures, and verifies alignment with ADR-001 (Cross-Plugin) 
    and ADR-002 (Multi-Skill Script Centralization) architectural conventions.

Layer: Investigate / Audit

Usage:
    python ./scripts/analyze_scripts.py

Related:
    - analysis_results.txt
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

def _load_whitelist(whitelist_path: Path) -> Dict[str, Any]:
    """Loads the whitelist configuration to ignore certain missing scripts."""
    whitelist: Dict[str, Any] = {"global_ignores": {}, "plugin_ignores": {}}
    if whitelist_path.exists():
        try:
            with open(whitelist_path, "r", encoding="utf-8") as f:
                whitelist = json.load(f)
        except Exception as e:
            print(f"Failed to load whitelist.json: {e}")
    return whitelist

def _find_python_files(plugin_path: Path) -> Tuple[List[Path], List[Path]]:
    """Separates physical python files from symlinks within a plugin."""
    physical_py_files: List[Path] = []
    symlink_py_files: List[Path] = []
    
    for p in plugin_path.rglob('*.py'):
        if '.git' in p.parts or 'node_modules' in p.parts or '.venv' in p.parts or '__pycache__' in p.parts:
            continue
        if p.is_symlink():
            symlink_py_files.append(p)
        elif p.is_file():
            physical_py_files.append(p)
            
    return physical_py_files, symlink_py_files

def _find_script_usages(plugin_path: Path, physical_py_files: List[Path]) -> Dict[str, Dict[str, Any]]:
    """Maps which scripts are referenced by which skills by scanning text contexts."""
    skills_dir = plugin_path / "skills"
    skill_usage: Dict[str, Dict[str, Any]] = {}
    
    if not skills_dir.exists():
        return skill_usage
        
    physical_names: Set[str] = {p.name for p in physical_py_files}
    
    for skill_path in skills_dir.iterdir():
        if not skill_path.is_dir() or skill_path.name.startswith('.'): 
            continue
        skill_name = skill_path.name
        
        # Check all text files in skill for regex *.py mentions
        for p in skill_path.rglob('*'):
            if '.git' in p.parts or 'node_modules' in p.parts or '.venv' in p.parts or '__pycache__' in p.parts:
                continue
            if p.is_file() and not p.name.startswith('.') and p.suffix in ['.md', '.json', '.py', '.sh', '.txt', '.yaml', '.yml', '.jinja']:
                try:
                    content = p.read_text('utf-8')
                    found_scripts = re.findall(r'[a-zA-Z0-9_-]+\.py', content)
                    for s in found_scripts:
                        exists_physically = s in physical_names
                        if s not in skill_usage: 
                            skill_usage[s] = {"skills": set(), "physically_exists": False}
                        skill_usage[s]["skills"].add(skill_name)
                        if exists_physically:
                            skill_usage[s]["physically_exists"] = True
                except Exception:
                    pass
        
        # Ensure any py files inside this skill's scripts dir register as used by this skill
        for p in skill_path.rglob('*.py'):
            s = p.name
            if s not in skill_usage: 
                skill_usage[s] = {"skills": set(), "physically_exists": True}
            skill_usage[s]["skills"].add(skill_name)
            skill_usage[s]["physically_exists"] = True
            
    return skill_usage

def _print_adr001_violations(symlink_py_files: List[Path], plugin_path: Path) -> None:
    """Detects and prints any symlink pointing completely outside the local plugin root."""
    cross_plugin_symlinks: List[Path] = []
    str_plugin_path = str(plugin_path.resolve())
    for p in symlink_py_files:
        try:
   

*(content truncated)*

## See Also

- [[only-check-files-in-pluginsskills]]
- [[check-for-broken-symlinks]]
- [[check-if-we-already-emitted-for-this-completion-avoid-duplicate-events]]
- [[for-a-skill]]
- [[only-process-plugin-root-level-files-not-skill-files]]
- [[ordered-list-of-marker-files-label-env-vars-for-project-type-detection]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/analyze_scripts.py`
- **Indexed:** 2026-04-27T05:21:03.816858+00:00
