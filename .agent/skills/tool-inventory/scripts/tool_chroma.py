#!/usr/bin/env python3
"""
tool_chroma.py — Embedded ChromaDB wrapper for tool-inventory plugin
=====================================================================

Purpose:
    Dedicated vector store for tool discovery. Provides semantic search
    over tool summaries without requiring Ollama or external services.

Layer: Plugin / Tool-Inventory

Usage:
    # As a library (imported by manage_tool_inventory.py)
    from tool_chroma import ToolChroma
    tc = ToolChroma()
    tc.upsert("tools/cli.py", "CLI router for all sanctuary commands", {"category": "orchestrator"})
    results = tc.search("distiller", n=5)

    # As a CLI
    python3 plugins/tool-inventory/scripts/inventory.py
    python3 plugins/tool-inventory/scripts/tool_chroma.py stats
    python3 plugins/tool-inventory/scripts/tool_chroma.py search "query cache"
    python3 plugins/tool-inventory/scripts/tool_chroma.py list
    python3 plugins/tool-inventory/scripts/tool_chroma.py import-json .agent/learning/rlm_tool_cache.json
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Determine plugin data directory for persistent ChromaDB storage
SCRIPT_DIR = Path(__file__).parent.resolve()
PLUGIN_ROOT = SCRIPT_DIR.parent.resolve()
CHROMA_DATA_DIR = str(PLUGIN_ROOT / "data" / "chroma")

COLLECTION_NAME = "tool_summaries"


class ToolChroma:
    """Thin wrapper around ChromaDB for tool-specific semantic search."""

    def __init__(self, persist_dir: str = None):
        """Initialize ChromaDB client with persistent storage."""
        try:
            import chromadb
        except ImportError:
            print("❌ chromadb not installed. Run: pip install chromadb")
            sys.exit(1)

        self.persist_dir = persist_dir or CHROMA_DATA_DIR
        os.makedirs(self.persist_dir, exist_ok=True)

        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Tool summaries for semantic search"}
        )

    def upsert(self, tool_path: str, summary: str, metadata: Dict = None) -> bool:
        """Add or update a tool entry in the collection."""
        if not summary or summary == "TBD":
            return False

        meta = metadata or {}
        meta["last_updated"] = datetime.now().isoformat()
        meta["tool_path"] = tool_path

        # ChromaDB requires string values in metadata
        clean_meta = {k: str(v) for k, v in meta.items() if v is not None}

        self.collection.upsert(
            ids=[tool_path],
            documents=[f"{tool_path}: {summary}"],
            metadatas=[clean_meta]
        )
        return True

    def remove(self, tool_path: str) -> bool:
        """Remove a tool from the collection."""
        try:
            self.collection.delete(ids=[tool_path])
            return True
        except Exception:
            return False

    def search(self, query: str, n: int = 5) -> List[Dict]:
        """Semantic search for tools matching a query."""
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n, self.collection.count() or 1)
        )

        matches = []
        if results and results["ids"] and results["ids"][0]:
            for i, tool_id in enumerate(results["ids"][0]):
                match = {
                    "path": tool_id,
                    "summary": results["documents"][0][i] if results["documents"] else "",
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                }
                if results["metadatas"] and results["metadatas"][0]:
                    match["metadata"] = results["metadatas"][0][i]
                matches.append(match)

        return matches

    def list_all(self) -> List[Dict]:
        """Return all entries in the collection."""
        count = self.collection.count()
        if count == 0:
            return []

        results = self.collection.get(
            include=["documents", "metadatas"]
        )

        entries = []
        for i, tool_id in enumerate(results["ids"]):
            entry = {
                "path": tool_id,
                "summary": results["documents"][i] if results["documents"] else "",
            }
            if results["metadatas"] and results["metadatas"][i]:
                entry["metadata"] = results["metadatas"][i]
            entries.append(entry)

        return entries

    def get_stats(self) -> Dict:
        """Return collection statistics."""
        count = self.collection.count()
        return {
            "collection": COLLECTION_NAME,
            "entries": count,
            "persist_dir": self.persist_dir,
        }

    def import_from_json(self, json_path: str) -> int:
        """Import entries from an existing rlm_tool_cache.json file."""
        cache_path = Path(json_path)
        if not cache_path.exists():
            print(f"❌ Cache file not found: {json_path}")
            return 0

        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)

        imported = 0
        for tool_path, entry in cache.items():
            summary = entry.get("summary", "")
            if not summary or "[DISTILLATION FAILED]" in summary:
                continue

            # Parse structured summary if it's JSON
            if summary.startswith("{"):
                try:
                    parsed = json.loads(summary)
                    summary = parsed.get("purpose", summary)
                except json.JSONDecodeError:
                    pass

            meta = {
                "source": "rlm_tool_cache",
                "original_hash": entry.get("hash", ""),
            }

            if self.upsert(tool_path, summary, meta):
                imported += 1

        return imported


# ============================================================
# CLI Interface
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Tool ChromaDB Manager")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("stats", help="Show collection statistics")
    subparsers.add_parser("list", help="List all entries")

    search_p = subparsers.add_parser("search", help="Semantic search")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("-n", type=int, default=5, help="Number of results")

    import_p = subparsers.add_parser("import-json", help="Import from rlm_tool_cache.json")
    import_p.add_argument("json_path", help="Path to JSON cache file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    tc = ToolChroma()

    if args.command == "stats":
        stats = tc.get_stats()
        print(f"\n📊 Tool ChromaDB Stats")
        print(f"   Collection: {stats['collection']}")
        print(f"   Entries:    {stats['entries']}")
        print(f"   Storage:    {stats['persist_dir']}")

    elif args.command == "list":
        entries = tc.list_all()
        if not entries:
            print("📂 Collection is empty.")
        else:
            print(f"\n📂 {len(entries)} tools in collection:\n")
            for e in entries:
                print(f"  📦 {e['path']}")
                summary = e.get('summary', '')[:100]
                print(f"     {summary}")
                print()

    elif args.command == "search":
        results = tc.search(args.query, n=args.n)
        if not results:
            print(f"❌ No results for '{args.query}'")
        else:
            print(f"\n🔍 Top {len(results)} results for '{args.query}':\n")
            for r in results:
                dist = f" (distance: {r['distance']:.3f})" if 'distance' in r else ""
                print(f"  📦 {r['path']}{dist}")
                summary = r.get('summary', '')[:120]
                print(f"     {summary}")
                print()

    elif args.command == "import-json":
        count = tc.import_from_json(args.json_path)
        print(f"✅ Imported {count} entries from {args.json_path}")


if __name__ == "__main__":
    main()
