---
concept: as-a-library
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/tool-inventory/scripts/tool_chroma.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.372408+00:00
cluster: tool
content_hash: 34f3007cea9cba1e
---

# As a library

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python3
"""
tool_chroma.py (CLI)
=====================================

Purpose:
    Dedicated ChromaDB vector store for tool discovery. Provides semantic
    search over tool summaries without requiring Ollama or external services.

Layer: Curate / Tool-Inventory

Usage Examples:
    # As a library
    from tool_chroma import ToolChroma
    tc = ToolChroma()
    tc.upsert("plugins/example_script.py", "CLI router", {"category": "orchestrator"})
    results = tc.search("distiller", n=5)

    # As a CLI
    python3 plugins/tool-inventory/scripts/tool_chroma.py stats
    python3 plugins/tool-inventory/scripts/tool_chroma.py search "query cache"
    python3 plugins/tool-inventory/scripts/tool_chroma.py list
    python3 plugins/tool-inventory/scripts/tool_chroma.py import-json .agents/learning/rlm_tool_cache.json

Supported Object Types:
    - Tool Inventory JSON / RLM cache entries

CLI Arguments:
    stats            - Show collection statistics
    list             - List all entries
    search <query>   - Semantic search, optional -n for result count
    import-json      - Import from rlm_tool_cache.json

Input Files:
    - .agents/learning/rlm_tool_cache.json (for import-json command)

Output:
    - Persistent ChromaDB collection at plugins/tool-inventory/data/chroma/

Key Functions:
    - ToolChroma.__init__: Initializes ChromaDB persistent client.
    - ToolChroma.upsert: Adds or updates a tool entry.
    - ToolChroma.search: Semantic search over tool summaries.
    - ToolChroma.import_from_json: Bulk import from RLM cache file.
    - main: CLI dispatcher.

Script Dependencies:
    - chromadb (pip install chromadb)

Consumed by:
    - manage_tool_inventory.py (optional semantic search feature)
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

    def __init__(self, persist_dir: Optional[str] = None) -> None:
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
            n_results=m

*(content truncated)*

## See Also

- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[atomically-replace-an-existing-path-with-a-new-symlink-pointing-to-src]]
- [[audit-a-single-file]]
- [[data-is-a-dict-of-id-iso-timestamp-prune-entries-outside-dedup-window]]
- [[extract-row-count-if-data-has-a-recognizable-structure]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/tool-inventory/scripts/tool_chroma.py`
- **Indexed:** 2026-04-27T05:21:04.372408+00:00
