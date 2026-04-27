---
concept: t029-lossless-yaml-ruamelyaml-preferred-fallback-warning
source: plugin-code
source_file: obsidian-wiki-engine/scripts/vault_ops.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.269120+00:00
cluster: self
content_hash: 902b9ceec9d03c7a
---

# --- T029: Lossless YAML (ruamel.yaml preferred, fallback warning) ---

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/obsidian-wiki-engine/scripts/vault_ops.py -->
"""
vault_ops.py (CLI)
=====================================

Purpose:
    Safe Create/Read/Update/Append operations for Obsidian Vault notes.
    Implements atomic writes, advisory locking, concurrent edit detection,
    and lossless YAML frontmatter handling.

Layer: Core Operations

Usage Examples:
    pythonult_ops.py read --file note.md
    pythonult_ops.py create --file note.md --content "Hello"

Supported Object Types:
    - .md (Markdown notes with Obsidian syntax)

CLI Arguments:
    Subcommands: read, create, update, append. Run with --help for details.

Input Files:
    - .md files.

Output:
    - JSON results or status messages.

Key Functions:
    read_note(): Read a note and return its frontmatter and body.
    create_note(): Create a new note with optional frontmatter.
    update_note(): Update a note's body, preserving frontmatter.
    append_to_note(): Append content to an existing note.

Script Dependencies:
    os, sys, json, argparse, tempfile, subprocess, pathlib, typing, ruamel.yaml

Consumed by:
    - obsidian-vault-crud skill
"""
import os
import sys
import json
import argparse
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# --- T029: Lossless YAML (ruamel.yaml preferred, fallback warning) ---
try:
    from ruamel.yaml import YAML
    _yaml = YAML()
    _yaml.preserve_quotes = True
    _yaml.default_flow_style = False
    HAS_RUAMEL = True
except ImportError:
    HAS_RUAMEL = False
    print("WARNING: ruamel.yaml not installed. Frontmatter operations will be unavailable.", file=sys.stderr)
    print("Install with: pip install ruamel.yaml", file=sys.stderr)

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
VAULT_ROOT = Path(os.environ.get("VAULT_PATH", Path(__file__).resolve().parents[4]))
LOCK_FILE = VAULT_ROOT / ".agent-lock"


# ---------------------------------------------------------------------------
# T027: Advisory Lock Protocol
# ---------------------------------------------------------------------------
class AgentLock:
    """
    Advisory lock for agent-vs-agent write coordination.
    Creates `.agent-lock` at the vault root before write batches.
    """

    def __init__(self, vault_root: Path = VAULT_ROOT) -> None:
        self.lock_path = vault_root / ".agent-lock"
        self._acquired = False

    def acquire(self, agent_name: str = "Antigravity") -> bool:
        """Acquire the advisory lock. Returns False if already locked."""
        if self.lock_path.exists():
            try:
                lock_info = json.loads(self.lock_path.read_text())
                print(f"WARNING: Vault is locked by agent '{lock_info.get('agent', 'unknown')}' "
                      f"since {lock_info.get('timestamp', 'unknown')}", file=sys.stderr)
            except (json.JSONDecodeError, OSError):
                print("WARNING: Stale lock file detected.", file=sys.stderr)
            return False

        lock_data = {
            "agent": agent_name,
            "pid": os.getpid(),
            "timestamp": _now_iso()
        }
        self.lock_path.write_text(json.dumps(lock_data, indent=2))
        self._acquired = True
        return True

    def release(self) -> None:
        """Release the advisory lock."""
        if self._acquired and self.lock_path.exists():
            self.lock_path.unlink()
            self._acquired = False

    def __enter__(self) -> "AgentLock":
        if not self.acquire():
            raise RuntimeError("Failed to acquire agent lock. Another agent is writing.")
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> bool:
        self.release()
        return False


# ---------------------------------------------------------------------------
# T028: Concurrent Edit Detection (mtime guard)
# ------------------------

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/obsidian-canvas-architect/scripts/vault_ops.py -->
"""
vault_ops.py (CLI)
=====================================

Purpose:
    Safe Create/Read/Update/Append operations for Obsidian Vault notes.
    Implements atomic writes, advisory locking, concurrent edit detection,
    and lossless YAML frontmatter handling.

Layer: Core Operations

Usage Examples:
    python3 vault_ops.py read --file note.md
    python3 vault_ops.py create --file note.md --content "Hello"

Supported Object Types:
    - .md (Markdown notes with Obsidian syntax)

CLI Arguments:
    Subcommands: read, create, update, append. Run with --help for details.

Input Files:
    - .md files.

Output:
    - JSON results or status messages.

Key Functions:
    read_note(): Read a note and return its frontmatter and body.
    create_note(): Create a new note with optional front

*(combined content truncated)*

## See Also

- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[fallback-to-appending-directly-if-kernel-is-missing]]
- [[handle-yaml-multiline-indicators]]
- [[parse-simple-key-value-yaml-frontmatter-between-the-two-----delimiters]]
- [[part-0-is-empty-part-1-is-yaml]]
- [[procedural-fallback-tree-red-team-review]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/scripts/vault_ops.py`
- **Indexed:** 2026-04-27T05:21:04.269120+00:00
