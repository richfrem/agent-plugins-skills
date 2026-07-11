#!/usr/bin/env python3
"""
session_start.py
=====================================
Purpose:
    Hook executed at session start. Injects the bootstrap constraints and
    active session context directly into the LLM system prompt.

Key Input Dependencies:
    - skills/using-exploration-cycle/SKILL.md (bootstrap constraints text)
    - exploration/exploration-dashboard.md (active session status, optional)
    - CLAUDE_PROJECT_DIR, COPILOT_CLI, CURSOR_PLUGIN_ROOT environment variables
      (used to detect which IDE harness output format to emit)
"""
import os
import sys
import json
from pathlib import Path

def _load_bootstrap_content(plugin_root: Path) -> str:
    """Read the using-exploration-cycle SKILL.md, or return a fallback string if missing."""
    bootstrap_path = plugin_root / "skills" / "using-exploration-cycle" / "SKILL.md"
    if bootstrap_path.exists():
        return bootstrap_path.read_text(encoding="utf-8")
    return "The exploration-cycle-plugin is active. Follow the exploration-workflow."


def _build_session_context(bootstrap_content: str, dashboard_path: Path) -> str:
    """Build the session-start context block, including active dashboard status if present."""
    session_context = f"<EXTREMELY_IMPORTANT>\nYou have the exploration-cycle-plugin installed.\n\n{bootstrap_content}\n"

    # Check active dashboard status with defensive parsing
    if dashboard_path.exists():
        try:
            dashboard_content = dashboard_path.read_text(encoding="utf-8")
            lines = dashboard_content.splitlines()
            phase_line = next((line for line in lines if "**Current Phase:**" in line), "**Current Phase:** Phase 1 — Problem Framing")
            status_line = next((line for line in lines if "**Status:**" in line), "**Status:** In Progress")

            session_context += "\n## Active Workspace State\n"
            session_context += f"- {phase_line}\n"
            session_context += f"- {status_line}\n"
            session_context += "- An active exploration session is detected on disk. You MUST orient the user around this active session and run the exploration-workflow.\n"
        except Exception:
            session_context += "\n- An active exploration session exists but the dashboard is corrupt or parsing failed.\n"

    session_context += "</EXTREMELY_IMPORTANT>"
    return session_context


def _build_output_data(session_context: str) -> dict:
    """Build the hook output payload in the format expected by the active IDE harness."""
    # Deduplicate to prevent double injection in Claude Code
    is_claude_code = "CLAUDE_PROJECT_DIR" in os.environ and "COPILOT_CLI" not in os.environ and "CURSOR_PLUGIN_ROOT" not in os.environ
    is_copilot = "COPILOT_CLI" in os.environ
    is_cursor = "CURSOR_PLUGIN_ROOT" in os.environ

    if is_claude_code:
        return {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": session_context
            }
        }
    if is_copilot:
        return {"additionalContext": session_context}
    if is_cursor:
        return {"additional_context": session_context}
    # Fallback for general or unknown runners (like terminal or custom runners)
    return {
        "additionalContext": session_context,
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": session_context
        }
    }


def main() -> None:
    """Inject bootstrap constraints and active session context into the LLM system prompt."""
    try:
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
        plugin_root = Path(__file__).resolve().parents[1]
        dashboard_path = Path(project_dir) / "exploration" / "exploration-dashboard.md"

        bootstrap_content = _load_bootstrap_content(plugin_root)
        session_context = _build_session_context(bootstrap_content, dashboard_path)
        output_data = _build_output_data(session_context)

        # Output as single-line JSON to ensure clean parsing by shell harnesses
        sys.stdout.write(json.dumps(output_data) + "\n")
        sys.stdout.flush()

    except Exception as e:
        # Fallback behavior when injection fails
        sys.stderr.write(f"[exploration-cycle] Warning: SessionStart hook context injection failed: {str(e)}\n")
        sys.exit(0) # Hooks must fail silently to avoid crashing startup

if __name__ == "__main__":
    main()
