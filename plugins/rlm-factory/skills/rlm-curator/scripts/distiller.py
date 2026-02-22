#!/usr/bin/env python3
"""
distiller.py
=====================================

Purpose:
    RLM Engine: Recursively summarizes repository files using Ollama.
    Reads from a named profile in rlm_profiles.json and writes summaries
    to the corresponding cache JSON (crash-resilient, incremental).

Layer: Curate / Rlm

Usage:
    python plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py --profile plugins
    python plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py --profile tools --file path/to/file.py --force
    python plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py --profile plugins --since 24

Related:
    - rlm_config.py (configuration & utilities)
    - cleanup_cache.py (orphan removal)
    - inventory.py (coverage audit)
"""
import os
import sys
import json
import time
import argparse
import traceback
import requests
from string import Template
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# ============================================================
# PATHS
# File is at: plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py
# Root is 6 levels up (scripts→rlm-curator→skills→rlm-factory→plugins→ROOT)
# ============================================================
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

# Ollama HTTP endpoint (overridable via OLLAMA_HOST env var)
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434") + "/api/generate"

# Global debug flag — set via --debug CLI argument
DEBUG_MODE = False


def debug(msg: str) -> None:
    """Print a debug message if DEBUG_MODE is enabled."""
    if DEBUG_MODE:
        print(f"[DEBUG] {msg}")


# ----------------------------------------------------------
# call_ollama — LLM summarization via local HTTP API
# ----------------------------------------------------------
def call_ollama(
    content: str,
    file_path: str,
    prompt_template: str,
    model_name: str
) -> Optional[str]:
    """
    Submit a file's content to Ollama and return the generated summary.

    Truncates content exceeding 12,000 characters to stay within context limits.
    Cleans up common LLM output artifacts before returning.

    Args:
        content: Raw file text to summarize.
        file_path: Relative path of the file (injected into the prompt).
        prompt_template: Prompt string with `{file_path}` and `{content}` placeholders.
        model_name: Ollama model identifier (e.g. `granite3.2:8b`).

    Returns:
        Cleaned summary string, or None if Ollama returned an error/timeout.
    """
    # Truncate large files to avoid context overflow
    if len(content) > 12000:
        content = content[:12000] + "\n...[TRUNCATED]..."

    # Convert gold-standard `{var}` placeholders to Template `$var` format
    template_str = (
        prompt_template
        .replace("{file_path}", "${file_path}")
        .replace("{content}", "${content}")
    )
    prompt = Template(template_str).safe_substitute(file_path=file_path, content=content)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"num_ctx": 4096, "temperature": 0.1}
            },
            timeout=300
        )
        if response.status_code == 200:
            summary = response.json().get("response", "").strip()
            # Strip common preamble artifacts
            if summary.startswith("Here is"):
                summary = summary.split(":", 1)[-1].strip()
            # Strip markdown code fences if the model wrapped output
            if summary.startswith("```"):
                lines = summary.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                summary = "\n".join(lines).strip()
            return summary
        else:
            print(f"⚠️ Ollama error {response.status_code}: {response.text[:100]}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Ollama at {OLLAMA_URL}. Run: ollama serve")
        return None
    except Exception as e:
        print(f"⚠️ Ollama request failed: {e}")
        return None


# ----------------------------------------------------------
# distill — main incremental distillation loop
# ----------------------------------------------------------
def distill(
    config: RLMConfig,
    target_files: Optional[List[Path]] = None,
    force: bool = False,
    injected_summary: Optional[str] = None
) -> None:
    """
    Iterate over target files, generate summaries via Ollama, and persist the cache.

    Skips files whose content hash matches the existing cache entry (unless
    `force=True`). Writes the cache after every successful distillation to
    ensure crash-resilience.

    Args:
        config: Active RLMConfig providing manifest, cache path, and model.
        target_files: Explicit file list; if None, uses collect_files(config).
        force: If True, ignores existing cache entries and re-distills everything.
        injected_summary: Pre-generated summary to use instead of calling Ollama.
    """
    print(f"RLM Distiller [{config.profile_name.upper()}] — {config.description}")
    print(f"   Cache: {config.cache_path.name}")
    print("=" * 50)

    cache: Dict = load_cache(config.cache_path)
    files = target_files if target_files is not None else collect_files(config)
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

            # Cache hit: skip unless forced
            if not force and rel_path in cache and cache[rel_path].get("hash") == content_hash:
                stats["hits"] += 1
                if i == 1 or i % 20 == 0 or i == total:
                    print(f"   [{i}/{total}] {rel_path} [CACHE HIT]")
                continue

            print(f"   [{i}/{total}] Distilling {rel_path}...")

            summary = injected_summary or call_ollama(
                content, rel_path, config.prompt_template, config.llm_model
            )

            if summary:
                cache[rel_path] = {
                    "hash": content_hash,
                    "summary": summary,
                    "summarized_at": datetime.now().isoformat()
                }
                # Persist immediately for crash resilience
                save_cache(cache, config.cache_path)
                stats["processed"] += 1
            else:
                stats["errors"] += 1

        except Exception as e:
            stats["errors"] += 1
            print(f"❌ Error processing {file_path}: {e}")
            if DEBUG_MODE:
                traceback.print_exc()

    duration = time.time() - start_time
    print("=" * 50)
    print(f"✅ Distillation complete in {duration:.1f}s")
    print(f"   Processed: {stats['processed']} | Hits: {stats['hits']} | Errors: {stats['errors']}")


# ----------------------------------------------------------
# run_cleanup — stale entry removal
# ----------------------------------------------------------
def run_cleanup(config: RLMConfig) -> int:
    """
    Remove cache entries whose source files no longer exist on disk.

    Args:
        config: Active RLMConfig providing the cache path.

    Returns:
        Number of entries removed.
    """
    print("🧹 Running cleanup for stale cache entries...")
    cache = load_cache(config.cache_path)
    stale = [k for k in cache if not (PROJECT_ROOT / k).exists()]

    if not stale:
        print("   ✅ No stale entries found.")
        return 0

    for k in stale:
        del cache[k]
    save_cache(cache, config.cache_path)
    print(f"   ✅ Removed {len(stale)} stale entries.")
    return len(stale)


# ============================================================
# CLI ENTRY POINT
# ============================================================
def main() -> None:
    """Parse CLI arguments and dispatch to distill() or run_cleanup()."""
    parser = argparse.ArgumentParser(description="RLM Distiller — Ollama-powered semantic cache builder")
    parser.add_argument("--profile", required=True, help="RLM profile name (from rlm_profiles.json)")
    parser.add_argument("--file", "-f", help="Single file to process (relative to project root)")
    parser.add_argument("--force", action="store_true", help="Re-distill even if hash matches cache")
    parser.add_argument("--cleanup", action="store_true", help="Remove stale entries before distilling")
    parser.add_argument("--since", type=int, metavar="HOURS", help="Only process files changed in last N hours")
    parser.add_argument("--summary", help="Inject a pre-generated summary (skips Ollama)")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug logging")

    args = parser.parse_args()

    if args.debug:
        global DEBUG_MODE
        DEBUG_MODE = True

    try:
        config = RLMConfig(profile_name=args.profile)

        if args.cleanup:
            run_cleanup(config)

        # Determine the target file set
        target_files: Optional[List[Path]] = None
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
