#!/usr/bin/env python3
"""
distiller.py (CLI)
=====================================

Purpose:
    RLM Engine: Recursive summarization of repo content using Ollama.
"""

import os
import sys
import json
import time
import argparse
import requests
import traceback
from string import Template
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Paths standardization
# File is at: plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py
# Root is 6 levels up
PROJECT_ROOT = Path(__file__).resolve().parents[5]
SCRIPT_DIR = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from rlm_config import (
        RLMConfig,
        compute_hash,
        load_cache,
        save_cache,
        should_skip,
        collect_files
    )
except ImportError as e:
    print(f"❌ Could not import local RLMConfig from {SCRIPT_DIR}: {e}")
    sys.exit(1)

# Ollama Connection
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434") + "/api/generate"
DEBUG_MODE = False

def debug(msg: str):
    if DEBUG_MODE:
        print(f"[DEBUG] {msg}")

def call_ollama(content: str, file_path: str, prompt_template: str, model_name: str) -> Optional[str]:
    """Call Ollama to generate summary."""
    if len(content) > 12000:
        content = content[:12000] + "\n...[TRUNCATED]..."
    
    # Use standard Template substitution
    template_str = prompt_template.replace("{file_path}", "${file_path}").replace("{content}", "${content}")
    template = Template(template_str)
    prompt = template.safe_substitute(file_path=file_path, content=content)
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_ctx": 4096,
                    "temperature": 0.1
                }
            },
            timeout=300
        )
        
        if response.status_code == 200:
            summary = response.json().get("response", "").strip()
            # Clean up artifacts
            if summary.startswith("Here is"):
                summary = summary.split(":", 1)[-1].strip()
            if summary.startswith("```"):
                lines = summary.splitlines()
                if lines[0].startswith("```"): lines = lines[1:]
                if lines and lines[-1].startswith("```"): lines = lines[:-1]
                summary = "\n".join(lines).strip()
            return summary
        else:
            print(f"⚠️ Ollama error {response.status_code}: {response.text[:100]}")
            return None
    except Exception as e:
        print(f"⚠️ Error calling Ollama: {e}")
        return None

def distill(config: RLMConfig, target_files: List[Path] = None, force: bool = False, injected_summary: str = None):
    """Main distillation loop."""
    print(f"RLM Distiller [{config.profile_name.upper()}] - {config.description}")
    print(f"   Cache: {config.cache_path.name}")
    print("=" * 50)
    
    cache = load_cache(config.cache_path)
    files = target_files if target_files else collect_files(config)
    total = len(files)
    
    print(f"Processing {total} files...")
    stats = {"processed": 0, "hits": 0, "errors": 0}
    start_time = time.time()
    
    for i, file_path in enumerate(files, 1):
        try:
            rel_path = str(file_path.relative_to(PROJECT_ROOT))
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            if not content.strip():
                continue
            
            content_hash = compute_hash(content)
            
            # Cache check
            if not force and rel_path in cache and cache[rel_path].get("hash") == content_hash:
                stats["hits"] += 1
                if i == 1 or i % 20 == 0 or i == total:
                    print(f"   [{i}/{total}] {rel_path} [CACHE HIT]")
                continue

            print(f"   [{i}/{total}] Distilling {rel_path}...")
            
            if injected_summary:
                summary = injected_summary
            else:
                summary = call_ollama(content, rel_path, config.prompt_template, config.llm_model)
            
            if summary:
                cache[rel_path] = {
                    "hash": content_hash,
                    "summary": summary,
                    "summarized_at": datetime.now().isoformat()
                }
                save_cache(cache, config.cache_path)
                stats["processed"] += 1
            else:
                stats["errors"] += 1
                
        except Exception as e:
            stats["errors"] += 1
            print(f"❌ Error processing {file_path}: {e}")

    duration = time.time() - start_time
    print("=" * 50)
    print(f"Distillation Complete in {duration:.1f}s")
    print(f"   Processed: {stats['processed']} | Hits: {stats['hits']} | Errors: {stats['errors']}")

def run_cleanup(config: RLMConfig):
    """Remove stale entries for files that no longer exist."""
    print("🧹 Running cleanup for stale cache entries...")
    cache = load_cache(config.cache_path)
    stale_keys = [k for k in cache.keys() if not (PROJECT_ROOT / k).exists()]
    
    if not stale_keys:
        print("   ✅ No stale entries found.")
        return
    
    for k in stale_keys:
        del cache[k]
    save_cache(cache, config.cache_path)
    print(f"   ✅ Removed {len(stale_keys)} stale entries.")

def main():
    parser = argparse.ArgumentParser(description="RLM Distiller")
    parser.add_argument("--profile", required=True, help="RLM Profile name")
    parser.add_argument("--file", help="Single file to process")
    parser.add_argument("--force", action="store_true", help="Force re-distillation")
    parser.add_argument("--cleanup", action="store_true", help="Remove stale entries")
    parser.add_argument("--since", type=int, help="Process files changed in last N hours")
    parser.add_argument("--summary", help="Inject a pre-generated summary")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    if args.debug:
        global DEBUG_MODE
        DEBUG_MODE = True
        
    try:
        config = RLMConfig(profile_name=args.profile)
        
        if args.cleanup:
            run_cleanup(config)
            
        target_files = None
        if args.file:
            f_path = (PROJECT_ROOT / args.file).resolve()
            if not f_path.exists():
                print(f"❌ File not found: {args.file}")
                sys.exit(1)
            target_files = [f_path]
        elif args.since:
            cutoff = datetime.now().timestamp() - (args.since * 3600)
            target_files = [f for f in collect_files(config) if f.stat().st_mtime >= cutoff]
            
        distill(config, target_files=target_files, force=args.force, injected_summary=args.summary)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
