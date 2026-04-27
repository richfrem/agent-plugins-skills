---
concept: separator-line-used-in-report-output
source: plugin-code
source_file: agent-scaffolders/scripts/hook_linter.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.831679+00:00
cluster: print
content_hash: 63e15a3faf6aa78d
---

# Separator line used in report output

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
        p

*(content truncated)*

## See Also

- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[broken-symlinks-repair-report]]
- [[check-all-text-files-in-skill-for-regex-py-mentions]]
- [[ensure-unicode-output-works-on-windows]]
- [[ensure-unicode-output-works-on-windows-terminals-that-default-to-cp1252]]
- [[files-to-exclude-from-output-listings]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/hook_linter.py`
- **Indexed:** 2026-04-27T05:21:03.831679+00:00
