#!/usr/bin/env python
"""
05_report_unfixable_links.py (CLI)
=====================================

Purpose:
    Reporter: Generates a structured markdown report for human review of remaining issues.
    This is Phase 5 of the Link Checker pipeline.

Usage:
    python05_report_unfixable_links.py

Output:
    - unfixable_links_report.md: Human-readable report of gaps.

Key Input Dependencies:
    - broken_links.json (from Step 3) or remaining_broken_links.json (from Step 4, preferred if present)
"""
import os
import json
import argparse
from typing import List, Dict, Any

def _resolve_input_path(args) -> None:
    """Prefer remaining_broken_links.json (post-Step-4 output) over the default input, if present."""
    if args.input == 'broken_links.json' and os.path.exists('remaining_broken_links.json'):
        args.input = 'remaining_broken_links.json'
        print("Using remaining_broken_links.json (post-fix output from Step 4).")
    elif args.input == 'broken_links.json':
        print("Note: remaining_broken_links.json not found — report reflects pre-fix audit state.")
        print("      Run Step 4 without --dry-run to generate post-fix data.")


def _write_report(broken_list: list, output_path: str) -> None:
    """Write the grouped-by-source-file Markdown report of unfixable links."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Unfixable Links Report\n\n")
        f.write("The following link references require manual review or content creation. ")
        f.write("They could not be auto-fixed by the unique-naming pipeline.\n\n")

        if not broken_list:
            f.write("✅ **No broken links found!** All references either resolved correctly or were auto-fixed.\n")
            return

        # Group by source file
        grouped = {}
        for item in broken_list:
            sf = item['source_file']
            if sf not in grouped:
                grouped[sf] = []
            grouped[sf].append(item)

        for source_file, issues in grouped.items():
            f.write(f"## {source_file}\n\n")
            f.write("| Line | Link Reference | Issue Type | Candidates / Note |\n")
            f.write("|:---|:---|:---|:---|\n")

            for issue in issues:
                status = "MISSING" if not issue['candidates'] else "AMBIGUOUS"
                note = "File not found in inventory." if not issue['candidates'] else f"Potential matches: `{', '.join(issue['candidates'])}`"

                f.write(f"| {issue['line']} | `{issue['link']}` | **{status}** | {note} |\n")
            f.write("\n")


def main() -> None:
    """Generate the human-readable unfixable-links Markdown report from Step 3/4 output."""
    parser = argparse.ArgumentParser(description="Step 5: Generate unfixable links report.")
    parser.add_argument("--input", default="broken_links.json", help="Input JSON file from Step 3")
    parser.add_argument("--output", default="unfixable_links_report.md", help="Output Markdown report name")
    args = parser.parse_args()

    _resolve_input_path(args)

    if not os.path.exists(args.input):
        print(f"Error: {args.input} not found. Run Step 3 (and optionally Step 4) first.")
        return

    with open(args.input, 'r', encoding='utf-8') as f:
        broken_list = json.load(f)

    print(f"Generating report from {len(broken_list)} broken links...")
    _write_report(broken_list, args.output)
    print(f"✅ Report generated: {args.output}")

if __name__ == "__main__":
    main()
