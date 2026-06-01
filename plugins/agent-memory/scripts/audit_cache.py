#!/usr/bin/env python
"""
audit_cache.py
=====================================

Purpose:
    Compares the RLM semantic cache against the live filesystem (based on profiles)
    and reports coverage gaps. Produces CSV and text reports of missing files.

Usage:
    python audit_cache.py --profile wiki --csv ./missing.csv --report ./audit.txt
"""

import sys
import argparse
import csv
import json
from pathlib import Path
from datetime import datetime

# ============================================================
# PATHS
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
    from rlm_config import RLMConfig, load_cache, collect_files
except ImportError as e:
    print(f"[ERROR] Could not import local rlm_config from {SCRIPT_DIR}: {e}")
    sys.exit(1)

def run_audit(profile_name: str, csv_path: str = None, report_path: str = None, cache_override: str = None):
    try:
        config = RLMConfig(profile_name=profile_name)
    except Exception as e:
        print(f"[ERROR] Failed to load profile '{profile_name}': {e}")
        return

    # Use override or default from config
    cache_dir = Path(cache_override) if cache_override else config.cache_path.with_suffix('')
    
    print(f"[AUDIT] Starting RLM Cache Audit for profile: {profile_name}")
    print(f"   Manifest: {config.manifest_path}")
    print(f"   Cache Dir: {cache_dir}")

    # 1. Collect all expected files from the manifest
    fs_files = collect_files(config)
    fs_paths = []
    for f in fs_files:
        try:
            # Keys are relative to project root with forward slashes
            rel = str(f.relative_to(PROJECT_ROOT)).replace("\\", "/")
            fs_paths.append(rel)
        except ValueError:
            continue

    total_expected = len(fs_paths)
    
    # 2. Check cache status
    missing = []
    found_count = 0
    
    for rel_path in fs_paths:
        # Check for matching .md file in cache dir
        # If the input file is already .md, we just check its path
        # If it's something else (e.g. .js), we check for the .md summary
        clean_path = rel_path[:-3] if rel_path.endswith(".md") else rel_path
        target_md = cache_dir / f"{clean_path}.md"
        
        if target_md.exists():
            found_count += 1
        else:
            missing.append(rel_path)

    missing_count = len(missing)
    coverage_pct = (found_count / total_expected * 100) if total_expected > 0 else 0
    gap_pct = (missing_count / total_expected * 100) if total_expected > 0 else 0

    # 3. Build Report String
    report_lines = [
        "--- RLM WIKI CACHE INVENTORY AUDIT ---",
        f"Generated: {datetime.now().isoformat()}",
        f"Profile:   {profile_name}",
        f"Root:      {PROJECT_ROOT}",
        "",
        f"Total Files in Manifest:  {total_expected}",
        f"Indexed (in cache):       {found_count}",
        f"Not Indexed (Gap):        {missing_count}",
        "",
        f"Coverage Indexed:         {coverage_pct:.2f}%",
        f"Coverage Gap:             {gap_pct:.2f}%",
        "--------------------------------------"
    ]
    report_text = "\n".join(report_lines)
    print(f"\n{report_text}")

    # 4. Save Outputs
    if report_path:
        rp = Path(report_path)
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(report_text, encoding="utf-8")
        print(f"[OK] Report saved to: {rp}")

    if csv_path:
        cp = Path(csv_path)
        cp.parent.mkdir(parents=True, exist_ok=True)
        with open(cp, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Missing File Path"])
            for m in sorted(missing):
                writer.writerow([m])
        print(f"[OK] Missing files list saved to: {cp}")

def main():
    parser = argparse.ArgumentParser(description="RLM Cache Audit - Compare manifest to markdown cache")
    parser.add_argument("--profile", required=True, help="Profile name from rlm_profiles.json")
    parser.add_argument("--csv", help="Path to export missing files CSV")
    parser.add_argument("--report", help="Path to export text report")
    parser.add_argument("--cache-dir", help="Optional override for cache directory")
    
    args = parser.parse_args()
    run_audit(args.profile, args.csv, args.report, args.cache_dir)

if __name__ == "__main__":
    main()
