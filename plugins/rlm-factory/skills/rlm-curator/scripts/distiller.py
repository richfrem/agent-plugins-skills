#!/usr/bin/env python3
"""
distiller.py (CLI)
=====================================

Purpose:
    RLM Engine: Recursive summarization of repo content using Ollama.

Layer: Curate / Rlm

Usage Examples:
    # 1. Distill a specific profile (Default)
    python plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py --profile plugins
    python plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py --profile plugins --since 24

    # 2. Force update
    python plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py --profile plugins --target plugins/rlm-factory/ --force

    IMPORTANT: Check tools/standalone/rlm_factory/manifest-index.json for defined profiles.
    - project: Documentation only (rlm_summary_cache.json)
    - tool:    Code/Scripts (rlm_tool_cache.json)

Supported Object Types:
    - Generic

CLI Arguments:
    --file          : Single file to process
    --model         : Ollama model to use
    --cleanup       : Remove stale entries for deleted/renamed files
    --since         : Process only files changed in last N hours
    --no-cleanup    : Skip auto-cleanup on incremental distills
    --target        : Target directories to process  (use with caution currently will process all files in the target directory)
    --force         : Force update (regenerate summaries even if unchanged)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - load_manifest(): No description.
    - load_cache(): Load existing cache or return empty dict.
    - save_cache(): Persist cache to disk immediately (crash-resilient).
    - compute_hash(): Compute SHA256 hash of file content.
    - call_ollama(): Call Ollama API for summarization.
    - distill(): Main distillation loop.
    - run_cleanup(): Remove stale entries for deleted/renamed files.

Script Dependencies:
    - plugins/rlm-factory/scripts/rlm_config.py (Configuration)
    - plugins/rlm-factory/scripts/cleanup_cache.py (Orphan Removal)

Consumed by:
    - (None Detected)
"""

import os
import sys
import json
import hashlib
import time
import traceback
from string import Template
from pathlib import Path
from datetime import datetime
from datetime import datetime
from typing import Dict, List, Optional

# ============================================================
# DEBUGGERS
# ============================================================
DEBUG_MODE = False

def debug(msg: str):
    if DEBUG_MODE:
        try:
            print(f"[DEBUG] {msg}")
        except UnicodeEncodeError:
            # Fallback for Windows consoles (e.g., PowerShell cp1252)
            print(f"[DEBUG] {msg.encode('utf-8', 'backslashreplace').decode()}")

try:
    import requests
except ImportError:
    print("❌ Missing dependency: pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

# ============================================================
# CONFIGURATION
# ============================================================



try:
    from tools.codify.rlm.rlm_config import (
        RLMConfig, 
        PROJECT_ROOT, 
        load_cache, 
        save_cache, 
        compute_hash, 
        should_skip, 
        collect_files
    )
except ImportError:
    # Fallback to local import
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from rlm_config import (
        RLMConfig, 
        PROJECT_ROOT, 
        load_cache, 
        save_cache, 
        compute_hash, 
        should_skip, 
        collect_files
    )

OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434") + "/api/generate"

# ============================================================
# CORE LOGIC
# ============================================================

def call_ollama(content: str, file_path: str, prompt_template: str, model_name: str) -> Optional[str]:
    """Call Ollama to generate summary."""
    # Truncate large files
    if len(content) > 12000: # Increased for code files
        content = content[:12000] + "\n...[TRUNCATED]..."
    
    # Use standard Template substitution (safe for JSON/Code content)
    # 1. Convert "Gold Standard" prompts ({var}) to Template format ($var)
    template_str = prompt_template.replace("{file_path}", "${file_path}").replace("{content}", "${content}")
    
    # 2. Use safe_substitute to prevent KeyErrors
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
            # Clean up common LLM artifacts
            if summary.startswith("Here is"):
                summary = summary.split(":", 1)[-1].strip()
            
            # Remove markdown code blocks if the agent included them
            if summary.startswith("```"):
                lines = summary.splitlines()
                if lines[0].startswith("```"): lines = lines[1:]
                if lines and lines[-1].startswith("```"): lines = lines[:-1]
                summary = "\n".join(lines).strip()
                
            return summary
        else:
            print(f"⚠️  Ollama error {response.status_code}: {response.text[:100]}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"⚠️  Timeout for {file_path}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Ollama at {OLLAMA_URL}")
        print("   Run: ollama serve")
        return None
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return None

def distill(config: RLMConfig, target_files: List[Path] = None, force: bool = False, injected_summary: str = None):
    """Main distillation loop."""
    print(f"RLM Distiller [{config.type.upper()}] - {config.description}")
    print(f"   Manifest: {config.manifest_path.name}")
    print(f"   Cache:    {config.cache_path.name}")
    print("=" * 50)
    
    cache = load_cache(config.cache_path)
    print(f"Loaded cache with {len(cache)} existing entries")
    
    # Determine files to process
    if target_files:
        files = target_files
    else:
        files = collect_files(config)
    
    total = len(files)
    print(f"Found {total} files to process")
    
    cache_hits = 0
    processed = 0
    errors = 0
    start_time = time.time()
    
    for i, file_path in enumerate(files, 1):
        # Path Resolution Block
        try:
            rel_path = file_path.resolve().relative_to(PROJECT_ROOT).as_posix()
        except ValueError as e:
            debug(f"Path resolution failed: {file_path} not relative to PROJECT_ROOT ({e})")
            rel_path = file_path.resolve().as_posix()
        
        try:
            # 1. Skip Check (Safety)
            if should_skip(file_path, config, debug_fn=debug):
                print(f"Skipping {rel_path} (excluded)")
                continue

            debug(f"Reading {rel_path}")
            # NOTE: errors="ignore" may change content hash for malformed UTF-8/Binary files
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            
            # Skip empty files
            if not content.strip():
                debug("File content empty")
                continue
            
            # Compute hash for cache lookup
            content_hash = compute_hash(content)
            
            # Check cache
            if not force and rel_path in cache and cache[rel_path].get("hash") == content_hash:
                cache_hits += 1
                if cache_hits == 1 or i % 10 == 0: # Improve UX: Show first hit, then throttle
                     print(f"   [{i}/{total}] {rel_path} [CACHE HIT]")
                continue
            
            # 2. Distill (if needed)
            if injected_summary:
                debug("Using injected summary (skipping Ollama)")
                summary = injected_summary
            else:
                summary = call_ollama(content, rel_path, config.prompt_template, config.llm_model)
            
            if summary:
                # 3. Update Ledger
                # Update cache with metadata
                cache[rel_path] = {
                    "hash": content_hash,
                    "summary": summary,
                    "file_mtime": file_path.stat().st_mtime,
                    "summarized_at": datetime.now().isoformat()
                }
                # PERSIST IMMEDIATELY (crash-resilient)
                debug(f"Writing cache entry for {rel_path}")
                save_cache(cache, config.cache_path)
                debug(f"Cache size now: {len(cache)} entries")
                processed += 1
                
                # Feedback Loop: Update Inventory Description (If Tool)
                if config.type == "tool":
                    try:
                        # Extract purpose from summary JSON
                        summary_data = json.loads(summary)
                        purpose = summary_data.get("purpose", "")
                        
                        if purpose:
                            # Import locally to avoid circular top-level imports
                            # (Though headers say cyclic, we defer import to runtime)
                            sys.path.append(str(PROJECT_ROOT)) # ensure path
                            from tools.tool_inventory.manage_tool_inventory import InventoryManager
                            
                            mgr = InventoryManager(PROJECT_ROOT / "tools/tool_inventory.json")
                            mgr.update_tool(
                                tool_path=rel_path, 
                                new_desc=purpose, 
                                suppress_distillation=True
                            )
                            debug(f"Inventory updated for {rel_path}")
                            
                    except Exception as e:
                        # Non-blocking error
                        print(f"⚠️  Inventory update failed for {rel_path}: {e}")
            else:
                errors += 1
                cache[rel_path] = {
                    "hash": content_hash,
                    "summary": "[DISTILLATION FAILED]",
                    "summarized_at": datetime.now().isoformat()
                }
                save_cache(cache, config.cache_path)
                
        except Exception as e:
            errors += 1
            print(f"❌ Error processing {rel_path}")
            if DEBUG_MODE:
                traceback.print_exc()
            else:
                print(f"   Reason: {e}")
            
            # Attempt to save partial progress even on error
            save_cache(cache, config.cache_path)
    
    duration = time.time() - start_time
    
    # Final consistency check and save
    save_cache(cache, config.cache_path)
    
    print("=" * 50)
    print(f"Distillation Complete!")
    print(f"   Total files: {total}")
    print(f"   Cache hits:  {cache_hits}")
    print(f"   Processed:   {processed}")
    print(f"   Errors:      {errors}")
    print(f"   Duration:    {duration:.1f}s")
    print(f"   Cache saved: {config.cache_path}")

    # Zero-Work Guardrail (Phantom Execution Protection)
    debug(f"Guardrail check -> Total: {total}, Processed: {processed}, Hits: {cache_hits}, Errors: {errors}")
    if total > 0 and processed == 0 and cache_hits == 0 and errors == 0:
        print("❌ CRITICAL: Distiller ran but no files were processed.")
        print("   This indicates a configuration or path resolution failure.")
        if DEBUG_MODE:
            print("   Debug mode was enabled — review logs above.")
        sys.exit(2)

# ============================================================
# CLEANUP FUNCTION
# ============================================================

def run_cleanup(config: RLMConfig):
    """Remove stale entries for files that no longer exist."""
    print("🧹 Running cleanup for stale cache entries...")
    cache = load_cache(config.cache_path)
    
    stale_keys = []
    for rel_path in list(cache.keys()):
        full_path = PROJECT_ROOT / rel_path
        # Note: In tool mode, we might want to cross check inventory existence?
        # For now, file existence is the gold standard.
        if not full_path.exists():
            stale_keys.append(rel_path)
    
    if not stale_keys:
        print("   ✅ No stale entries found.")
        return 0
    
    print(f"   Found {len(stale_keys)} stale entries")
    for key in stale_keys:
        del cache[key]
    
    save_cache(cache, config.cache_path)
    print(f"   ✅ Removed {len(stale_keys)} stale entries")
    return len(stale_keys)

# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import argparse
    from datetime import datetime, timedelta
    
    parser = argparse.ArgumentParser(description="Recursive Learning Model (RLM) Distiller")
    parser.add_argument("--type", choices=["profiles", "other"], help="[Legacy] RLM Type (loads manifest from factory)")
    parser.add_argument("--profile", help="[New] RLM Profile name (from rlm_profiles.json)")
    parser.add_argument("--target", "-t", nargs="+", help="Override target directories to process")
    parser.add_argument("--file", "-f", help="Single file to process")
    parser.add_argument("--model", "-m", help="Ollama model to use")
    parser.add_argument("--cleanup", action="store_true", help="Remove stale entries for deleted/renamed files")
    parser.add_argument("--since", type=int, metavar="HOURS", help="Process only files changed in last N hours")
    parser.add_argument("--no-cleanup", action="store_true", help="Skip auto-cleanup on incremental distills")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug logging for troubleshooting")
    parser.add_argument("--force", action="store_true", help="Force re-distillation of files (bypass cache)")
    parser.add_argument("--summary", help="Inject a pre-generated JSON or Text summary (skips Ollama)")
    
    args = parser.parse_args()
    
    if args.debug:
        DEBUG_MODE = True
        print("[DEBUG] Debug mode enabled")
    
    if not args.type and not args.profile:
        print("⚠️  No profile specified, defaulting to legacy 'project' type.")
        args.type = "project"
        
    # Load Config based on Type or Profile
    try:
        if args.profile:
            config = RLMConfig.from_profile(args.profile, project_root=None)
            if args.target:
                config.targets = args.target
        else:
            config = RLMConfig(run_type=args.type, override_targets=args.target)
            
        if args.model:
            config.llm_model = args.model  # Override model in config
            print(f"🤖 Using model override: {config.llm_model}")
            
        debug(f"Config initialized type: {config.type}")
        debug(f"Config cache path: {config.cache_path}")
    except Exception as e:
        print(f"DEBUG: Error init config: {e}")
        sys.exit(1)
    
    # Handle cleanup
    if args.cleanup:
        run_cleanup(config)
        
    if args.since:
        # Auto-cleanup for incremental (unless --no-cleanup)
        if not args.no_cleanup and not args.cleanup: # Avoid double cleanup
            run_cleanup(config)
        
        # Filter files by modification time
        cutoff = datetime.now().timestamp() - (args.since * 3600)
        files = collect_files(config)
        recent_files = [f for f in files if f.stat().st_mtime >= cutoff]
        print(f"⏰ Processing {len(recent_files)} files changed in last {args.since} hours")
        
        distill(config, target_files=recent_files, force=args.force)
    else:
        target_files = None
        if args.file:
            # Canonicalize path at boundary (Red Team Fix)
            f_path_raw = PROJECT_ROOT / args.file
            f_path = f_path_raw.resolve()
            
            # Instrument Path Resolution (Red Team Fix)
            debug(f"Raw CLI file argument: {args.file}")
            debug(f"Computed raw path: {f_path_raw}")
            debug(f"Resolved absolute path: {f_path}")
            debug(f"PROJECT_ROOT: {PROJECT_ROOT}")
            
            if not f_path.exists() or not f_path.is_file():
                print(f"❌ Invalid file: {args.file} (Resolved: {f_path})")
                sys.exit(1)
            target_files = [f_path]
            
        distill(config, target_files=target_files, force=args.force, injected_summary=args.summary)
