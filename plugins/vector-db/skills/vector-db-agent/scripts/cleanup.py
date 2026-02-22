#!/usr/bin/env python3
"""
cleanup.py (CLI)
=====================================

Purpose:
    Removes stale chunk entries for files that have been deleted or renamed on disk.
    Not strictly required due to complete overwrite logic on ingested parents, but useful for manual sweeps.

Usage Example:
    python plugins/vector-db/skills/vector-db-agent/scripts/cleanup.py
"""

import sys
from pathlib import Path

# Project paths
SCRIPT_DIR = Path(__file__).parent
project_root_fallback = SCRIPT_DIR.parent.parent.parent
if str(project_root_fallback) not in sys.path:
    sys.path.append(str(project_root_fallback))

PROJECT_ROOT = project_root_fallback

try:
    from operations import VectorDBOperations
except ImportError:
    sys.path.append(str(SCRIPT_DIR))
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
    
    for i, meta in enumerate(all_data.get('metadatas', [])):
        source = meta.get('source', '')
        if source:
            doc_id = all_data['ids'][i]
            if source not in id_to_source:
                id_to_source[source] = []
            id_to_source[source].append(doc_id)
    
    stale_ids = []
    stale_count = 0
    for rel_path, ids in id_to_source.items():
        full_path = Path(cortex.project_root) / rel_path
        if not full_path.exists():
            stale_ids.extend(ids)
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
    cortex = VectorDBOperations(str(PROJECT_ROOT))
    run_cleanup(cortex)

if __name__ == "__main__":
    main()
