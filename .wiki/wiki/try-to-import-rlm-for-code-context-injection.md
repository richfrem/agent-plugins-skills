---
concept: try-to-import-rlm-for-code-context-injection
source: plugin-code
source_file: vector-db/scripts/ingest.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.430844+00:00
cluster: vec_config
content_hash: c2e932c3f232a39f
---

# Try to import RLM for code context injection

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
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
    import time
    start_time = time.perf_counter()
    print(f"\n[RUN] Starting Environment Setup at {datetime.now().strftime('%H:%M:%S')}")

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
        parent_chunk_overlap=vec_conf

*(content truncated)*

## See Also

- [[pre-parse-for---headless-to-set-non-interactive-backend-before-pyplot-import]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]
- [[add-the-scripts-directory-so-we-can-import-rlm-config]]
- [[attempt-to-handle-langchain-version-differences-for-storage]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/scripts/ingest.py`
- **Indexed:** 2026-04-27T05:21:04.430844+00:00
