#!/usr/bin/env python3
"""
cleanup_cache.py
=====================================

Purpose:
    RLM Cleanup: Removes stale and orphan entries from the RLM semantic ledger.
    Supports dry-run mode by default; requires --apply to commit changes.

Layer: Curate / Rlm

Usage:
    # Dry run — preview stale entries
    python ./scripts/cleanup_cache.py --profile plugins

    # Remove files whose source no longer exists
    python ./scripts/cleanup_cache.py --profile plugins --apply

    # Remove entries outside the manifest + failed distillations
    python ./scripts/cleanup_cache.py --profile tools --prune-orphans --prune-failed --apply

Related:
    - rlm_config.py (configuration & utilities)
    - inventory.py (coverage audit)
    - distiller.py (cache population)
"""
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional, Set

# ============================================================
# PATHS
# File is at: ./scripts/cleanup_cache.py
# Root is 6 levels up (scripts→rlm-curator→skills→rlm-factory→plugins→ROOT)
# ============================================================
def _find_project_root(start_path: Path) -> Path:
    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
    return current.parents[3]

PROJECT_ROOT = _find_project_root(Path(__file__))
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from rlm_config import RLMConfig, load_cache, save_cache, collect_files
except ImportError as e:
    print(f"[ERROR] Could not import local rlm_config from {SCRIPT_DIR}: {e}")
    sys.exit(1)


# ----------------------------------------------------------
# run_cleanup — entry-by-entry sweep of the cache
# ----------------------------------------------------------
def run_cleanup(
    config: RLMConfig,
    apply: bool,
    prune_orphans: bool,
    prune_failed: bool,
    verbose: bool
) -> int:
    """
    Scan the cache for stale, orphan, and failed entries, then optionally remove them.

    Three removal criteria (controlled by flags):
    1. **Stale**: Source file no longer exists on disk (always checked).
    2. **Failed**: Summary is the sentinel string `[DISTILLATION FAILED]`.
    3. **Orphan**: File exists but is not covered by the profile's manifest.

    Args:
        config: Active RLMConfig defining the cache and manifest.
        apply: If True, write the pruned cache to disk. If False, dry-run only.
        prune_orphans: Include orphan entries (not in manifest) in removals.
        prune_failed: Include entries with failed distillations in removals.
        verbose: Print per-entry status during the scan.

    Returns:
        Number of entries removed (or that would be removed in dry-run mode).
    """
    print(f"[CLEAN] Checking cache [{config.profile_name.upper()}]: {config.cache_path.name}")

    if not config.cache_path.exists() and not config.cache_path.with_suffix('').exists():
        print("   Cache not found. Nothing to clean.")
        return 0

    cache: Dict = load_cache(config.cache_path)
    print(f"   Entries in cache: {len(cache)}")

    entries_to_remove = []
    authorized_files: Optional[Set[str]] = None

    for rel_path, entry in list(cache.items()):
        full_path = PROJECT_ROOT / rel_path

        # 1. Failed distillation check
        if prune_failed and entry.get("summary") == "[DISTILLATION FAILED]":
            entries_to_remove.append(rel_path)
            if verbose:
                print(f"   [FAILED]  {rel_path}")
            continue

        # 2. Stale check — source file missing from disk
        if not full_path.exists():
            entries_to_remove.append(rel_path)
            if verbose:
                print(f"   [MISSING] {rel_path}")
            continue

        # 3. Orphan check — file exists but is not in manifest
        if prune_orphans:
            if authorized_files is None:
                print("   Building authorized file list from manifest...")
                authorized_files = {str(f.resolve()) for f in collect_files(config)}
                print(f"   Authorized files: {len(authorized_files)}")

            if str(full_path.resolve()) not in authorized_files:
                entries_to_remove.append(rel_path)
                if verbose:
                    print(f"   [ORPHAN]  {rel_path}")
                continue

        if verbose:
            print(f"   [OK]      {rel_path}")

    count = len(entries_to_remove)
    print(f"   Entries to remove: {count}")

    if count == 0:
        print("   [OK] Cache is clean.")
        return 0

    if apply:
        for key in entries_to_remove:
            del cache[key]
        save_cache(cache, config.cache_path)
        print(f"   [OK] Removed {count} entries.")
    else:
        print(f"\n   DRY RUN: Would remove {count} entries. Re-run with --apply to commit.")

    return count


# ----------------------------------------------------------
# remove_entry — programmatic single-entry removal API
# ----------------------------------------------------------
def remove_entry(profile_name: str, file_path: str) -> bool:
    """
    Programmatic API to remove a single entry from a profile's cache.

    Normalizes path separators before performing the lookup to ensure
    cross-platform compatibility.

    Args:
        profile_name: Name of the RLM profile whose cache to modify.
        file_path: Relative path of the cache key to remove.

    Returns:
        True if the entry was found and removed, False otherwise.
    """
    try:
        config = RLMConfig(profile_name=profile_name)
        if not config.cache_path.exists() and not config.cache_path.with_suffix('').exists():
            return False
        cache = load_cache(config.cache_path)
        norm_path = file_path.replace("\\", "/")
        if norm_path in cache:
            del cache[norm_path]
            save_cache(cache, config.cache_path)
            print(f"[DELETE]  [RLM] Removed '{norm_path}' from '{profile_name}' cache.")
            return True
        print(f"[WARN]  [RLM] Entry not found: {file_path}")
        return False
    except Exception as e:
        print(f"[ERROR] [RLM] Error: {e}")
        return False


# ============================================================
# CLI ENTRY POINT
# ============================================================
def main() -> None:
    """Parse CLI arguments and dispatch to run_cleanup()."""
    parser = argparse.ArgumentParser(
        description="RLM Cleanup — prune stale, orphan, and failed cache entries"
    )
    parser.add_argument("--profile", required=True, help="RLM profile name (from rlm_profiles.json)")
    parser.add_argument("--apply", action="store_true", help="Commit the removal (default is dry run)")
    parser.add_argument("--prune-orphans", action="store_true", help="Remove entries not covered by the manifest")
    parser.add_argument("--prune-failed", action="store_true", help="Remove entries with [DISTILLATION FAILED]")
    parser.add_argument("--v", action="store_true", help="Verbose per-entry logging")

    args = parser.parse_args()
    config = RLMConfig(profile_name=args.profile)
    run_cleanup(
        config,
        apply=args.apply,
        prune_orphans=args.prune_orphans,
        prune_failed=args.prune_failed,
        verbose=args.v
    )


if __name__ == "__main__":
    main()
