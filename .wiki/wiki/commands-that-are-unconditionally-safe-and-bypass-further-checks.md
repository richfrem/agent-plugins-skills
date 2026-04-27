---
concept: commands-that-are-unconditionally-safe-and-bypass-further-checks
source: plugin-code
source_file: agent-scaffolders/scripts/validate_bash.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.842113+00:00
cluster: command
content_hash: 12af8ed8285bd177
---

# Commands that are unconditionally safe and bypass further checks

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
validate_bash.py
=====================================

Purpose:
    PreToolUse hook that validates Bash tool commands before execution.
    Reads hook JSON from stdin, extracts tool_input.command, checks for
    safe quick-approve patterns, and blocks or escalates dangerous commands
    (rm -rf, dd, mkfs, sudo) by emitting JSON decision output to stderr.

Layer: Codify

Usage:
    echo '<pretooluse-json>' | python validate_bash.py
"""
import sys
import json
import re

# Commands that are unconditionally safe and bypass further checks
_SAFE_PATTERN = re.compile(r"^(ls|pwd|echo|date|whoami)(\s|$)")

# Patterns for commands that should be outright denied
_DENY_PATTERNS: list = [
    ("rm -rf", "Dangerous command detected: rm -rf"),
    ("rm -fr", "Dangerous command detected: rm -rf"),
    ("dd if=", "Dangerous system operation detected"),
    ("mkfs", "Dangerous system operation detected"),
    ("> /dev/", "Dangerous system operation detected"),
]


# Emit a JSON hook decision to stderr and exit with the given code
def _respond(decision: str, message: str, exit_code: int) -> None:
    """
    Write a hook decision JSON payload to stderr and terminate.

    Args:
        decision: One of "deny" or "ask" — maps to permissionDecision.
        message: Human-readable systemMessage for the agent.
        exit_code: Process exit code (should be 2 for hook block/ask).

    Raises:
        SystemExit: Always raises with exit_code.
    """
    json.dump(
        {"hookSpecificOutput": {"permissionDecision": decision},
         "systemMessage": message},
        sys.stderr,
    )
    sys.stderr.write("\n")
    sys.exit(exit_code)


# Entry point: read PreToolUse hook payload from stdin and validate the command
def main() -> None:
    """
    Validate a Bash command from the PreToolUse hook payload.

    Reads JSON from stdin, extracts `tool_input.command`, and applies a
    layered set of pattern checks to approve, deny, or escalate the command.

    Raises:
        SystemExit: Code 0 to approve; code 2 to block or request confirmation.
    """
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # Malformed input — safe to approve

    command: str = (data.get("tool_input") or {}).get("command", "")

    if not command:
        print('{"continue": true}')
        sys.exit(0)

    # Fast-pass known-safe commands
    if _SAFE_PATTERN.match(command):
        sys.exit(0)

    # Deny destructive patterns
    for pattern, message in _DENY_PATTERNS:
        if pattern in command:
            _respond("deny", message, 2)

    # Escalate privilege escalation attempts
    if command.startswith("sudo") or command.startswith("su"):
        _respond("ask", "Command requires elevated privileges", 2)

    # Approve
    sys.exit(0)


if __name__ == "__main__":
    main()


## See Also

- [[match-pythonexecution-paths-that-are-hardcoded-to-the-repo-root-plugins-folder]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]
- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[absolute-path-prefixes-that-should-never-be-written-to]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[capture-optional-leading-so-image-links-are-preserved-correctly]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/validate_bash.py`
- **Indexed:** 2026-04-27T05:21:03.842113+00:00
