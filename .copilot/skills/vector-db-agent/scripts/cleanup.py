#!/usr/bin/env python3
"""
cleanup.py (CLI)
=====================================

Purpose:
    Removes stale chunk entries for files that have been deleted or renamed on disk.
"""

import sys
import argparse
from pathlib import Path

# Project paths
# File is at: plugins/vector-db/skills/vector-db-agent/scripts/cleanup.py
PROJECT_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vector_config import VectorConfig
from operations import VectorDBOperations


def run_cleanup(cortex: VectorDBOperations) -> int:
    """Scan and sweep orphaned database entries."""
    print("🧹 Running cleanup for stale entries...")
    
    try:
        collection = cortex.chroma_client.get_collection(name=cortex.child_collection_name)
    except Exception as e:
        print(f"❌ Collection not found: {e}")
        return 0
    
    total_chunks = collection.count()
    if total_chunks == 0:
        print("   Collection is empty. Nothing to clean.")
        return 0
    
    all_data = collection.get(include=["metadatas"])
    id_to_source = {}
    
    metadatas = all_data.get('metadatas') or []
    ids = all_data.get('ids', [])
    
    for i, meta in enumerate(metadatas):
        source = meta.get('source', '')
        if source and i < len(ids):
            doc_id = ids[i]
            if source not in id_to_source:
                id_to_source[source] = []
            id_to_source[source].append(doc_id)
    
    stale_ids = []
    stale_count = 0
    for rel_path, chunk_ids in id_to_source.items():
        full_path = Path(cortex.project_root) / rel_path
        if not full_path.exists():
            stale_ids.extend(chunk_ids)
            stale_count += 1
    
    if not stale_ids:
        print("   ✅ No stale entries found.")
        return 0
    
    print(f"   Found {stale_count} missing files ({len(stale_ids)} chunks)")
    
    # Batch delete
    batch_size = 5000
    for i in range(0, len(stale_ids), batch_size):
        batch = stale_ids[i:i + batch_size]
        collection.delete(ids=batch)
    
    print(f"   ✅ Removed {len(stale_ids)} stale chunks")
    return len(stale_ids)


def main():
    parser = argparse.ArgumentParser(description="Clean up stale chunks in Vector DB")
    parser.add_argument("--profile", type=str, help="Vector DB profile to use (e.g., knowledge)")
    args = parser.parse_args()
    
    # Load configuration from JSON profile (no .env)
    vec_config = VectorConfig(profile_name=args.profile, project_root=str(PROJECT_ROOT))
    
    cortex = VectorDBOperations(
        str(PROJECT_ROOT),
        child_collection=vec_config.child_collection,
        parent_collection=vec_config.parent_collection,
        chroma_host=vec_config.chroma_host,
        chroma_port=vec_config.chroma_port,
        chroma_data_path=vec_config.chroma_data_path
    )
        
    run_cleanup(cortex)

if __name__ == "__main__":
    main()
