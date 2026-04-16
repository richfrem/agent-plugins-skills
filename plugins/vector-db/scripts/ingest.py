#!/usr/bin/env python3
"""
ingest.py
=====================================

Purpose:
    Command-line interface for the Vector DB ingestion pipeline.
    Parses the project manifest and feeds documentation/code into the Vector backend
    using high-speed batching configured via vector_profiles.json.

Layer: Curate / Retrieve

Usage:
    python ingest.py --profile wiki
"""

import sys
import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from langchain_core.documents import Document

def _find_project_root(start_path: Path) -> Path:
    """Walks up from start_path to find the first directory containing .git."""
    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
    return current.parents[2]

PROJECT_ROOT = _find_project_root(Path(__file__))
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vector_config import VectorConfig
from operations import VectorDBOperations

# Try to import RLM for code context injection
HAS_RLM_IMPORTS = False
rlm_script_dir = PROJECT_ROOT / ".agents" / "skills" / "rlm-curator" / "scripts"
if rlm_script_dir.exists():
    if str(rlm_script_dir) not in sys.path:
        sys.path.insert(0, str(rlm_script_dir))
    try:
        from rlm_config import RLMConfig, load_cache
        HAS_RLM_IMPORTS = True
    except ImportError:
        pass

# Code shim for advanced parsing
try:
    import ingest_code_shim as code_shim
    HAS_CODE_SHIM = True
except ImportError:
    HAS_CODE_SHIM = False


def _load_rlm_cache(profile_name: str) -> Tuple[Dict, bool]:
    """Attempts to load a paired RLM cache for context injection."""
    if not HAS_RLM_IMPORTS:
        return {}, False
    try:
        rlm_config = RLMConfig(profile_name=profile_name, project_root=PROJECT_ROOT)
        return load_cache(rlm_config.cache_path), True
    except Exception:
        return {}, False


def ingest_batch(cortex: VectorDBOperations, docs: List[Document], current: int, total: int) -> int:
    """Ingests a single batch of documents and prints progress."""
    res = cortex.ingest_documents(docs)
    chunks = res.get("chunks", 0)
    print(f"   ... Progress: {current}/{total} (Chunks Created: {chunks})")
    return chunks


def main() -> None:
    """Main entry point for the ingestion CLI."""
    parser = argparse.ArgumentParser(description="Ingest documentation into Vector DB")
    parser.add_argument("--profile", type=str, help="Vector DB profile to use (e.g., wiki)")
    parser.add_argument("--full", action="store_true", help="Force full re-indexing (wipes database)")
    parser.add_argument("--since", type=int, help="Only ingest files modified in last N hours")
    parser.add_argument("--file", type=str, help="Ingest a specific file relative to root")
    parser.add_argument("--folder", type=str, help="Ingest a specific folder relative to root")
    
    args = parser.parse_args()
    
    # 1. Configuration Setup (Now dynamic from profile)
    vec_config = VectorConfig(profile_name=args.profile, project_root=str(PROJECT_ROOT))
    manifest = vec_config.load_manifest()
    rlm_cache, has_rlm = _load_rlm_cache(vec_config.profile_name)

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
        child_chunk_overlap=vec_config.child_chunk_overlap,
        device=vec_config.device
    )
    
    if args.full:
        print("[PURGE] Wipe and Re-index requested.")
        cortex.purge()
        target_files = manifest.get_files()
    elif args.file:
        target_files = [args.file]
    elif args.folder:
        target_files = manifest.get_files_in_folder(args.folder)
    else:
        if args.since:
            cutoff = datetime.now() - timedelta(hours=args.since)
            target_files = manifest.get_files_modified_since(cutoff)
        else:
            target_files = manifest.get_files()
            print("[SYNC] Smart Sync: Checking all files for changes...")

    if not target_files:
        print("[OK] No files found to ingest.")
        return

    import time
    start_time = time.perf_counter()
    print(f"\n[RUN] Starting Ingestion at {datetime.now().strftime('%H:%M:%S')}")
    print(f"[RUN] Processing {len(target_files)} files (Batch Size: {vec_config.batch_size})...")
    
    stats = {"success": 0, "failed": 0, "skipped": 0, "chunks": 0}
    docs_batch: List[Document] = []
    
    for i, rel_path in enumerate(target_files, 1):
        full_path = PROJECT_ROOT / rel_path
        if not full_path.exists():
            stats["skipped"] += 1
            continue
            
        try:
            if HAS_CODE_SHIM and full_path.suffix.lower() in ['.py', '.js', '.ts', '.tsx', '.xml', '.sql']:
                content = code_shim.convert_code_file(full_path) or full_path.read_text(encoding='utf-8', errors='replace')
            else:
                content = full_path.read_text(encoding='utf-8', errors='replace')
            
            metadata = {
                "source": rel_path.replace("\\", "/"),
                "type": full_path.suffix.lstrip('.'),
                "last_modified": os.path.getmtime(full_path),
                "has_rlm_context": False
            }
            
            if has_rlm:
                rlm_entry = rlm_cache.get(rel_path.replace("\\", "/"))
                if rlm_entry and "summary" in rlm_entry:
                    content = f"--- RLM SUPER-RAG CONTEXT ---\n{rlm_entry['summary']}\n---------------------------\n\n{content}"
                    metadata["has_rlm_context"] = True
            
            docs_batch.append(Document(page_content=content, metadata=metadata))
            
            # Batch size is now dynamic from vec_config.batch_size
            if len(docs_batch) >= vec_config.batch_size or i == len(target_files):
                stats["chunks"] += ingest_batch(cortex, docs_batch, i, len(target_files))
                stats["success"] += len(docs_batch)
                docs_batch = []
                
        except Exception as e:
            print(f"[ERROR] Ingesting {rel_path}: {e}")
            stats["failed"] += 1

    duration = time.perf_counter() - start_time
    print(f"\n[DONE] Ingestion Finished at {datetime.now().strftime('%H:%M:%S')}")
    print(f"[DONE] Total Duration: {duration:.2f} seconds")
    print(f"[DONE] Success: {stats['success']}, Chunks: {stats['chunks']}")


if __name__ == "__main__":
    main()
