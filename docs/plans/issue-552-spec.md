# TASK_SPEC.md — Issue #552: `_rebuild_schema_transactional()` Atomicity Fix

**Task ID:** `issue-552`
**Status:** DRAFT_PLAN
**Runtime:** claude-code

---

## 1. The Job

Fix `SqlitePersistenceAdapter._rebuild_schema_transactional()` in
`plugins/agent-agentic-os/scripts/control_plane/adapters.py` (lines ~507-589) so that a
mid-rebuild exception actually rolls back cleanly, instead of leaving the database in a
half-migrated state with both the real tables and `_<table>_migrating` orphan tables
present simultaneously.

Root cause (confirmed empirically, both via the issue's own repro and a live incident
during this session — see §5): `conn.executescript(SCHEMA_SQL)` at line 528, called
partway through the `BEGIN IMMEDIATE` transaction opened at line 513, silently commits
that transaction (documented CPython `sqlite3` behavior — `executescript()` issues an
implicit `COMMIT` before running, and script statements execute outside any
transaction). Everything after that call — trigger drop/recreate, the row-copy loop,
`schema_version` update — runs unprotected. A second, distinct symptom of the same root
cause was also found live tonight: `SCHEMA_SQL` itself begins with `PRAGMA foreign_keys
= ON;`, so `executescript()` silently re-enables FK enforcement that the method
explicitly turned off at its own top (line 512) — this is what produced the `FOREIGN
KEY constraint failed` error during tonight's incident recovery, not a separate bug.

Target files:
- `plugins/agent-agentic-os/scripts/control_plane/adapters.py` — the fix itself.
- New test file: `plugins/agent-agentic-os/tests/test_control_plane_schema_rebuild_atomicity.py`.
- `plugins/agent-agentic-os/scripts/control_plane/agent_control.py` (or equivalent
  entrypoint) — startup health check (§4, item 2).
- A new runbook doc for manual recovery (§4, item 3), location TBD in implementation
  plan (likely `plugins/agent-agentic-os/references/` or `docs/plans/`).

## 2. The Why

`_rebuild_schema_transactional()`'s own docstring claims "a mid-sequence failure rolls
back cleanly instead of leaving a corrupted intermediate state." That claim is false as
currently implemented. This matters because the method runs on every schema version
bump (including #523's own v4→v5 bump) via `ensure_schema()`'s self-healing path, and a
partial failure (malformed row, disk-full, killed process) mid-copy-loop leaves task
history — the control plane's own durable record of task state — split across orphaned
`_<table>_migrating` tables with no working `tasks` table left behind.

This is not hypothetical. During this session's intake, `context/control_plane.db` was
found live in exactly this corrupted state (see §5) — real task history, including
#523's own record, was trapped in `_tasks_migrating` with an empty `tasks` table. A
second, independent recurrence happened during this session's own recovery attempt (see
§5), reinforcing that the failure mode is easy to hit by accident, not just by
adversarial fault injection.

## 3. Semantic Guardrails & Operational Reasons

- **No behavior change to the migration's actual DDL/data effects** — only the
  transaction boundary changes. The set of tables created, triggers (re)created, and
  rows copied must be identical before/after the fix. *Reason: this method runs
  unattended on every version bump; any behavior drift here is effectively a silent
  schema regression.*
- **All three leading PRAGMA statements in `SCHEMA_SQL` (`foreign_keys = ON`,
  `journal_mode = WAL`, `busy_timeout = 5000`) must be skipped during the split, not
  just `foreign_keys`.** *Reason (spec-review finding #2): under the split-execute
  approach, `PRAGMA journal_mode = WAL;` is a documented no-op once a transaction is
  active — a real, distinct behavior change from today's `executescript()` path, where
  it runs genuinely pre-transaction. Harmless in practice (mode is already WAL, set by
  `ensure_schema()` line 386 before this method runs), but it must be an explicit,
  documented skip with a one-line comment, not an accidental silent no-op. `PRAGMA
  foreign_keys = OFF` must stay OFF for the full duration of the rebuild — this was the
  original guardrail and remains the primary one (observed breaking tonight).
  `busy_timeout` has no transaction restriction and is fine either way but is skipped
  for consistency.*
- **The `BEGIN IMMEDIATE` transaction must remain open and unbroken from before the
  first `ALTER TABLE RENAME` through the final `COMMIT`.** *Reason: this is the entire
  point of the fix — verified by the new regression test in §4.*
- **`_log_orphan_merge_conflicts()`'s filesystem write (`map-debt.md` append, called via
  `_merge_orphaned_tasks_old()` at line 554, before `COMMIT` at line 585) must not
  execute until the SQL transaction has actually committed.** *Reason (spec-review
  finding #1, HIGH): this write is invisible to SQLite's rollback — if any statement
  after line 554 fails, the SQL side now rolls back cleanly under this fix, but the
  map-debt.md append is not undone. A retried rebuild can then append a duplicate/
  contradictory entry for a rebuild that never completed. Collect conflicts in a local
  list during the copy loop; only call `_log_orphan_merge_conflicts()` after `COMMIT`
  succeeds, on the success path only.*
- **The startup health check (§4 item 2) must be the literal first operation in
  `ensure_schema()`** — before line 386's `PRAGMA journal_mode` and line 387's
  unconditional `executescript(SCHEMA_SQL)` call, not merely "before the rebuild call."
  *Reason (spec-review finding #4): as originally scoped, an orphan-table check placed
  only immediately before `_rebuild_schema_transactional()` would let line 387's
  blanket `executescript()` already run DDL against a corrupted DB first — an
  uncharacterized interaction. Checking first, before any DDL touches the connection,
  is strictly safer and no more expensive.*
- **The health check must not misfire against a different process's legitimate,
  in-progress rebuild.** *Reason (spec-review finding #5, MODERATE): this is a shared,
  multi-session SQLite DB (WAL mode, `busy_timeout=5000`, opened concurrently by
  separate agent sessions). A false-loud-failure here — one process's health check
  tripping on another process's genuinely-mid-flight, uncommitted rebuild — is a real
  denial-of-service risk, not just a correctness nit. WAL snapshot isolation should make
  a second connection see either the fully pre-rebuild or fully post-commit state, never
  the mid-flight renamed tables, but this must be verified with an explicit two-connection
  test (§4 item 2), not merely inferred from general WAL semantics.*
- **Do not touch `_sync_valid_transitions()` (lines 411-430) or `ensure_schema()`'s
  outer `executescript(SCHEMA_SQL)` call at line 387.** *Reason: line 387's
  `executescript()` call runs before any `BEGIN IMMEDIATE` is opened, so it has no
  atomicity claim to violate — out of scope. `_sync_valid_transitions()` already uses
  individual `execute()`/`executemany()` calls correctly and is unaffected by this bug.*
- **Recovery script/runbook must not be folded into `agent_control.py init` or
  `ensure_schema()` as an automatic/silent repair.** *Reason: automatically discarding
  or restoring orphan tables without a human decision point risks silent data loss if a
  future orphan case isn't a pure duplicate — per this session's live incident, manual
  verification (row-count diff before recovery) was what caught that the naive
  drop-and-recreate approach would have (and initially did) discard 7 tasks' worth of
  history. See `.agent/rules/destructive-action-guard.md`.*
- **The recovery runbook must call the existing `_sync_valid_transitions(conn)` method
  directly, not hand-roll the same INSERT/DELETE logic a second time.** *Reason
  (spec-review finding #6): that method is already correct and atomic (per the existing
  `test_sync_valid_transitions_is_atomic_not_left_empty_on_failure` regression test) —
  this is the exact lesson tonight's Live Incident #3 already taught (see §5); only
  `schema_version` needs a direct, hand-written statement in the runbook, not both.*

## 4. Definition of Done (DoD)

1. **RED test, then GREEN fix.** `test_control_plane_schema_rebuild_atomicity.py` forces
   an exception partway through `_rebuild_schema_transactional()`'s copy loop (e.g. a
   malformed row via a monkeypatched `_copy_common_columns` or a corrupted source table)
   against a **non-empty, realistic DB** (multiple tasks across different states, child
   table rows present) and asserts:
   - Before the fix: the DB is left with orphan `_<table>_migrating` tables and empty/
     partial real tables (documents the current broken behavior — this is the RED test).
   - After the fix: on failure, the DB is restored to its exact pre-rebuild state (no
     orphan tables, no data loss, `schema_version` unchanged) — true rollback.
   - Also add/confirm a happy-path test with **non-empty realistic data** (the existing
     `test_trigger_survives_schema_rebuild` only covers an empty DB — this is the
     "missing test category" gap identified during intake).
2. **Startup health check.** `ensure_schema()` checks for the presence of any
   `_<table>_migrating` orphan table as its **literal first operation** — before line
   386's `PRAGMA journal_mode` and line 387's `executescript(SCHEMA_SQL)` (spec-review
   finding #4) — and if found, fails loudly with a clear, actionable error message (not
   a bare `FOREIGN KEY constraint failed` or similar low-level exception) — pointing at
   the recovery runbook from item 3. Verified by:
   - a test that seeds an orphan table and asserts the clear error is raised.
   - a **two-connection concurrency test** (spec-review finding #5, MODERATE): open
     connection A, begin a rebuild (rename tables to `_*_migrating`, hold the
     transaction open, do not commit), then have connection B call `ensure_schema()`
     and assert its health check does **not** false-fire against A's legitimate,
     uncommitted, in-progress rebuild (WAL snapshot isolation should make B see the
     pre-rebuild state cleanly). If this assumption doesn't hold under
     `busy_timeout` contention, that materially changes the fix's safety story and must
     be surfaced, not silently worked around.
3. **Recovery runbook.** A short, tested/documented procedure (script + doc, or a single
   well-commented script) for manually recovering a DB already stuck in this corrupted
   state — codifying the four lessons from tonight's live incidents: (a) always back up
   before touching the DB, (b) diff row counts between real and orphan tables before
   assuming it's safe to drop orphans, (c) suspend `enforce_valid_transition`/
   `enforce_valid_initial_state` triggers during the raw copy (skipping this caused the
   first recovery attempt tonight to silently delete all 7 recovered tasks via
   `enforce_valid_initial_state`, since `valid_transitions` was empty at the time), (d)
   repopulate `valid_transitions` by calling the existing `_sync_valid_transitions(conn)`
   method directly (spec-review finding #6) rather than hand-rolling the same
   INSERT/DELETE logic again — only `schema_version` needs a direct manual statement.
4. **Statement-splitter unit test**, independent of the full rebuild path (spec-review
   finding #3, MODERATE): calls the `SCHEMA_SQL` splitter directly and asserts the exact
   count and first-token of each resulting statement — 3 leading PRAGMAs filtered out
   (finding #2), 8 `CREATE TABLE` statements, 3 `CREATE INDEX` statements, and both
   `CREATE TRIGGER ... BEGIN ... END;` bodies parsed intact as single statements, not
   fragmented on their embedded semicolons.
5. **`journal_mode`/`busy_timeout` regression test** (spec-review finding #2): asserts
   `PRAGMA journal_mode` is still `wal` and `PRAGMA busy_timeout` is still `5000` on the
   connection after a rebuild, confirming the three skipped leading PRAGMAs in
   `SCHEMA_SQL` caused no behavior drift.
6. **Map-debt write ordering test** (spec-review finding #1, HIGH): forces a
   post-merge-but-pre-commit failure in `_rebuild_schema_transactional()` when an orphan
   `_tasks_old`/merge-conflict path is active, and asserts `map-debt.md` receives **no**
   entry when the transaction rolls back (only on a genuinely committed rebuild).
7. `python3 -m pytest plugins/agent-agentic-os/tests/test_control_plane_schema_rebuild_atomicity.py -v` — all tests pass (covers DoD items 1, 4, 5, 6 above).
8. Full existing control-plane test suite still green: `python3 -m pytest plugins/agent-agentic-os/tests/ -v` (no regressions, especially `test_control_plane_trigger_enforcement.py`).
9. `python3 plugins/agent-scaffolders/scripts/audit.py --path plugins/agent-agentic-os` and `audit_plugin_structure.py` both clean.
10. Docstring on `_rebuild_schema_transactional()` updated to accurately describe the
    real (now-true) atomicity guarantee, including the map-debt write-ordering fix.

## 5. Evidence Log (this session)

- **Original issue repro** (from #552's body): `conn.in_transaction` flips to `False`
  immediately after `conn.executescript(...)` inside a `BEGIN IMMEDIATE` block — proven
  via a 3-line in-memory SQLite repro.
- **Live incident #1 (this session, 2026-09-07):** `context/control_plane.db` found
  already in the corrupted state this issue describes — `tasks` empty, all 7 real task
  records (including #523's own history) plus their full transition/critic-review/
  verification-receipt/decision history trapped in `_*_migrating` orphan tables, from an
  earlier interrupted rebuild this same evening. Recovered via manual backup + row-count
  diff + column-intersection copy, confirmed zero data loss (backup retained at
  `context/control_plane.db.pre-recovery-backup-20260907101549`).
- **Live incident #2 (this session, same recovery attempt):** the first hand-written
  recovery script did **not** suspend `enforce_valid_transition`/
  `enforce_valid_initial_state` before copying rows back into `tasks`, because
  `valid_transitions` was empty at the time (only populated by
  `_sync_valid_transitions()`, never re-run). Every copied row was silently deleted by
  `enforce_valid_initial_state` and logged to `transition_violations` instead — a second
  real (if self-inflicted) data-loss near-miss, caught only by an explicit before/after
  row-count check, not by any error or exception. Recovered again from the untouched
  backup with triggers correctly suspended during the copy.
- **Live incident #3 (this session, same recovery attempt):** after recovery, calling
  the real `ensure_schema()` to repopulate `valid_transitions` (rather than reimplementing
  that logic by hand) re-triggered `_rebuild_schema_transactional()` — because
  `schema_version` was still 4 against `CURRENT_SCHEMA_VERSION = 5` — which hit the
  *same* `executescript()`-implicit-commit bug a second time, plus the `PRAGMA
  foreign_keys = ON;` re-enable side effect described in §1, corrupting the DB a third
  time (again recovered cleanly from the same untouched backup, this time by populating
  `valid_transitions` and `schema_version` directly rather than calling the buggy
  method). **Relevant to #523's own residual-risk disclosure**, not just #552: it shows
  #523's trigger-enforcement design can silently discard legitimate writes when any
  caller doesn't replicate the exact trigger-drop/recreate choreography
  `_rebuild_schema_transactional()` uses internally — same shape as #523's Finding #4
  drift risk, now actually observed rather than theoretical. **Action:** post this as a
  comment on #523 (closed) for its residual-risk record — #523 itself does not need
  reopening.

## 6. Out of Scope (file separately if it surfaces further)

- Any change to `_sync_valid_transitions()`, `_schema_needs_rebuild()`,
  `_copy_common_columns()`, or `_merge_orphaned_tasks_old()` beyond what the atomicity
  fix mechanically requires.
- Any change to the trigger *logic* itself (`enforce_valid_transition`,
  `enforce_valid_initial_state`) — only their drop/recreate choreography within the now-
  atomic rebuild is in scope.
- Broader "what if `_sync_valid_transitions()`-style choreography drift happens
  elsewhere" audit — flagged as a comment on #523, not expanded here.
- **Lock-hold-time increase** (spec-review finding, MINOR): this fix necessarily makes
  `_rebuild_schema_transactional()` hold its `BEGIN IMMEDIATE` RESERVED lock for the
  full rebuild duration — previously released early by the implicit-commit bug. A second
  process attempting a concurrent rebuild during that window now waits up to
  `busy_timeout` (5s) or raises `sqlite3.OperationalError: database is locked`, where
  before it would not have contended at all. Not required for this DoD (no test suite
  currently exercises true multi-process concurrent rebuilds), but track as a map-debt
  follow-up since it's a direct side effect of this fix, not a pre-existing condition.
- **`docs/plans/` and `docs/superpowers/` gitignore convention** — raised during this
  session's intake, deferred to a separate follow-up change after #552 ships. Unrelated
  to the atomicity fix; would be scope creep on this diff.
