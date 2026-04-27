---
concept: install-plugin-in-a-different-repo-eg-context-bundler-specifically
source: plugin-code
source_file: plugin-manager/scripts/plugin_installer.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.028844+00:00
cluster: agents
content_hash: bf340a0583c265bd
---

# install plugin in a different repo e.g. context-bundler specifically

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

"""
Bridge Installer (CLI)
=====================

    Installs Agent Plugins into .agents/ central repository natively 
    and symlinks them across locally installed agent platforms.

Layer: Plugin Manager / Installation

Usage Examples:
    python plugins/plugin-manager/scripts/plugin_installer.py --plugin plugins/my-plugin

    # install plugin in a different repo e.g. context-bundler specifically
    python <full install path>/agent-plugins-skills/plugins/plugin-manager/scripts/plugin_installer.py --plugin <full install path>/agent-plugins-skills/plugins/context-bundler

Platform Command Mapping (commands/ vs workflows/):
    Plugin source always uses commands/ as the canonical folder name.
    The installer maps this to the correct platform-specific directory at install time:

        Source folder:   plugin/commands/*.md
        ─────────────────────────────────────────────────────────
        .agents/         → workflows/<plugin>_<cmd>.md  (canonical)
        .claude/         → commands/<plugin>_<cmd>.md   (Claude Code)

    This means the same source file appears under "workflows/" on .agents/
    but under "commands/" on Claude Code — by design. Never rename the source
    folder to match any single platform.

Supported Object Types:
    - None (Filesystem operations)

CLI Arguments:
    --plugin: Path to plugin directory (Required)
    --dry-run: Preview actions without writing files
    --install-rules: Also install rules (disabled by default)

Input Files:
    - .claude-plugin/plugin.json (Manifest reader)

Output:
    - Creates symlinks and updates skills-lock.json

    _is_pointer_file(): Checks if file is a pointer.
    _copy_resolving_pointers(): Copies resolving pointers.
    _symlink_or_copy(): Symlinks or copies fallback.
    _write_toml_command(): Writes TOML command wrapper.
    deploy_commands(): Deploys commands.
    deploy_agents(): Deploys agents.
    deploy_rules(): Deploys rules.
    write_project_lock(): Writes project lockfile.
    provision_central_and_symlink(): Provisions central and symlinks.

Script Dependencies:
    os, sys, shutil, json, argparse, datetime, pathlib

Consumed by:
    - None (Standalone script)
"""

import os
import sys
import shutil
import json
import argparse
import datetime
from pathlib import Path

# Force UTF-8 output on Windows to avoid UnicodeEncodeError with emoji in print()
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Agent environments that require their own directory layout alongside .agents/.
#
# Antigravity, Gemini CLI, and GitHub Copilot have all adopted the standard
# .agents/ install path — they read skills, workflows, and rules directly from
# there. No per-agent symlinks are needed for those platforms anymore; the
# canonical .agents/ copy is sufficient. As agents converge on .agents/ as the
# standard, this list shrinks. Only environments that still require a separate
# directory tree (Claude Code, Azure) remain here.
DETECTABLE_AGENTS = {
    ".claude": {
        "name": "claude",
        # Skills, agents, commands, and hooks are intentionally NOT symlinked
        # into .claude/ — Claude Code picks all of these up directly from
        # .agents/ (the canonical multi-IDE store). Symlinking them into
        # .claude/ as well causes every skill to appear twice in /context
        # (once as "Project" from .agents/skills/ and once as "Plugin" from
        # .claude/skills/), doubling the Skills token cost for no benefit.
        "skills": None,
        "agents": None,
        "commands": None,
        "rules": None,
        "rules_append_target": "CLAUDE.md",
        "hooks": None,
        "rules_mode": "append",
    },
    ".azure": {
        "name": "azure",
        "skills": ".azure/skills",
        "commands": None,
        "rules": None,
        "hooks": None,
    },
}

def _is_pointer_file(p

*(content truncated)*

## See Also

- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[initialize-empty-hooks-schema-in-a-nested-hooks-dir]]
- [[install-from-the-local-repo-select-plugins-interactively]]
- [[1-handle-absolute-paths-from-repo-root]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[add-script-dir-to-path-to-import-plugin-inventory]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `plugin-manager/scripts/plugin_installer.py`
- **Indexed:** 2026-04-27T05:21:04.028844+00:00
