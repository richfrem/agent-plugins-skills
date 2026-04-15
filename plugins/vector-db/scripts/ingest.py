#!/usr/bin/env python3
"""
ingest.py (CLI)
=====================================

Purpose:
    Command-line interface for the Vector DB ingestion pipeline.
    Parses the project manifest and feeds documentation/code into the Vector backend.
"""

import sys
import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path
from langchain_core.documents import Document

# Project paths
# ============================================================
# CONFIG / PATHS
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

from vector_config import VectorConfig
from operations import VectorDBOperations

# Try to import RLM for code context injection if available
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


def main():
    parser = argparse.ArgumentParser(description="Ingest documentation into Vector DB")
    parser.add_argument("--profile", type=str, help="Vector DB profile to use (e.g., wiki)")
    parser.add_argument("--full", action="store_true", help="Force full re-indexing (wipes database)")
    parser.add_argument("--since", type=int, help="Only ingest files modified in last N hours")
    parser.add_argument("--file", type=str, help="Ingest a specific file relative to root")
    parser.add_argument("--folder", type=str, help="Ingest a specific folder relative to root")
    
    args = parser.parse_args()
    
    # 1. Load configuration from JSON profile (no .env)
    vec_config = VectorConfig(profile_name=args.profile, project_root=str(PROJECT_ROOT))
    manifest = vec_config.load_manifest()
    
    # 1b. Attempt to load paired RLM profile for Super-RAG Context Injection
    rlm_cache = {}
    HAS_RLM = False
    if HAS_RLM_IMPORTS:
        try:
            rlm_config = RLMConfig(profile_name=vec_config.profile_name, project_root=PROJECT_ROOT)
            rlm_cache = load_cache(rlm_config.cache_path)
            HAS_RLM = True
            print(f"[RLM] Integration Active: Loaded cache for Super-RAG injection.")
        except SystemExit:
            print(f"[WARN] No paired RLM profile for '{vec_config.profile_name}'. Proceeding without Super-RAG.")
        except Exception as e:
            print(f"[WARN] RLM error: {e}")
    
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
        print("[PURGE] Wipe and Re-index requested.")
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
            print(f"[TIME] Incremental ingest: Checking files modified since {cutoff.strftime('%Y-%m-%d %H:%M')}")
        else:
            # Default to checking everything
            target_files = manifest.get_files()
            print("[SYNC] Smart Sync: Checking all files for changes...")

    if not target_files:
        print("[OK] No files found to ingest.")
        return

    print(f"[RUN] Processing {len(target_files)} files...")
    
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
                "source": rel_path.replace("\\", "/"),
                "type": full_path.suffix.lstrip('.'),
                "last_modified": os.path.getmtime(full_path),
                "has_rlm_context": False
            }
            
            # Super-RAG Injection
            if HAS_RLM and rlm_cache:
                rlm_entry = rlm_cache.get(rel_path.replace("\\", "/"))
                if rlm_entry and "summary" in rlm_entry:
                    summary_text = rlm_entry["summary"]
                    content = f"--- RLM SUPER-RAG CONTEXT ---\n{summary_text}\n---------------------------\n\n{content}"
                    metadata["has_rlm_context"] = True
            
            # Ingest via Core
            doc = Document(page_content=content, metadata=metadata)
            res = cortex.ingest_documents([doc])
            
            stats["success"] += 1
            stats["chunks"] += res.get("chunks", 0)
            
            if i % 100 == 0:
                print(f"   ... Progress: {i}/{len(target_files)} (Chunks: {stats['chunks']})")
                
        except Exception as e:
            print(f"[ERROR] Ingesting {rel_path}: {e}")
            stats["failed"] += 1

    print(f"\n[DONE] Ingestion Finished:")
    print(f"   - Success: {stats['success']}")
    print(f"   - Failed:  {stats['failed']}")
    print(f"   - Skipped: {stats['skipped']}")
    print(f"   - Chunks:  {stats['chunks']}")


if __name__ == "__main__":
    main()
