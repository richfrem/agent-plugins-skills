#!/usr/bin/env python3
"""
dependencies.py (CLI)
====================================

Purpose:
    Traces Call Graph (Upstream/Downstream) using Map + Deep Search.

Layer: Curate / Search

Usage Examples:
    python plugins/dependency-analysis/scripts/dependencies.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    --target        : Target Object ID (e.g. FORM0000, PROJECT_ACCESS_LOGS)
    --deep          : Enable Deep Search (scan raw source files for references)
    --json          : Output results as JSON format
    --applications  : Trace upstream to find parent applications (APP1, APP2, etc.)
    --direction     : Scope of analysis (default: both)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - load_dependency_map(): Loads the primary dependency inventory file (dependency_map.json).
    - find_upstream(): Finds "Upstream" dependencies (Reverse Lookups).
    - trace_applications(): Performs a Breadth-First Search (BFS) upstream to identify which Main Application Modules
    - find_downstream(): Finds "Downstream" dependencies (Forward Lookups).
    - deep_search(): Executes a "Deep Search" by scanning raw source files for textual references.
    - main(): Main entry point for CLI execution.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import json
import os
import re
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List

# Paths
CWD = Path.cwd()
REF_DATA_DIR = CWD / 'legacy-system' / 'reference-data' / 'inventories'
DEPENDENCY_MAP_PATH = REF_DATA_DIR / 'dependency_map.json'
EXCLUDE_LIST_PATH = CWD / 'legacy-system' / 'reference-data' / 'master_object_collection_exclude_list.json'

# Load Exclude List
EXCLUDE_CONFIG = {"objects": [], "files": []}
if EXCLUDE_LIST_PATH.exists():
    try:
        with open(EXCLUDE_LIST_PATH, 'r', encoding='utf-8') as f:
            exclude_data = json.load(f)
            EXCLUDE_CONFIG["objects"] = [x.upper() for x in exclude_data.get("objects", [])]
            EXCLUDE_CONFIG["files"] = [x.lower() for x in exclude_data.get("files", [])]
            EXCLUDE_CONFIG["patterns"] = [x.lower() for x in exclude_data.get("patterns", [])]
    except Exception as e:
        pass # Fail silently


# Source directories for deep search
# These paths point to the raw source files used for "Deep Search" grepping.
SOURCE_DIRS = {
    'Forms': CWD / 'legacy-system' / 'oracle-forms' / 'XML',
    'Libraries': CWD / 'legacy-system' / 'oracle-forms' / 'pll',
    'Packages': CWD / 'legacy-system' / 'oracle-database' / 'source' / 'Packages',
    'Procedures': CWD / 'legacy-system' / 'oracle-database' / 'Procedures',
    'Functions': CWD / 'legacy-system' / 'oracle-database' / 'Functions',
    'Views': CWD / 'legacy-system' / 'oracle-database' / 'Views',
    'Triggers': CWD / 'legacy-system' / 'oracle-database' / 'Triggers',
    'Types': CWD / 'legacy-system' / 'oracle-database' / 'Types',
    'Sequences': CWD / 'legacy-system' / 'oracle-database' / 'Sequences',
    'Indexes': CWD / 'legacy-system' / 'oracle-database' / 'Indexes',
    'Constraints': CWD / 'legacy-system' / 'oracle-database' / 'Constraints',
    'Menus': CWD / 'legacy-system' / 'oracle-forms' / 'XML', # MMBs live here too
}


def load_dependency_map() -> Dict[str, Any]:
    """
    Loads the primary dependency inventory file (dependency_map.json).

    Returns:
        Dict[str, Any]: The dependency graph. Returns empty dict on failure.
    """
    if not DEPENDENCY_MAP_PATH.exists():
        return {}
    try:
        with open(DEPENDENCY_MAP_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def find_upstream(target: str, data: Dict[str, Any]) -> List[str]:
    """
    Finds "Upstream" dependencies (Reverse Lookups).
    Identifies all objects in the system that explicitly list the Target 
    as a dependency in their own definition.

    Args:
        target (str): The ID of the object to find callers for (e.g., 'MY_FORM').
        data (Dict): The loaded dependency map.

    Returns:
        List[str]: A sorted list of Object IDs that depend on the target.
    """
    upstream = []
    target = target.upper()
    
    for obj_name, obj_data in data.items():
        if obj_name == target:
            continue
        
        deps = obj_data.get('Dependencies', {})
        # Check all relevant dependency categories
        for category in ['Forms', 'Reports', 'PLLs', 'Packages', 'ExternalCalls', 'Tables', 'Views', 'Inheritance']:
            if target in deps.get(category, []):
                upstream.append(obj_name)
                break
        
        # Check MenuModule (Forms can specify a Menu Module)
        if obj_data.get('MenuModule') == target:
            upstream.append(obj_name)
                
    return sorted(set(upstream))


# Main Application Modules (Generic placeholders)
MAIN_MODULES = {
    'FORM0001': 'APP1',
    'FORM0002': 'APP2',
    'FORM0003': 'APP3',
}


def trace_applications(target: str, data: Dict[str, Any], max_depth: int = 3) -> Dict[str, str]:
    """
    Performs a Breadth-First Search (BFS) upstream to identify which Main Application Modules
    can reach the target object.

    Args:
        target (str): The object ID to trace.
        data (Dict): The dependency map.
        max_depth (int): Maximum levels to traverse upstream (default: 3).

    Returns:
        Dict[str, str]: Map of Main Module ID -> Application Acronym.
                        Example: {'FORM0000': 'APP1'}
    """
    target = target.upper()
    found_apps = {}
    
    # BFS Queue: (node, depth)
    queue = [(target, 0)]
    visited = {target}
    
    while queue:
        current, depth = queue.pop(0)
        
        # Check if current node is a known Main Module
        if current in MAIN_MODULES:
            found_apps[current] = MAIN_MODULES[current]
            continue  # Don't traverse further from main modules
        
        # Stop at max depth
        if depth >= max_depth:
            continue
        
        # Find who calls current node
        upstream = find_upstream(current, data)
        
        for parent in upstream:
            if parent not in visited:
                visited.add(parent)
                queue.append((parent, depth + 1))
    
    return found_apps


def find_downstream(target: str, data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Finds "Downstream" dependencies (Forward Lookups).
    Returns the list of objects that the Target explicitly calls or uses.

    Args:
        target (str): The object ID to analyze.
        data (Dict): The dependency map.

    Returns:
        Dict[str, List[str]]: Dictionary categorized by type (e.g., 'Forms', 'Tables').
    """
    target = target.upper()
    if target not in data:
        return {}
        
    obj_data = data[target]
    deps = obj_data.get('Dependencies', {})
    result = {}
    for category, items in deps.items():
        if items and isinstance(items, list):
            result[category] = sorted(items)
    
    # Add MenuModule if it exists (for Forms)
    menu = obj_data.get('MenuModule')
    if menu:
        result['MenuModule'] = [menu]
            
    return result


def deep_search(target: str) -> Dict[str, List[str]]:
    """
    Executes a "Deep Search" by scanning raw source files for textual references.
    This is useful for finding dependencies hidden in dynamic PL/SQL or 
    not captured by the static analysis parser.

    Logic:
    Iterates through all known source directories (Forms XML, PLLs, DB Scripts)
    and uses Regex to find exact word matches of the target ID.
    Ignores common noise files like 'output.txt'.

    Args:
        target (str): The string identifier to search for (e.g., 'GET_CLIENT_DETAILS').

    Returns:
        Dict[str, List[str]]: Matches categorized by source type (Caller Type -> List[Callers]).
                              Example: {'Forms': ['FORM0020'], 'Packages': ['CUSTOM_PKG']}
    """
    results = {
        'Forms': [],
        'Libraries': [],
        'Packages': [],
        'Procedures': [],
        'Functions': [],
        'Views': [],
        'Triggers': [],
        'Types': [],
        'Sequences': [],
        'Indexes': [],
        'Constraints': [],
        'Menus': []
    }
    
    target_upper = target.upper()
    # Pattern to find table/view references as exact words
    pattern = re.compile(rf'\b{re.escape(target_upper)}\b', re.IGNORECASE)
    
    for source_type, source_dir in SOURCE_DIRS.items():
        if not source_dir.exists():
            continue
            
        # Determine file pattern based on source type
        if source_type == 'Forms':
            files = list(source_dir.glob('*_fmb.xml'))
        elif source_type == 'Menus':
            files = list(source_dir.glob('*_mmb.xml'))
        elif source_type == 'Libraries':
            files = list(source_dir.glob('*.txt'))
        else:
            files = list(source_dir.glob('*.sql'))
        
        for f in files:
            # FILTER: Check against Master Exclude List
            f_name_lower = f.name.lower()
            if f_name_lower in EXCLUDE_CONFIG["files"]:
                continue
            if any(p in f_name_lower for p in EXCLUDE_CONFIG["patterns"]):
                continue

            if f.name.lower() in ['output.txt', 'errors.txt', 'log.txt']:
                continue

            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                if pattern.search(content):
                    # Extract clean artifact name from filename
                    name = f.stem
                    if name.endswith('_fmb') or name.endswith('_mmb'):
                        name = name[:-4].upper()
                    else:
                        name = name.upper()
                    
                    # Check Excluded Objects (Dynamic from JSON)
                    if name in EXCLUDE_CONFIG["objects"]:
                         continue
                    
                    if any(pattern in name.lower() for pattern in EXCLUDE_CONFIG["patterns"]):
                         continue
                         
                    # Prevent circular reference (self-match)
                    if name != target_upper:
                        results[source_type].append(name)
            except Exception:
                continue
    
    # Sort and deduplicate results
    for k in results:
        results[k] = sorted(set(results[k]))
    
    return results


def main():
    """
    Main entry point for CLI execution.
    Parses command-line arguments, loads the dependency map, and orchestrates
    the dependency analysis based on user-specified options.

    Supports:
    - Standard upstream/downstream dependency lookup.
    - "Deep Search" for references in raw source files.
    - Application tracing to identify parent main modules.
    - JSON or human-readable output formats.
    """
    parser = argparse.ArgumentParser(
        description="Query Dependency Map and Deep Search Source Code",
        epilog="Example: python dependencies.py --target PROJECT_ACCESS_LOGS --deep"
    )
    parser.add_argument("--target", required=True, help="Target Object ID (e.g. FORM0000, PROJECT_ACCESS_LOGS)")
    parser.add_argument("--deep", action="store_true", help="Enable Deep Search (scan raw source files for references)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON format")
    parser.add_argument("--applications", action="store_true", help="Trace upstream to find parent applications (APP1, APP2, etc.)")
    parser.add_argument("--direction", choices=['upstream', 'downstream', 'both'], default='both', help="Scope of analysis (default: both)")
    args = parser.parse_args()
    
    data = load_dependency_map()
    target = args.target.upper()
    
    # Mode 1: Application Trace
    if args.applications:
        apps = trace_applications(target, data, max_depth=3)
        if args.json:
            print(json.dumps({'target': target, 'applications': apps}, indent=2))
        else:
            print(f"\n📱 Application Trace for: {target}")
            print("=" * 60)
            if apps:
                print("   Reachable from Main Modules:")
                for module, app_name in sorted(apps.items()):
                    print(f"      - [{app_name}] {module}")
            else:
                print("   ⚠️  No Main Modules found within 3 levels upstream.")
                print("   (Form may be orphaned or called via library indirection)")
            print("=" * 60)
        return
    
    # Mode 2: Standard Dependency Analysis
    downstream = {}
    if args.direction in ['downstream', 'both']:
        downstream = find_downstream(target, data)

    upstream = []
    deep_results = {}
    if args.direction in ['upstream', 'both']:
        upstream = find_upstream(target, data)
        # Perform Deep Search if requested
        if args.deep:
            deep_results = deep_search(target)
    
    # Merge Static Upstream with Deep Search Upstream
    all_callers = {
        'Forms': list(set(upstream) | set(deep_results.get('Forms', []))),
        'Libraries': deep_results.get('Libraries', []),
        'Packages': deep_results.get('Packages', []),
        'Procedures': deep_results.get('Procedures', []),
        'Functions': deep_results.get('Functions', []),
        'Views': deep_results.get('Views', []),
        'Triggers': deep_results.get('Triggers', []),
        'Types': deep_results.get('Types', []),
        'Sequences': deep_results.get('Sequences', []),
        'Indexes': deep_results.get('Indexes', []),
        'Constraints': deep_results.get('Constraints', []),
        'Menus': deep_results.get('Menus', [])
    }
    
    # Heuristic Classification: Assign loose upstream callers to categories
    for caller in upstream:
        if caller not in all_callers['Forms']:
            # Assume *LIB callers are Libraries
            if caller.endswith('LIB'):
                if caller not in all_callers['Libraries']:
                    all_callers['Libraries'].append(caller)
    
    # Final Sort
    for k in all_callers:
        all_callers[k] = sorted(set(all_callers[k]))
    
    # Output
    if args.json:
        # Load Master Collection for Fallback Path Resolution
        master_data = {}
        master_path = CWD / 'legacy-system' / 'reference-data' / 'master_object_collection.json'
        if master_path.exists():
            try:
                with open(master_path, 'r', encoding='utf-8') as f:
                    master_data = json.load(f)
            except Exception:
                pass

        def resolve_path_from_master(target_id: str) -> str:
            if not master_data:
                return None
            obj = master_data.get('objects', {}).get(target_id.upper())
            if not obj:
                return None
            
            artifacts = obj.get('artifacts', {})
            # Priority: Source/XML > SQL > Overview
            for key in ['xml', 'source', 'sql', 'definition', 'overview']:
                if key in artifacts:
                    return artifacts[key]
            return None

        def enrich_list(names: List[str]) -> List[Dict[str, Any]]:
            enriched = []
            for n in names:
                info = {'id': n}
                path = None
                
                # 1. Try Dependency Map (Primary)
                if n in data and 'FilePath' in data[n] and data[n]['FilePath']:
                     path = data[n]['FilePath']
                
                # 2. Fallback: Master Collection
                if not path:
                    path = resolve_path_from_master(n)
                
                if path:
                    info['FilePath'] = path
                
                enriched.append(info)
            return enriched

        output = {'target': target}
        
        if args.direction in ['downstream', 'both']:
            # Enrich downstream
            enriched_downstream = {}
            for k, v in downstream.items():
                enriched_downstream[k] = enrich_list(v)
            output['downstream'] = enriched_downstream
            
        if args.direction in ['upstream', 'both']:
            # Enrich upstream (callers)
            enriched_callers = {}
            for k, v in all_callers.items():
                if v: # Only add non-empty categories
                    enriched_callers[k] = enrich_list(v)
            output['callers'] = enriched_callers

        print(json.dumps(output, indent=2))
    else:
        # Human readable report
        print(f"\nDependency Analysis for: {target}")
        print("=" * 60)
        
        if args.direction in ['downstream', 'both']:
            print(f"\n➡️  Calls To (Downstream):")
            # Filter out noise categories
            if not downstream:
                print("   (None detected)")
            else:
                for category, items in downstream.items():
                    if category in ['TableCRUD', 'InternalCalls']:
                        continue
                    if items:
                        print(f"   [{category}]: {', '.join(items[:10])}")
        
        if args.direction in ['upstream', 'both']:
            print(f"\n⬅️  Called By (Upstream):")
            has_callers = any(all_callers.values())
            if not has_callers:
                print("   (None detected)")
            else:
                for category, items in all_callers.items():
                    if items:
                        print(f"   [{category}]: {', '.join(items[:10])}")
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
