#!/usr/bin/env bash
# Closure guard stop hook — delegates to closure_guard.py
exec python3 "${CLAUDE_PLUGIN_ROOT}/scripts/closure_guard.py" "$@"
