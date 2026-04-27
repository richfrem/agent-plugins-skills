---
concept: keys-that-cannot-be-overwritten-via-state-update-prompt-injection-defense
source: plugin-code
source_file: agent-agentic-os/scripts/kernel.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.295339+00:00
cluster: return
content_hash: ec79ea5a402e2607
---

# Keys that cannot be overwritten via state_update (prompt injection defense)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-agentic-os/scripts/kernel.py -->
#!/usr/bin/env python
"""
kernel.py — Agentic OS Event Bus and Lock Manager
======================================================

Purpose:
    Core operational kernel for the Agentic OS. Provides persistent memory bus,
    process coordination, and distributed locks for multiple sub-agents.
    Deliberately minimal. Solves the triple-loop use case: one ORCHESTRATOR,
    one INNER_AGENT, securely sharing data.

Layer: 
    OS Kernel primitives

Usage Examples:
    pythonkernel.py acquire_lock my_lock --ttl 30
    pythonkernel.py emit_event --agent worker --type intent --action task_start

Supported Object Types:
    - JSONL Event payloads
    - File-based Locks
    - JSON State Dictionaries

CLI Arguments:
    acquire_lock, release_lock, emit_event, 
    read_events, state_update, state_increment, claim_task

Input Files:
    - context/os-state.json
    - context/agents.json

Output:
    - Appends to context/events.jsonl
    - Mutates context/os-state.json
    - Drops lock dirs in context/.locks/

Key Functions:
    acquire_lock()
    emit_event()
    state_update()
    read_events()

Script Dependencies:
    - None

Consumed by:
    - All background hooks and sub-agents
"""
import os, sys, json, time, uuid, random, argparse
from pathlib import Path
from datetime import datetime, timezone

KERNEL_DIR  = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())) / "context"
EVENTS_FILE = KERNEL_DIR / "events.jsonl"
LOCKS_DIR   = KERNEL_DIR / ".locks"
STATE_FILE  = KERNEL_DIR / "os-state.json"
AGENTS_FILE = KERNEL_DIR / "agents.json"
AGENTS_DIR  = KERNEL_DIR / "agents"
EVENTS_MAX_BYTES = 10 * 1024 * 1024  # 10 MB before rotation

# Keys that cannot be overwritten via state_update (prompt injection defense)
PROTECTED_STATE_KEYS = frozenset({"execution_mode", "hook_sample_rate"})


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _load(path, default):
    try:
        if Path(path).exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def _pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # exists, just can't signal it


def _is_stale(lock_path):
    """Lease-based stale check: dead PID > expired TTL > mtime fallback."""
    meta = _load(lock_path / "meta.json", {})
    if meta:
        if meta.get("pid") and not _pid_alive(meta["pid"]):
            return True
        if meta.get("expires_at", 0) < time.time():
            return True
        return False
    # Legacy lock without metadata — use mtime
    try:
        timeout = _load(STATE_FILE, {}).get("lock_timeout_seconds", 1800)
        return time.time() - lock_path.stat().st_mtime > timeout
    except OSError:
        return True


def _clear(lock_path):
    """Remove all files in lock dir then rmdir."""
    try:
        for f in Path(lock_path).iterdir():
            f.unlink()
        os.rmdir(lock_path)
    except OSError:
        pass


def _spinlock(lock_path, timeout=30):
    """Directory spinlock. Returns True on success."""
    os.makedirs(LOCKS_DIR, exist_ok=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            os.mkdir(lock_path)
            return True
        except FileExistsError:
            try:
                if time.time() - Path(lock_path).stat().st_mtime > 20:
                    _clear(lock_path)
            except OSError:
                pass
            time.sleep(random.uniform(0.05, 0.15))
    return False


def _validate_agent(name):
    r = _load(AGENTS_FILE, {})
    if name in r.get("permitted_agents", []):
        return True
    print(f"[Kernel] Unregistered agent:

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/os-clean-locks/kernel.py -->
#!/usr/bin/env python3
"""
kernel.py — Agentic OS Event Bus and Lock Manager
======================================================

Purpose:
    Core operational kernel for the Agentic OS. Provides persistent memory bus,
    process coordination, and distributed locks for multiple sub-agents.
    Deliberately minimal. Solves the triple-loop use case: one ORCHESTRATOR,
    one INNER_AGENT, securely sharing data.

Layer: 
    OS Kernel primitives

Usage Examples:
    python3 kernel.py acquire_lock my_lock --ttl 30
    python3 kernel.py emit_event --agent worker --type intent --action task_start

Supported Object Types:
    - JSONL Event payloads
    - File-based Locks
    - JSON State Dictionaries

CLI Arguments:
    acquire_lock, release_lock, emit_event, 
    read_events, state_update, state_increment, claim_tas

*(combined content truncated)*

## See Also

- [[absolute-path-prefixes-that-should-never-be-written-to]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[commands-that-are-unconditionally-safe-and-bypass-further-checks]]
- [[default-discovery-tags-for-llm-retraining-crawlers-override-via-hugging-face-tags-env-var]]
- [[ensure-unicode-output-works-on-windows-terminals-that-default-to-cp1252]]
- [[match-pythonexecution-paths-that-are-hardcoded-to-the-repo-root-plugins-folder]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/scripts/kernel.py`
- **Indexed:** 2026-04-27T05:21:04.295339+00:00
