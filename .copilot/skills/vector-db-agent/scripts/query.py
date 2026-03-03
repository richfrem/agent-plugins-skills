#!/usr/bin/env python3
"""
query.py (CLI)
=====================================

Purpose:
    Command-line interface for semantic search over the Vector DB index.
    Outputs results retrieved from the underlying Parent Store via the Child search match.
"""

import sys
import argparse
from pathlib import Path

# Project paths
# File is at: plugins/vector-db/skills/vector-db-agent/scripts/query.py
PROJECT_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vector_config import VectorConfig
from operations import VectorDBOperations


def main():
    parser = argparse.ArgumentParser(description="Query the Vector DB")
    parser.add_argument("query", type=str, help="The semantic search query string")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of parent documents to return")
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
    
    print(f"\n🔍 Searching Vector Index for: '{args.query}'\n")
    results = cortex.query(args.query, max_results=args.limit)
    
    if not results:
        print("⚠️ No matching context found.")
        return
        
    for i, r in enumerate(results, 1):
        score = r.get("score", 0.0)
        source = r.get("source", "unknown")
        parent_id = r.get("parent_id_matched", "none")
        content = r.get("content", "")
        
        print(f"\n{'='*60}")
        print(f"🏆 Result {i} (Score: {score:.4f})")
        print(f"📄 Source: {source}")
        print(f"🧩 Parent Chunk: {parent_id}")
        if r.get("has_rlm_context"):
            print(f"🧠 RLM Summary Super-RAG Applied")
        print(f"{'-'*60}")
        
        # Display an excerpt to prevent terminal flooding
        if len(content) > 1000:
            print(content[:1000] + "\n... [TRUNCATED] ...")
        else:
            print(content)

if __name__ == "__main__":
    main()
