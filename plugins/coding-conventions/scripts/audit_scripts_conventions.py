#!/usr/bin/env python3
"""
audit_scripts_conventions.py
=====================================

Purpose:
    Audits directories OR specific Python files for coding conventions compliance.
    Checks for file headers, docstrings, and type hints in signatures.

Layer: Investigate / Curate

Usage:
    # Audit a single file
    python3 audit_scripts_conventions.py path/to/script.py
    
    # Audit all files in a directory (recursively)
    python3 audit_scripts_conventions.py path/to/scripts_dir/
"""

import os
import sys
from typing import List, Tuple

def check_script(filepath: str) -> bool:
    """
    Checks header and type-hints on a single Python script.
    
    Args:
        filepath: Absolute path to the script file.
        
    Returns:
        True if compliant, False otherwise.
    """
    name = os.path.basename(filepath)
    if not filepath.endswith(".py"):
        # Shell scripts generally don't use strict python conventions
        return True
        
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"[❌] {name} - Error reading: {e}")
        return False
        
    if not lines:
        return True # Empty file is theoretically compliant but trivial
        
    header_chunk = "".join(lines[:10])
    has_header = '"""' in header_chunk or "Purpose:" in header_chunk or "purpose:" in header_chunk
    
    missing_hints = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("def "):
            if "(" in stripped and ")" in stripped:
                if "->" not in stripped:
                    missing_hints.append("return type")
                params = stripped[stripped.find("(")+1:stripped.rfind(")")]
                for p in params.split(","):
                    p = p.strip()
                    if p and p not in ["self", "cls"] and ":" not in p:
                        if not p.startswith("*"):
                            missing_hints.append(f"param '{p}'")

    status = "✅" if has_header and not missing_hints else "❌"
    if status == "❌":
         print(f"[{status}] {filepath}")
         if not has_header:
              print(f"     -> Missing File Header")
         if missing_hints:
              print(f"     -> Missing Type Hints: " + ", ".join(missing_hints))
    return has_header and not missing_hints

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 audit_scripts_conventions.py <file_or_directory>")
        sys.exit(1)
    
    target = sys.argv[1]
    if not os.path.exists(target):
        print(f"Path not found: {target}")
        sys.exit(1)
        
    passed = 0
    failed = 0
    total = 0

    if os.path.isfile(target):
         if check_script(target):
              passed += 1
         else:
              failed += 1
         total += 1
         print(f"\nFinal: {passed} Passed, {failed} Failed.")
    else:
         print(f"Auditing coding conventions recursive for scripts inside {target}...\n")
         for root, dirs, files in os.walk(target):
             for name in files:
                  if name.endswith(".py"):
                       path = os.path.join(root, name)
                       total += 1
                       if check_script(path):
                            passed += 1
                       else:
                            failed += 1

         print(f"\nScorecard Breakdown: {passed} Passed, {failed} Failed out of {total} scripts.")
