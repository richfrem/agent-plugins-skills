#!/usr/bin/env python3
"""
check_broken_paths.py (CLI)
=====================================

Purpose:
    Inspector: Recursively scans documentation files for broken relative links.

Layer: Curate / Cli_Entry_Points

Usage Examples:
    python plugins/link-checker/scripts/check_broken_paths.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    target_dir      : Directory to scan (defaults to current working directory)
    --file          : Specific file to check. If provided, only this file is scanned.

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - find_files(): Recursively finds files with specific extensions, excluding noise directories.
    - check_broken_links(): Checks for broken relative links in a specific file.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import re
import argparse
from urllib.parse import unquote
from typing import List, Set, Optional

def find_files(root_dir: str, extensions: List[str]) -> List[str]:
    """
    Recursively finds files with specific extensions, excluding noise directories.

    Args:
        root_dir: The root directory to start the search.
        extensions: A list of file extensions to include (e.g., ['.md', '.txt']).

    Returns:
        List of absolute file paths matching the criteria.
    """
    matches = []
    excluded_dirs = {'node_modules', '.git', '.venv', '.next', 'bin', 'obj', 'dist', 'build', '.vs', 'archive', 'coverage'}

    for root, dirnames, filenames in os.walk(root_dir):
        # Modify dirnames in-place to prevent os.walk from recursing
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]
        
        for filename in filenames:
            if filename in ['broken_links.log', 'broken_links_report.txt', 'broken_links_log.txt']:
                continue
            if any(filename.endswith(ext) for ext in extensions):
                matches.append(os.path.join(root, filename))
    return matches

def check_broken_links(file_path: str) -> List[str]:
    """
    Checks for broken relative links in a specific file.

    Args:
        file_path: Absolute path to the file to check.

    Returns:
        List of broken link strings found in the file.
    """
    broken_links = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return [] # Skip binary files or weird encodings

    # Regex for Markdown links: [text](path)
    # We'll specifically look for the standard [label](url) pattern.
    link_pattern = re.compile(r'\[.*?\]\((.*?)\)')
    
    # Also look for HTML-style links <a href="..."> and src="..."
    src_pattern = re.compile(r'(?:src|href)=[\'"](.*?)[\'"]')
    
    # Legacy path detector (unquoted refs to legacy-system/)
    legacy_pattern = re.compile(r'(?:\s|`|\'|")(legacy-system/[\w\-\./]+)(?:\s|`|\'|")')

    # Gather potential paths
    links = link_pattern.findall(content)
    links.extend(src_pattern.findall(content))
    links.extend(legacy_pattern.findall(content))

    for link in links:
        # Ignore web links
        if link.startswith('http') or link.startswith('mailto:') or link.startswith('#'):
            continue
            
        # Ignore absolute paths/URLs
        if link.startswith('/') or ':' in link:
            continue

        # Clean anchor tags #section
        clean_link = link.split('#')[0]
        if not clean_link:
            continue
            
        clean_link = unquote(clean_link)
            
        # Construct absolute path for verification (relative to current file)
        file_dir = os.path.dirname(file_path)
        target_path = os.path.join(file_dir, clean_link)
        
        if not os.path.exists(target_path):
            # Fallback heuristic: check relative to repo root for 'legacy-system' paths
            if clean_link.startswith('legacy-system/') or clean_link.startswith('tools/'):
                 root_target = os.path.join(os.getcwd(), clean_link)
                 if os.path.exists(root_target):
                     continue # It exists at root!
            
            broken_links.append(link)

    return broken_links

def main():
    parser = argparse.ArgumentParser(description="Check for broken file paths in the repository.")
    parser.add_argument("target_dir", nargs="?", default=os.getcwd(), help="Directory to scan (defaults to current working directory)")
    parser.add_argument("--file", help="Specific file to check. If provided, only this file is scanned.")
    args = parser.parse_args()

    root_dir = os.path.abspath(args.target_dir)
    log_file = os.path.join(os.path.dirname(__file__), "broken_links.log")
    
    print(f"Scanning for broken links in {root_dir}...\n")
    
    extensions = ['.md', '.txt', '.json', '.markdown', '.mmd'] 
    
    files = []
    if args.file:
        if os.path.exists(args.file):
            files.append(os.path.abspath(args.file))
            print(f"Checking single file: {args.file}")
        else:
            print(f"Error: File not found: {args.file}")
            return
    else:
        files = find_files(root_dir, extensions)
        print(f"Scanning directory: {root_dir}")
    
    total_broken = 0
    files_scanned = 0
    
    with open(log_file, 'w', encoding='utf-8') as log:
        for file_path in files:
            # Skip temp files
            basename = os.path.basename(file_path)
            if basename.startswith('temp_') or basename.startswith('temp-'):
                continue
            
            files_scanned += 1
            if files_scanned % 100 == 0:
                print(f"  Scanned {files_scanned} files...", flush=True)
                
            broken = check_broken_links(file_path)
            if broken:
                rel_path = os.path.relpath(file_path, root_dir)
                log.write(f"FILE: {rel_path}\n")
                print(f"FILE: {rel_path}")
                for link in broken:
                    log.write(f"  [MISSING] {link}\n")
                    # print(f"  [MISSING] {link}") # Reduce stdout spam
                log.write("\n")
                total_broken += len(broken)
                
        log.write(f"Scan complete. Found {total_broken} broken references.\n")
            
    print(f"Scan complete. Scanned {files_scanned} files. Found {total_broken} broken references. See {log_file} for details.", flush=True)

if __name__ == "__main__":
    main()
