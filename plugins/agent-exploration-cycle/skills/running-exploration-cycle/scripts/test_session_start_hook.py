#!/usr/bin/env python3
"""
test_session_start_hook.py
=====================================
Purpose:
    Regression test for hooks/session_start.py after the skill consolidation: the SessionStart
    hook must inject the real bootstrap constraints (the mandatory state gate), not the one-line
    fallback it prints when the bootstrap file is missing, and must surface an active session.

Key Input Dependencies:
    - ../../../hooks/session_start.py (invoked as a subprocess)
    - references/using-exploration-cycle.md (the bootstrap text)
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[3] / "hooks" / "session_start.py"
FALLBACK = "The agent-exploration-cycle is active. Follow the exploration-workflow."


def _run_hook(project_dir: Path) -> str:
    """Run the SessionStart hook for a project directory and return the injected additionalContext string."""
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    env.pop("COPILOT_CLI", None)
    env.pop("CURSOR_PLUGIN_ROOT", None)
    proc = subprocess.run([sys.executable, str(HOOK)], cwd=str(project_dir), env=env,
                          capture_output=True, text=True, timeout=20)
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    return payload["hookSpecificOutput"]["additionalContext"]


def test_hook_injects_real_bootstrap_not_fallback(tmp_path):
    """The hook must inject the bootstrap constraints, not the stub fallback, and not the absorbed-skill header."""
    context = _run_hook(tmp_path)
    assert FALLBACK not in context, "hook fell back to the stub: bootstrap file path is stale"
    assert "Mandatory State Gate" in context
    assert "Database Sovereignty" in context
    assert "Original trigger description" not in context, "absorbed-skill header must not be injected"


def test_hook_reports_active_session(tmp_path):
    """An in-progress dashboard must surface its current phase in the injected context."""
    (tmp_path / "exploration").mkdir()
    (tmp_path / "exploration" / "exploration-dashboard.md").write_text(
        "# Exploration Session Dashboard\n\n**Session:** Demo\n**Status:** In Progress\n"
        "**Current Phase:** Phase 2 — Visual Blueprinting\n", encoding="utf-8")
    context = _run_hook(tmp_path)
    assert "Phase 2" in context
    assert "active exploration session" in context.lower()
