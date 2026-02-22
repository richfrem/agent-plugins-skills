#!/usr/bin/env python3
"""
query.py (CLI)
=====================================

Purpose:
    Command-line interface for semantic search over the Vector DB index.
    Outputs results retrieved from the underlying Parent Store via the Child search match.

Usage Example:
    python plugins/vector-db/skills/vector-db-agent/scripts/query.py "what is the protocol for learning loops?"
"""

import sys
import argparse
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

def main():
    parser = argparse.ArgumentParser(description="Query the Vector DB")
    parser.add_argument("query", type=str, help="The semantic search query string")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of parent documents to return")
    
    args = parser.parse_args()
    
    cortex = VectorDBOperations(str(PROJECT_ROOT))
    
    print(f"\\n🔍 Searching Vector Index for: '{args.query}'\\n")
    results = cortex.query(args.query, max_results=args.limit)
    
    if not results:
        print("⚠️ No matching context found.")
        return
        
    for i, r in enumerate(results, 1):
        score = r.get("score", 0.0)
        source = r.get("source", "unknown")
        parent_id = r.get("parent_id_matched", "none")
        content = r.get("content", "")
        
        print(f"\\n{'='*60}")
        print(f"🏆 Result {i} (Score: {score:.4f})")
        print(f"📄 Source: {source}")
        print(f"🧩 Parent Chunk: {parent_id}")
        if r.get("has_rlm_context"):
            print(f"🧠 RLM Summary Super-RAG Applied")
        print(f"{'-'*60}")
        
        # Display an excerpt to prevent terminal flooding
        if len(content) > 1000:
            print(content[:1000] + "\\n... [TRUNCATED] ...")
        else:
            print(content)

if __name__ == "__main__":
    main()
