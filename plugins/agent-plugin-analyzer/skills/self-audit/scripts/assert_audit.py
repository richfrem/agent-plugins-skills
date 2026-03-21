"""
assert_audit.py — Programmatic regression assertions for self-audit scanner results.

Reads the JSON output of inventory_plugin.py and asserts expected counts for known
test fixtures (gold-standard, flawed, self). Exits non-zero on assertion failure.

Usage:
    python3 assert_audit.py --fixture flawed --json-output scan_output.json
    python3 assert_audit.py --fixture gold --json-output scan_output.json
    python3 assert_audit.py --fixture self --json-output scan_output.json
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
        print(line)

    if failed:
        print(f"\nAUDIT REGRESSION ({fixture}): {len(failed)} assertion(s) failed")
        return False

    print(f"\nAUDIT PASSED ({fixture}): {len(passed)} assertion(s) passed")
    return True


def main() -> None:
    """Entry point for CLI invocation."""
    parser = argparse.ArgumentParser(description="Regression assertions for self-audit scanner output")
    parser.add_argument("--fixture", required=True, choices=list(ASSERTIONS),
                        help="Which fixture to assert against (flawed|gold|self)")
    parser.add_argument("--json-output", required=True,
                        help="Path to the JSON output file from inventory_plugin.py")
    args = parser.parse_args()

    data = load_json(args.json_output)
    ok = assert_fixture(args.fixture, data)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
