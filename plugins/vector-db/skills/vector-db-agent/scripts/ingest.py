#!/usr/bin/env python3
"""
ingest.py (CLI)
=====================================

Purpose:
    Vector Ingestion: Chunks code/docs and generates embeddings via VectorDBOperations.

Layer: Curate / Vector

Usage Examples:
    python plugins/vector-db/scripts/ingest.py --help

CLI Arguments:
    --full          : Full rebuild (purge + ingest all)
    --folder        : Ingest specific folder
    --file          : Ingest specific file
    --since         : Ingest files changed in last N hours (e.g., --since 24)
    --query         : Test query against the database
    --stats         : Show database statistics
    --purge         : Purge database only
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from langchain_core.documents import Document

import os
from dotenv import load_dotenv

load_dotenv()

# Project paths
SCRIPT_DIR = Path(__file__).parent
project_root_fallback = SCRIPT_DIR.parent.parent.parent
if str(project_root_fallback) not in sys.path:
    sys.path.append(str(project_root_fallback))

PROJECT_ROOT = project_root_fallback

# Manifest Configuration
MANIFEST_PATH = PROJECT_ROOT / "plugins" / "vector-db" / "ingest_manifest.json"

def load_manifest():
    if MANIFEST_PATH.exists():
        try:
            with open(MANIFEST_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error reading manifest: {e}")
    return None

manifest = load_manifest()
if manifest:
    DEFAULT_DIRS = manifest.get("include", ["legacy-system"])
    EXCLUDE_PATTERNS = manifest.get("exclude", [])
    print(f"📋 Loaded configuration from manifest ({len(DEFAULT_DIRS)} paths)")
else:
    print("⚠️  Manifest not found, using fallback defaults.")
    DEFAULT_DIRS = ["legacy-system"]
    EXCLUDE_PATTERNS = ["/archive/", "/.git/", "/node_modules/"]

# RLM Integration
try:
    from tools.codify.rlm.rlm_config import RLMConfig
    rlm_config = RLMConfig(run_type="legacy")
    RLM_CACHE_PATH = rlm_config.cache_path
except ImportError:
    RLM_CACHE_PATH = PROJECT_ROOT / ".agent" / "learning" / "rlm_summary_cache.json"

def load_rlm_cache() -> Dict[str, Any]:
    if RLM_CACHE_PATH.exists():
        try:
            with open(RLM_CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            pass
    return {}

# Code Shim
try:
    sys.path.append(str(Path(__file__).parent))
    from ingest_code_shim import convert_code_file
except ImportError:
    def convert_code_file(p): return p.read_text(errors='ignore')

def should_skip(path: Path) -> bool:
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False

def collect_files(targets: List[str], since_hours: Optional[int] = None) -> List[Path]:
    files = []
    cutoff_time = datetime.now().timestamp() - (since_hours * 3600) if since_hours else None
    CODE_EXTS = {".xml", ".sql", ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".pll", ".fmb"} 
    ALL_EXTS = {".md", ".txt"} | CODE_EXTS

    for target in targets:
        path = PROJECT_ROOT / target
        if not path.exists(): continue
            
        if path.is_file():
            if path.suffix.lower() in ALL_EXTS:
                if cutoff_time and path.stat().st_mtime < cutoff_time: continue
                files.append(path)
        else:
            for root, _, filenames in os.walk(path):
                for name in filenames:
                    f_path = Path(root) / name
                    if f_path.suffix.lower() in ALL_EXTS and not should_skip(f_path):
                        if cutoff_time and f_path.stat().st_mtime < cutoff_time: continue
                        files.append(f_path)
    return list(set(files))

def create_document_with_context(file_path: Path, rlm_cache: Dict[str, Any]) -> Optional[Document]:
    try:
        if file_path.suffix.lower() in [".md", ".txt"]:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        else:
            content = convert_code_file(file_path)

        if not content or not content.strip(): return None

        rel_path = str(file_path.relative_to(PROJECT_ROOT))
        
        rlm_entry = rlm_cache.get(rel_path, {})
        summary = rlm_entry.get("summary", "")
        
        augmented_content = f"[CONTEXT: {summary}]\\n\\n{content}" if summary else content
        
        return Document(
            page_content=augmented_content,
            metadata={
                "source": rel_path,
                "filename": file_path.name,
                "has_rlm_context": bool(summary),
                "file_type": file_path.suffix
            }
        )
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        return None

# Import decoupled operations library
sys.path.append(str(Path(__file__).parent))
from operations import VectorDBOperations

def main():
    parser = argparse.ArgumentParser(description="Project Vector DB Ingestion via Cortex")
    parser.add_argument("--full", action="store_true", help="Full rebuild (purge + ingest all)")
    parser.add_argument("--folder", type=str, help="Ingest specific folder")
    parser.add_argument("--file", type=str, help="Ingest specific file")
    parser.add_argument("--since", type=int, metavar="HOURS", help="Ingest files changed in last N hours (e.g., --since 24)")
    parser.add_argument("--query", type=str, help="Test query against the database")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--purge", action="store_true", help="Purge database only")
    # Note: --cleanup removed as VectorDBOperations manages orphaned context via overwrite on full syncs
    
    args = parser.parse_args()
    
    # Initialize operations module
    cortex = VectorDBOperations(str(PROJECT_ROOT))
    
    # Read-only operations
    if args.stats:
        stats = cortex.get_stats()
        print(f"\\n📊 Vector DB Stats")
        print(json.dumps(stats, indent=2))
        return
        
    if args.query:
        print(f"\\n🔍 Querying: {args.query}")
        results = cortex.query(args.query)
        for i, r in enumerate(results, 1):
            print(f"\\n--- Result {i} (score: {r['score']:.4f}) ---")
            print(f"Source: {r['source']} (Parent: {r['parent_id_matched']})")
            print(f"Has RLM Context: {r['has_rlm_context']}")
            print(r['content'][:500] + "..." if len(r['content']) > 500 else r['content'])
        return
        
    if args.purge:
        cortex.purge()
        print("✅ Database purged")
        return
        
    # Ingestion modes
    if args.full:
        print("🚀 Full Vector DB Rebuild")
        cortex.purge()
        targets = DEFAULT_DIRS
    elif args.folder:
        print(f"📂 Ingesting folder: {args.folder}")
        targets = [args.folder]
    elif args.file:
        print(f"📄 Ingesting file: {args.file}")
        targets = [args.file]
    elif args.since:
        print(f"⏰ Ingesting files changed in last {args.since} hours")
        targets = DEFAULT_DIRS
    else:
        parser.print_help()
        return

    print("📖 Loading RLM cache for Super-RAG context injection...")
    rlm_cache = load_rlm_cache()
    
    files = collect_files(targets, since_hours=args.since)
    print(f"📁 Found {len(files)} files to ingest")
    if not files: return
    
    documents = []
    total_docs = 0
    total_chunks = 0
    total_parents = 0
    start_time = time.time()
    
    BATCH_SIZE = 100
    print(f"⚡ Ingesting in batches of {BATCH_SIZE}...")
    
    for i, f in enumerate(files, 1):
        doc = create_document_with_context(f, rlm_cache)
        if doc: documents.append(doc)
            
        if len(documents) >= BATCH_SIZE or i == len(files):
            stats = cortex.ingest_documents(documents)
            total_chunks += stats["chunks"]
            total_parents += stats["parents"]
            total_docs += len(documents)
            
            sys.stdout.write(f"\\r   [{i}/{len(files)}] Processed {len(documents)} docs -> {stats['parents']} parents, {stats['chunks']} chunks")
            sys.stdout.flush()
            if i == len(files): print()
            documents = []
            
    elapsed = time.time() - start_time
    print(f"\\n✅ Ingestion Complete!")
    print(f"   Documents: {total_docs}")
    print(f"   Parent Blocks: {total_parents}")
    print(f"   Child Chunks: {total_chunks}")
    print(f"   Time: {elapsed:.2f}s")

if __name__ == "__main__":
    main()
