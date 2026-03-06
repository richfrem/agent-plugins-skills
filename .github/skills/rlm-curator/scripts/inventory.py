#!/usr/bin/env python3
"""
inventory.py
=====================================

Purpose:
    RLM Auditor: Compares the semantic cache against the live filesystem to
    report coverage gaps. Identifies files that are uncached (missing) and
    cache entries whose source files have been deleted (stale).

Layer: Curate / Rlm

Usage:
    python plugins/rlm-factory/skills/rlm-curator/scripts/inventory.py --profile plugins
    python plugins/rlm-factory/skills/rlm-curator/scripts/inventory.py --profile tools

Related:
    - rlm_config.py (configuration & file collection)
    - distiller.py (cache population)
    - cleanup_cache.py (stale entry removal)
"""
import sys
import argparse
from pathlib import Path
from typing import Set

# ============================================================
# PATHS
# File is at: plugins/rlm-factory/skills/rlm-curator/scripts/inventory.py
# Root is 6 levels up (scripts→rlm-curator→skills→rlm-factory→plugins→ROOT)
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from rlm_config import RLMConfig, load_cache, collect_files
except ImportError as e:
    print(f"❌ Could not import RLMConfig from {SCRIPT_DIR}: {e}")
    sys.exit(1)


# ----------------------------------------------------------
# audit_inventory — coverage report for a single profile
# ----------------------------------------------------------
def audit_inventory(config: RLMConfig, show_full: bool = False, export_tasks: bool = False) -> None:
    """
    Compare the RLM cache against the live filesystem and print a coverage report.

    Identifies:
      - Files on disk that are not yet in the cache (missing).
      - Cache entries whose source files no longer exist (stale).

    Args:
        config: Active RLMConfig defining the cache and manifest to audit.
        show_full: If True, prints the complete list of missing/stale files without truncation.
        export_tasks: If True, writes a Markdown checklist of missing files to disk.
    """
    print(f"📊 Auditing RLM Inventory [{config.profile_name.upper()}]...")
    print(f"   Cache: {config.cache_path.name}")

    # 1. Load existing cache
    cache = load_cache(config.cache_path)
    cached_paths: Set[str] = set(cache.keys())

    # 2. Collect live files from manifest
    fs_files = collect_files(config)
    fs_paths: Set[str] = set()
    for f in fs_files:
        try:
            fs_paths.add(str(f.relative_to(PROJECT_ROOT)))
        except ValueError:
            pass

    # 3. Compute coverage deltas
    missing_in_cache = fs_paths - cached_paths
    stale_in_cache = cached_paths - fs_paths
    overlap = fs_paths & cached_paths

    # 4. Print report
    print(f"\n📈 Statistics:")
    print(f"   Files on Disk:    {len(fs_paths)}")
    print(f"   Entries in Cache: {len(cached_paths)}")
    pct = (len(overlap) / len(fs_paths) * 100) if fs_paths else 0
    print(f"   Coverage:         {len(overlap)} / {len(fs_paths)} ({pct:.1f}%)")

    if missing_in_cache:
        print(f"\n❌ Missing from Cache ({len(missing_in_cache)}):")
        sorted_missing = sorted(missing_in_cache)
        if show_full:
            for p in sorted_missing:
                print(f"   - {p}")
        else:
            for p in sorted_missing[:10]:
                print(f"   - {p}")
            if len(missing_in_cache) > 10:
                print(f"   ... and {len(missing_in_cache) - 10} more (use --full to see all).")

        # Export tasks if requested
        if export_tasks:
            task_file = PROJECT_ROOT / f"rlm_distill_tasks_{config.profile_name}.md"
            with open(task_file, "w", encoding="utf-8") as f:
                f.write(f"# RLM Distillation Tasks: {config.profile_name.upper()}\n\n")
                f.write(f"Generated: {len(missing_in_cache)} missing files to distill into `{config.cache_path.name}`.\n\n")
                for p in sorted_missing:
                    # Provide an actionable command for the agent/user
                    f.write(f"- [ ] `{p}`\n")
                    f.write(f"  - Command: `python plugins/rlm-factory/skills/rlm-curator/scripts/inject_summary.py --profile {config.profile_name} --file \"{p}\" --summary \"YOUR_SUMMARY_HERE\"`\n")
            print(f"\n📝 Exported task list to: {task_file.relative_to(PROJECT_ROOT)}")

    if stale_in_cache:
        print(f"\n⚠️  Stale in Cache ({len(stale_in_cache)}):")
        sorted_stale = sorted(stale_in_cache)
        if show_full:
            for p in sorted_stale:
                print(f"   - {p}")
        else:
            for p in sorted_stale[:10]:
                print(f"   - {p}")
            if len(stale_in_cache) > 10:
                print(f"   ... and {len(stale_in_cache) - 10} more (use --full to see all).")

    if not missing_in_cache and not stale_in_cache:
        print("\n✅ RLM Inventory is perfectly synchronized.")


# ============================================================
# CLI ENTRY POINT
# ============================================================
def main() -> None:
    """Parse CLI arguments and run the audit for the specified profile."""
    parser = argparse.ArgumentParser(description="RLM Inventory — cache coverage audit")
    parser.add_argument("--profile", required=True, help="RLM profile name (from rlm_profiles.json)")
    parser.add_argument("--full", action="store_true", help="Print the full list of missing/stale files without truncation")
    parser.add_argument("--tasks", action="store_true", help="Generate a markdown task compilation checklist of missing files")

    args = parser.parse_args()

    try:
        config = RLMConfig(profile_name=args.profile)
        audit_inventory(config, show_full=args.full, export_tasks=args.tasks)
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()