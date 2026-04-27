---
concept: robustly-discover-the-project-root
source: plugin-code
source_file: vector-db/scripts/audit_vector.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.431761+00:00
cluster: path
content_hash: 56515967aa9259cb
---

# Robustly discover the Project Root

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/vector-db/scripts/audit_vector.py -->
#!/usr/bin/env python
"""
audit_vector.py
=====================================

Purpose:
    Compares the Vector DB index against the live filesystem (based on profiles)
    and reports coverage gaps. Produces CSV and text reports of missing files.

Layer: Retrieve / Curate

Usage:
    python audit_vector.py --profile wiki --csv ./missing_vector.csv --report ./vector_audit.txt
"""

import sys
import argparse
import csv
from pathlib import Path
from datetime import datetime
from typing import Set, List, Dict, Any, Optional

# Robustly discover the Project Root
def _find_project_root(start_path: Path) -> Path:
    """Walks up from start_path to find the first directory containing .git."""
    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
    return current.parents[2]

PROJECT_ROOT = _find_project_root(Path(__file__))
SCRIPT_DIR = Path(__file__).resolve().parent

# Ensure local imports work correctly
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from vector_config import VectorConfig
    from operations import VectorDBOperations
except ImportError as e:
    print(f"[ERROR] Could not import vector dependencies from {SCRIPT_DIR}: {e}")
    sys.exit(1)


def run_audit(profile_name: str, csv_path: Optional[str] = None, report_path: Optional[str] = None) -> None:
    """
    Performs the actual comparison between manifest and vector store.

    Args:
        profile_name: The Vector profile to audit.
        csv_path: Optional path to save CSV of missing files.
        report_path: Optional path to save a detailed summary report.
    """
    try:
        config = VectorConfig(profile_name=profile_name, project_root=str(PROJECT_ROOT))
    except (SystemExit, Exception) as e:
        print(f"[ERROR] Failed to load profile '{profile_name}': {e}")
        return

    print(f"[AUDIT] Starting Vector DB Audit for profile: {profile_name}")
    
    # 1. Collect all expected files from the manifest
    manifest = config.load_manifest()
    fs_files = manifest.get_files()
    total_expected = len(fs_files)
    print(f"   Searching for {total_expected} manifest files in Vector DB...")

    # 2. Check Vector DB status
    cortex = VectorDBOperations(
        str(PROJECT_ROOT),
        child_collection=config.child_collection,
        parent_collection=config.parent_collection,
        chroma_host=config.chroma_host,
        chroma_port=config.chroma_port,
        chroma_data_path=config.chroma_data_path,
        embedding_model=config.embedding_model,
        parent_chunk_size=config.parent_chunk_size,
        parent_chunk_overlap=config.parent_chunk_overlap,
        child_chunk_size=config.child_chunk_size,
        child_chunk_overlap=config.child_chunk_overlap,
        device=config.device
    )

    # Get all sources currently in the child collection
    try:
        collection_obj = cortex.chroma_client.get_collection(name=config.child_collection)
        all_data = collection_obj.get(include=['metadatas'])
        indexed_sources: Set[str] = set()
        if all_data and 'metadatas' in all_data:
            for meta in all_data['metadatas']:
                if meta and 'source' in meta:
                    indexed_sources.add(meta['source'])
    except Exception as e:
        print(f"[ERROR] Failed to query ChromaDB: {e}")
        return

    missing: List[str] = []
    found_count = 0
    
    for rel_path in fs_files:
        clean_path = str(rel_path).replace("\\", "/")
        if clean_path in indexed_sources:
            found_count += 1
        else:
            missing.append(clean_path)

    missing_count = len(missing)
    coverage_pct = (found_count / total_expected * 100) if total_expected > 0 else 0
    gap_pct = (missing_count / total_expected * 100) if total_expected > 0 else 0

    # 3. Build Report String
    report_lines = [
        "--- VECTOR DB INVENTORY AUDIT ---",
        f"Gen

*(content truncated)*

<!-- Source: plugin-code/vector-db/scripts/cleanup.py -->
#!/usr/bin/env python
"""
cleanup.py
=====================================

Purpose:
    Removes stale chunk entries for files that have been deleted or renamed
    on disk, keeping the ChromaDB vector store in sync with the filesystem.

Layer: Curate / Retrieve

Usage:
    python cleanup.py --profile wiki
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Robustly discover the Project Root
def _find_project_root(start_path: Path) -> Path:
    """Walks up from start_path to find the first directory containing .git."""
    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
    return current.parents[2]

PROJECT_ROOT = _find_project_root(Path(__file__))
SCRIPT_DIR = Path(__file__).resolve().pare

*(combined content truncated)*

## See Also

- [[add-project-root-to-syspath]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[match-pythonexecution-paths-that-are-hardcoded-to-the-repo-root-plugins-folder]]
- [[project-root]]
- [[1-check-root-structure]]
- [[1-handle-absolute-paths-from-repo-root]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/scripts/audit_vector.py`
- **Indexed:** 2026-04-27T05:21:04.431761+00:00
