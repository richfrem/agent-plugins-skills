#!/usr/bin/env python
"""
hook_linter.py
=====================================

Purpose:
    Lints Claude Code / APM hook scripts (Python and Bash) against best-practice
    checks including shebang presence, safety flags, stdin reading, hardcoded
    paths, harness-neutral state paths (SF-11), exit codes, and long-running
    patterns. Exits non-zero if any script has errors (warnings are non-fatal).

Layer: Investigate

Usage:
    python hook_linter.py <hook-script> [hook-script2 ...]
    python hook_linter.py plugins/<plugin>/.apm/hooks/validate-bash.py

Key Input Dependencies:
    - Hook script file path(s) or directory passed via CLI arguments
    - os, re, pathlib (standard library)
"""
import os
import re
import sys
from pathlib import Path

# Separator line used in report output
_SEPARATOR = "━" * 40


def _is_python_script(script: str, lines: list[str]) -> bool:
    """Return True if the hook script is a Python script."""
    if script.endswith(".py"):
        return True
    first_line = lines[0].rstrip() if lines else ""
    return "python" in first_line


# Checks 1-2: executable bit and shebang presence
def _check_executable_and_shebang(script: str, lines: list) -> tuple:
    """Checks 1-2: executable bit and shebang presence. Returns (errors, warnings)."""
    warnings = 0
    errors = 0

    if not os.access(script, os.X_OK):
        print(f"⚠️  Not executable (chmod +x {script})")
        warnings += 1

    first_line = lines[0].rstrip() if lines else ""
    if not first_line.startswith("#!"):
        print("❌ Missing shebang (#!/usr/bin/env python3 or #!/bin/bash)")
        errors += 1

    return errors, warnings


# Checks 3-5: safety flag, stdin reading, JSON parsing
def _check_safety_and_input(content: str, is_python: bool) -> int:
    """Checks 3-5: safety flags, stdin reading, JSON parsing. Returns warnings."""
    warnings = 0

    if is_python:
        if not re.search(r"sys\.stdin|input\(|fileinput", content):
            print("💡 Tip: Hook does not read stdin payload (sys.stdin)")
        return warnings

    if "set -euo pipefail" not in content:
        print("⚠️  Missing 'set -euo pipefail' (recommended for safety)")
        warnings += 1

    if not re.search(r"\bcat\b|\bread\b", content):
        print("⚠️  Doesn't appear to read input from stdin")
        warnings += 1

    if re.search(r"\btool_input\b|\btool_name\b", content) and "jq" not in content:
        print("⚠️  Parses hook input but doesn't use jq")
        warnings += 1

    return warnings


# Checks 6-8: unquoted variables, hardcoded paths, SF-11 harness-neutral paths
def _check_quoting_and_paths(content: str, non_comment_content: str, is_python: bool) -> int:
    """Checks 6-8: unquoted variables, hardcoded paths, SF-11 harness-neutral paths. Returns warnings."""
    warnings = 0

    if not is_python and re.search(r'\$[A-Za-z_][A-Za-z0-9_]*[^"]', non_comment_content):
        print("⚠️  Potentially unquoted variables detected (injection risk)")
        print('   Always use double quotes: "$variable" not $variable')
        warnings += 1

    if re.search(r'^[^#]*/home/|^[^#]*/Users/|^[^#]*/opt/', content, re.MULTILINE):
        print("⚠️  Hardcoded absolute machine paths detected")
        print("   Use Path(__file__).resolve() or $CLAUDE_PROJECT_DIR / $CLAUDE_PLUGIN_ROOT")
        warnings += 1

    # SF-11: Hook scripts run under every target harness (claude, copilot, codex).
    # They must not hardcode .claude/ or .agents/ paths for script location or project state.
    if re.search(r"""['"][^'"]*(?:\.claude/|\.agents/)[^'"]*['"]""", non_comment_content):
        print("⚠️  SF-11 (hook_script_harness_path): Hardcoded '.claude/' or '.agents/' path detected")
        print("   Use Path(__file__).resolve() for sibling files and 'context/' for project state")
        warnings += 1

    if not is_python and "CLAUDE_PLUGIN_ROOT" not in content and "CLAUDE_PROJECT_DIR" not in content:
        print("💡 Tip: Use $CLAUDE_PLUGIN_ROOT for plugin-relative paths")

    return warnings


# Checks 9-10: explicit exit codes, JSON decision output tip
def _check_exit_and_output(content: str, is_python: bool) -> int:
    """Checks 9-10: explicit exit codes, JSON decision output tip. Returns warnings."""
    warnings = 0

    if is_python:
        has_exit = bool(re.search(r"sys\.exit\(|return\s+[012]\b|raise\s+SystemExit", content))
    else:
        has_exit = "exit 0" in content or "exit 2" in content

    if not has_exit:
        print("⚠️  No explicit exit codes (should exit 0 or 2)")
        warnings += 1

    if re.search(r"\bPreToolUse\b|\bStop\b", content):
        if "permissionDecision" not in content and '"decision"' not in content:
            print("💡 Tip: PreToolUse/Stop hooks should output decision JSON")

    return warnings


# Checks 11-13: long-running patterns, stderr error messages, input validation tip
def _check_runtime_and_validation(content: str, non_comment_content: str, is_python: bool) -> int:
    """Checks 11-13: long-running patterns, stderr errors, input validation tip. Returns warnings."""
    warnings = 0

    if re.search(r"sleep [0-9]{3,}|time\.sleep\([0-9]{3,}|while true|while True", non_comment_content):
        print("⚠️  Potentially long-running code detected")
        print("   Hooks should complete quickly (< 60s)")
        warnings += 1

    if not is_python and re.search(r'echo.*".*[Ee]rror|[Dd]enied', content) and ">&2" not in content:
        print("⚠️  Error messages should be written to stderr (>&2)")
        warnings += 1

    if not is_python and not re.search(r"if.*empty|if.*null|if.*-z", content):
        print("💡 Tip: Consider validating input fields aren't empty")

    return warnings


def check_script(script: str) -> bool:
    """
    Lint a single hook script file against best-practice checks.

    Args:
        script: Path to the script file to lint.

    Returns:
        True if no errors were found (warnings are tolerated); False otherwise.
    """
    print(f"🔍 Linting: {script}")
    print()

    if not os.path.isfile(script):
        print("❌ Error: File not found")
        return False

    with open(script, encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()

    content = "".join(lines)
    non_comment_content = "".join(
        ln for ln in lines if not ln.strip().startswith("#")
    )
    is_python = _is_python_script(script, lines)

    errors, warnings = _check_executable_and_shebang(script, lines)
    warnings += _check_safety_and_input(content, is_python)
    warnings += _check_quoting_and_paths(content, non_comment_content, is_python)
    warnings += _check_exit_and_output(content, is_python)
    warnings += _check_runtime_and_validation(content, non_comment_content, is_python)

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


def _expand_targets(raw_args: list[str]) -> list[str]:
    """Expand any directory arguments into their contained .py and .sh hook scripts."""
    scripts: list[str] = []
    for arg in raw_args:
        p = Path(arg)
        if p.is_dir():
            for ext in ("*.py", "*.sh"):
                scripts.extend(str(f) for f in sorted(p.glob(ext)))
        else:
            scripts.append(arg)
    return scripts


def main() -> None:
    """Lint all provided hook script files and exit with aggregate pass/fail."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <hook-script-or-dir> [hook-script2 ...]")
        print()
        print("Checks hook scripts for:")
        for check in (
            "Shebang presence",
            "Safety flags / stdin reading",
            "Proper error handling",
            "Variable quoting",
            "Exit code usage",
            "Hardcoded machine paths",
            "SF-11 harness-neutral paths (no hardcoded .claude/ or .agents/)",
            "Timeout considerations",
        ):
            print(f"  - {check}")
        sys.exit(1)

    print("🔎 Hook Script Linter")
    print(_SEPARATOR)
    print()

    targets = _expand_targets(sys.argv[1:])
    if not targets:
        print("✅ No hook scripts found to lint")
        sys.exit(0)

    total_errors = 0
    for script in targets:
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
