#!/usr/bin/env python3
"""
02_extract_link_references.py (CLI)
=====================================

Purpose:
    Extractor: Generic scanner that extracts all link/path references from files.
    This is Phase 2 of the Link Checker pipeline.

Usage:
    python3 02_extract_link_references.py --root .

Output:
    - link_references.json: { "source_file": [{"link": "path", "line": 1, "type": "markdown"}, ...] }
"""
import os
import json
import re
import argparse
from typing import Dict, List, Any

# Regex patterns for different reference types
PATTERNS = {
    'markdown_link': re.compile(r'\[.*?\]\((?!http|mailto|#)(.*?)\)'),
    'markdown_image': re.compile(r'\!\[.*?\]\((?!http|#)(.*?)\)'),
    # Simple heuristic for relative paths in code (starting with ./ or ../)
    'relative_path': re.compile(r'[\'"](\.{1,2}/[a-zA-Z0-9_\-\./]+)[\'"]'),
    # Reference to other files in the same directory (no path, just filename with extension)
    # This is noisier, but useful for documentation linking.
    # 'file_ref': re.compile(r'\[\[(.*?)\]\]') # Obsidian style wikilinks
}

def extract_links_from_file(file_path: str, root_dir: str) -> List[Dict[str, Any]]:
    """
    Extracts all link references from a single file.
    """
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                for ref_type, pattern in PATTERNS.items():
                    matches = pattern.findall(line)
                    for match in matches:
                        # Clean up fragments and queries
                        clean_ref = match.split('#')[0].split('?')[0]
                        if clean_ref:
                            results.append({
                                'ref': clean_ref,
                                'line': line_num,
                                'type': ref_type
                            })
    except (UnicodeDecodeError, PermissionError):
        # Skip binary or inaccessible files
        pass
    except Exception as e:
        print(f"  Error reading {file_path}: {e}")
        
    return results

def main() -> None:
    parser = argparse.ArgumentParser(description="Step 2: Extract all link references.")
    parser.add_argument("--root", default=".", help="Root directory to scan")
    parser.add_argument("--output", default="link_references.json", help="Output JSON file name")
    args = parser.parse_args()

    root_dir = args.root
    all_refs = {}
    
    # Same excludes as Step 1
    excludes = {'.git', 'node_modules', '.venv', '.next', 'bin', 'obj', '.agents', '.gemini', '__pycache__'}
    
    # We primarily care about documentation and source files
    target_extensions = {'.md', '.txt', '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.mmd', '.mermaid'}
    
    print(f"Extracting references in: {os.path.abspath(root_dir)}")
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in excludes]
        
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext not in target_extensions:
                continue
                
            file_path = os.path.join(root, filename)
            rel_file_path = os.path.relpath(file_path, root_dir).replace('\\', '/')
            
            # Skip the output files from this pipeline (prevents false positives on re-runs)
            if filename in {
                'file_inventory.json', 'link_references.json',
                'broken_links.log', 'broken_links.json',
                'remaining_broken_links.json', 'unfixable_links_report.md',
            }:
                continue
                
            found = extract_links_from_file(file_path, root_dir)
            if found:
                all_refs[rel_file_path] = found
                
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(all_refs, f, indent=2)
        
    print(f"✅ Extracted references from {len(all_refs)} files to {args.output}")

if __name__ == "__main__":
    main()
