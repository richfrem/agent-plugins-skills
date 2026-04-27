---
concept: expected-minimums-per-fixture
source: plugin-code
source_file: agent-scaffolders/scripts/assert_audit.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.345001+00:00
cluster: json
content_hash: 489d1589c1fa8136
---

# Expected minimums per fixture

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/assert_audit.py -->
#!/usr/bin/env python
"""
assert_audit.py (CLI)
=====================================

Purpose:
    Programmatic regression assertions for self-audit scanner results.
    Reads the JSON output of inventory_plugin.py and asserts expected counts 
    for known test fixtures. Exits non-zero on assertion failure.

Layer: Investigate / Audit / Regression

Usage Examples:
    pythonassert_audit.py --fixture flawed --json-output scan_output.json
    pythonassert_audit.py --fixture gold --json-output scan_output.json
    pythonassert_audit.py --fixture self --json-output scan_output.json

Supported Object Types:
    Scanner auditing reports.

CLI Arguments:
    --fixture: Which fixture to assert (flawed | gold | self) (Required)
    --json-output: Path to the JSON scanner output file (Required)

Input Files:
    - scan_output.json (From inventory_plugin.py)

Output:
    Standard output containing PASS/FAIL metrics. Exits non-zero on failure.

Key Functions:
    - load_json()
    - assert_fixture()

Script Dependencies:
    None

Consumed by:
    auditor regression tests.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# Expected minimums per fixture
ASSERTIONS: dict[str, dict[str, Any]] = {
    "flawed": {
        "security_flags_min": 4,
        "issues_min": 1,
        "warnings_min": 2,
        "security_flags_note": "network calls + env access (obfuscated credential is LLM-only, not scanner)",
    },
    "gold": {
        "security_flags_max": 0,
        "issues_max": 0,
        "warnings_max": 0,
    },
    "self": {
        "security_flags_max": 0,
        "issues_max": 0,
    },
}


def load_json(path: str) -> dict[str, Any]:
    """Load and parse the JSON output file from inventory_plugin.py."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: JSON output file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(2)


def assert_fixture(fixture: str, data: dict[str, Any]) -> bool:
    """Run assertions for the given fixture. Returns True if all pass."""
    rules = ASSERTIONS.get(fixture)
    if rules is None:
        print(f"ERROR: Unknown fixture '{fixture}'. Valid: {list(ASSERTIONS)}", file=sys.stderr)
        sys.exit(2)

    security_flags = data.get("security_flags", [])
    issues = data.get("issues", [])
    warnings = data.get("warnings", [])

    passed: list[str] = []
    failed: list[str] = []

    def check_min(field: str, actual: list, minimum: int, note: str = "") -> None:
        label = f"len({field}) >= {minimum}"
        if note:
            label += f"  [{note}]"
        if len(actual) >= minimum:
            passed.append(f"PASS  {label}  (got {len(actual)})")
        else:
            failed.append(f"FAIL  {label}  (got {len(actual)})")

    def check_max(field: str, actual: list, maximum: int) -> None:
        label = f"len({field}) <= {maximum}"
        if len(actual) <= maximum:
            passed.append(f"PASS  {label}  (got {len(actual)})")
        else:
            failed.append(f"FAIL  {label}  (got {len(actual)})")

    if "security_flags_min" in rules:
        check_min("security_flags", security_flags, rules["security_flags_min"],
                  rules.get("security_flags_note", ""))
    if "security_flags_max" in rules:
        check_max("security_flags", security_flags, rules["security_flags_max"])
    if "issues_min" in rules:
        check_min("issues", issues, rules["issues_min"])
    if "issues_max" in rules:
        check_max("issues", issues, rules["issues_max"])
    if "warnings_min" in rules:
        check_min("warnings", warnings, rules["warnings_min"])
    if "warnings_max" in rules:
        check_max("warnings", warnings, rules["warnings_max"])

    for line in passed:
        print(line)
    for line in failed:
      

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/self-audit/scripts/assert_audit.py -->
#!/usr/bin/env python3
"""
assert_audit.py (CLI)
=====================================

Purpose:
    Programmatic regression assertions for self-audit scanner results.
    Reads the JSON output of inventory_plugin.py and asserts expected counts 
    for known test fixtures. Exits non-zero on assertion failure.

Layer: Investigate / Audit / Regression

Usage Examples:
    python3 assert_audit.py --fixture flawed --json-output scan_output.json
    python3 assert_audit.py --fixture gold --json-output scan_output.json
    python3 assert_audit.py --fixture self --json-output scan_output.json

Supported Object Types:
    Scanner auditing reports.

CLI Arguments:
    --fixture: Which fixture to assert (flawed | gold | self) (Required)
    --json-output: Path to the JSON scanner output file (Required)

I

*(combined content truncated)*

## See Also

- [[maximum-raw-content-characters-kept-per-record-before-truncation]]
- [[premium-dispatch-claude-sonnet-46-for-complex-multi-file-generation-charged-per-request-batch-everything]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/assert_audit.py`
- **Indexed:** 2026-04-27T05:21:04.345001+00:00
