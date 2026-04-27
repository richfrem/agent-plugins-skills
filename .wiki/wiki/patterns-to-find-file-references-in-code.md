---
concept: patterns-to-find-file-references-in-code
source: plugin-code
source_file: agent-scaffolders/scripts/path_reference_auditor.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.304521+00:00
cluster: phase
content_hash: 36e603d30dfc3885
---

# Patterns to find file references in code

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/path_reference_auditor.py -->
#!/usr/bin/env python
"""
path_reference_auditor.py
=====================================

Purpose:
    Two-phase audit that scans codebases for internal file reference queries 
    (like `./path/to/file`) inside agent skill environments and verifies their integrity.

Layer: Investigate / Repair

Usage Examples:
    pythonpath_reference_auditor.py --project . --phase scan
    pythonpath_reference_auditor.py --project . --phase verify
    pythonpath_reference_auditor.py --project . --phase report --report missing

Supported Object Types:
    Recursive script/markdown links queries.

CLI Arguments:
    --project: Absolute or relative project root directory. (Required)
    --phase: Mode operation [scan, verify, report]. (Required)
    --report: Sub-formatting report type output for the view layer.
    --inventory: Cache dashboard metadata location pointer.

Input Files:
    - Codebase directories scan.
    - temp/inventory.json

Output:
    Structured summary lists and populated inventory stream payloads.

Key Functions:
    - PathReferenceAuditor.phase_scan()
    - PathReferenceAuditor.phase_verify()
    - PathReferenceAuditor.check_reference_status()

Script Dependencies:
    - argparse, json, os, re, sys, datetime, Path (pathlib)

Consumed by:
    Static container checks post-audit verification loops.
"""

import os
import re
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

class PathReferenceAuditor:
    def __init__(self, project_root: str | Path, inventory_file: str | Path = 'temp/inventory.json') -> None:
        self.project_root = Path(project_root).resolve()
        self.inventory_file = Path(inventory_file)
        self.inventory = {
            "metadata": {
                "scanned_at": None,
                "verified_at": None,
                "project_root": str(self.project_root),
                "total_files_scanned": 0,
                "total_references_found": 0,
                "phase": "initial"
            },
            "references": []  # List of {source_file, reference, line, status}
        }

        # Patterns to find file references in code
        self.patterns = [
            r'\.\/([a-zA-Z0-9_\-/\.]+\.(md|mmd|py|json|sh|txt|in|yaml|yml))',  # ./path/to/file
            r'`([a-zA-Z0-9_\-/\.]+\.(md|mmd|py|json|sh|txt|in|yaml|yml))`',     # `path/to/file`
            r'\[([a-zA-Z0-9_\-/\.]+\.(md|mmd|py|json|sh|txt|in|yaml|yml))\]',   # [path/to/file]
            r'\(([a-zA-Z0-9_\-/\.]+\.(md|mmd|py|json|sh|txt|in|yaml|yml))\)',   # (path/to/file)
        ]

        self.file_extensions = {'.py', '.md', '.mmd', '.json', '.sh'}

    # ============================================================================
    # PHASE 1: SCAN - Find all references and populate inventory
    # ============================================================================

    def find_references_in_file(self, file_path: str | Path) -> list[dict]:
        """Extract all path references from a single file."""
        references = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for pattern in self.patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    ref_path = match.group(1)
                    line_num = content[:match.start()].count('\n') + 1

                    # Avoid duplicates in same file
                    if not any(r['reference'] == ref_path and r['line'] == line_num for r in references):
                        references.append({
                            'reference': ref_path,
                            'line': line_num
                        })
        except Exception as e:
            pass

        return references

    def phase_scan(self) -> None:
        """
        Phase 1: SCAN
        Walk all plugins/skills directories and find every ./reference.
        Populate inventory with raw ref

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/path-reference-auditor/references/path_reference_auditor.py -->
#!/usr/bin/env python3
"""
path_reference_auditor.py
=====================================

Purpose:
    Two-phase audit that scans codebases for internal file reference queries 
    (like `./path/to/file`) inside agent skill environments and verifies their integrity.

Layer: Investigate / Repair

Usage Examples:
    python3 path_reference_auditor.py --project . --phase scan
    python3 path_reference_auditor.py --project . --phase verify
    python3 path_reference_auditor.py --project . --phase report --report missing

Supported Object Types:
    Recursive script/markdown links queries.

CLI Arguments:
    --project: Absolute or relative project root directory. (Required)
    --phase: Mode operation [scan, verify, report]. (Required)
    --report: Sub-formattin

*(combined content truncated)*

## See Also

- [[default-file-extensions-to-index-if-manifest-is-empty]]
- [[thin-wrapper-delegates-to-the-canonical-implementation-in-scripts]]
- [[try-to-import-rlm-for-code-context-injection]]
- [[use-yaml-block-scalar-to-avoid-breaking-on-quotes-in-description]]
- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/path_reference_auditor.py`
- **Indexed:** 2026-04-27T05:21:04.304521+00:00
