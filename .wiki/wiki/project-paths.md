---
concept: project-paths
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/vector-db-ingest/scripts/ingest.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.391807+00:00
cluster: import
content_hash: 2848da549def4597
---

# Project paths

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/vector-db-ingest/scripts/ingest.py -->
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
# File is at: ./scripts/ingest.py
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
    parser.add_argument("--profile", type=str, help="Vector DB profile to use (e.g., knowledge)")
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
            rlm_config = RLMConfig(profile_name=args.profile, project_root=PROJECT_ROOT)
            rlm_cache = load_cache(rlm_config.cache_path)
            HAS_RLM = True
            print(f"🧠 RLM Integration Active: Loaded cache for Super-RAG injection.")
        except SystemExit:
            print(f"⚠️ No paired RLM profile for '{args.profile}'. Proceeding without Super-RAG.")
    
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
            targ

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/vector-db-search/scripts/ingest.py -->
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
# File is at: ./scripts/ingest.py
# ============================================================
# CONFIG / PATHS
# ============================================================
def _fi

*(combined content truncated)*

## See Also

- [[1-handle-absolute-paths-from-repo-root]]
- [[add-project-root-to-syspath]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[match-pythonexecution-paths-that-are-hardcoded-to-the-repo-root-plugins-folder]]
- [[ordered-list-of-marker-files-label-env-vars-for-project-type-detection]]
- [[paths]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/vector-db-ingest/scripts/ingest.py`
- **Indexed:** 2026-04-27T05:21:04.391807+00:00
