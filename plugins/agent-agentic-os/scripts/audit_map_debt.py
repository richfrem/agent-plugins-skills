#!/usr/bin/env python3
"""
audit_map_debt.py (Python Service)
=====================================

Purpose:
    Parses and audits map-debt.md for compliance.
    Supports both:
      1. Standard Markdown Table format (| ID | Title | Status | ... |)
      2. Legacy '---'-separated key-value block format (- Key: Value)
    Exits with code 1 if any OPEN entry:
      - Is older than 14 days (EXPIRED).
      - Has Repeat set to YES (REPEAT).

Layer: Backend / py_services / DevOps

Key Input Dependencies:
    - references/map-debt.md or .agent/map-debt.md
"""

import re
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_DEBT_FILE = Path(__file__).resolve().parents[3] / "references" / "map-debt.md"
if not DEFAULT_DEBT_FILE.exists():
    ALT_FILE = Path(__file__).resolve().parents[3] / ".agent" / "map-debt.md"
    if ALT_FILE.exists():
        DEFAULT_DEBT_FILE = ALT_FILE


def parse_table_entries(content: str) -> list[dict]:
    """Parses standard markdown table format with header row."""
    lines = [l.strip() for l in content.splitlines() if l.strip().startswith("|")]
    if len(lines) < 2:
        return []

    # Find header row
    header_line = lines[0]
    headers = [h.strip() for h in header_line.split("|")[1:-1]]

    entries = []
    for line in lines[1:]:
        # Skip separator row like |---|---|
        if re.match(r"^\|(\s*:?-+:?\s*\|)+$", line):
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) == len(headers):
            entry = dict(zip(headers, cols))
            # Standardize keys for evaluator
            normalized = {
                "ID": entry.get("ID", ""),
                "Artifact": entry.get("Title", entry.get("Artifact", "")),
                "Status": entry.get("Status", ""),
                "Severity": entry.get("Severity", ""),
                "Repeat": entry.get("Repeat", "NO"),
                "Logged": entry.get("First Seen", entry.get("Logged", "")),
                "Description": entry.get("Description", ""),
                "Resolution Commit": entry.get("Resolution Commit", "")
            }
            entries.append(normalized)
    return entries


def parse_debt_entries(file_path: Path) -> list[dict]:
    """Parses map-debt.md using either markdown table or '---'-separated format."""
    if not file_path.exists():
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # If it's a markdown table
    if re.search(r"\|\s*ID\s*\|\s*Title\s*\|", content, re.IGNORECASE) or re.search(r"\|\s*ID\s*\|\s*Artifact\s*\|", content, re.IGNORECASE):
        return parse_table_entries(content)

    # Legacy: split sections by markdown horizontal rules
    sections = [s.strip() for s in content.split("---") if s.strip()]
    
    entries = []
    for section in sections:
        entry = {}
        for line in section.splitlines():
            line = line.strip()
            if line.startswith("- "):
                parts = line[2:].split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = parts[1].strip()
                    entry[key] = val
        if entry:
            entries.append(entry)
            
    return entries


def evaluate_debt(entries: list[dict], today_str: str | None = None) -> list[str]:
    """Checks entries against expiry and repeat constraints. Returns list of errors."""
    if today_str:
        today = datetime.strptime(today_str, "%Y-%m-%d")
    else:
        today = datetime.now()

    errors = []
    for i, entry in enumerate(entries):
        status = entry.get("Status", "").upper()
        if status != "OPEN":
            continue

        logged_date_str = entry.get("Logged")
        artifact = entry.get("Artifact", f"Entry #{i+1}")
        repeat = entry.get("Repeat", "").upper()

        if logged_date_str:
            try:
                logged_date = datetime.strptime(logged_date_str, "%Y-%m-%d")
                days_old = (today - logged_date).days
                if days_old > 14:
                    errors.append(
                        f"⚠ EXPIRED MAP DEBT: {artifact} logged on {logged_date_str} is {days_old} days old (> 14 days)."
                    )
            except ValueError:
                errors.append(f"⚠ INVALID DATE FORMAT: {artifact} has invalid date '{logged_date_str}' (expected YYYY-MM-DD).")

        if repeat == "YES":
            errors.append(
                f"⚠ REPEAT MAP DEBT: {artifact} has Repeat=YES and is still OPEN. Repetitive friction must be escalated or resolved."
            )

    return errors


def main():
    """Parse CLI args, audit the map-debt file, and exit 1 on any expired/repeat entry."""
    import argparse
    parser = argparse.ArgumentParser(description="Audit map debt registry for aging/repeat friction")
    parser.add_argument("--file", type=str, default=str(DEFAULT_DEBT_FILE), help="Path to map-debt.md file")
    args = parser.parse_args()

    debt_file = Path(args.file)
    if not debt_file.exists():
        print(f"✓ No map debt file found at {debt_file}. Assuming clean state.")
        sys.exit(0)

    entries = parse_debt_entries(debt_file)
    errors = evaluate_debt(entries)

    if errors:
        print("\n==================================================")
        print("   MAP DEBT AUDIT FAILURES")
        print("==================================================")
        for error in errors:
            print(error)
        print("==================================================")
        print("Please resolve the expired/repeating debt or escalate to the user.")
        sys.exit(1)
    else:
        print(f"✓ Map debt audit passed. Checked {len(entries)} entries successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
