---
concept: function-parse-xml-to-markdown
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/vector-db-ingest/scripts/ingest_code_shim.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.383227+00:00
cluster: text
content_hash: ccaac3982ac54f2b
---

# Function: parse_xml_to_markdown

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python3
"""
ingest_code_shim.py (CLI)
=====================================

Purpose:
    Shim for ingesting code files into Vector DB.

Layer: Curate / Vector

Usage Examples:
    python ./scripts/ingest_code_shim.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - find_project_root(): Find the project root (where .git or legacy-system exists).
    - parse_xml_to_markdown(): No description.
    - parse_sql_to_markdown(): No description.
    - parse_json_to_markdown(): No description.
    - parse_python_to_markdown(): No description.
    - parse_javascript_to_markdown(): No description.
    - convert_code_file(): Returns markdown string for a given code file

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import ast
import os
import sys
import re
import json
from pathlib import Path
from typing import Optional

def find_project_root() -> Path:
    """Find the project root (where .git or legacy-system exists)."""
    current = Path.cwd()
    for _ in range(5):
        if (current / ".git").exists() or (current / "legacy-system").exists():
            return current
        current = current.parent
    return Path.cwd()

#============================================
# Function: parse_xml_to_markdown
# Purpose: Optimized for Oracle Forms XML exports
#============================================
def parse_xml_to_markdown(file_path: Path) -> str:
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        return f"# Error: Python XML library missing\n"

    try:
        filename = file_path.name
        project_root = find_project_root()
        try:
            relative_path = file_path.relative_to(project_root)
        except ValueError:
            relative_path = file_path

        markdown_output = f"# Oracle Forms XML: {filename}\n\n"
        markdown_output += f"**Path:** `{relative_path}`\n\n"

        tree = ET.parse(file_path)
        root = tree.getroot()

        # Extract Module Name
        module_name = root.attrib.get('Name', 'Unknown')
        markdown_output += f"## Module: `{module_name}`\n\n"

        # 1. Triggers (Form Level)
        triggers = root.findall(".//Trigger")
        if triggers:
            markdown_output += "## Triggers\n\n"
            for trig in triggers:
                name = trig.attrib.get('Name')
                text = trig.find('TriggerText')
                if name and text is not None and text.text:
                    markdown_output += f"### Trigger: `{name}`\n"
                    excerpt = text.text[:500] + "..." if len(text.text) > 500 else text.text
                    markdown_output += f"```plsql\n{excerpt}\n```\n\n"

        # 2. Program Units (PL/SQL)
        prog_units = root.findall(".//ProgramUnit")
        if prog_units:
            markdown_output += "## Program Units (Functions/Procedures)\n\n"
            for pu in prog_units:
                name = pu.attrib.get('Name')
                text = pu.find('ProgramUnitText')
                if name and text is not None and text.text:
                     markdown_output += f"### Unit: `{name}`\n"
                     # Extract signature if possible (first line)
                     first_line = text.text.strip().split('\n')[0]
                     markdown_output += f"**Signature:** `{first_line}`\n"
                     markdown_output += f"```plsql\n{text.text}\n```\n\n"

        # 3. Blocks and Items structure
        blocks = root.findall(".//Block")
        if blocks:
            markdown_output += "## Data Blocks\n\n"
            for blk in blocks:
                blk_name = blk.attrib.get('Name')
                markdown_output += f"### Block: `{blk_name}`\n"
                items = blk.findall(".//Item")
                if items:
                    item_names = [i.attrib.get('Name') for i in items if i.attrib is not None and i.attrib.get('N

*(content truncated)*

## See Also

- [[pre-parse-for---headless-to-set-non-interactive-backend-before-pyplot-import]]
- [[result-type-tells-downstream-tools-how-to-parse-the-entry]]
- [[1-parse-the-hook-payload]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[absolute-path-prefixes-that-should-never-be-written-to]]
- [[add-project-root-to-syspath]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/vector-db-ingest/scripts/ingest_code_shim.py`
- **Indexed:** 2026-04-27T05:21:04.383227+00:00
