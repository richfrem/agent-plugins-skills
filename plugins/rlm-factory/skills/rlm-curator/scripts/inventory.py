#!/usr/bin/env python3
"""
inventory.py (CLI)
=====================================

Purpose:
    RLM Auditor: Reports coverage of the semantic ledger against the filesystem.
"""

import sys
import argparse
from pathlib import Path

# Paths standardization
# File is at: plugins/rlm-factory/skills/rlm-curator/scripts/inventory.py
# Root is 6 levels up
PROJECT_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from rlm_config import RLMConfig, load_cache, collect_files
except ImportError as e:
    print(f"❌ Could not import local RLMConfig from {SCRIPT_DIR}: {e}")
    sys.exit(1)


def audit_inventory(config: RLMConfig):
    """Compare RLM cache against actual file system."""
    
    print(f"📊 Auditing RLM Inventory [{config.profile_name.upper()}]...")
    print(f"   Cache: {config.cache_path.name}")
    
    # 1. Load Cache
    cache = load_cache(config.cache_path)
    cached_paths = set(cache.keys())
    
    # 2. Scan File System
    fs_files = collect_files(config)
    
    # Convert absolute paths to relative keys matching cache format
    fs_paths = set()
    for f in fs_files:
        try:
            rel = str(f.relative_to(PROJECT_ROOT))
            fs_paths.add(rel)
        except ValueError:
            pass
            
    # 3. Compare
    missing_in_cache = fs_paths - cached_paths
    stale_in_cache = cached_paths - fs_paths
    
    # 4. Report
    print(f"\n📈 Statistics:")
    print(f"   Files on Disk: {len(fs_paths)}")
    print(f"   Entries in Cache: {len(cached_paths)}")
    percentage = (len(fs_paths & cached_paths)/len(fs_paths)*100) if fs_paths else 0
    print(f"   Coverage: {len(fs_paths & cached_paths)} / {len(fs_paths)} ({percentage:.1f}%)")
    
    if missing_in_cache:
        print(f"\n❌ Missing from Cache ({len(missing_in_cache)}):")
        for p in sorted(list(missing_in_cache))[:10]:
             print(f"   - {p}")
        if len(missing_in_cache) > 10:
            print(f"   ... and {len(missing_in_cache) - 10} more.")
            
    if stale_in_cache:
        print(f"\n⚠️  Stale in Cache ({len(stale_in_cache)}):")
        for p in sorted(list(stale_in_cache))[:10]:
             print(f"   - {p}")
        if len(stale_in_cache) > 10:
             print(f"   ... and {len(stale_in_cache) - 10} more.")
             
    if not missing_in_cache and not stale_in_cache:
        print("\n✅ RLM Inventory is perfectly synchronized.")


def main():
    parser = argparse.ArgumentParser(description="Audit RLM Cache Coverage")
    parser.add_argument("--profile", required=True, help="RLM Profile name (from rlm_profiles.json)")
    
    args = parser.parse_args()
    
    try:
        config = RLMConfig(profile_name=args.profile)
        audit_inventory(config)
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()