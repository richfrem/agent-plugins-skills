#!/usr/bin/env python3
"""
[SKILL_ROOT]/scripts/audit_template_compliance.py (CLI)
=====================================

Purpose:
    Audits Form Overviews for template compliance (missing headers, BR format).

Layer: Curate / Inventories

Usage Examples:
    python [SKILL_ROOT]/scripts/audit_template_compliance.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - analyze_file(): No description.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import re
from pathlib import Path

# Configuration
# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()

DOCS_DIR = PROJECT_ROOT / 'legacy-system' / 'oracle-forms-overviews' / 'forms'
TEMPLATE_PATH = SCRIPT_DIR.parent / 'assets' / 'templates' / 'form-overview-template.md'
OUTPUT_REPORT = PROJECT_ROOT / 'legacy-system' / 'reference-data' / 'audit_compliance_report.md'

MANDATORY_HEADERS = [
    "## Overview",
    "## Applications with Access",
    "## Functional Description",  # Or "Functionality" (FORM0000 variant)
    "## Technical Implementation",
    "## Security", # Should contain "Active Roles" or "User Roles"
    "## Business Rules",
    "## Navigation",
    "## MenuConfig UI Access Table",
    "## Fine-Grained Access Control Rules", # Optional in template but user requested it? No, user implied consistency.
    "## Validated Dependencies"
]

def analyze_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    issues = []
    
    # Check Headers
    for header in MANDATORY_HEADERS:
        # Create a regex pattern that matches the header at the start of a line
        # allowing for optional extra text on the same line (e.g., " (Key Items)")
        header_pattern = r"^" + re.escape(header) + r".*$"
        
        # Exception for "Functional Description" vs "Functionality"
        if header == "## Functional Description":
             if not (re.search(r"^## Functional Description", content, re.MULTILINE) or 
                     re.search(r"^## Functionality", content, re.MULTILINE)):
                issues.append(f"Missing Header: {header}")
        elif header == "## Security":
             # Match "## Security"
             if not re.search(r"^## Security", content, re.MULTILINE):
                issues.append(f"Missing Header: {header}")
        else:
            if header == "## Overview":
                # Match "## Overview" OR "## Purpose"
                if not (re.search(r"^## Overview", content, re.MULTILINE) or re.search(r"^## Purpose", content, re.MULTILINE)):
                    issues.append(f"Missing Header: {header} (or ## Purpose)")
            else:
                if not re.search(header_pattern, content, re.MULTILINE):
                    issues.append(f"Missing Header: {header}")

    # Check BR Format
    br_section = re.search(r"## Business Rules.*?(?=\n##|\Z)", content, re.DOTALL | re.MULTILINE)
    br_style = "Unknown"
    if br_section:
        text = br_section.group(0)
        if "| Rule ID |" in text or "| **[BR-" in text:
            br_style = "Table"
        elif re.search(r"^\*\s+\*\*\[?BR-", text, re.MULTILINE):
            br_style = "List"
        elif "None Detected" in text:
             br_style = "None"
        elif "Table Switching" in text and not "|" in text: # FORM0000 case
             br_style = "List"

    return issues, br_style

def main():
    print(f"Scanning {DOCS_DIR}...")
    
    results = []
    style_counts = {"Table": 0, "List": 0, "Unknown": 0, "None": 0}
    
    files = sorted(list(DOCS_DIR.glob("*.md")))
    
    for file_path in files:
        issues, br_style = analyze_file(file_path)
        style_counts[br_style] = style_counts.get(br_style, 0) + 1
        
        if issues or br_style == "Unknown":
            results.append({
                "file": file_path.name,
                "issues": issues,
                "br_style": br_style
            })
            
    # Generate Report
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write("# Form Overview Compliance Audit\n\n")
        f.write(f"**Total Forms Scanned:** {len(files)}\n")
        f.write(f"**BR Style Distribution:** {style_counts}\n\n")
        
        f.write("## Detailed Gaps\n")
        f.write("| File | BR Style | Missing Headers |\n")
        f.write("|---|---|---|\n")
        
        for r in results:
            issues_str = "<br>".join(r['issues']) if r['issues'] else "None"
            f.write(f"| {r['file']} | {r['br_style']} | {issues_str} |\n")
            
    print(f"Audit Complete. Report written to {OUTPUT_REPORT}")
    print(f"Style Distribution: {style_counts}")

if __name__ == "__main__":
    main()
