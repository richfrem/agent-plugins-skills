#!/usr/bin/env python
"""
cleanup.py
=====================================

Purpose:
    Removes stale chunk entries for files that have been deleted or renamed
    on disk, keeping the ChromaDB vector store in sync with the filesystem.

Layer: Curate / Retrieve

Usage:
    python cleanup.py --profile wiki
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Robustly discover the Project Root
def _find_project_root(start_path: Path) -> Path:
    """Walks up from start_path to find the first directory containing .git."""
    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
    return current.parents[2]

PROJECT_ROOT = _find_project_root(Path(__file__))
SCRIPT_DIR = Path(__file__).resolve().parent

# Ensure local imports work correctly
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from vector_config import VectorConfig
    from operations import VectorDBOperations
except ImportError as e:
    print(f"[ERROR] Could not import vector dependencies from {SCRIPT_DIR}: {e}")
    sys.exit(1)


def run_cleanup(cortex: VectorDBOperations, dry_run: bool = True) -> int:
    """
    Scans the database and removes entries for files no longer on disk.

    Args:
        cortex: Initialized VectorDBOperations instance.
        dry_run: When True (default), only reports stale entries without deleting.
                 Pass False (via --apply) to perform actual deletion.

    Returns:
        Number of chunks removed (or that would be removed in dry-run mode).
    """
    mode = "[DRY RUN]" if dry_run else "[CLEANUP]"
    print(f"{mode} Scanning for stale database entries...")
    
    try:
        collection_name = cortex.child_collection_name
        collection = cortex.chroma_client.get_collection(name=collection_name)
    except Exception as e:
        print(f"[WARN] Collection not found: {e}")
        return 0
    
    total_chunks = collection.count()
    if total_chunks == 0:
        print("   Collection is empty. Nothing to clean.")
        return 0
    
    all_data = collection.get(include=["metadatas"])
    id_to_source: Dict[str, List[str]] = {}
    
    metadatas = all_data.get('metadatas') or []
    ids = all_data.get('ids', [])
    
    for i, meta in enumerate(metadatas):
        source = meta.get('source', '')
        if source and i < len(ids):
            doc_id = ids[i]
            if source not in id_to_source:
                id_to_source[source] = []
            id_to_source[source].append(doc_id)
    
    stale_ids: List[str] = []
    stale_count = 0
    for rel_path, chunk_ids in id_to_source.items():
        full_path = cortex.project_root / rel_path
        if not full_path.exists():
            stale_ids.extend(chunk_ids)
            stale_count += 1
    
    if not stale_ids:
        print("   [OK] No stale entries found.")
        return 0

    print(f"   Found {stale_count} missing files ({len(stale_ids)} chunks)")

    if dry_run:
        for rel_path in id_to_source:
            full_path = cortex.project_root / rel_path
            if not full_path.exists():
                print(f"   [WOULD REMOVE] {rel_path} ({len(id_to_source[rel_path])} chunks)")
        print(f"\n   [DRY RUN] {len(stale_ids)} chunks would be removed. Re-run with --apply to delete.")
        return len(stale_ids)

    # Batch delete (only reached when --apply is passed)
    batch_size = 5000
    for i in range(0, len(stale_ids), batch_size):
        batch = stale_ids[i:i + batch_size]
        collection.delete(ids=batch)

    print(f"   [DONE] Removed {len(stale_ids)} stale chunks.")
    return len(stale_ids)


def main() -> None:
    """Main entry point for the cleanup CLI."""
    parser = argparse.ArgumentParser(
        description="Clean up stale chunks in Vector DB. Dry-run by default — use --apply to delete."
    )
    parser.add_argument("--profile", type=str, help="Vector DB profile to use (e.g., wiki)")
    parser.add_argument(
        "--apply", action="store_true",
        help="Perform actual deletion. Without this flag the command reports stale entries without deleting."
    )
    args = parser.parse_args()
    dry_run = not args.apply
    
    # 1. Configuration Setup (Dynamic from profile)
    vec_config = VectorConfig(profile_name=args.profile, project_root=str(PROJECT_ROOT))
    
    # 2. Operations Setup with dynamic parameters
    cortex = VectorDBOperations(
        str(PROJECT_ROOT),
        child_collection=vec_config.child_collection,
        parent_collection=vec_config.parent_collection,
        chroma_host=vec_config.chroma_host,
        chroma_port=vec_config.chroma_port,
        chroma_data_path=vec_config.chroma_data_path,
        embedding_model=vec_config.embedding_model,
        parent_chunk_size=vec_config.parent_chunk_size,
        parent_chunk_overlap=vec_config.parent_chunk_overlap,
        child_chunk_size=vec_config.child_chunk_size,
        child_chunk_overlap=vec_config.child_chunk_overlap
    )
        
    run_cleanup(cortex, dry_run=dry_run)


if __name__ == "__main__":
    main()
