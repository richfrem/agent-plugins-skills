#!/usr/bin/env python3
"""
ingest_code_shim.py (CLI)
=====================================

Purpose:
    Shim for ingesting code files into Vector DB.

Layer: Curate / Vector

Usage Examples:
    python plugins/vector-db/scripts/ingest_code_shim.py --help

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
                    item_names = [i.attrib.get('Name') for i in items if i.attrib.get('Name')]
                    markdown_output += f"**Items:** {', '.join(item_names)}\n\n"

        return markdown_output
    except Exception as e:
        return f"# Error parsing XML: {str(e)}\n\nOriginal file path: {file_path}"

#============================================
# Function: parse_sql_to_markdown
#============================================
def parse_sql_to_markdown(file_path: Path) -> str:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        source = f.read()
    
    filename = file_path.name
    markdown_output = f"# SQL Script: {filename}\n\n"
    
    # Extract object creations
    # CREATE [OR REPLACE] [TYPE] NAME
    pattern = re.compile(r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:FORCE\s+)?(VIEW|TABLE|PROCEDURE|FUNCTION|PACKAGE|TRIGGER|INDEX)\s+([a-zA-Z0-9_$.]+)', re.IGNORECASE)
    
    found_objects = []
    for match in pattern.finditer(source):
        obj_type = match.group(1).upper()
        obj_name = match.group(2)
        found_objects.append(f"- **{obj_type}**: `{obj_name}`")
        
    if found_objects:
        markdown_output += "## Defined Objects\n\n" + "\n".join(found_objects) + "\n\n"
    
    # Just dump the whole thing in a block for semantic search to find keywords
    markdown_output += "## Source Code\n\n```sql\n" + source + "\n```\n"
    return markdown_output

#============================================
# Function: parse_json_to_markdown
#============================================
def parse_json_to_markdown(file_path: Path) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        filename = file_path.name
        markdown_output = f"# JSON Data: {filename}\n\n"
        
        def summarize_obj(obj, indent=0):
            summary = ""
            spacing = "  " * indent
            if isinstance(obj, dict):
                keys = list(obj.keys())
                summary += f"{spacing}- **Document Keys:** {', '.join(keys[:10])}"
                if len(keys) > 10: summary += "..."
                summary += "\n"
                # Deep dive first level
                for k in keys[:5]:
                    summary += f"{spacing}  - `{k}`: {type(obj[k]).__name__}\n"
            elif isinstance(obj, list):
                summary += f"{spacing}- **List:** {len(obj)} items\n"
                if obj and isinstance(obj[0], dict):
                    summary += f"{spacing}  - Item Schema keys: {', '.join(list(obj[0].keys())[:5])}\n"
            return summary

        markdown_output += "## Structure Summary\n\n"
        markdown_output += summarize_obj(data)
        
        # Dump string rep for searchability (truncated)
        text_rep = json.dumps(data, indent=2)
        if len(text_rep) > 50000:
            text_rep = text_rep[:50000] + "\n...[Truncated]"
            
        markdown_output += "\n## Content\n\n```json\n" + text_rep + "\n```\n"
        return markdown_output
        
    except Exception as e:
        return f"Error parsing JSON: {e}"

#============================================
# Function: parse_python_to_markdown
#============================================
def parse_python_to_markdown(file_path: Path) -> str:
    file_path = Path(file_path)
    if not file_path.exists():
        return f"File not found: {file_path}"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()
    
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return f"# Syntax Error in {file_path.name}\n\n```\n{e}\n```"
    
    filename = file_path.name
    markdown_output = f"# Code File: {filename}\n\n**Language:** Python\n\n"
    
    # Docstring
    docstring = ast.get_docstring(tree)
    if docstring:
        markdown_output += f"## Module Description\n\n{docstring}\n\n"
    
    # Classes and Functions
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            type_label = "Class" if isinstance(node, ast.ClassDef) else "Function"
            name = node.name
            start_line = node.lineno
            doc = ast.get_docstring(node) or "No docstring."
            
            # Simple signature reconstruction
            markdown_output += f"## {type_label}: `{name}`\n"
            markdown_output += f"**Line:** {start_line}\n"
            markdown_output += f"**Docs:** {doc}\n\n"
            
            # Source segment
            segment = ast.get_source_segment(source, node)
            if segment:
                markdown_output += f"```python\n{segment}\n```\n\n"
                
    return markdown_output

#============================================
# Function: parse_javascript_to_markdown (Regex Shim)
#============================================
def parse_javascript_to_markdown(file_path: Path) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()
        
    filename = file_path.name
    markdown_output = f"# Code File: {filename}\n\n**Language:** JS/TS\n\n"
    
    # Functions
    func_pattern = re.compile(r'function\s+(\w+)\s*\((.*?)\)')
    for match in func_pattern.finditer(source):
        name = match.group(1)
        args = match.group(2)
        markdown_output += f"## Function: `{name}`\n**Signature:** `{name}({args})`\n\n"
        
    # Full source (truncated if huge)
    if len(source) < 50000:
        markdown_output += f"## Source\n```javascript\n{source}\n```\n"
    else:
        markdown_output += f"## Source\n```javascript\n{source[:50000]}\n...[Truncated]\n```\n"
        
    return markdown_output

#============================================
# Main Converter Entry Point
#============================================
def convert_code_file(input_file: Path) -> str:
    """Returns markdown string for a given code file"""
    suffix = input_file.suffix.lower()
    
    if suffix == '.py':
        return parse_python_to_markdown(input_file)
    elif suffix in ['.js', '.jsx', '.ts', '.tsx']:
        return parse_javascript_to_markdown(input_file)
    elif suffix == '.xml':
        return parse_xml_to_markdown(input_file)
    elif suffix == '.sql':
        return parse_sql_to_markdown(input_file)
    elif suffix == '.json':
        return parse_json_to_markdown(input_file)
    else:
        # Generic fallback
        try:
            content = input_file.read_text(encoding='utf-8', errors='ignore')
            return f"# File: {input_file.name}\n\n```\n{content}\n```"
        except:
            return ""

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(convert_code_file(Path(sys.argv[1])))
