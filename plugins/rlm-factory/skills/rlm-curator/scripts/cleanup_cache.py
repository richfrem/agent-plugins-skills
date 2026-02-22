#!/usr/bin/env python3
"""
cleanup_cache.py (CLI)
=====================================

Purpose:
    RLM Cleanup: Removes stale and orphan entries from the RLM ledger.

Usage:
    python plugins/rlm-factory/skills/rlm-curator/scripts/cleanup_cache.py --profile plugins --apply
    python plugins/rlm-factory/skills/rlm-curator/scripts/cleanup_cache.py --profile plugins --prune-orphans
    python plugins/rlm-factory/skills/rlm-curator/scripts/cleanup_cache.py --profile tools --prune-failed --apply
"""

import sys
import argparse
from pathlib import Path

# Paths standardization
PROJECT_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from rlm_config import RLMConfig, load_cache, save_cache, collect_files
except ImportError as e:
    print(f"❌ Could not import rlm_config: {e}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Clean up RLM cache.")
    parser.add_argument("--profile", required=True, help="RLM Profile name (from rlm_profiles.json)")
    parser.add_argument("--apply", action="store_true", help="Perform the deletion (default is dry run)")
    parser.add_argument("--prune-orphans", action="store_true", help="Remove entries not in manifest")
    parser.add_argument("--prune-failed", action="store_true", help="Remove entries with [DISTILLATION FAILED]")
    parser.add_argument("--v", action="store_true", help="Verbose mode")
    args = parser.parse_args()

    config = RLMConfig(profile_name=args.profile)

    print(f"🧹 Checking cache [{config.profile_name.upper()}]: {config.cache_path.name}")
    
    if not config.cache_path.exists():
        print("   Cache file not found. Nothing to clean.")
        return

    cache = load_cache(config.cache_path)
    print(f"   Entries in cache: {len(cache)}")

    entries_to_remove = []
    authorized_files = None

    for rel_path, entry in list(cache.items()):
        full_path = PROJECT_ROOT / rel_path

        # 1. Prune failed distillations
        if args.prune_failed and entry.get("summary") == "[DISTILLATION FAILED]":
            entries_to_remove.append(rel_path)
            if args.v: print(f"   [FAILED] {rel_path}")
            continue

        # 2. Prune missing files (stale)
        if not full_path.exists():
            entries_to_remove.append(rel_path)
            if args.v: print(f"   [MISSING] {rel_path}")
            continue

        # 3. Prune orphans (not in manifest)
        if args.prune_orphans:
            if authorized_files is None:
                print("   Building authorized file list from manifest...")
                authorized_files = set(str(f.resolve()) for f in collect_files(config))
                print(f"   Authorized files: {len(authorized_files)}")
            
            if str(full_path.resolve()) not in authorized_files:
                entries_to_remove.append(rel_path)
                if args.v: print(f"   [ORPHAN] {rel_path}")
                continue

        if args.v: print(f"   [OK] {rel_path}")

    print(f"   Entries to remove: {len(entries_to_remove)}")

    if not entries_to_remove:
        print("   ✅ Cache is clean.")
        return

    if args.apply:
        for key in entries_to_remove:
            del cache[key]
        save_cache(cache, config.cache_path)
        print(f"   ✅ Removed {len(entries_to_remove)} entries.")
    else:
        print(f"\n   DRY RUN: Would remove {len(entries_to_remove)} entries.")
        print(f"   Re-run with --apply to commit changes.")


def remove_entry(profile_name: str, file_path: str) -> bool:
    """Programmatic API to remove a single entry from a profile's cache."""
    try:
        config = RLMConfig(profile_name=profile_name)
        if not config.cache_path.exists():
            return False
        cache = load_cache(config.cache_path)
        norm_path = file_path.replace('\\', '/')
        if norm_path in cache:
            del cache[norm_path]
            save_cache(cache, config.cache_path)
            print(f"🗑️  [RLM] Removed {norm_path} from '{profile_name}' cache.")
            return True
        print(f"⚠️  [RLM] Entry not found: {file_path}")
        return False
    except Exception as e:
        print(f"❌ [RLM] Error: {e}")
        return False


if __name__ == "__main__":
    main()
