#!/usr/bin/env python3
"""
ingest.py (CLI)
=====================================

Purpose:
    Command-line interface for the Vector DB ingestion pipeline.
    Parses the project manifest and feeds documentation/code into the Vector backend.

Workflow:
    1. Resolve Project Root.
    2. Load Config from JSON Profile (VectorConfig).
    3. Initialize VectorDBOperations.
    4. Execute Ingestion (Since time or Full reset).
"""

import sys
import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path
from langchain_core.documents import Document

# Project paths
# File is at: plugins/vector-db/skills/vector-db-agent/scripts/ingest.py
# Root is 6 levels up (0: scripts, 1: agent, 2: skills, 3: vector-db, 4: plugins, 5: ROOT)
PROJECT_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vector_config import VectorConfig
from operations import VectorDBOperations

# Try to import RLM for code context injection if available
try:
    # This might be in a different plugin or legacy path
    from rlm_config import RLMConfig
    HAS_RLM = True
except ImportError:
    HAS_RLM = False

# Code shim for advanced parsing
try:
    import ingest_code_shim as code_shim
    HAS_CODE_SHIM = True
except ImportError:
    HAS_CODE_SHIM = False


def main():
    parser = argparse.ArgumentParser(description="Ingest documentation into Vector DB")
    parser.add_argument("--profile", type=str, help="Vector DB profile to use (e.g., knowledge)")
    parser.add_argument("--full", action="store_true", help="Force full re-indexing (wipes database)")
    parser.add_argument("--since", type=int, help="Only ingest files modified in last N hours")
    parser.add_argument("--file", type=str, help="Ingest a specific file relative to root")
    parser.add_argument("--folder", type=str, help="Ingest a specific folder relative to root")
    
    args = parser.parse_args()
    
    # 1. Load configuration from JSON profile (no .env)
    vec_config = VectorConfig(profile_name=args.profile, project_root=str(PROJECT_ROOT))
    manifest = vec_config.load_manifest()
    
    # 2. Initialize operations module with profile config
    cortex = VectorDBOperations(
        str(PROJECT_ROOT),
        child_collection=vec_config.child_collection,
        parent_collection=vec_config.parent_collection,
        chroma_host=vec_config.chroma_host,
        chroma_port=vec_config.chroma_port,
        chroma_data_path=vec_config.chroma_data_path
    )
    
    if args.full:
        print("💥 Wipe and Re-index requested.")
        cortex.purge()
        target_files = manifest.get_files()
    elif args.file:
        target_files = [args.file]
    elif args.folder:
        target_files = manifest.get_files_in_folder(args.folder)
    else:
        # Incremental by since hours
        if args.since:
            cutoff = datetime.now() - timedelta(hours=args.since)
            target_files = manifest.get_files_modified_since(cutoff)
            print(f"🕒 Incremental ingest: Checking files modified since {cutoff.strftime('%Y-%m-%d %H:%M')}")
        else:
            # Default to checking everything but only updating if file hash changed
            target_files = manifest.get_files()
            print("🔄 Smart Sync: Checking all files for changes...")

    if not target_files:
        print("✅ No files found to ingest.")
        return

    print(f"🚀 Processing {len(target_files)} files...")
    
    stats = {"success": 0, "failed": 0, "skipped": 0, "chunks": 0}
    
    for i, rel_path in enumerate(target_files, 1):
        full_path = PROJECT_ROOT / rel_path
        if not full_path.exists():
            stats["skipped"] += 1
            continue
            
        try:
            # Try to use code shim for structured parsing if applicable
            if HAS_CODE_SHIM and full_path.suffix.lower() in ['.py', '.js', '.ts', '.tsx', '.xml', '.sql']:
                content = code_shim.convert_code_file(full_path)
                if not content:
                    content = full_path.read_text(encoding='utf-8', errors='replace')
            else:
                content = full_path.read_text(encoding='utf-8', errors='replace')
            
            # Simple metadata
            metadata = {
                "source": rel_path,
                "type": full_path.suffix.lstrip('.'),
                "last_modified": os.path.getmtime(full_path)
            }
            
            # Ingest via Core
            doc = Document(page_content=content, metadata=metadata)
            res = cortex.ingest_documents([doc])
            
            stats["success"] += 1
            stats["chunks"] += res.get("chunks", 0)
            
            if i % 50 == 0:
                print(f"   ... Progress: {i}/{len(target_files)} (Chunks: {stats['chunks']})")
                
        except Exception as e:
            print(f"❌ Error ingesting {rel_path}: {e}")
            stats["failed"] += 1

    print(f"\n✨ Ingestion Finished:")
    print(f"   - Success: {stats['success']}")
    print(f"   - Failed:  {stats['failed']}")
    print(f"   - Skipped: {stats['skipped']}")
    print(f"   - Chunks:  {stats['chunks']}")


if __name__ == "__main__":
    main()
