---
concept: force-utf-8-output-on-windows-if-possible
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/auto-update-plugins/scripts/check_and_sync.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.306449+00:00
cluster: plugin
content_hash: 361db727b4bcef6f
---

# Force UTF-8 output on Windows if possible

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/auto-update-plugins/scripts/check_and_sync.py -->
"""
check_and_sync.py
=================

Purpose:
    GitHub-native pull-based auto-sync script for consumer projects.
    Reads plugin-sources.json at the project root, checks the latest commit
    SHA from the GitHub API for each source repo, and runs plugin_add.py
    when upstream changes are detected.

    Designed to be called from a SessionStart hook on every agent session start.
    The SHA check is a single lightweight API call (~1 KB). The full clone +
    install only runs when there is an actual upstream change.

    No local clone of the source repo required.

Usage:
    python3 .agents/scripts/check_and_sync.py
    python3 .agents/scripts/check_and_sync.py --force   # ignore SHA cache, always sync
    python3 .agents/scripts/check_and_sync.py --dry-run # print what would happen
    python3 .agents/scripts/check_and_sync.py --source agent-plugins-skills

Layer: Plugin Manager / Consumer Auto-Sync

Input Files:
    - plugin-sources.json (project root) - subscription declarations
    - .agents/plugin-sync-state.json     - local SHA cache (auto-created)

Output:
    - Updated .agents/ skills and agent environments if source changed.
    - Updated .agents/plugin-sync-state.json with new commit SHAs.

plugin-sources.json format:
    {
      "sources": [
        {
          "name": "agent-plugins-skills",
          "github": "richfrem/agent-plugins-skills",
          "plugins": "all"                             // or ["spec-kitty-plugin", ...]
        }
      ]
    }
"""

import os
import sys
import json
import argparse
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# Force UTF-8 output on Windows if possible
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


PROJECT_ROOT = Path.cwd()
SOURCES_FILE = PROJECT_ROOT / "plugin-sources.json"
SYNC_STATE_FILE = PROJECT_ROOT / ".agents" / "plugin-sync-state.json"

# Resolve plugin_add.py — find it relative to this script or walk up from cwd
def _find_plugin_add() -> Path | None:
    """Return plugin_add.py if installed in .agents/, otherwise None (caller uses uvx)."""
    installed = PROJECT_ROOT / ".agents" / "skills" / "plugin-installer" / "scripts" / "plugin_add.py"
    return installed if installed.exists() else None


def _fetch_latest_sha(owner_repo: str) -> str | None:
    """
    Fetch the latest commit SHA for the default branch from GitHub API.
    Returns None if unreachable or rate-limited.
    """
    url = f"https://api.github.com/repos/{owner_repo}/commits?per_page=1"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json",
                                               "User-Agent": "check_and_sync/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list) and data:
                return data[0].get("sha", "")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"  [auto-sync] GitHub rate limit hit — skipping SHA check for '{owner_repo}'.")
        else:
            print(f"  [auto-sync] GitHub API error {e.code} for '{owner_repo}'.")
    except Exception:
        print(f"  [auto-sync] GitHub unreachable — skipping sync for '{owner_repo}'.")
    return None


def _load_sync_state() -> dict:
    if SYNC_STATE_FILE.exists():
        try:
            return json.loads(SYNC_STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_sync_state(state: dict) -> None:
    SYNC_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    SYNC_STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _load_sources() -> list:
   

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/plugin-installer/scripts/install_all_plugins.py -->
"""
Install All Plugins (CLI)
=========================

Purpose:
    Iterates through all directories in `plugins/` and runs the `plugin_installer.py` for each one 
    to orchestrate a bulk repository update, strictly using the new .agents centralized symlink pattern.

Layer: Plugin Manager / Installation

Usage Examples:
    python3 plugins/plugin-manager/scripts/install_all_plugins.py
    python3 plugins/plugin-manager/scripts/install_all_plugins.py --plugins-dir "temp/agent-plugins-skills/plugins"

Supported Object Types:
    - None (Batch execution)

CLI Arguments:
    --dry-run: Pass --dry-run to each bridge_installer invocation.
    --install-rules: Pass --install-rules to each bridge_installer invocation (rules not installed by default).


*(combined content truncated)*

## See Also

- [[force-utf-8-for-windows-consoles]]
- [[ensure-unicode-output-works-on-windows]]
- [[ensure-unicode-output-works-on-windows-terminals-that-default-to-cp1252]]
- [[prefer-remaining-broken-linksjson-post-fix-output-from-step-4-if-present-and]]
- [[check-if-we-already-emitted-for-this-completion-avoid-duplicate-events]]
- [[default-file-extensions-to-index-if-manifest-is-empty]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/auto-update-plugins/scripts/check_and_sync.py`
- **Indexed:** 2026-04-27T05:21:04.306449+00:00
