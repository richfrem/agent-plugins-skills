#!/usr/bin/env python3
"""
audit_vector.py
=====================================

Purpose:
    Compares the Vector DB index against the live filesystem (based on profiles)
    and reports coverage gaps. Produces CSV and text reports of missing files.

Usage:
    python audit_vector.py --profile wiki --csv ./missing_vector.csv --report ./vector_audit.txt
"""

import sys
import argparse
import csv
from pathlib import Path
from datetime import datetime
from typing import Set

# ============================================================
# PATHS
# ============================================================
def _find_project_root(start_path: Path) -> Path:
    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
    return current.parents[2]

PROJECT_ROOT = _find_project_root(Path(__file__))
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from vector_config import VectorConfig
    from operations import VectorDBOperations
except ImportError as e:
    print(f"[ERROR] Could not import vector dependencies from {SCRIPT_DIR}: {e}")
    sys.exit(1)

def run_audit(profile_name: str, csv_path: str = None, report_path: str = None):
    try:
        config = VectorConfig(profile_name=profile_name, project_root=str(PROJECT_ROOT))
    except SystemExit:
        return
    except Exception as e:
        print(f"[ERROR] Failed to load profile '{profile_name}': {e}")
        return

    print(f"[AUDIT] Starting Vector DB Audit for profile: {profile_name}")
    print(f"   Manifest: {config.manifest_path}")
    
    # 1. Collect all expected files from the manifest
    manifest = config.load_manifest()
    fs_files = manifest.get_files()
    total_expected = len(fs_files)
    
    print(f"   Searching for {total_expected} manifest files in Vector DB...")

    # 2. Check Vector DB status
    cortex = VectorDBOperations(
        str(PROJECT_ROOT),
        child_collection=config.child_collection,
        parent_collection=config.parent_collection,
        chroma_host=config.chroma_host,
        chroma_port=config.chroma_port,
        chroma_data_path=config.chroma_data_path
    )

    # Get all sources currently in the child collection
    try:
        all_data = cortex.chroma_client.get_collection(name=config.child_collection_name).get(include=['metadatas'])
        indexed_sources: Set[str] = set()
        if all_data and 'metadatas' in all_data:
            for meta in all_data['metadatas']:
                if meta and 'source' in meta:
                    indexed_sources.add(meta['source'])
    except Exception as e:
        print(f"[ERROR] Failed to query ChromaDB: {e}")
        return

    missing = []
    found_count = 0
    
    for rel_path in fs_files:
        # Normalize to forward slashes for matching
        clean_path = str(rel_path).replace("\\", "/")
        if clean_path in indexed_sources:
            found_count += 1
        else:
            missing.append(clean_path)

    missing_count = len(missing)
    coverage_pct = (found_count / total_expected * 100) if total_expected > 0 else 0
    gap_pct = (missing_count / total_expected * 100) if total_expected > 0 else 0

    # 3. Build Report String
    report_lines = [
        "--- VECTOR DB INVENTORY AUDIT ---",
        f"Generated: {datetime.now().isoformat()}",
        f"Profile:   {profile_name}",
        f"Root:      {PROJECT_ROOT}",
        f"Collection: {config.child_collection_name}",
        "",
        f"Total Files in Manifest:  {total_expected}",
        f"Indexed (in Vector DB):   {found_count}",
        f"Not Indexed (Gap):        {missing_count}",
        "",
        f"Coverage Indexed:         {coverage_pct:.2f}%",
        f"Coverage Gap:             {gap_pct:.2f}%",
        "----------------------------------"
    ]
    report_text = "\n".join(report_lines)
    print(f"\n{report_text}")

    # 4. Save Outputs
    if report_path:
        rp = Path(report_path).resolve()
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(report_text, encoding="utf-8")
        print(f"[OK] Report saved to: {rp}")

    if csv_path:
        cp = Path(csv_path).resolve()
        cp.parent.mkdir(parents=True, exist_ok=True)
        with open(cp, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Missing File Path"])
            for m in sorted(missing):
                writer.writerow([m])
        print(f"[OK] Missing files list saved to: {cp}")

def main():
    parser = argparse.ArgumentParser(description="Vector DB Audit - Compare manifest to ChromaDB collection")
    parser.add_argument("--profile", required=False, help="Profile name from vector_profiles.json")
    parser.add_argument("--csv", help="Path to export missing files CSV")
    parser.add_argument("--report", help="Path to export text report")
    
    args = parser.parse_args()
    run_audit(args.profile, args.csv, args.report)

if __name__ == "__main__":
    main()
