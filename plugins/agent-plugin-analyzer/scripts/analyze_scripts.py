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
            target = str(p.resolve())
            if not target.startswith(str_plugin_path):
                cross_plugin_symlinks.append(p)
        except Exception:
            pass
            
    if cross_plugin_symlinks:
        print(f"\n[!] CROSS-PLUGIN SYMLINK VIOLATIONS (ADR-001):")
        for p in cross_plugin_symlinks:
            try:
                print(f"      - {p.relative_to(plugin_path)} -> {p.resolve()}")
            except Exception:
                print(f"      - {p.name} -> {p.resolve()}")

def _print_script_analysis(
    script_name: str, 
    plugin_path: Path, 
    skill_usage: Dict[str, Dict[str, Any]], 
    physical_py_files: List[Path], 
    symlink_py_files: List[Path]
) -> None:
    """Outputs the detailed structural breakdown for a specific unique script."""
    script_data = skill_usage.get(script_name, {"skills": set(), "physically_exists": False})
    uses: Set[str] = script_data.get("skills", set())
    
    physical_locations = [p for p in physical_py_files if p.name == script_name]
    symlink_locations = [p for p in symlink_py_files if p.name == script_name]
    all_locations = physical_locations + symlink_locations
    
    physically_exists = len(all_locations) > 0
    root_script_path = plugin_path / "scripts" / script_name
    exists_in_root = root_script_path in all_locations
    
    if not physically_exists:
        return
        
    print(f"\nScript: {script_name}")
    print(f"  1. Exists physically in plugin: {'Yes' if physically_exists else 'No'} ({len(all_locations)} location(s))")
    
    if physically_exists:
        print(f"     -> Exists at pluginroot/scripts: {'Yes' if exists_in_root else 'No'}")
        
    uses_list = sorted(list(uses))
    print(f"  2. Used by skills: {', '.join(uses_list) if uses_list else 'None'}")
    
    if len(uses) == 1:
        skill_name = uses_list[0]
        only_in_skill = len(physical_locations) > 0
        for p in physical_locations:
            if skill_name not in p.parts:
                only_in_skill = False
                break
        print(f"  3. Only used by 1 skill. Physically exists ONLY in that skill ({skill_name})? {'Yes' if only_in_skill else 'No'}")
        if not only_in_skill and physically_exists:
            print(f"     -> Found in: {[str(p.relative_to(plugin_path)) for p in physical_locations]}")
            
    elif len(uses) > 1:
        print(f"  4. Used by {len(uses)} skills. Exists in plugin root (scripts/)? {'Yes' if exists_in_root else 'No'}")
        if not exists_in_root and physically_exists:
             print(f"     -> Physically located in: {[str(p.relative_to(plugin_path)) for p in physical_locations]}")
        if exists_in_root:
            skills_with_symlink: Set[str] = set()
            for p in symlink_locations:
                parts = p.parts
                if "skills" in parts:
                    idx = parts.index("skills")
                    if idx + 1 < len(parts):
                        skills_with_symlink.add(parts[idx + 1])
                        
            all_have_symlink = uses.issubset(skills_with_symlink)
            missing = uses - skills_with_symlink
            
            if all_have_symlink:
                print(f"  5. Symlink exists in all {len(uses)} utilizing skills? Yes")
            else:
                print(f"  5. Symlink exists in all utilizing skills? No.")
                print(f"     -> Missing symlinks in: {', '.join(sorted(list(missing)))}")

def analyze_plugins(base_dir: str) -> None:
    """Core entrypoint controlling plugin iteration and analysis phases."""
    plugins_dir = Path(base_dir) / "plugins"
    if not plugins_dir.exists():
        print(f"Error: {plugins_dir} not found.")
        return

    whitelist = _load_whitelist(Path(__file__).parent / "whitelist.json")
    global_missing_summary: Dict[str, List[Tuple[str, List[str]]]] = {}

    for plugin_path in plugins_dir.iterdir():
        if not plugin_path.is_dir() or plugin_path.name.startswith('.'):
            continue
            
        plugin_name = plugin_path.name
        
        physical_py_files, symlink_py_files = _find_python_files(plugin_path)
        skill_usage = _find_script_usages(plugin_path, physical_py_files)
                    
        all_unique_scripts: Set[str] = set(skill_usage.keys())
        for p in physical_py_files + symlink_py_files:
            all_unique_scripts.add(p.name)
            
        if not all_unique_scripts:
            continue
            
        print(f"\n{'='*70}")
        print(f"PLUGIN: {plugin_name}")
        print(f"{'='*70}")

        _print_adr001_violations(symlink_py_files, plugin_path)
        
        for script_name in sorted(list(all_unique_scripts)):
            _print_script_analysis(script_name, plugin_path, skill_usage, physical_py_files, symlink_py_files)

        # Missing Scripts
        missing_scripts = [s for s, data in skill_usage.items() if not data.get("physically_exists")]
        
        global_ignores = set(whitelist.get("global_ignores", {}).keys())
        plugin_ignores = set(whitelist.get("plugin_ignores", {}).get(plugin_name, {}).keys())
        
        filtered_missing_scripts = [s for s in missing_scripts if s not in global_ignores and s not in plugin_ignores]
                
        if filtered_missing_scripts:
            global_missing_summary[plugin_name] = []
            print(f"\n[!] MISSING OR UNRESOLVED SCRIPTS (See Global Summary below):")
            for s in sorted(filtered_missing_scripts):
                script_data = skill_usage[s]
                uses_set = script_data.get("skills", set())
                uses = sorted(list(uses_set))
                global_missing_summary[plugin_name].append((s, uses))
                print(f"      - {s} (Referenced by: {', '.join(uses)})")

    if global_missing_summary:
        print(f"\n\n{'='*70}")
        print("GLOBAL SUMMARY: MISSING SCRIPTS PER PLUGIN")
        print(f"{'='*70}")
        for p_name in sorted(list(global_missing_summary.keys())):
            print(f"\n{p_name}:")
            for s, uses in global_missing_summary[p_name]:
                print(f"  - {s} (via: {', '.join(uses)})")

if __name__ == '__main__':
    base_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    analyze_plugins(base_dir_path)
