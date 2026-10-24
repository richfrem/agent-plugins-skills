"""
control_plane_path.py - find the running-control-plane skill that sits beside this one.

Purpose:
    The setup scripts use the control-plane package (identity, SSH signing, database bootstrap, git-guard
    wiring). That package lives in the sibling skill `running-control-plane`. APM installs skills side by
    side in one folder (project `.claude/skills`, `.agents/skills`, or a user-level folder), and the source
    tree keeps them side by side under one plugin, so the sibling is always `<this skill>/../running-control-plane`.

Key Functions:
    - control_scripts_dir() -- the sibling skill's scripts folder, or None
    - ensure_control_plane_on_path() -- put it on sys.path, or exit with an instruction
"""

import sys
from pathlib import Path

CONTROL_SKILL = "running-control-plane"


def control_scripts_dir():
    """The sibling skill's scripts folder, or None when it is not installed beside this skill."""
    candidate = Path(__file__).resolve().parent.parent.parent / CONTROL_SKILL / "scripts"
    return candidate if (candidate / "control_plane").is_dir() else None


def ensure_control_plane_on_path() -> Path:
    """Make `control_plane`, `agent_control` and `control_plane_hooks` importable; exit clearly if missing."""
    scripts = control_scripts_dir()
    if scripts is None:
        sys.exit(
            f"ERROR: the {CONTROL_SKILL} skill was not found beside setting-up-agentic-os "
            f"({Path(__file__).resolve().parent.parent.parent}).\n"
            f"The setup scripts use its control_plane package. Install it (apm install) and retry."
        )
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    return scripts
