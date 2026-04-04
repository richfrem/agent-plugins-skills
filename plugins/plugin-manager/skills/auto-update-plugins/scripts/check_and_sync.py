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
    if not SOURCES_FILE.exists():
        return []
    try:
        data = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
        return data.get("sources", [])
    except Exception as e:
        print(f"  [auto-sync] Warning: Could not read plugin-sources.json: {e}")
        return []


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Auto-sync plugins from registered GitHub source repos."
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Ignore SHA cache and always sync all sources."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would happen without making changes."
    )
    parser.add_argument(
        "--source", help="Only sync a specific source by name."
    )
    args = parser.parse_args()

    sources = _load_sources()
    if not sources:
        # Silently exit if no subscription file found.
        return

    if args.source:
        sources = [s for s in sources if s.get("name") == args.source]
        if not sources:
            print(f"  [auto-sync] No source found with name '{args.source}'")
            return

    plugin_add = _find_plugin_add()
    if not plugin_add:
        print("  [auto-sync] plugin_add.py not found locally — will use uvx fallback.")

    sync_state = _load_sync_state()
    any_synced = False

    for source in sources:
        name = source.get("name", "unknown")
        owner_repo = source.get("github", "")
        plugins_selection = source.get("plugins", "all")

        if not owner_repo or "/" not in owner_repo:
            print(f"  [auto-sync] Skipping '{name}': missing or invalid 'github' field "
                  f"(expected 'owner/repo').")
            continue

        # Fetch latest SHA from GitHub
        latest_sha = _fetch_latest_sha(owner_repo)
        if latest_sha is None:
            # Unreachable — skip gracefully
            continue

        cached_sha = sync_state.get(name, {}).get("sha", "")

        if latest_sha == cached_sha and not args.force:
            print(f"  [auto-sync] '{name}' is up to date (sha: {latest_sha[:8]}…).")
            continue

        # Upstream changed — run plugin_add.py
        if args.dry_run:
            print(f"  [auto-sync] [DRY RUN] Would sync '{name}' from github:{owner_repo}")
            continue

        print(f"  [auto-sync] Changes detected in '{name}' "
              f"({cached_sha[:8] if cached_sha else 'new'} → {latest_sha[:8]}). Syncing...")

        if plugin_add:
            cmd = [sys.executable, str(plugin_add), owner_repo, "--all", "-y"]
        else:
            # uvx fallback — works in any consumer project without a local clone
            cmd = ["uvx", "--from", "git+https://github.com/richfrem/agent-plugins-skills",
                   "plugin-add", owner_repo, "--all", "-y"]
        # If specific plugins requested (not "all"), we can't filter via CLI yet —
        # fall back to --all and note it. Future: add --plugin filter to plugin_add.py.
        if plugins_selection != "all" and isinstance(plugins_selection, list):
            print(f"  [auto-sync] Note: installing all plugins from '{name}' "
                  f"(per-plugin filtering not yet supported in non-interactive mode).")

        try:
            subprocess.run(cmd, check=True, text=True)
            sync_state[name] = {"sha": latest_sha, "github": owner_repo}
            any_synced = True
            print(f"  [auto-sync] '{name}' sync complete.")
        except subprocess.CalledProcessError as e:
            print(f"  [auto-sync] ERROR: Failed to sync '{name}': {e}")
        except Exception as e:
            print(f"  [auto-sync] ERROR: Unexpected error syncing '{name}': {e}")

    if any_synced:
        _save_sync_state(sync_state)


if __name__ == "__main__":
    main()
