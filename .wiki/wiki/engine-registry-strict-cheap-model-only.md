---
concept: engine-registry-strict-cheap-model-only
source: plugin-code
source_file: obsidian-wiki-engine/scripts/distill_wiki.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.012131+00:00
cluster: path
content_hash: 0dc92eff924548a7
---

# ─── ENGINE REGISTRY (strict cheap-model only) ────────────────────────────────

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
distill_wiki.py
=====================================

Purpose:
    Cheap-model RLM distillation orchestrator for the Obsidian Wiki Engine.
    Iterates over all wiki nodes needing RLM summaries, auto-detects the
    cheapest available LLM CLI, and generates three summary layers per concept:
    summary.md, bullets.md, deep.md.

    Distillation is performed entirely within this plugin — no cross-plugin
    script calls. RLM summaries are written to a configurable cache directory
    (default: {wiki_root}/rlm/) or to a shared path under .agent/learning/
    when --rlm-cache-dir is set to point there.

    Fallback chain (strict — Ollama is fully deprecated):
        1. copilot  -> gpt-5-mini
        2. claude   -> claude-haiku-4-5
        3. gemini   -> gemini-3-flash-preview

Layer: Distill / Wiki

Usage:
    python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root
    python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root --source arch-docs
    python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root --engine claude
    python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root --dry-run
    python ./scripts/distill_wiki.py --wiki-root /path/to/wiki-root \\
        --rlm-cache-dir /path/to/project/.agent/learning/rlm_wiki_cache

Related:
    - raw_manifest.py  (WikiSourceConfig + agent-memory.json)
    - wiki_builder.py  (consumes the rlm/ summaries it produces)
    - audit.py         (reports missing summaries)
"""
import sys
import os
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from raw_manifest import now_iso

# ─── ENGINE REGISTRY (strict cheap-model only) ────────────────────────────────
# Ollama is fully deprecated for distillation tasks.
ENGINE_PRIORITY: List[Tuple[str, str]] = [
    ("copilot", "gpt-5-mini"),
    ("claude",  "claude-haiku-4-5"),
    ("gemini",  "gemini-3-flash-preview"),
]

# ─── PATH AUGMENTATION (stripped PATH in some environments) ──────────────────
_EXTRA_PATHS = [
    "/opt/homebrew/bin",
    "/usr/local/bin",
    os.path.expanduser("~/.local/bin"),
    os.path.expanduser("~/.npm-global/bin"),
    os.path.expanduser("~/n/bin"),
]
for _p in _EXTRA_PATHS:
    if _p not in os.environ.get("PATH", "") and Path(_p).exists():
        os.environ["PATH"] = _p + os.pathsep + os.environ.get("PATH", "")


def detect_engine(override: Optional[str] = None) -> Tuple[str, str]:
    """
    Detect the cheapest available LLM CLI on PATH.

    Args:
        override: Force a specific engine name (e.g. 'claude').

    Returns:
        (engine_name, model_name) tuple.

    Raises:
        SystemExit: If override is unknown or no engine is found.
    """
    if override:
        for engine, model in ENGINE_PRIORITY:
            if engine == override.lower():
                if shutil.which(engine):
                    return (engine, model)
                print(f"[ERROR] Engine '{override}' not found on PATH.")
                print(f"   Install: https://github.com/cli/{override}")
                sys.exit(1)
        print(f"[ERROR] Unknown engine '{override}'. Choose from: {[e for e, _ in ENGINE_PRIORITY]}")
        sys.exit(1)

    for engine, model in ENGINE_PRIORITY:
        if shutil.which(engine):
            print(f"[ENGINE] Using: {engine} ({model})")
            return (engine, model)

    print("[ERROR] No LLM CLI found on PATH.")
    print("   Install one of:")
    for engine, model in ENGINE_PRIORITY:
        print(f"     {engine} (model: {model})")
    sys.exit(1)


def build_prompt(layer: str, concept: str, content: str) -> str:
    """
    Build the distillation prompt for the given layer.

    Args:
        layer:   One of 'summary', 'bullets', 'deep'.
        concept: The concept slug being distilled.
        content: The raw wiki node content excerpt.

   

*(content truncated)*

## See Also

- [[1-heartbeat-free-model-always-first]]
- [[obsidian-wiki-engine-plugin]]
- [[only-check-files-in-pluginsskills]]
- [[only-include-those-appearing-in-2-of-the-last-n-traces]]
- [[only-process-plugin-root-level-files-not-skill-files]]
- [[re-use-engine-detection-llm-call-from-distill-wiki]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/scripts/distill_wiki.py`
- **Indexed:** 2026-04-27T05:21:04.012131+00:00
