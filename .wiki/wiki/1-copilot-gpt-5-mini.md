---
concept: 1-copilot-gpt-5-mini
source: plugin-code
source_file: rlm-factory/scripts/distill_one.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.036523+00:00
cluster: path
content_hash: efe499191c6156a9
---

# 1. Copilot (GPT-5 mini)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
distill_one.py
=====================================

Purpose:
    Single-file distillation smoke test. Reads one file, calls the specified
    agent CLI to generate an RLM summary, then injects the result into the
    correct cache directory via inject_summary.py.

    Use this to verify the full pipeline works end-to-end before running the
    full swarm batch.

Usage:
    # 1. Copilot (GPT-5 mini)
    python ./scripts/distill_one.py --profile wiki --file plugin-research/superpowers/decision.md --engine copilot

    # 2. Gemini (Gemini-3 Flash Preview)
    python ./scripts/distill_one.py --profile wiki --file plugin-research/superpowers/quick-wins.md --engine gemini --model gemini-3-flash-preview

    # 3. Claude (Haiku-4.5)
    python ./scripts/distill_one.py --profile wiki --file plugin-research/superpowers/capabilities-matrix.md --engine claude --model haiku-4.5

    # Dry-run: print the prompt but don't call the CLI:
    python ./scripts/distill_one.py --profile wiki --file plugins/adr-manager/README.md --dry-run

Related:
    - inject_summary.py  (cache persistence)
    - rlm_config.py      (profile + path resolution)
    - swarm_run.py       (batch version of this script)
"""

import sys
import shlex
import argparse
import subprocess
from pathlib import Path

# ─── PATH BOOTSTRAP ─────────────────────────────────────────────────────────
def _find_project_root(start: Path) -> Path:
    for p in [start.resolve()] + list(start.resolve().parents):
        if (p / ".git").is_dir():
            return p
    return start.resolve().parents[3]

PROJECT_ROOT = _find_project_root(Path(__file__))
SCRIPT_DIR   = Path(__file__).resolve().parent

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# ─── AUGMENT PATH for subprocesses ─────────────────────────────────────────
# Antigravity runs with a stripped PATH. Add common locations for CLI tools.
import os
import platform as _platform

_extra_paths = [
    "/opt/homebrew/bin",
    "/usr/local/bin",
    os.path.expanduser("~/.local/bin"),
    os.path.expanduser("~/.npm-global/bin"),
    os.path.expanduser("~/n/bin"),
    "/usr/local/share/npm/bin",
]

# Add the VSCode Copilot Chat extension's bundled copilot CLI.
# The path varies by OS — detect at runtime rather than hardcoding.
# Users who install copilot CLI via npm/brew don't need these fallbacks;
# they're here for the common case where it's only installed via VSCode.
_vscode_copilot_dir = {
    "Darwin": os.path.expanduser(
        "~/Library/Application Support/Code/User/globalStorage/"
        "github.copilot-chat/copilotCli"
    ),
    "Windows": os.path.expanduser(
        "~/AppData/Roaming/Code/User/globalStorage/"
        "github.copilot-chat/copilotCli"
    ),
    "Linux": os.path.expanduser(
        "~/.config/Code/User/globalStorage/"
        "github.copilot-chat/copilotCli"
    ),
}.get(_platform.system())
if _vscode_copilot_dir:
    _extra_paths.append(_vscode_copilot_dir)

for _p in _extra_paths:
    if _p not in os.environ.get("PATH", "") and Path(_p).exists():
        os.environ["PATH"] = _p + ":" + os.environ.get("PATH", "")

try:
    from rlm_config import RLMConfig
except ImportError as e:
    print(f"[ERROR] Cannot import rlm_config: {e}")
    sys.exit(1)

# ─── ENGINE DEFAULTS ─────────────────────────────────────────────────────────
ENGINE_DEFAULTS = {
    "copilot": "gpt-5-mini",
    "gemini":  "gemini-3-flash-preview",
    "claude":  "claude-haiku-4-5",
}


def build_llm_cmd(engine: str, model: str, prompt_payload: str) -> tuple[list[str], str]:
    """
    Build the CLI command list and the stdin payload for the given engine.

    Returns:
        (cmd_args, stdin_text)
    """
    engine = engine.lower()

    if engine == "claude":
        return (
            ["claude", "--model", model, "-p", prompt_payload, "--no-session-persistence"],
            ""  # claude reads -p, no stdin needed
        )
    elif engine == "gemini":
        return (
       

*(content truncated)*

## See Also

- [[simple-tasks-no---model-flag-defaults-to-freecheap-model-gpt-5-mini-via-copilot]]
- [[1-basic-summarize-all-documents]]
- [[1-check-env]]
- [[1-check-root-structure]]
- [[1-configuration-setup-dynamic-from-profile]]
- [[1-handle-absolute-paths-from-repo-root]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `rlm-factory/scripts/distill_one.py`
- **Indexed:** 2026-04-27T05:21:04.036523+00:00
