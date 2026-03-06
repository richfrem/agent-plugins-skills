#!/usr/bin/env python3
"""
find_source_links.py (CLI)
=====================================

Purpose:
    Finds source file references in documentation.

Layer: Curate / Utilities

Usage Examples:
    python plugins/link-checker/scripts/find_source_links.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    identifier      : The identifier to search for (e.g. FORM0000, EXAMPLE_LIB)
    --doc-path      : The path of the document you are writing (to calculate relative links)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - find_files(): Finds related files for a given identifier (case-insensitive).
    - generate_links(): Generates Markdown links relative to a start path (default: repo root).
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import argparse
import sys
from pathlib import Path

# Configuration
# REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
LEGACY_ROOT = REPO_ROOT / "legacy-system"

def find_files(identifier):
    """Finds related files for a given identifier (case-insensitive)."""
    results = {
        "md": None,
        "xml": None,
        "pll": None,
        "fmb": None
    }
    
    search_id = identifier.lower()
    
    # Walk through legacy-system to find matches
    for root, dirs, files in os.walk(LEGACY_ROOT):
        for file in files:
            file_lower = file.lower()
            
            # Exact match logic or refined containment
            # Forms: FORM0000.fmb, FORM0000_fmb.xml, FORM0000-FormModule.md
            # Libraries: EXAMPLE_LIB.pll, EXAMPLE_LIB_pll.xml
            
            if search_id in file_lower:
                path = Path(root) / file
                
                try:
                    rel_path = path.relative_to(REPO_ROOT)
                except ValueError:
                    continue # Should not happen given root
                
                # Categorize
                if file_lower.endswith(".md") and "formmodule" in file_lower:
                    if file_lower == f"{search_id}-formmodule.md":
                         results["md"] = rel_path
                elif file_lower.endswith(".xml"):
                    if file_lower == f"{search_id}_fmb.xml" or file_lower == f"{search_id}.xml" or file_lower == f"{search_id}_pll.xml":
                        results["xml"] = rel_path
                elif file_lower.endswith(".pll"):
                    if file_lower == f"{search_id}.pll":
                        results["pll"] = rel_path
                elif file_lower.endswith(".fmb"):
                    if file_lower == f"{search_id}.fmb":
                        results["fmb"] = rel_path

    return results

def generate_links(identifier, results, start_path=None):
    """Generates Markdown links relative to a start path (default: repo root)."""
    links = []
    
    # Define relativity
    if start_path:
        base = Path(start_path).parent
    else:
        # Default to absolute-ish (repo relative) or just standard assumption
        # Note: User wants relative links in the docs.
        # Let's assume usage in `legacy-system/oracle-forms-overviews/forms/` directory often.
        # But for general output, let's output path relative to REPO ROOT, user can adjust.
        # OR better: output the string required for the standard location.
        base = REPO_ROOT / "legacy-system" / "oracle-forms-overviews" / "forms"

    def make_link(label, target_path):
        try:
            # Calculate logic relative to the "Overview" folder location for portability
            rel = os.path.relpath(REPO_ROOT / target_path, base)
            return f"[[{label}]({rel.replace(os.sep, '/')})]"
        except Exception:
            return f"[[{label}]({target_path})]"

    if results.get("pll"):
        links.append(f"`{identifier.upper()}`")
        links.append(make_link("PLL", results["pll"]))
        
    if results.get("fmb"):
         links.append(f"`{identifier.lower()}.fmb`")
    
    if results.get("md"):
        links.append(make_link("MD", results["md"]))
        
    if results.get("xml"):
        links.append(make_link("XML", results["xml"]))

    return " ".join(links)

def main():
    parser = argparse.ArgumentParser(description="Find source code links for an artifact.")
    parser.add_argument("identifier", help="The identifier to search for (e.g. FORM0000, EXAMPLE_LIB)")
    parser.add_argument("--doc-path", help="The path of the document you are writing (to calculate relative links)", default=None)
    
    args = parser.parse_args()
    
    # If doc_path is not provided, use a default that works for overview files
    if not args.doc_path:
        # Default to a mock location inside forms overviews
        default_doc_loc = REPO_ROOT / "legacy-system" / "oracle-forms-overviews" / "forms" / "mock.md"
        start_path = default_doc_loc
    else:
        start_path = Path(args.doc_path)

    results = find_files(args.identifier)
    
    if not any(results.values()):
        print(f"No exact matches found for {args.identifier}")
        return

    link_text = generate_links(args.identifier, results, start_path)
    print(link_text)

if __name__ == "__main__":
    main()
