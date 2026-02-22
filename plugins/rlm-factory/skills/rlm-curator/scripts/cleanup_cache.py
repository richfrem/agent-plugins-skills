#!/usr/bin/env python3
"""
cleanup_cache.py (CLI)
=====================================

Purpose:
    RLM Cleanup: Removes stale and orphan entries from the Recursive Language Model ledger.

Layer: Curate / Rlm

Usage Examples:
    python plugins/rlm-factory/scripts/cleanup_cache.py --help
    python plugins/rlm-factory/scripts/cleanup_cache.py --apply --prune-orphans

Supported Object Types:
    - Generic

CLI Arguments:
    --apply         : Perform the deletion
    --prune-orphans : Remove entries not matching manifest
    --v             : Verbose mode

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - load_manifest_globs(): Load include/exclude patterns from manifest.
    - matches_any(): Check if path matches any glob pattern or is inside a listed directory.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import sys
import argparse
from pathlib import Path

# Add project root to sys.path to find tools package
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

try:
    from rlm_config import RLMConfig, load_cache, save_cache, should_skip
except ImportError:
    try:
        from tools.tool_inventory.rlm_config import RLMConfig, load_cache, save_cache, should_skip
    except ImportError:
        print("❌ Could not import RLMConfig (tried local and tools.tool_inventory)")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Clean up RLM cache.")
    parser.add_argument("--type", choices=["project", "tool"], help="[Legacy] RLM Configuration Profile")
    parser.add_argument("--profile", help="[New] RLM Profile name (from rlm_profiles.json)")
    parser.add_argument("--apply", action="store_true", help="Perform the deletion")
    parser.add_argument("--prune-orphans", action="store_true", help="Remove entries not matching manifest")
    parser.add_argument("--prune-failed", action="store_true", help="Remove entries with [DISTILLATION FAILED]")
    parser.add_argument("--v", action="store_true", help="Verbose mode")
    args = parser.parse_args()
    
    if not args.type and not args.profile:
        print("⚠️  No profile specified, defaulting to legacy 'project' type.")
        args.type = "project"
        
    # Load Config based on Type or Profile
    if args.profile:
        config = RLMConfig.from_profile(args.profile)
    else:
        config = RLMConfig(run_type=args.type)

    print(f"Checking cache at: {config.cache_path}")
    
    if not config.cache_path.exists():
        print("Cache file not found.")
        return

    cache = load_cache(config.cache_path)

    if args.prune_orphans:
        print(f"Loaded configuration for [{config.type.upper()}] with parser: {config.parser_type}")

    initial_count = len(cache)
    print(f"Total entries in cache: {initial_count}")

    # The Logic
    entries_to_remove = []
    authorized_files = None
    
    for relative_path, entry in list(cache.items()):
        full_path = PROJECT_ROOT / relative_path
        
        # 1. Check Distillation Failure (Explicit request)
        if args.prune_failed:
            summary = entry.get("summary", "")
            if summary == "[DISTILLATION FAILED]":
                entries_to_remove.append(relative_path)
                if args.v:
                    print(f"  [FAILED] {relative_path}")
                continue

        # 2. Check existence (Stale)
        if not full_path.exists():
            entries_to_remove.append(relative_path)
            if args.v:
                print(f"  [MISSING] {relative_path}")
            continue

        # 3. Check manifest (Orphan)
        if args.prune_orphans:
            # STRICT ORPHAN CHECK:
            # If the file is not in the list of files matched by the configuration (Manifest/Inventory),
            # it is an orphan.
            
            # Lazy load authorized set on first use
            if authorized_files is None:
                print("Building authorized file list from manifest...")
                # We need to import collect_files from rlm_config
                try:
                    from rlm_config import collect_files
                except ImportError:
                    from tools.tool_inventory.rlm_config import collect_files
                files = collect_files(config)
                # Store as set of resolved strings for fast lookup
                authorized_files = set(str(f.resolve()) for f in files)
                print(f"Authorized files count: {len(authorized_files)}")

            try:
                # Resolve cache path to absolute for comparison
                full_path_str = str(full_path.resolve())
                
                if full_path_str not in authorized_files:
                    entries_to_remove.append(relative_path)
                    if args.v:
                        print(f"  [ORPHAN] {relative_path} (Not in manifest)")
                    continue
            except Exception as e:
                # If we can't resolve, it might be a bad path, safety remove? 
                # Or keep safe. Let's log.
                if args.v: print(f"  [ERROR] resolving {relative_path}: {e}")
                continue

        if args.v:
           print(f"  [OK] {relative_path}")

    remove_count = len(entries_to_remove)
    print(f"Entries to remove: {remove_count}")

    if remove_count == 0:
        print("Cache is clean. No action needed.")
        return

    if args.apply:
        print(f"Removing {remove_count} entries...")
        for key in entries_to_remove:
            if key in cache:
                del cache[key]
        
        save_cache(cache, config.cache_path)
        print("Cache updated successfully.")
    else:
        print("\nDRY RUN COMPLETE.")
        print(f"Found {remove_count} entries to remove (Stale + Orphans).")
        print("To actually remove these entries, run:")
        if args.prune_orphans:
            print(f"  python plugins/rlm-factory/scripts/cleanup_cache.py --apply --prune-orphans")
        else:
            print(f"  python plugins/rlm-factory/scripts/cleanup_cache.py --apply")

def remove_entry(run_type: str, file_path: str) -> bool:
    """
    Programmatic API to remove a single entry from the cache.
    Args:
        run_type: 'legacy' or 'tool'
        file_path: Relative path to the file (e.g. tools/cli.py)
    Returns:
        True if removed, False if not found or error.
    """
    try:
        config = RLMConfig(run_type=run_type)
        if not config.cache_path.exists():
            return False
            
        cache = load_cache(config.cache_path)
        
        # Normalize keys
        target_keys = [
            file_path, 
            file_path.replace('\\', '/'),
            str(Path(file_path)) 
        ]
        
        found_key = None
        for k in cache.keys():
            if k in target_keys:
                found_key = k
                break
        
        if found_key:
            del cache[found_key]
            save_cache(cache, config.cache_path)
            print(f"🗑️  [RLM] Removed {found_key} from {run_type} cache.")
            return True
        else:
             print(f"⚠️  [RLM] Entry not found in cache: {file_path}")
             return False

    except Exception as e:
        print(f"❌ [RLM] Error removing {file_path}: {e}")
        return False

if __name__ == "__main__":
    main()
