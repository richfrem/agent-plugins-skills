# Control Plane Schema Rebuild Recovery Runbook (issue-552)

## When to use this

`ensure_schema()` raises `RuntimeError: control_plane.db has orphaned migration tables...`
(or, before issue-552's fix, a database opened via `context/control_plane.db` shows tables
named `_tasks_migrating`, `_task_transitions_migrating`, etc. alongside empty real tables).
This means a `_rebuild_schema_transactional()` run was interrupted before completing —
either by a bug this issue fixed, or by an external interruption (process killed, disk
full) during a future rebuild.

**After issue-552's fix, this should not happen from a bug in the rebuild method itself** —
the RED/GREEN tests in `test_control_plane_schema_rebuild_atomicity.py` prove a mid-rebuild
failure now rolls back completely. This runbook exists for: (a) a DB corrupted before the
fix was applied, or (b) any future truly external interruption (e.g. `kill -9` mid-COMMIT,
which no software-level fix can prevent).

## Recovery procedure

### 1. Back up first, always

```bash
cp context/control_plane.db "context/control_plane.db.pre-recovery-backup-$(date +%Y%m%d%H%M%S)"
```

Never skip this. Every step below is reversible only if this backup exists.

### 2. Diff row counts before touching anything

For each real/orphan table pair, confirm the orphan table's rows are the *only* copy — not
a duplicate of data already present in the real table:

```python
import sqlite3
conn = sqlite3.connect("context/control_plane.db")
pairs = [
    ("tasks", "_tasks_migrating"),
    ("task_transitions", "_task_transitions_migrating"),
    ("locked_verifier_baselines", "_locked_verifier_baselines_migrating"),
    ("critic_reviews", "_critic_reviews_migrating"),
    ("verification_receipts", "_verification_receipts_migrating"),
    ("asymmetric_persistence_log", "_asymmetric_persistence_log_migrating"),
    ("transition_decisions", "_transition_decisions_migrating"),
]
for real, orphan in pairs:
    real_n = conn.execute(f'SELECT COUNT(*) FROM "{real}"').fetchone()[0]
    orphan_n = conn.execute(f'SELECT COUNT(*) FROM "{orphan}"').fetchone()[0]
    print(f"{real}: {real_n} rows | {orphan}: {orphan_n} rows")
```

If both a real table and its orphan counterpart have rows, **stop** — this is not the
simple case this runbook covers. Investigate manually (likely a partially-successful
retried rebuild) before proceeding.

### 3. Copy orphan rows into the real tables, with enforcement triggers suspended

The `tasks` table has `enforce_valid_transition`/`enforce_valid_initial_state` triggers
that silently revert/delete any row whose transition isn't registered in
`valid_transitions`. If `valid_transitions` is empty at recovery time (common — it's only
populated by `_sync_valid_transitions()`, which a stuck DB may not have run recently), a
naive `INSERT` copy will have every row **silently deleted** by
`enforce_valid_initial_state` and logged to `transition_violations` instead — with no
error raised. **This exact mistake happened during this issue's own live incident
recovery** (see `docs/plans/issue-552-spec.md` §5, Live Incident #2). Always suspend both
triggers before copying:

```python
conn.execute("PRAGMA foreign_keys = OFF;")
conn.execute("BEGIN IMMEDIATE;")
conn.execute("DROP TRIGGER IF EXISTS enforce_valid_initial_state;")
conn.execute("DROP TRIGGER IF EXISTS enforce_valid_transition;")

for real, orphan in pairs:
    source_cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{orphan}");').fetchall()]
    dest_cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{real}");').fetchall()]
    common_cols = [c for c in source_cols if c in dest_cols]
    cols_str = ", ".join(f'"{c}"' for c in common_cols)
    conn.execute(f'INSERT INTO "{real}" ({cols_str}) SELECT {cols_str} FROM "{orphan}";')
    conn.execute(f'DROP TABLE "{orphan}";')

# Recreate both triggers — copy the exact CREATE TRIGGER statements from SCHEMA_SQL in
# plugins/agent-agentic-os/scripts/control_plane/adapters.py.
conn.execute(""" CREATE TRIGGER IF NOT EXISTS enforce_valid_transition ... """)
conn.execute(""" CREATE TRIGGER IF NOT EXISTS enforce_valid_initial_state ... """)

conn.execute("COMMIT;")
conn.execute("PRAGMA foreign_keys = ON;")
```

### 4. Repopulate `valid_transitions` — call the existing method, don't hand-roll it

**Do not** reimplement the INSERT/DELETE logic by hand. Call the adapter's own
`_sync_valid_transitions(conn)` directly — it is already correct and atomic (see
`test_sync_valid_transitions_is_atomic_not_left_empty_on_failure` in
`test_control_plane_trigger_enforcement.py`). Hand-rolling it a second time is exactly the
mistake this issue's own Live Incident #3 made.

```python
import sys
sys.path.insert(0, "plugins/agent-agentic-os/scripts")
from pathlib import Path
from control_plane.adapters import SqlitePersistenceAdapter, FilesystemAdapter

adapter = SqlitePersistenceAdapter(Path("context/control_plane.db"), FilesystemAdapter())
conn = adapter.get_connection()
adapter._sync_valid_transitions(conn)
conn.close()
```

### 5. Set `schema_version` directly

`_sync_valid_transitions()` does not touch `schema_version` — set it directly to the
current value from `plugins/agent-agentic-os/scripts/control_plane/adapters.py`'s
`CURRENT_SCHEMA_VERSION` constant:

```python
conn = adapter.get_connection()
conn.execute("BEGIN IMMEDIATE;")
conn.execute("DELETE FROM schema_version;")
conn.execute("INSERT INTO schema_version (version) VALUES (?);", (CURRENT_SCHEMA_VERSION,))
conn.execute("COMMIT;")
conn.close()
```

### 6. Verify stability

```python
adapter.ensure_schema()  # must complete with no exception and no further rebuild triggered
```

If this raises again, stop and investigate — do not retry blindly.

## Do not

- Do not fold this recovery into `agent_control.py init` or `ensure_schema()` as an
  automatic/silent repair. A human decision point is required — see
  `.agent/rules/destructive-action-guard.md`.
- Do not skip the row-count diff in step 2 — assuming orphan tables are safe to drop
  without checking is what this runbook exists to prevent.
- Do not hand-roll `valid_transitions` population — see step 4.
