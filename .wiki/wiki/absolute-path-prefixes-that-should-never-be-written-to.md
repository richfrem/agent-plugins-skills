---
concept: absolute-path-prefixes-that-should-never-be-written-to
source: plugin-code
source_file: agent-scaffolders/scripts/validate_write.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.843914+00:00
cluster: file_path
content_hash: 5a224e2ba4a7a470
---

# Absolute path prefixes that should never be written to

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
validate_write.py
=====================================

Purpose:
    PreToolUse hook that validates Write/Edit tool operations before they
    execute. Reads hook JSON from stdin, extracts tool_input.file_path, and
    blocks writes that target path-traversal sequences, system directories
    (/etc/, /sys/, /usr/), or sensitive file patterns (.env, secret,
    credentials).

Layer: Codify

Usage:
    echo '<pretooluse-json>' | python validate_write.py
"""
import sys
import json

# Absolute path prefixes that should never be written to
_SYSTEM_DIRS: tuple = ("/etc/", "/sys/", "/usr/")

# Substrings in a filename that flag it as sensitive
_SENSITIVE_PATTERNS: tuple = (".env", "secret", "credentials")


# Emit a JSON hook decision to stderr and exit with the given code
def _respond(decision: str, message: str, exit_code: int) -> None:
    """
    Write a hook decision JSON payload to stderr and terminate.

    Args:
        decision: One of "deny" or "ask" — maps to permissionDecision.
        message: Human-readable systemMessage for the agent.
        exit_code: Process exit code (should be 2 for block/ask).

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


# Entry point: read PreToolUse hook payload from stdin and validate the file path
def main() -> None:
    """
    Validate a file write operation from the PreToolUse hook payload.

    Reads JSON from stdin, extracts `tool_input.file_path`, and checks for
    path traversal, system directory writes, and sensitive file patterns.

    Raises:
        SystemExit: Code 0 to approve; code 2 to block or request confirmation.
    """
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # Malformed input — safe to approve

    file_path: str = (data.get("tool_input") or {}).get("file_path", "")

    if not file_path:
        print('{"continue": true}')
        sys.exit(0)

    # Block path traversal
    if ".." in file_path:
        _respond("deny", f"Path traversal detected in: {file_path}", 2)

    # Block system directories
    if any(file_path.startswith(d) for d in _SYSTEM_DIRS):
        _respond("deny", f"Cannot write to system directory: {file_path}", 2)

    # Escalate sensitive files
    if any(pat in file_path for pat in _SENSITIVE_PATTERNS):
        _respond("ask", f"Writing to potentially sensitive file: {file_path}", 2)

    # Approve
    sys.exit(0)


if __name__ == "__main__":
    main()


## See Also

- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[atomically-replace-an-existing-path-with-a-new-symlink-pointing-to-src]]
- [[ensure-unicode-output-works-on-windows-terminals-that-default-to-cp1252]]
- [[keys-that-cannot-be-overwritten-via-state-update-prompt-injection-defense]]
- [[match-pythonexecution-paths-that-are-hardcoded-to-the-repo-root-plugins-folder]]
- [[track-real-filesystem-paths-first-encountered-rel-path-to-avoid-archiving-duplicate-symlinked-content]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/validate_write.py`
- **Indexed:** 2026-04-27T05:21:03.843914+00:00
