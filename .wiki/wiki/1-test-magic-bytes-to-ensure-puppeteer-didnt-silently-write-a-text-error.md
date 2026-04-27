---
concept: 1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/convert-mermaid/scripts/verify_png.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.081717+00:00
cluster: total_errors
content_hash: 10002c22b124488e
---

# 1. Test Magic Bytes to ensure Puppeteer didn't silently write a text error

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/convert-mermaid/scripts/verify_png.py -->
#!/usr/bin/env python3
"""
verify_png.py (CLI)
=====================================

Purpose:
    Perform a structural linting of generated PNG files.
    Creates a strict L5 Delegated Constraint Verification Loop.

Layer: Cli_Entry_Points

Usage Examples:
    python3 verify_png.py output.png

Supported Object Types:
    - Generic

CLI Arguments:
    png_file: Path to output PNG file.

Input Files:
    - PNG file (.png).

Output:
    - JSON summary of verification status and errors.

Key Functions:
    verify_png(): Structural verification of a PNG file.

Script Dependencies:
    json, sys, pathlib

Consumed by:
    - mermaid-to-png skill
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

def verify_png(file_path: Path) -> Dict[str, Any]:
    if not file_path.exists():
        return {"status": "errors_found", "total_errors": 1, "error_summary": {"FileMissing": {"count": 1, "locations": ["File does not exist."]}}}
    
    if file_path.stat().st_size == 0:
        return {"status": "errors_found", "total_errors": 1, "error_summary": {"EmptyFile": {"count": 1, "locations": ["File is empty 0 bytes."]}}}

    errors: dict[str, list[str]] = {
        "MissingMagicBytes": [],
    }
    
    total_errors: int = 0
    
    try:
        # 1. Test Magic Bytes to ensure Puppeteer didn't silently write a text error
        with open(file_path, "rb") as f:
            header = f.read(8)
            # Standard PNG magic bytes: \x89 \x50 \x4e \x47 \x0d \x0a \x1a \x0a
            if header != b'\x89PNG\r\n\x1a\n':
                errors["MissingMagicBytes"].append(f"The file does not have a valid PNG header. It started with: {header!r}")
                total_errors += 1
            
    except Exception as e:
        errors["MissingMagicBytes"].append(f"Failed to read PNG binary: {str(e)}")
        total_errors += 1
        
    result: dict = {
        "status": "success" if total_errors == 0 else "errors_found",
        "total_errors": total_errors,
        "error_summary": {}
    }
    
    for err_type, locations in errors.items():
        if locations:
            result["error_summary"][err_type] = {
                "count": len(locations),
                "locations": locations[:10]
            }
            
    return result

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python verify_png.py <png_file>")
        sys.exit(1)
        
    file_path = Path(sys.argv[1])
    result = verify_png(file_path)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()


<!-- Source: plugin-code/mermaid-to-png/scripts/verify_png.py -->
#!/usr/bin/env python
"""
verify_png.py (CLI)
=====================================

Purpose:
    Perform a structural linting of generated PNG files.
    Creates a strict L5 Delegated Constraint Verification Loop.

Layer: Cli_Entry_Points

Usage Examples:
    pythonverify_png.py output.png

Supported Object Types:
    - Generic

CLI Arguments:
    png_file: Path to output PNG file.

Input Files:
    - PNG file (.png).

Output:
    - JSON summary of verification status and errors.

Key Functions:
    verify_png(): Structural verification of a PNG file.

Script Dependencies:
    json, sys, pathlib

Consumed by:
    - mermaid-to-png skill
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

def verify_png(file_path: Path) -> Dict[str, Any]:
    if not file_path.exists():
        return {"status": "errors_found", "total_errors": 1, "error_summary": {"FileMissing": {"count": 1, "locations": ["File does not exist."]}}}
    
    if file_path.stat().st_size == 0:
        return {"status": "errors_found", "total_errors": 1, "error_summary": {"EmptyFile": {"count": 1, "locations": ["File is empty 0 bytes."]}}}

    errors: dict[str, list[str]] = {
        "MissingMagicBytes": [],
    }
    
    total_errors: int = 0
    
    try:
        # 1. Test Magic Bytes to ensure Puppeteer didn't silently write a text error
        with open(file_path, "rb") as f:
            header = f.read(8)
            # Standard PNG magic bytes: \x89 \x50 \x4e \x47 \x0d \x0a \x1a \x0a
            if header != b'\x89PNG\r\n\x1a\n':
                errors["MissingMagicBytes"].append(f"The file does not have a valid PNG header. It started with: {header!r}")
                total_errors += 1
            
    except Exception as e:
        errors["MissingMagicBytes"].append(f"Failed to read PNG binary: {str(e)}")
        total_errors += 1
        
    result: dict = {
        "status": "success" if total_errors == 0 else "errors_found",
        "total_errors": total_errors,
        "error_summary": {}
    }
    
    for err_type, locations in errors.items():
        if locations:
            result["error_summary"][err_type] = {
                "count": len(locations),
                "locations": locations[:10]
            }


*(combined content truncated)*

## See Also

- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[1-test-ms-word-zip-archive-integrity]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[atomically-replace-an-existing-path-with-a-new-symlink-pointing-to-src]]
- [[ensure-unicode-output-works-on-windows-terminals-that-default-to-cp1252]]
- [[fix-1-literal-n-chars-write-back-immediately-so-json-parse-can-proceed]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/convert-mermaid/scripts/verify_png.py`
- **Indexed:** 2026-04-27T05:21:04.081717+00:00
