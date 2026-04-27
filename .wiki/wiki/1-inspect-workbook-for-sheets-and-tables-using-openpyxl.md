---
concept: 1-inspect-workbook-for-sheets-and-tables-using-openpyxl
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/excel-to-csv/scripts/convert.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.231038+00:00
cluster: sheet
content_hash: 24458dcd90735504
---

# 1. Inspect workbook for sheets and tables using openpyxl

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python3
"""
convert.py (CLI)
=====================================

Purpose:
    Convert all (or selected) sheets from an Excel workbook into CSV files.

Layer: Data Processing Utilities

Usage Examples:
    python3 scripts/convert.py --excel data.xlsx --sheets "Sheet1" --outdir ./output
    python3 scripts/convert.py --excel data.xlsx --sheets "SalesTable" --outdir ./output

Supported Object Types:
    - .xlsx
    - .xls

CLI Arguments:
    --excel         : Path to the Excel workbook.
    --outdir        : Output directory for CSV files (default: current directory).
    --sheets        : Comma-separated list of sheet names to convert.
    --write-empty   : Write a CSV even if the sheet has no non-empty rows/columns.

Output:
    - CSV files generated in the specified output directory.

Key Functions:
    - sanitize_sheet_name()
    - convert_excel_to_csv()
"""

from pathlib import Path
import argparse
import sys
import re

try:
    import pandas as pd
    import openpyxl
    from openpyxl.utils.cell import range_boundaries
except ImportError as e:
    print("Missing dependency: pandas or openpyxl. Install with `pip install pandas openpyxl` and try again.", file=sys.stderr)
    sys.exit(1)


def sanitize_sheet_name(name: str) -> str:
    """Make filename-safe: replace spaces and illegal chars."""
    name = name.strip()
    name = re.sub(r"[\\/:*?\"<>|]+", "_", name)
    name = name.replace(" ", "_")
    return name[:120]


def convert_excel_to_csv(excel_path: Path, out_dir: Path, sheets: str | None = None, write_empty: bool = False, encoding: str = "utf-8-sig") -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    
    target_names = [s.strip() for s in sheets.split(",")] if sheets else None
    
    # 1. Inspect workbook for sheets and tables using openpyxl
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    
    # Maps requested name -> {'type': 'sheet'|'table', 'sheet_name': str, 'bounds': (min_col, min_row, max_col, max_row)}
    extractions = {}
    
    if target_names:
        for target in target_names:
            found = False
            # Check if it's a sheet
            if target in wb.sheetnames:
                extractions[target] = {'type': 'sheet', 'sheet_name': target}
                found = True
            else:
                # Check if it's a table in any sheet
                for sheet in wb.sheetnames:
                    ws = wb[sheet]
                    if target in ws.tables:
                        tbl = ws.tables[target]
                        bounds = range_boundaries(tbl.ref)
                        extractions[target] = {'type': 'table', 'sheet_name': sheet, 'bounds': bounds}
                        found = True
                        break
            if not found:
                print(f"Warning: '{target}' not found as a sheet or table. Skipping.", file=sys.stderr)
    else:
        # Default behavior: extract all sheets
        for sheet in wb.sheetnames:
            extractions[sheet] = {'type': 'sheet', 'sheet_name': sheet}

    # 2. Extract parsed targets using pandas
    summary = {"written": [], "skipped": []}
    
    # Cache loaded dataframes per sheet so we only read them once
    loaded_sheets = {}

    for target, info in extractions.items():
        sheet_name = info['sheet_name']
        
        if sheet_name not in loaded_sheets:
            try:
                # Select engine based on extension
                engine = "openpyxl" if excel_path.suffix.lower() == ".xlsx" else "xlrd"
                df = pd.read_excel(excel_path, sheet_name=sheet_name, engine=engine, header=None)
                loaded_sheets[sheet_name] = df
            except ImportError:
                print(f"Error: Missing dependency for {excel_path.suffix} files. Please install '{engine}' (e.g., pip install {engine}).", file=sys.stderr)
                summary["skipped"].append(sheet_name)
                continue
            except Exception as e:
                

*(content truncated)*

## See Also

- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[1-basic-summarize-all-documents]]
- [[1-check-env]]
- [[1-check-root-structure]]
- [[1-configuration-setup-dynamic-from-profile]]
- [[1-copilot-gpt-5-mini]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/excel-to-csv/scripts/convert.py`
- **Indexed:** 2026-04-27T05:21:04.231038+00:00
