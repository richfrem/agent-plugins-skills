---
concept: extract-module-name
source: plugin-code
source_file: vector-db/scripts/ingest_code_shim.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.431404+00:00
cluster: text
content_hash: 954878fc72611533
---

# Extract Module Name

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
ingest_code_shim.py
=====================================

Purpose:
    Specialized parser for converting code files (Oracle Forms XML, SQL, Python, JS, JSON)
    into searchable Markdown optimized for Vector DB ingestion.

Layer: Curate / Retrieve

Usage:
    from ingest_code_shim import convert_code_file
"""

import ast
import os
import sys
import re
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

def find_project_root() -> Path:
    """Find the project root by searching for .git or legacy-system markers."""
    current = Path.cwd()
    for _ in range(5):
        if (current / ".git").exists() or (current / "legacy-system").exists():
            return current
        current = current.parent
    return Path.cwd()

def parse_xml_to_markdown(file_path: Path) -> str:
    """
    Parses Oracle Forms XML exports into structured Markdown.

    Args:
        file_path: Path to the .xml export file.

    Returns:
        Markdown-formatted string representing the Forms module.
    """
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
                    item_names = [i.attrib.get('Name') for i in items if i.attrib is not None and i.attrib.get('Name')]
                    markdown_output += f"**Items:** {', '.join(item_names)}\n\n"

        return markdown_output
    except Exception as e:
        return f"# Error parsing XML: {str(e)}\n\nOriginal file path: {file_path}"

def parse_sql_to_markdown(file_path: Path) -> str:
    """Parses SQL scripts and extracts DDL object definitions."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        source = f.read()
    
    filename = file_path.name
    markdown_output = f"# SQL Script: {filename

*(content truncated)*

## See Also

- [[extract-row-count-if-data-has-a-recognizable-structure]]
- [[no-direct-usage-shared-module]]
- [[sample-payloads-keyed-by-claude-code-event-type-name]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/scripts/ingest_code_shim.py`
- **Indexed:** 2026-04-27T05:21:04.431404+00:00
