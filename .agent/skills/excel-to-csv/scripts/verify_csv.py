#!/usr/bin/env python3
"""
verify_csv.py
=====================================

Purpose:
    Perform a structural linting of generated CSV files to create a strict L5 Delegated Constraint Verification Loop.

Layer: Data Processing Utilities

Usage Examples:
    python3 verify_csv.py output.csv

Supported Object Types:
    - CSV files (.csv)

CLI Arguments:
    file_path: Path to the CSV file.

Input Files:
    - CSV file to verify.

Output:
    - JSON report detailing any errors found (JaggedRow, EmptyFile, etc.).

Key Functions:
    - verify_csv()

Script Dependencies:
    None

Consumed by:
    - Excel explicitly to CSV conversion workflow
"""

import csv
import json
import sys
from pathlib import Path

def verify_csv(file_path: Path) -> dict:
    if not file_path.exists():
        return {"status": "errors_found", "total_errors": 1, "error_summary": {"FileMissing": {"count": 1, "locations": ["File does not exist."]}}}
    
    if file_path.stat().st_size == 0:
        return {"status": "errors_found", "total_errors": 1, "error_summary": {"EmptyFile": {"count": 1, "locations": ["File is empty 0 bytes."]}}}

    errors = {
        "JaggedRow": [],
        "TrailingComma": []
    }
    
    total_errors = 0
    
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
                header_count = len(headers)
            except StopIteration:
                return {"status": "errors_found", "total_errors": 1, "error_summary": {"NoHeaders": {"count": 1, "locations": ["File has no headers."]}}}
            
            if len(headers) != len(set(headers)):
                errors["DuplicateHeader"] = [h for h in headers if headers.count(h) > 1]
                total_errors += len(errors["DuplicateHeader"])
            
            for i, row in enumerate(reader, start=2):
                if len(row) != header_count:
                    err_name = "JaggedRow" if len(row) > header_count else "RowCountMismatch"
                    errors[err_name].append(f"Row {i} has {len(row)} columns, expected {header_count}")
                    total_errors += 1
                
                for col_idx, cell in enumerate(row):
                    try:
                        cell.encode('ascii')
                    except UnicodeEncodeError:
                        if "NonAscii" not in errors: errors["NonAscii"] = []
                        errors["NonAscii"].append(f"Row {i}, Col {col_idx} contains non-ASCII characters.")
                        total_errors += 1

    except Exception as e:
        return {"status": "errors_found", "total_errors": 1, "error_summary": {"ParsingError": {"count": 1, "locations": [str(e)]}}}
        
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
        print("Usage: python verify_csv.py <csv_file>")
        sys.exit(1)
        
    file_path = Path(sys.argv[1])
    result = verify_csv(file_path)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
