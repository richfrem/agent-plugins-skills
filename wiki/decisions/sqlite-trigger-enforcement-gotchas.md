# SQLite trigger-based enforcement: three empirically-discovered gotchas

**Status:** CONFIRMED
**Source:** GitHub Issue #523 (control-plane transition enforcement), 2026-09-07

## Context

Implementing a SQLite-trigger backstop for enforcing legal `(from_state, to_state)`
transitions on `context/control_plane.db`, independent of the Python application layer.
Three non-obvious SQLite behaviors were found only by empirical testing, not by design
review or a single-trigger prototype — future work adding triggers to this or any other
SQLite schema in this repo should check against these first.

## Gotcha 1: `RAISE(ABORT)`/`FAIL`/`IGNORE` roll back the *entire* statement, including earlier
triggers' side effects

A "log the violation, then reject the write" design using two triggers (one `INSERT`s into
an audit table, a second `RAISE(ABORT)`s) does not work: SQLite's conflict-resolution
mechanisms roll back every change made during the statement, including the audit-log
`INSERT` from the *other* trigger. Verified directly against a toy schema. The only
mechanism that both blocks the illegal write and preserves the audit log entry is an
`AFTER` trigger that logs, then issues its own corrective `UPDATE`/`DELETE` to undo the
change — never `RAISE`.

## Gotcha 2: one trigger's corrective action can cascade into a *different* trigger,
silently defeating the fix

If two triggers exist on the same table (e.g. one on `INSERT`, one on `UPDATE`), and the
`INSERT` trigger's corrective action is itself an `UPDATE` (e.g. "coerce this illegal value
back to a safe default"), that corrective `UPDATE` can satisfy the *other* trigger's firing
condition — which then reverts the correction right back, treating it as its own illegal
transition. This is **not** gated by `PRAGMA recursive_triggers` (that pragma only governs
a trigger firing *itself* again — cross-trigger cascades fire regardless of the setting).
**Mitigation:** where an `INSERT`-trigger correction would otherwise need to `UPDATE` a
row, prefer `DELETE` instead if there's no accumulated state on the row worth preserving —
`DELETE` doesn't trigger `AFTER UPDATE` triggers, sidestepping the cascade entirely.

## Gotcha 3: `ALTER TABLE ... RENAME TO ...` re-points existing triggers rather than
dropping them

A common self-healing schema-migration pattern (rename table → recreate fresh → copy rows
→ drop old) silently orphans any trigger that existed on the original table: the rename
causes the trigger to follow the renamed (soon-to-be-dropped) table rather than being
dropped, so a subsequent `CREATE TRIGGER IF NOT EXISTS` against the *new* table is a no-op
(a trigger of that name already exists, just misdirected) — and the trigger is then
permanently destroyed when the old/renamed table is finally dropped. **Mitigation:**
explicitly `DROP TRIGGER IF EXISTS` before the rename step and recreate every trigger
after the table swap completes; never assume `CREATE TRIGGER IF NOT EXISTS` inside the
fresh schema DDL is sufficient during a rename-based migration.

## Gotcha 4: `conn.executescript()` silently commits any open transaction — and its
statements' own embedded `PRAGMA`s can silently override the caller's connection settings

**Status:** CONFIRMED — fixed via GitHub Issue #552, 2026-09-07.

`conn.executescript()` in Python's `sqlite3` module implicitly commits any open
transaction before running (documented CPython behavior) — a `BEGIN IMMEDIATE` opened
before an `executescript()` call provides no real atomicity for anything after that call.
This predates issue #523 (found in `_rebuild_schema_transactional()`, which dates to an
earlier extraction).

A second, easy-to-miss consequence: if the executed script itself contains `PRAGMA`
statements (e.g. a `CREATE TABLE`/`CREATE TRIGGER` schema script that leads with
`PRAGMA foreign_keys = ON;` for standalone use), those PRAGMAs also run — silently
overriding any connection-level setting the caller had explicitly configured moments
earlier (e.g. `PRAGMA foreign_keys = OFF;` set specifically to suppress FK enforcement
during a table-rename-based migration, per Gotcha 3's pattern). Combined with SQLite's
foreign-key-definition auto-repoint-on-rename behavior, this produced a third, distinct,
silent-data-loss failure mode: `DROP TABLE` on a renamed parent table (with FK
enforcement now unexpectedly back on) cascade-deleted not-yet-migrated rows in a child
table whose FK definition had auto-repointed to follow the same rename — with **no
exception raised at all**, only discovered via a non-empty-data regression test.

**Mitigation:** never call `executescript()` inside a manually-managed transaction whose
atomicity actually matters. Split the script into individual statements (Python's
`sqlite3.complete_statement()` correctly handles multi-statement blocks like
`CREATE TRIGGER ... BEGIN ... END;` that have embedded semicolons) and `execute()` them
one at a time inside the transaction — explicitly filtering out any `PRAGMA` statements
from the script if the transaction depends on a specific PRAGMA state the caller already
established, since those must not be allowed to silently override it mid-transaction.

## When this applies

Any future work adding `CREATE TRIGGER` to a SQLite schema in this repo — especially one
with more than one trigger on the same table, or one that participates in a rename-based
migration pattern.
