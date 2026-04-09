#!/usr/bin/env python3
"""
validate_hook_schema.py
=====================================

Purpose:
    Validates a Claude Code hooks.json file for JSON syntax, valid event names,
    matcher and hooks array presence, hook type validity (command/prompt),
    hardcoded absolute paths, and timeout range constraints.

Layer: Investigate

Usage:
    python3 validate_hook_schema.py <path/to/hooks.json>
"""
import sys
import os
import json

_SEPARATOR = "━" * 40

# All event types recognised by the Claude Code hook system
VALID_EVENTS = frozenset({
    "PreToolUse", "PostToolUse", "UserPromptSubmit", "Stop",
    "SubagentStop", "SessionStart", "SessionEnd", "PreCompact", "Notification",
})
# Hook types that accept prompt-based handlers (not all events support them)
PROMPT_SUPPORTED_EVENTS = frozenset({"Stop", "SubagentStop", "UserPromptSubmit", "PreToolUse"})


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

# Validate a single hook object within a hook-entry's hooks array
def _check_hook(event: str, i: int, j: int, hook: dict, errors: list, warnings: list) -> None:
    """
    Validate one hook object and append issue strings to errors/warnings.

    Args:
        event: Parent event name (e.g. "PreToolUse").
        i: Index of the hook entry within the event list.
        j: Index of this hook within the hook entry's `hooks` array.
        hook: The hook dict to validate.
        errors: Mutable list; error strings are appended here.
        warnings: Mutable list; warning strings are appended here.
    """
    prefix = f"{event}[{i}].hooks[{j}]"
    hook_type = hook.get("type")

    if not hook_type:
        errors.append(f"❌ {prefix}: Missing 'type' field")
        return

    if hook_type not in ("command", "prompt"):
        errors.append(f"❌ {prefix}: Invalid type '{hook_type}' (must be 'command' or 'prompt')")
        return

    if hook_type == "command":
        command = hook.get("command")
        if not command:
            errors.append(f"❌ {prefix}: Command hooks must have 'command' field")
        elif command.startswith("/") and "${CLAUDE_PLUGIN_ROOT}" not in command:
            warnings.append(
                f"⚠️  {prefix}: Hardcoded absolute path detected. "
                "Consider using ${CLAUDE_PLUGIN_ROOT}"
            )

    elif hook_type == "prompt":
        if not hook.get("prompt"):
            errors.append(f"❌ {prefix}: Prompt hooks must have 'prompt' field")
        if event not in PROMPT_SUPPORTED_EVENTS:
            warnings.append(
                f"⚠️  {prefix}: Prompt hooks may not be fully supported on {event} "
                "(best on Stop, SubagentStop, UserPromptSubmit, PreToolUse)"
            )

    # Timeout range check
    timeout = hook.get("timeout")
    if timeout is not None:
        if not isinstance(timeout, int):
            errors.append(f"❌ {prefix}: Timeout must be a number")
        elif timeout > 600:
            warnings.append(f"⚠️  {prefix}: Timeout {timeout}s is very high (max 600s)")
        elif timeout < 5:
            warnings.append(f"⚠️  {prefix}: Timeout {timeout}s is very low")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

# Entry point: validate hooks.json and report all issues
def main() -> None:
    """
    Validate a hooks.json file and print a structured report.

    Raises:
        SystemExit: Code 0 on pass (with or without warnings); code 1 on errors.
    """
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path/to/hooks.json>")
        print()
        print("Validates hook configuration file for:")
        for item in (
            "Valid JSON syntax",
            "Required fields",
            "Hook type validity",
            "Matcher patterns",
            "Timeout ranges",
        ):
            print(f"  - {item}")
        sys.exit(1)

    hooks_file = sys.argv[1]

    if not os.path.isfile(hooks_file):
        print(f"❌ Error: File not found: {hooks_file}")
        sys.exit(1)

    print(f"🔍 Validating hooks configuration: {hooks_file}")
    print()

    # Check 1: Valid JSON
    print("Checking JSON syntax...")
    try:
        with open(hooks_file) as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        print(f"❌ Invalid JSON syntax: {exc}")
        sys.exit(1)
    print("✅ Valid JSON")

    # Check 1b: Detect literal \n chars (invalid JSON encoding from Python json.dump)
    with open(hooks_file, encoding="utf-8") as raw_fh:
        raw_content = raw_fh.read()
    if r"\n" in raw_content and "\n" not in raw_content:
        print("❌ File contains literal \\n characters instead of real newlines.")
        print("   Run fix_plugin_load_errors.py to auto-fix.")
        sys.exit(1)

    # Check 1c: Root must be an object, not an array
    if isinstance(data, list):
        print("❌ Root must be an object, not an array. Expected: {\"hooks\": {}}")
        sys.exit(1)

    # Unwrap nested { "hooks": {...} } format (canonical Claude Code format)
    # Old flat format had events at root; new format wraps them under "hooks" key.
    if "hooks" in data and isinstance(data.get("hooks"), dict):
        unwrapped = data["hooks"]
        if not unwrapped:
            print("✅ Empty hooks configuration: {\"hooks\": {}}")
            sys.exit(0)
        data = unwrapped
    elif len(data) == 0:
        print("⚠️  Empty {} detected. Preferred form is {\"hooks\": {}}")
        sys.exit(0)

    # Check 2: Root structure - event name validity
    print()
    print("Checking root structure...")
    for event in data:
        if event not in VALID_EVENTS:
            print(f"⚠️  Unknown event type: {event}")
    print("✅ Root structure valid")

    # Check 3: Validate individual hooks
    print()
    print("Validating individual hooks...")
    errors: list = []
    warnings: list = []

    for event, hook_list in data.items():
        if not isinstance(hook_list, list):
            errors.append(
                f"❌ {event}: Value must be an array of hook entries, got {type(hook_list).__name__}. "
                "Check for old flat format: {\"EventName\": {\"command\": \"...\"}} — "
                "wrap in {\"hooks\": {\"EventName\": [{\"matcher\": \"\", \"hooks\": [{...}]}]}}"
            )
            continue
        for i, entry in enumerate(hook_list):
            if not entry.get("matcher"):
                errors.append(f"❌ {event}[{i}]: Missing 'matcher' field")
                continue
            hooks = entry.get("hooks")
            if not hooks:
                errors.append(f"❌ {event}[{i}]: Missing 'hooks' array")
                continue
            for j, hook in enumerate(hooks):
                _check_hook(event, i, j, hook, errors, warnings)

    for msg in errors + warnings:
        print(msg)

    print()
    print(_SEPARATOR)

    if not errors and not warnings:
        print("✅ All checks passed!")
        sys.exit(0)
    if not errors:
        print(f"⚠️  Validation passed with {len(warnings)} warning(s)")
        sys.exit(0)
    print(f"❌ Validation failed with {len(errors)} error(s) and {len(warnings)} warning(s)")
    sys.exit(1)


if __name__ == "__main__":
    main()
