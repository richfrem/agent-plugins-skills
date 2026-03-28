#!/usr/bin/env python3
"""
verify_docx.py (CLI)
=====================================

Purpose:
    Perform a structural linting of generated DOCX files.
    Creates a strict L5 Delegated Constraint Verification Loop.

Layer: Cli_Entry_Points

Usage Examples:
    python3 verify_docx.py output.docx

Supported Object Types:
    - Generic

CLI Arguments:
    docx_file: Path to output DOCX file.

Input Files:
    - Word document (.docx).

Output:
    - JSON summary of verification status and errors.

Key Functions:
    verify_docx(): Structural verification of a DOCX file.

Script Dependencies:
    json, sys, pathlib, python-docx

Consumed by:
    - markdown-to-msword-converter skill
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

try:
    from docx import Document
except ImportError:
    print(json.dumps({
        "status": "errors_found",
        "total_errors": 1,
        "error_summary": {"DependencyMissing": {"count": 1, "locations": ["python-docx is not installed."]}}
    }))
    sys.exit(1)

def verify_docx(file_path: Path) -> Dict[str, Any]:
    if not file_path.exists():
        return {"status": "errors_found", "total_errors": 1, "error_summary": {"FileMissing": {"count": 1, "locations": ["File does not exist."]}}}
    
    if file_path.stat().st_size == 0:
        return {"status": "errors_found", "total_errors": 1, "error_summary": {"EmptyFile": {"count": 1, "locations": ["File is empty 0 bytes."]}}}

    errors: dict[str, list[str]] = {
        "ArchiveCorrupt": [],
        "NoParagraphs": []
    }
    
    total_errors: int = 0
    
    try:
        # 1. Test MS Word ZIP Archive Integrity
        doc = Document(file_path)
        
        # 2. Test Content Generation
        if len(doc.paragraphs) == 0:
            errors["NoParagraphs"].append("The generated DOCX contains 0 text paragraphs. Conversion likely failed silently.")
            total_errors += 1
            
    except Exception as e:
        errors["ArchiveCorrupt"].append(f"Failed to parse DOCX archive: {str(e)}")
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
        print("Usage: python verify_docx.py <docx_file>")
        sys.exit(1)
        
    file_path = Path(sys.argv[1])
    result = verify_docx(file_path)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
