#!/usr/bin/env python
"""
hook_linter.py
=====================================

Purpose:
    Lints Claude Code hook scripts against 13 best-practice checks including
    shebang presence, `set -euo pipefail`, stdin reading, jq usage, unquoted
    variables, hardcoded paths, exit codes, long-running patterns, and more.
    Exits non-zero if any script has errors (warnings are non-fatal).

Layer: Investigate

Usage:
    python hook_linter.py <hook-script> [hook-script2 ...]
    python hook_linter.py hooks/validate-bash.py
"""
import sys
import os
import re

# Separator line used in report output
_SEPARATOR = "━" * 40


# ---------------------------------------------------------------------------
# Check helpers
# ---------------------------------------------------------------------------

# Run all 13 lint checks against a single hook script file
def check_script(script: str) -> bool:
    """
    Lint a single hook script file against 13 best-practice checks.

    Args:
        script: Path to the script file to lint.

    Returns:
        True if no errors were found (warnings are tolerated); False otherwise.
    """
    warnings = 0
    errors = 0

    print(f"🔍 Linting: {script}")
    print()

    if not os.path.isfile(script):
        print("❌ Error: File not found")
        return False

    # Check 1: Executable bit
    if not os.access(script, os.X_OK):
        print(f"⚠️  Not executable (chmod +x {script})")
        warnings += 1

    with open(script, errors="replace") as fh:
        lines = fh.readlines()

    content = "".join(lines)
    non_comment_content = "".join(
        ln for ln in lines if not ln.strip().startswith("#")
    )

    # Check 2: Shebang
    first_line = lines[0].rstrip() if lines else ""
    if not first_line.startswith("#!"):
        print("❌ Missing shebang (#!/bin/bash)")
        errors += 1

    # Check 3: set -euo pipefail
    if "set -euo pipefail" not in content:
        print("⚠️  Missing 'set -euo pipefail' (recommended for safety)")
        warnings += 1

    # Check 4: Reads from stdin
    if not re.search(r"\bcat\b|\bread\b", content):
        print("⚠️  Doesn't appear to read input from stdin")
        warnings += 1

    # Check 5: jq for JSON parsing
    if re.search(r"\btool_input\b|\btool_name\b", content) and "jq" not in content:
        print("⚠️  Parses hook input but doesn't use jq")
        warnings += 1

    # Check 6: Unquoted variables (injection risk)
    if re.search(r'\$[A-Za-z_][A-Za-z0-9_]*[^"]', non_comment_content):
        print('⚠️  Potentially unquoted variables detected (injection risk)')
        print('   Always use double quotes: "$variable" not $variable')
        warnings += 1

    # Check 7: Hardcoded absolute paths
    if re.search(r'^[^#]*/home/|^[^#]*/usr/|^[^#]*/opt/', content, re.MULTILINE):
        print("⚠️  Hardcoded absolute paths detected")
        print("   Use $CLAUDE_PROJECT_DIR or $CLAUDE_PLUGIN_ROOT")
        warnings += 1

    # Check 8: CLAUDE_PLUGIN_ROOT usage tip
    if "CLAUDE_PLUGIN_ROOT" not in content and "CLAUDE_PROJECT_DIR" not in content:
        print("💡 Tip: Use $CLAUDE_PLUGIN_ROOT for plugin-relative paths")

    # Check 9: Explicit exit codes
    if "exit 0" not in content and "exit 2" not in content:
        print("⚠️  No explicit exit codes (should exit 0 or 2)")
        warnings += 1

    # Check 10: JSON decision output for decision hooks
    if re.search(r"\bPreToolUse\b|\bStop\b", content):
        if "permissionDecision" not in content and '"decision"' not in content:
            print("💡 Tip: PreToolUse/Stop hooks should output decision JSON")

    # Check 11: Long-running patterns
    if re.search(r"sleep [0-9]{3,}|while true", non_comment_content):
        print("⚠️  Potentially long-running code detected")
        print("   Hooks should complete quickly (< 60s)")
        warnings += 1

    # Check 12: Error messages to stderr
    if re.search(r'echo.*".*[Ee]rror|[Dd]enied', content) and ">&2" not in content:
        print("⚠️  Error messages should be written to stderr (>&2)")
        warnings += 1

    # Check 13: Input validation
    if not re.search(r"if.*empty|if.*null|if.*-z", content):
        print("💡 Tip: Consider validating input fields aren't empty")

    print()
    print(_SEPARATOR)

    if errors == 0 and warnings == 0:
        print("✅ No issues found")
        return True
    if errors == 0:
        print(f"⚠️  Found {warnings} warning(s)")
        return True

    print(f"❌ Found {errors} error(s) and {warnings} warning(s)")
    return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

# Entry point: lint one or more hook script files and report aggregate result
def main() -> None:
    """
    Lint all provided hook script files and exit with aggregate pass/fail.

    Args are read from sys.argv (one or more script file paths).

    Raises:
        SystemExit: Code 0 if all scripts pass; code 1 if any have errors.
    """
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <hook-script> [hook-script2 ...]")
        print()
        print("Checks hook scripts for:")
        for check in (
            "Shebang presence",
            "set -euo pipefail usage",
            "Input reading from stdin",
            "Proper error handling",
            "Variable quoting",
            "Exit code usage",
            "Hardcoded paths",
            "Timeout considerations",
        ):
            print(f"  - {check}")
        sys.exit(1)

    print("🔎 Hook Script Linter")
    print(_SEPARATOR)
    print()

    total_errors = 0
    for script in sys.argv[1:]:
        if not check_script(script):
            total_errors += 1
        print()

    if total_errors == 0:
        print("✅ All scripts passed linting")
        sys.exit(0)

    print(f"❌ {total_errors} script(s) had errors")
    sys.exit(1)


if __name__ == "__main__":
    main()
