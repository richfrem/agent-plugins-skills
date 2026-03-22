# Backlog: SQLite backend for events and memory

**Plugin**: agent-agentic-os
**Priority**: Low
**Source**: gpt5-critical-review.md - Issue #5B / Design Smell #1
**Target version**: 2.0.0

## Problem

The current file-based backend has three scaling issues:
1. `events.jsonl` is append-only -- querying requires full linear scan
2. `context/memory.md` is freeform markdown -- no structured deduplication
3. File I/O on every hook call accumulates latency at scale

## Proposed Solution

Replace `events.jsonl` with an SQLite database (`context/events.db`) and optionally
`context/memory.md` with `context/memory.db`.

```sql
-- events table
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    time TEXT NOT NULL,
    agent TEXT NOT NULL,
    type TEXT NOT NULL,
    action TEXT NOT NULL,
    status TEXT,
    summary TEXT
);

-- memory table (structured facts)
CREATE TABLE memory (
    id TEXT PRIMARY KEY,   -- e.g. "build_cmd_001"
    type TEXT,
    topic TEXT,
    value TEXT,
    source TEXT,
    supersedes TEXT,       -- id of superseded fact
    created_at TEXT
);
```

`kernel.py emit_event` writes to SQLite instead of JSONL.
`post_run_metrics.py` queries with `SELECT COUNT(*) WHERE status='error'`.
`session-memory-manager` promotes facts as rows, not appended markdown lines.

## Migration Path

- `kernel.py` gains a `--backend sqlite|jsonl` flag (default jsonl for backwards compat)
- `os-state.json` gains `"event_backend": "sqlite"` to opt in
- Export script: `python3 context/kernel.py export_events --format jsonl` for portability
- Keep JSONL fallback so the OS works without sqlite3 (standard library, so always available)

## Acceptance Criteria

- [ ] `emit_event` writes to SQLite when `event_backend=sqlite`
- [ ] `post_run_metrics.py` queries SQLite correctly
- [ ] JSONL export works for backwards compatibility
- [ ] No performance regression on small projects (< 1000 events)
