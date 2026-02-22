#!/usr/bin/env python3
"""
inventory.py (CLI)
=====================================

Purpose:
    RLM Auditor: Reports coverage of the semantic ledger against the filesystem.

Layer: Curate / Rlm

Usage Examples:
    python plugins/rlm-factory/skills/rlm-curator/scripts/inventory.py --profile plugins

Supported Object Types:
    - RLM Cache (Sanctuary)

Input Files:
    - .agent/learning/rlm_summary_cache.json
    - Filesystem targets (defined in manifests)

Output:
    - Console report (Statistics, Missing Files, Stale Entries)

Key Functions:
    - audit_inventory(): Logic to compare cache keys against collected file paths.

Script Dependencies:
    - plugins/rlm_factory/scripts/rlm_config.py
"""
import os
import sys
import argparse
from pathlib import Path
from collections import defaultdict

# Add project root to sys.path to find tools package
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

try:
    from rlm_config import RLMConfig, load_cache, collect_files
except ImportError:
    from tools.rlm_factory.rlm_config import RLMConfig, load_cache, collect_files

def audit_inventory(config: RLMConfig):
    """Compare RLM cache against actual file system."""
    
    print(f"📊 Auditing RLM Inventory [{config.type.upper()}]...")
    print(f"   Cache: {config.cache_path.name}")
    
    # 1. Load Cache
    cache = load_cache(config.cache_path)
    cached_paths = set(cache.keys())
    
    # 2. Scan File System / Inventory
    fs_files = collect_files(config)
    
    # Get the true project root from the config module
    from rlm_config import PROJECT_ROOT as TRUE_PROJECT_ROOT
    
    # Convert absolute paths to relative keys matching cache format
    fs_paths = set()
    for f in fs_files:
        try:
            rel = str(f.relative_to(TRUE_PROJECT_ROOT))
            fs_paths.add(rel)
        except ValueError:
            pass
            
    # 3. Compare
    missing_in_cache = fs_paths - cached_paths
    stale_in_cache = cached_paths - fs_paths
    
    # 4. Report
    print(f"\n📈 Statistics:")
    print(f"   Files on Disk/Inventory: {len(fs_paths)}")
    print(f"   Entries in Cache:        {len(cached_paths)}")
    percentage = (len(fs_paths & cached_paths)/len(fs_paths)*100) if fs_paths else 0
    print(f"   Coverage:                {len(fs_paths & cached_paths)} / {len(fs_paths)} ({percentage:.1f}%)")
    
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
    parser.add_argument("--type", choices=["project", "tool"], help="[Legacy] RLM Type (loads manifest from factory)")
    parser.add_argument("--profile", help="[New] RLM Profile name (from rlm_profiles.json)")
    
    args = parser.parse_args()
    
    if not args.type and not args.profile:
        parser.error("Must specify either --type (legacy) or --profile (new JSON config).")
        
    # Load Config based on Type or Profile
    try:
        if args.profile:
            config = RLMConfig.from_profile(args.profile)
        else:
            config = RLMConfig(run_type=args.type)
            
        audit_inventory(config)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()