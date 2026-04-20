#!/usr/bin/env python
"""
query.py
=====================================

Purpose:
    Command-line interface for semantic search over the Vector DB index.
    Outputs results retrieved from the underlying Parent Store via the Child search match.

Layer: Retrieve

Usage:
    python query.py "search text" --profile wiki
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

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


def main() -> None:
    """Main entry point for the query CLI."""
    parser = argparse.ArgumentParser(description="Query the Vector DB")
    parser.add_argument("query", type=str, help="The semantic search query string")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of parent documents to return")
    parser.add_argument("--profile", type=str, help="Vector DB profile to use (e.g., wiki)")
    
    args = parser.parse_args()
    
    # 1. Configuration Setup (Dynamic from profile)
    vec_config = VectorConfig(profile_name=args.profile, project_root=str(PROJECT_ROOT))
    
    # 2. Operations Setup with profile settings
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
    
    print(f"\n[QUERY] Searching Vector Index for: '{args.query}'\n")
    results = cortex.query(args.query, max_results=args.limit)
    
    if not results:
        print("[WARN] No matching context found.")
        return
        
    for i, r in enumerate(results, 1):
        score = r.get("score", 0.0)
        source = r.get("source", "unknown")
        parent_id = r.get("parent_id_matched", "none")
        content = r.get("content", "")
        
        print(f"\n{'='*60}")
        print(f"[RESULT {i}] (Score: {score:.4f})")
        print(f"Source: {source}")
        print(f"Chunk ID: {parent_id}")
        if r.get("has_rlm_context"):
            print(f"[RLM] Super-RAG Context Applied")
        print(f"{'-'*60}")
        
        # Display an excerpt to prevent terminal flooding
        if len(content) > 1000:
            print(content[:1000] + "\n... [TRUNCATED] ...")
        else:
            print(content)


if __name__ == "__main__":
    main()
