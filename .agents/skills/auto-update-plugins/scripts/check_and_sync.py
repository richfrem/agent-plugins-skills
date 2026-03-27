"""
check_and_sync.py
=================

Purpose:
    Pull-based auto-sync script for consumer projects. Reads plugin-sources.json
    at the project root, resolves env var paths, computes source hashes, and runs
    install_all_plugins.py for any source that has changed since the last sync.

    Designed to be called from a SessionStart hook on every agent session start.
    Costs nothing (no LLM tokens) and is a no-op if nothing has changed.

Usage:
    python3 .agents/scripts/check_and_sync.py
    python3 .agents/scripts/check_and_sync.py --force   # ignore hash cache, always sync
    python3 .agents/scripts/check_and_sync.py --dry-run # print what would happen

Layer: Plugin Manager / Consumer Auto-Sync

Input Files:
    - plugin-sources.json (project root) - subscription declarations
    - .agents/plugin-sync-state.json     - local hash cache (auto-created)

Output:
    - Updated .agents/ skills and agent environments if source changed.
    - Updated .agents/plugin-sync-state.json with new hashes.
"""

import os
import sys
import json
import hashlib
import argparse
import subprocess
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


def _compute_folder_hash(folder: Path) -> str:
    """Compute a deterministic SHA-256 hash over all files in a folder."""
    hasher = hashlib.sha256()
    file_list = []

    for root_dir, dirs, files in os.walk(folder):
        # Filter directories in-place to control walk recursion
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".") and d not in ("node_modules", "__pycache__")
        ]
        for f in files:
            file_list.append(Path(root_dir) / f)

    file_list.sort(key=lambda p: str(p.relative_to(folder)))

    for f in file_list:
        try:
            rel_path = str(f.relative_to(folder)).replace("\\", "/")
            hasher.update(rel_path.encode("utf-8"))
            hasher.update(f.read_bytes())
        except Exception:
            pass

    return hasher.hexdigest()


def _load_sync_state() -> dict:
    """Load the local hash cache. Returns empty dict if not found."""
    if SYNC_STATE_FILE.exists():
        try:
            return json.loads(SYNC_STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_sync_state(state: dict) -> None:
    """Persist the local hash cache."""
    SYNC_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    SYNC_STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _load_sources() -> list:
    """Load and validate plugin-sources.json."""
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
        description="Auto-sync plugins from registered source repos."
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Ignore hash cache and always sync all sources."
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
        # Silently exit if no subscription file found - project may not use this system.
        return

    # Filter sources if --source is provided
    if args.source:
        sources = [s for s in sources if s.get("name") == args.source]
        if not sources:
            print(f"  [auto-sync] No source found with name '{args.source}'")
            return

    sync_state = _load_sync_state()
    any_synced = False

    for source in sources:
        name = source.get("name", "unknown")
        env_var = source.get("env", "")
        plugins_subdir = source.get("plugins_subdir", "plugins")
        installer_subpath = source.get(
            "installer_subpath",
            "plugins/plugin-manager/scripts/install_all_plugins.py"
        )

        # Resolve the source path from env var
        source_root_str = os.environ.get(env_var, "")
        if not source_root_str:
            print(
                f"  [auto-sync] Skipping '{name}': env var ${env_var} is not set. "
                f"Add it to your .zshrc or Windows User Environment Variables."
            )
            continue

        source_root = Path(source_root_str)
        plugins_path = source_root / plugins_subdir
        installer_path = source_root / installer_subpath

        if not plugins_path.exists():
            print(
                f"  [auto-sync] Skipping '{name}': plugins folder not found "
                f"at {plugins_path}"
            )
            continue

        if not installer_path.exists():
            print(
                f"  [auto-sync] Skipping '{name}': installer not found "
                f"at {installer_path}"
            )
            continue

        # Compute hash and compare
        current_hash = _compute_folder_hash(plugins_path)
        cached_hash = sync_state.get(name, {}).get("hash", "")

        if current_hash == cached_hash and not args.force:
            print(f"  [auto-sync] '{name}' is up to date. No changes detected.")
            continue

        # Source has changed - run installer
        if args.dry_run:
            print(
                f"  [auto-sync] [DRY RUN] Would sync '{name}' from {plugins_path}"
            )
            continue

        print(f"  [auto-sync] Changes detected in '{name}'. Syncing...")
        try:
            cmd = [sys.executable, str(installer_path), "--plugins-dir", str(plugins_path)]
            result = subprocess.run(cmd, check=True, text=True, capture_output=False)
            sync_state[name] = {"hash": current_hash}
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
