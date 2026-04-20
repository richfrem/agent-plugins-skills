#!/usr/bin/env python
"""
03_audit_broken_links.py (CLI)
=====================================

Purpose:
    Auditor: Cross-references extracted links with the file inventory.
    This is Phase 3 of the Link Checker pipeline.

Usage:
    python03_audit_broken_links.py --root .

Output:
    - broken_links.log: Human-readable log of issues.
    - broken_links.json: Machine-readable JSON for integration.
"""
import os
import json
import argparse
from urllib.parse import unquote
from typing import List, Dict, Any

def audit_links(inventory: Dict[str, List[str]], raw_refs: Dict[str, List[Dict[str, Any]]], root_dir: str) -> List[Dict[str, Any]]:
    """
    Identifies broken internal links across the repository.
    """
    broken_results = []
    
    for source_file, refs in raw_refs.items():
        source_dir = os.path.dirname(os.path.join(root_dir, source_file))
        
        for ref_data in refs:
            link_path = ref_data['ref']
            
            # 1. Handle absolute paths (from repo root)
            if link_path.startswith('/'):
                target_abs = os.path.join(root_dir, link_path.lstrip('/'))
            else:
                # 2. Handle relative paths (from source file)
                target_abs = os.path.normpath(os.path.join(source_dir, unquote(link_path)))
            
            if not os.path.exists(target_abs):
                # It's broken. Record it.
                basename = os.path.basename(target_abs)
                
                # Check inventory for candidates
                candidates = inventory.get(basename, [])
                
                broken_results.append({
                    'source_file': source_file,
                    'link': link_path,
                    'line': ref_data['line'],
                    'type': ref_data['type'],
                    'basename': basename,
                    'candidates': candidates
                })
                
    return broken_results

def main() -> None:
    parser = argparse.ArgumentParser(description="Step 3: Audit extract references against filesystem.")
    parser.add_argument("--root", default=".", help="Root directory of the repo")
    args = parser.parse_args()

    root_dir = os.path.abspath(args.root)
    inventory_path = "file_inventory.json"
    refs_path = "link_references.json"
    
    if not os.path.exists(inventory_path) or not os.path.exists(refs_path):
        print("Required files (inventory or refs) not found. Run Steps 1 and 2 first.")
        return

    with open(inventory_path, 'r', encoding='utf-8') as f:
        inventory = json.load(f)
    with open(refs_path, 'r', encoding='utf-8') as f:
        raw_refs = json.load(f)
        
    print(f"Auditing links in {root_dir}...")
    broken_list = audit_links(inventory, raw_refs, root_dir)
    
    # Write JSON output
    with open("broken_links.json", 'w', encoding='utf-8') as f:
        json.dump(broken_list, f, indent=2)
        
    # Write human-readable log
    with open("broken_links.log", 'w', encoding='utf-8') as f:
        if not broken_list:
            f.write("No broken links found! All references are valid.\n")
        else:
            f.write(f"Found {len(broken_list)} broken references.\n\n")
            current_file = None
            for idx, item in enumerate(broken_list, 1):
                if item['source_file'] != current_file:
                    current_file = item['source_file']
                    f.write(f"FILE: {current_file}\n")
                
                f.write(f"  [{item['line']}] [MISSING] {item['link']}\n")
                if item['candidates']:
                    f.write(f"    Possible matches: {', '.join(item['candidates'])}\n")
                    
    print(f"✅ Audit complete. Found {len(broken_list)} broken links. See broken_links.log/json.")

if __name__ == "__main__":
    main()
