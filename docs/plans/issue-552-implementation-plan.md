# Implementation Plan — Issue #552

Full spec: `docs/plans/issue-552-spec.md`

## Steps

0. ~~**File #523 comment**~~ — DONE: evidence from spec §5 posted as a comment on closed
   issue #523 (residual-risk record, not reopening):
   https://github.com/richfrem/agent-plugins-skills/issues/523#issuecomment-5573890618

1. **Statement splitter (standalone, tested first)**: write a small helper that splits
   `SCHEMA_SQL` into individual statements via `sqlite3.complete_statement`-driven
   parsing (correctly handling both `CREATE TRIGGER ... BEGIN ... END;` blocks), and
   filters out the 3 leading PRAGMA statements (`foreign_keys`, `journal_mode`,
   `busy_timeout` — spec-review finding #2). Write the dedicated unit test first
   (spec-review finding #3): assert exact statement count/first-token breakdown (3
   PRAGMAs filtered, 8 `CREATE TABLE`, 3 `CREATE INDEX`, 2 `CREATE TRIGGER` with intact
   bodies) before this helper is ever used inside the transactional method.

2. **RED test**: write `test_control_plane_schema_rebuild_atomicity.py` with a non-empty
   realistic DB fixture; force an exception mid-copy-loop; assert current (broken)
   behavior leaves orphan `_*_migrating` tables — confirms the failure reproduces.

3. **GREEN fix — transaction boundary**: replace `conn.executescript(SCHEMA_SQL)` in
   `_rebuild_schema_transactional()` with a loop of individual `conn.execute()` calls
   using the splitter from step 1, so `PRAGMA foreign_keys = OFF` and the open `BEGIN
   IMMEDIATE` transaction both hold for the method's full duration. Re-run RED test —
   should now show a full, clean rollback.

4. **GREEN fix — map-debt write ordering (spec-review finding #1, HIGH)**: change
   `_merge_orphaned_tasks_old()`/`_log_orphan_merge_conflicts()` so the `map-debt.md`
   filesystem append happens only *after* `COMMIT` succeeds, not at line 554 mid-
   transaction. Collect conflicting task_ids in a local list during the copy loop;
   call `_log_orphan_merge_conflicts()` once, after the `COMMIT` at line 585, on the
   success path only (inside `ensure_schema()`'s caller frame or right after the
   `try` block's `COMMIT` line, before `finally`). Add the map-debt write-ordering test
   (spec-review finding #1 / DoD item 6): force a post-merge-but-pre-commit failure with
   an active orphan-merge path, assert zero map-debt entries are written on rollback.

5. **Non-empty happy-path test**: add/extend a test exercising
   `_rebuild_schema_transactional()` against a DB with multiple tasks/child rows,
   asserting all data survives the rebuild intact (the missing test-category gap).

6. **`journal_mode`/`busy_timeout` regression test** (spec-review finding #2): assert
   both PRAGMAs are unchanged after a rebuild, confirming the 3-PRAGMA skip in step 1
   caused no behavior drift.

7. **Startup health check**: add an orphan-table check as the **literal first
   operation** inside `ensure_schema()` — before line 386's `PRAGMA journal_mode` and
   line 387's `executescript(SCHEMA_SQL)` (spec-review finding #4, corrected placement)
   — that fails loudly with a clear message + pointer to the recovery runbook if any
   `_*_migrating` table exists. Add:
   - a test seeding an orphan table and asserting the clear error is raised.
   - a **two-connection concurrency test** (spec-review finding #5, MODERATE): connection
     A begins a rebuild and holds it open (uncommitted); connection B calls
     `ensure_schema()` and must NOT false-fire the health check against A's legitimate
     in-progress rebuild. If WAL snapshot isolation doesn't hold this cleanly, surface
     that as a blocking finding, don't silently paper over it.

8. **Recovery runbook**: write a small, tested script + doc (based on tonight's
   corrected recovery script, scratchpad copy at
   `/private/tmp/.../recover_control_plane_db.py`) capturing the four corrected lessons
   (backup first, diff row counts, suspend enforcement triggers during raw copy, call
   `_sync_valid_transitions(conn)` directly rather than hand-rolling it — spec-review
   finding #6 — plus a direct `schema_version` statement).

9. **Docstring fix**: update `_rebuild_schema_transactional()`'s docstring to describe
   the real (now true) guarantee, including the map-debt write-ordering fix.

10. **Map-debt entry**: log the lock-hold-time-increase side effect (spec-review
    finding, MINOR — §6 Out of Scope) as an `OPEN` map-debt follow-up, not silently
    dropped.

11. **Full verification**: run full control-plane test suite, both plugin audits.

## Review approach

Single-agent review (not full multi-agent fan-out) for the spec stage — done: see
`cli-agents:security-auditor` REVISE verdict, 6 findings, all folded into spec §3/§4/§6
above. Post-implementation, run the same tier of single-agent review again (matching
#523's two-round precedent: spec-stage + implementation-stage), since actual SQL/test
code often surfaces gaps invisible from the spec alone.
