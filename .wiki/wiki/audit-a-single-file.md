---
concept: audit-a-single-file
source: plugin-code
source_file: coding-conventions/scripts/audit_scripts_conventions.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.955494+00:00
cluster: path
content_hash: 2cdb75b07e24d85e
---

# Audit a single file

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
audit_scripts_conventions.py
=====================================

Purpose:
    Audits directories OR specific Python files for coding conventions compliance.
    Checks for file headers, docstrings, and type hints in signatures.

Layer: Investigate / Curate

Usage:
    # Audit a single file
    python audit_scripts_conventions.py path/to/script.py
    
    # Audit all files in a directory (recursively)
    python audit_scripts_conventions.py path/to/scripts_dir/
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
    import ast
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                if node.returns is None:
                    missing_hints.append(f"return type on '{func_name}'")
                for arg in node.args.args:
                    if arg.arg not in ["self", "cls"] and arg.annotation is None:
                        missing_hints.append(f"param '{arg.arg}' on '{func_name}'")
    except Exception as e:
        # File is empty or has syntax issues
        pass

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
        print("Usage: python audit_scripts_conventions.py <file_or_directory>")
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


## See Also

- [[with-a-system-prompt-file]]
- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[as-a-library]]
- [[atomically-replace-an-existing-path-with-a-new-symlink-pointing-to-src]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `coding-conventions/scripts/audit_scripts_conventions.py`
- **Indexed:** 2026-04-27T05:21:03.955494+00:00
