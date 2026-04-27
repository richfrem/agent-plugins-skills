---
concept: install-from-the-local-repo-select-plugins-interactively
source: plugin-code
source_file: plugin-manager/scripts/plugin_add.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.027549+00:00
cluster: plugin
content_hash: 766469b010f2f9d7
---

# Install from the local repo (select plugins interactively)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

"""
Plugin Add (CLI)
================

Purpose:
    Interactive plugin installer with a multiselect TUI.
    Accepts a local path OR a GitHub owner/repo shorthand, clones into a
    temp directory if remote, discovers all plugins, lets the user select
    which to install, then runs plugin_installer.py for each.

    The interactive TUI design pattern (multiselect, arrow navigation, search,
    owner/repo GitHub shorthand, temp-clone-then-install flow) follows modern
    command-line interface best practices:
      https://github.com/vercel-labs/skills
      https://skills.sh
    This script re-implements those UX patterns in pure Python (stdlib only)
    for cross-platform compatibility and to operate at the plugin level
    (skills + agents + commands + hooks) rather than individual SKILL.md files.

Layer: Plugin Manager / Installation

Usage Examples:
    # Install from the local repo (select plugins interactively)
    python plugins/plugin-manager/scripts/plugin_add.py

    # Install from explicit local path (relative or absolute, Mac/Linux/Windows)
    python plugins/plugin-manager/scripts/plugin_add.py plugins/
    python plugins/plugin-manager/scripts/plugin_add.py plugins/agent-scaffolders
    python plugins/plugin-manager/scripts/plugin_add.py /Users/path/to/plugins
    python plugins/plugin-manager/scripts/plugin_add.py C:\\Users\\path\\to\\plugins

    # Install from a remote GitHub repo
    python plugins/plugin-manager/scripts/plugin_add.py richfrem/agent-plugins-skills

    # Install all plugins non-interactively
    python plugins/plugin-manager/scripts/plugin_add.py richfrem/agent-plugins-skills --all -y

    # Dry-run preview
    python plugins/plugin-manager/scripts/plugin_add.py --dry-run

CLI Arguments:
    source          GitHub owner/repo OR local path (optional; defaults to cwd)
    --all           Select all discovered plugins without prompting
    -y / --yes      Skip confirmation prompts
    --dry-run       Preview actions without writing files
    --install-rules Also install rules into CLAUDE.md

Script Dependencies:
    os, sys, argparse, subprocess, shutil, tempfile, json, pathlib
"""

import os
import sys
import argparse
import subprocess
import shutil
import tempfile
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# UTF-8 safety on Windows
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
INSTALLER_SCRIPT = SCRIPT_DIR / "plugin_installer.py"

# ---------------------------------------------------------------------------
# ANSI colour helpers (no external deps)
# ---------------------------------------------------------------------------
_ANSI = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else True


def _col(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _ANSI else text


def cyan(t: str) -> str:    return _col("96", t)
def green(t: str) -> str:   return _col("92", t)
def yellow(t: str) -> str:  return _col("93", t)
def dim(t: str) -> str:     return _col("2", t)
def bold(t: str) -> str:    return _col("1", t)
def red(t: str) -> str:     return _col("91", t)


# ---------------------------------------------------------------------------
# Terminal raw-mode helpers for arrow-key / space navigation
# ---------------------------------------------------------------------------
def _read_key():
    """Read one keypress.  Returns a string token."""
    if sys.platform == "win32":
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):          # special / arrow prefix
            ch2 = msvcrt.getw

*(content truncated)*

## See Also

- [[match-pythonexecution-paths-that-are-hardcoded-to-the-repo-root-plugins-folder]]
- [[1-handle-absolute-paths-from-repo-root]]
- [[install-plugin-in-a-different-repo-eg-context-bundler-specifically]]
- [[use-npx-to-lazily-execute-mermaid-cli-so-the-user-doesnt-need-to-globally-install-it]]
- [[1-configuration-setup-dynamic-from-profile]]
- [[1-parse-the-hook-payload]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `plugin-manager/scripts/plugin_add.py`
- **Indexed:** 2026-04-27T05:21:04.027549+00:00
