---
concept: regex-patterns-for-different-reference-types
source: plugin-code
source_file: link-checker/scripts/02_extract_link_references.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.247018+00:00
cluster: link
content_hash: 18691e41c1c3831b
---

# Regex patterns for different reference types

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/link-checker/scripts/02_extract_link_references.py -->
#!/usr/bin/env python
"""
02_extract_link_references.py (CLI)
=====================================

Purpose:
    Extractor: Generic scanner that extracts all link/path references from files.
    This is Phase 2 of the Link Checker pipeline.

Usage:
    python02_extract_link_references.py --root .

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
    Skips links inside fenced code blocks (both backtick and tilde fences)
    to avoid false positives from intentionally broken example links.
    """
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            in_code_block = False
            for line_num, line in enumerate(f, 1):
                stripped = line.strip()
                # Toggle code block state on fence delimiters; skip the fence line itself
                if stripped.startswith(('```', '~~~')):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    continue
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
                'file_inventory.json', 'link_references.js

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/link-checker-agent/scripts/02_extract_link_references.py -->
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
 

*(combined content truncated)*

## See Also

- [[check-all-text-files-in-skill-for-regex-py-mentions]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]
- [[all-event-types-recognised-by-the-claude-code-hook-system]]
- [[architectural-patterns-adapted-from-obrasuperpowers-mit-httpsgithubcomobrasuperpowers]]
- [[attempt-to-handle-langchain-version-differences-for-storage]]
- [[check-for-broken-symlinks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `link-checker/scripts/02_extract_link_references.py`
- **Indexed:** 2026-04-27T05:21:04.247018+00:00
