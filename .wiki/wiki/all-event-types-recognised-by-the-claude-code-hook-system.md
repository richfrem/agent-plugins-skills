---
concept: all-event-types-recognised-by-the-claude-code-hook-system
source: plugin-code
source_file: agent-scaffolders/scripts/validate_hook_schema.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.842838+00:00
cluster: timeout
content_hash: b29b340cc90df28b
---

# All event types recognised by the Claude Code hook system

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
validate_hook_schema.py
=====================================

Purpose:
    Validates a Claude Code hooks.json file for JSON syntax, valid event names,
    matcher and hooks array presence, hook type validity (command/prompt),
    hardcoded absolute paths, and timeout range constraints.

Layer: Investigate

Usage:
    pythonvalidate_hook_schema.py <path/to/hooks.json>
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

*(content truncated)*

## See Also

- [[sample-payloads-keyed-by-claude-code-event-type-name]]
- [[1-parse-the-hook-payload]]
- [[1-basic-summarize-all-documents]]
- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]
- [[add-the-scripts-directory-so-we-can-import-rlm-config]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/validate_hook_schema.py`
- **Indexed:** 2026-04-27T05:21:03.842838+00:00
