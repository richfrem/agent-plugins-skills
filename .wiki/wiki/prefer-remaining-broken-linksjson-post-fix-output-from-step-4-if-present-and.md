---
concept: prefer-remaining-broken-linksjson-post-fix-output-from-step-4-if-present-and
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/link-checker-agent/scripts/05_report_unfixable_links.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.248248+00:00
cluster: json
content_hash: 750bbf32509875b0
---

# Prefer remaining_broken_links.json (post-fix output from Step 4) if present and

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/link-checker-agent/scripts/05_report_unfixable_links.py -->
#!/usr/bin/env python3
"""
05_report_unfixable_links.py (CLI)
=====================================

Purpose:
    Reporter: Generates a structured markdown report for human review of remaining issues.
    This is Phase 5 of the Link Checker pipeline.

Usage:
    python3 05_report_unfixable_links.py

Output:
    - unfixable_links_report.md: Human-readable report of gaps.
"""
import os
import json
import argparse
from typing import List, Dict, Any

def main() -> None:
    parser = argparse.ArgumentParser(description="Step 5: Generate unfixable links report.")
    parser.add_argument("--input", default="broken_links.json", help="Input JSON file from Step 3")
    parser.add_argument("--output", default="unfixable_links_report.md", help="Output Markdown report name")
    args = parser.parse_args()

    # Prefer remaining_broken_links.json (post-fix output from Step 4) if present and
    # the caller didn't explicitly override --input. This ensures the report reflects
    # the actual post-fix state, not the stale pre-fix audit.
    if args.input == 'broken_links.json' and os.path.exists('remaining_broken_links.json'):
        args.input = 'remaining_broken_links.json'
        print("Using remaining_broken_links.json (post-fix output from Step 4).")
    elif args.input == 'broken_links.json':
        print("Note: remaining_broken_links.json not found — report reflects pre-fix audit state.")
        print("      Run Step 4 without --dry-run to generate post-fix data.")

    if not os.path.exists(args.input):
        print(f"Error: {args.input} not found. Run Step 3 (and optionally Step 4) first.")
        return

    with open(args.input, 'r', encoding='utf-8') as f:
        broken_list = json.load(f)
        
    print(f"Generating report from {len(broken_list)} broken links...")
    
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write("# Unfixable Links Report\n\n")
        f.write("The following link references require manual review or content creation. ")
        f.write("They could not be auto-fixed by the unique-naming pipeline.\n\n")
        
        if not broken_list:
            f.write("✅ **No broken links found!** All references either resolved correctly or were auto-fixed.\n")
        else:
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
                
    print(f"✅ Report generated: {args.output}")

if __name__ == "__main__":
    main()


<!-- Source: plugin-code/link-checker/scripts/05_report_unfixable_links.py -->
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
"""
import os
import json
import argparse
from typing import List, Dict, Any

def main() -> None:
    parser = argparse.ArgumentParser(description="Step 5: Generate unfixable links report.")
    parser.add_argument("--input", default="broken_links.json", help="Input JSON file from Step 3")
    parser.add_argument("--output", default="unfixable_links_report.md", help="Output Markdown report name")
    args = parser.parse_args()

    # Prefer remaining_broken_links.json (post-fix output from Step 4) if present and
    # the caller didn't explicitly override --input. This ensures the report reflects
    # the actual post-fix state, not the stale pre-fix audit.
    if args.input == 'broken_links.json' and os.path.exists('remaining_broken_links.json'):
        args.input = 'remaining_broken_links.json'
        print("Using remaining_broken_links.json (post-fix output from Step 4).")
    elif args.input == 'broken_links.json':
        print("Note: remaining_broken_links.json not found — report reflects pre-fix audit state.")
        print("      Run Step 4 without --dry-run to generate post-fix data.")

    if n

*(combined content truncated)*

## See Also

- [[files-to-exclude-from-output-listings]]
- [[force-utf-8-output-on-windows-if-possible]]
- [[get-all-unique-queries-from-train-and-test-sets-with-should-trigger-info]]
- [[load-and-validate-eval-results-data-from-tsv]]
- [[1-configuration-setup-dynamic-from-profile]]
- [[1-handle-absolute-paths-from-repo-root]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/link-checker-agent/scripts/05_report_unfixable_links.py`
- **Indexed:** 2026-04-27T05:21:04.248248+00:00
