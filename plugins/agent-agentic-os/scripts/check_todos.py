#!/usr/bin/env python3
"""
check_todos.py — TODO and Technical Debt Auditor
======================================================

Purpose:
    Audit a specific file for TODO comments, FIXME, HACK, or other technical debt markers.
    Used for pre-commit checks or reviewing task readiness.

Layer: 
    Scripts / Audit

Usage Examples:
    python3 ./scripts/check_todos.py <file_path>

Supported Object Types:
    - Code source files (Python, JS/TS, Markdown, etc.)

CLI Arguments:
    file_path               Target file absolute or relative path to inspect

Input Files:
    - Specified target file

Output:
    - Lists located matches to stdout
    - Returns non-zero error codes if missing files

Key Functions:
    check_todos()           Scans body using debt regex tracking matches index

Script Dependencies:
    - None

Consumed by:
    - Manual workflow hygiene passes or verify hooks
"""
import sys
import re
import os

def check_todos(file_path: str) -> int:
    if not os.path.isfile(file_path):
        print(f"Error: {file_path} not found.")
        return 1
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    # Matches common debt markers across languages:
    # TODO/FIXME/HACK/XXX/NOTE with optional colon, in # // /* <!-- comment styles
    DEBT_PATTERN = re.compile(
        r'(?:#|//|/\*|<!--|--)\s*'
        r'(?:TODO|FIXME|HACK|XXX|NOTE)\b',
        re.IGNORECASE
    )

    todo_found = False
    for i, line in enumerate(lines, 1):
        if DEBT_PATTERN.search(line):
            print(f"{file_path}:{i}: {line.strip()}")
            todo_found = True
            
    if not todo_found:
        print(f"No TODOs found in {file_path}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 check_todos.py <file_path>")
        sys.exit(1)
    sys.exit(check_todos(sys.argv[1]))
