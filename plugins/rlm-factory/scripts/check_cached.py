#!/usr/bin/env python3
"""
check_cached.py
=====================================

Purpose:
    Used as the `check_cmd` in swarm_run.py job files to skip files that
    are already present in the RLM markdown cache directory.

    Exit code 0  = file IS cached  -> swarm worker should SKIP it.
    Exit code 1  = file NOT cached -> swarm worker should process it.

Usage (invoked automatically by swarm_run.py via check_cmd):
    python3 ./plugins/rlm-factory/scripts/check_cached.py <relative-file-path>

    Example in a job file:
        check_cmd: python3 ./plugins/rlm-factory/scripts/check_cached.py {file}

    The cache directory is resolved from the RLM profile named 'wiki' in
    .agent/learning/rlm_profiles.json. Override with --profile <name>.

Related:
    - swarm_run.py   (calls this via check_cmd)
    - audit_cache.py (bulk coverage report)
    - inject_summary.py (writes to the same cache directory)
"""

import sys
import json
import argparse
from pathlib import Path


# ─── PATH BOOTSTRAP ─────────────────────────────────────────────────────────
def _find_project_root(start: Path) -> Path:
    """Walk up from start to find the git repository root."""
    for p in [start.resolve()] + list(start.resolve().parents):
        if (p / ".git").is_dir():
            return p
    return start.resolve().parents[3]


PROJECT_ROOT = _find_project_root(Path(__file__))
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def _load_cache_dir(profile_name: str) -> Path:
    """
    Resolve the RLM cache directory from the profile config.

    Returns the cache directory Path (strips .json extension from cache value).
    Falls back to a sensible default if the profile cannot be loaded.
    """
    profiles_path = PROJECT_ROOT / ".agent" / "learning" / "rlm_profiles.json"
    if not profiles_path.exists():
        profiles_path = PROJECT_ROOT / ".agents" / "learning" / "rlm_profiles.json"

    try:
        profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
        cache_rel = profiles["profiles"][profile_name]["cache"]
        cache_path = (PROJECT_ROOT / cache_rel).resolve()
        # Cache dir = cache_path with .json stripped (e.g. rlm_wiki_cache not rlm_wiki_cache.json)
        return cache_path.with_suffix("") if cache_path.suffix == ".json" else cache_path
    except Exception:
        # Sensible fallback
        return PROJECT_ROOT / ".agent" / "learning" / "rlm_wiki_cache"


def is_cached(file_rel: str, cache_dir: Path) -> bool:
    """
    Return True if a summary .md file exists in the cache for the given source file path.

    The cache mirrors the source tree: source/path/file.md -> cache_dir/source/path/file.md
    Non-md source files get .md appended: source/path/file.py -> cache_dir/source/path/file.py.md
    """
    clean = file_rel[:-3] if file_rel.endswith(".md") else file_rel
    target = cache_dir / f"{clean}.md"
    return target.exists()


def main() -> None:
    """Entry point: exit 0 if cached (skip), exit 1 if not cached (process)."""
    parser = argparse.ArgumentParser(
        description="Check whether a file is already in the RLM cache."
    )
    parser.add_argument("file", help="Relative path to the source file.")
    parser.add_argument(
        "--profile", default="wiki", help="RLM profile name (default: wiki)."
    )
    args = parser.parse_args()

    cache_dir = _load_cache_dir(args.profile)
    if is_cached(args.file, cache_dir):
        sys.exit(0)   # cached -> skip
    else:
        sys.exit(1)   # not cached -> process


if __name__ == "__main__":
    main()
