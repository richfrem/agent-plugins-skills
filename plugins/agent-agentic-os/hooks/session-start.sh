#!/usr/bin/env bash
# SessionStart hook wrapper for agent-agentic-os
#
# Purpose:
#   POSIX-safe wrapper that detects platform, applies a --resume guard to
#   avoid double-injection on resumed sessions, then invokes update_memory.py
#   with the resolved PLUGIN_ROOT.
#
# Platform detection:
#   Cursor sets CURSOR_PLUGIN_ROOT (may also set CLAUDE_PLUGIN_ROOT).
#   Claude Code sets CLAUDE_PLUGIN_ROOT only.
#   Both cases are handled; unknown platforms fall back to CLAUDE_PLUGIN_ROOT logic.
#
# --resume guard:
#   If events.jsonl was written within the last 60 seconds, this session is
#   almost certainly a --resume or compact-triggered restart. Skip the heavy
#   update_memory.py work (memory injection already happened in the prior
#   session start) and exit cleanly.
#
# printf vs heredoc:
#   Uses printf throughout to avoid a bash 5.3+ bug where heredoc variable
#   expansion hangs when content exceeds ~512 bytes.
#   See: https://github.com/obra/superpowers/issues/571
#
# Usage:
#   Called automatically by Claude Code / Cursor hooks system.
#   Receives hook event JSON on stdin.

set -euo pipefail

# ── Resolve paths ────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Prefer CLAUDE_PLUGIN_ROOT / CURSOR_PLUGIN_ROOT from env if set
# (they point to the installed skill root, not the source tree)
RESOLVED_ROOT="${CURSOR_PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT:-${PLUGIN_ROOT}}}"

# ── Detect project dir ───────────────────────────────────────────────────────

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# ── --resume guard ───────────────────────────────────────────────────────────
# If events.jsonl was modified within the last 60 seconds this is a resume
# (compact, /clear, or crash-restart) not a fresh session. Skip injection.

EVENTS_FILE="${PROJECT_DIR}/context/events.jsonl"
if [ -f "$EVENTS_FILE" ]; then
    # macOS: stat -f %m; Linux: stat -c %Y
    if stat -f %m "$EVENTS_FILE" > /dev/null 2>&1; then
        FILE_MTIME=$(stat -f %m "$EVENTS_FILE")
    else
        FILE_MTIME=$(stat -c %Y "$EVENTS_FILE")
    fi
    NOW=$(date +%s)
    AGE=$(( NOW - FILE_MTIME ))
    if [ "$AGE" -lt 60 ]; then
        # Resume detected - exit cleanly without re-injecting
        printf '{"continue": true}\n'
        exit 0
    fi
fi

# ── Invoke Python orchestrator ───────────────────────────────────────────────
# Pass RESOLVED_ROOT so update_memory.py can locate skill files regardless
# of whether we are running from the source tree or an installed .agents/ path.

# Read stdin payload (hook event data) and forward to Python
HOOK_PAYLOAD="$(cat)"

# Platform context for Python layer
export AGENTIC_OS_PLATFORM="${CURSOR_PLUGIN_ROOT:+cursor}"
AGENTIC_OS_PLATFORM="${AGENTIC_OS_PLATFORM:-${CLAUDE_PLUGIN_ROOT:+claude}}"
export AGENTIC_OS_PLATFORM="${AGENTIC_OS_PLATFORM:-unknown}"

# Invoke update_memory.py with payload; it handles event logging and memory
PYTHON_OUT=$(printf '%s' "$HOOK_PAYLOAD" | python3 "${RESOLVED_ROOT}/hooks/update_memory.py" "$HOOK_PAYLOAD" 2>/dev/null || true)

# ── Emit platform-correct JSON output ────────────────────────────────────────
# Claude Code reads hookSpecificOutput.additionalContext
# Cursor reads additional_context
# Both: use printf to avoid bash 5.3+ heredoc hang bug

if [ -n "${CURSOR_PLUGIN_ROOT:-}" ]; then
    # Cursor - emit additional_context
    if [ -n "$PYTHON_OUT" ]; then
        printf '%s\n' "$PYTHON_OUT"
    else
        printf '{"continue": true}\n'
    fi
else
    # Claude Code (or unknown) - emit hookSpecificOutput if Python produced output
    if [ -n "$PYTHON_OUT" ]; then
        printf '%s\n' "$PYTHON_OUT"
    else
        printf '{"continue": true}\n'
    fi
fi

exit 0
