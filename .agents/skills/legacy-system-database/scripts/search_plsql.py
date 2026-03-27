#!/usr/bin/env python3
"""
search_plsql.py (CLI)
=====================================

Purpose:
    Robust regex search with context for PL/SQL code.

Layer: Curate / Search

Usage Examples:
    python plugins/legacy-system-database/scripts/search_plsql.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    --file          : Target file path
    --term          : Search term (optional if using --structure)
    --regex         : Use regex for search
    --context       : Lines of context
    --structure     : Extract Form Structure (Tabs, Blocks)
    --json          : Output JSON

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - parse_markdown_structure(): Parses the specific Markdown format to extract Tabs, Blocks, Canvases, Windows.
    - search_text(): No description.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import argparse
import re
import json
import sys
import os

def parse_markdown_structure(filepath):
    """
    Parses the specific Markdown format to extract Tabs, Blocks, Canvases, Windows.
    Returns a dictionary of found objects.
    """
    objects = {"TabPage": [], "Block": [], "Canvas": [], "Window": [], "ProgramUnit": [], "Trigger": []}
    
    current_type = None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Detect Type Header
            # Format: ### Block OR ### TabPage
            if line.startswith("### "):
                header = line.replace("### ", "").strip()
                # Handle "Objectgroupchild" which hides Blocks sometimes?
                # No, standard MD format usually is explicit.
                # Adjust for headers like "ProgramUnit - NAME"
                if " - " in header:
                    # e.g. "ProgramUnit - CHECK_PACKAGE_FAILURE"
                    part_type, part_name = header.split(" - ", 1)
                    if part_type.strip() in ["ProgramUnit", "Trigger"]:
                        objects[part_type.strip()].append({"Name": part_name.strip(), "Line": i+1})
                        current_type = None # Parsed immediately
                elif header in objects:
                    current_type = header
                else:
                    current_type = None
            
            # Detect Name Attribute
            # | Name | VALUE |
            if current_type and line.startswith("| Name |"):
                parts = line.split("|")
                if len(parts) >= 4:
                    name_val = parts[2].strip()
                    objects[current_type].append({"Name": name_val, "Line": i+1})
                    current_type = None # Reset after finding name to avoid duplicates or confusion
                    
    except Exception as e:
        return {"error": str(e)}
        
    return objects

def search_text(filepath, term, is_regex=False, context=0):
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            match = False
            try:
                if is_regex:
                    if re.search(term, line, re.IGNORECASE):
                        match = True
                else:
                    if term.lower() in line.lower():
                        match = True
            except re.error as e:
                return [{"error": f"Invalid Regex: {e}"}]

            if match:
                # Extract Context
                start = max(0, i - context)
                end = min(len(lines), i + context + 1)
                snippet = "".join(lines[start:end])
                results.append({
                    "Line": i+1,
                    "Content": line.strip(),
                    "Snippet": snippet
                })
                
                if len(results) > 500: # Safety cap
                    break
                    
    except Exception as e:
        return [{"error": str(e)}]
        
    return results

def main():
    parser = argparse.ArgumentParser(description="Search PL/SQL and Form Structure")
    parser.add_argument("--file", required=True, help="Target file path")
    parser.add_argument("--term", help="Search term (optional if using --structure)")
    parser.add_argument("--regex", action="store_true", help="Use regex for search")
    parser.add_argument("--context", type=int, default=0, help="Lines of context")
    parser.add_argument("--structure", action="store_true", help="Extract Form Structure (Tabs, Blocks)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    output = {}
    
    if args.structure:
        output["structure"] = parse_markdown_structure(args.file)
        
    if args.term:
        output["matches"] = search_text(args.file, args.term, args.regex, args.context)
        
    if args.json:
        print(json.dumps(output, indent=2))
    else:
        # Text Output
        if "structure" in output:
            print("Structure Analysis:")
            for k, v in output["structure"].items():
                if v and isinstance(v, list):
                    names_list = [x['Name'] for x in v if isinstance(x, dict) and 'Name' in x]
                    # Print in chunks if too long
                    print(f"  {k}: {', '.join(names_list[:50])}")
                    if len(names_list) > 50:
                        print(f"       ... and {len(names_list)-50} more")
                elif v and isinstance(v, str):
                    print(f"  {k}: {v}")
        
        if "matches" in output:
            print(f"\nSearch Results for '{args.term}' ({len(output['matches'])} matches):")
            for m in output["matches"]:
                if "error" in m:
                    print(f"  Error: {m['error']}")
                    continue
                print(f"  Line {m['Line']}: {m['Content']}")
                if args.context > 0:
                    print("    ---")
                    print(m['Snippet'].rstrip())
                    print("    ---")

if __name__ == "__main__":
    main()
