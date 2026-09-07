# Implementation Plan: SQLite trigger-based transition enforcement (Issue #523)

Spec: `docs/plans/issue-523-trigger-enforcement-spec.md`

## Pre-work

1. Read ADR-007 (`docs/ADRs/007_maf_adapter_runtime_decision.md`) and any current
   control-plane security spec for conflicts with this change. Surface anything relevant
   before touching code.

## Steps

1. **Schema additions** (`control_plane/adapters.py`, `SCHEMA_SQL`):
   - `valid_transitions(from_state TEXT NOT NULL, to_state TEXT NOT NULL, PRIMARY KEY (from_state, to_state))`
   - `transition_violations(violation_id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL, attempted_from_state TEXT NOT NULL, attempted_to_state TEXT NOT NULL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)`
   - `CREATE TRIGGER IF NOT EXISTS enforce_valid_transition AFTER UPDATE ON tasks WHEN NEW.state != OLD.state AND NOT EXISTS (SELECT 1 FROM valid_transitions WHERE from_state = OLD.state AND to_state = NEW.state) BEGIN INSERT INTO transition_violations(task_id, attempted_from_state, attempted_to_state) VALUES (OLD.task_id, OLD.state, NEW.state); UPDATE tasks SET state = OLD.state, updated_at = OLD.updated_at WHERE task_id = NEW.task_id; END;` — note both `state` and `updated_at` are restored (finding #7).
   - `CREATE TRIGGER IF NOT EXISTS enforce_valid_initial_state AFTER INSERT ON tasks WHEN NOT EXISTS (SELECT 1 FROM valid_transitions WHERE from_state IS NULL AND to_state = NEW.state) BEGIN INSERT INTO transition_violations(task_id, attempted_from_state, attempted_to_state) VALUES (NEW.task_id, NULL, NEW.state); DELETE FROM tasks WHERE task_id = NEW.task_id; END;` (finding #5) — **revised during implementation:** deletes the illegal row rather than coercing to `INTAKE`. The original coerce-to-`INTAKE` design caused a cross-trigger cascade bug — the corrective `UPDATE` fired `enforce_valid_transition`, which then saw e.g. `DONE → INTAKE` as illegal and reverted the coercion right back, silently defeating the fix. Delete avoids this entirely since `DELETE` doesn't touch the UPDATE trigger; this doesn't reverse the UPDATE trigger's own coerce-not-delete decision (see spec guardrail table for why the two triggers legitimately differ). Requires `valid_transitions` to also carry a row per legal *initial* state (`from_state IS NULL`) sourced from `LEGAL_INITIAL_STATES` (see Step 2's note on this constant's provenance).
   - **`LEGAL_INITIAL_STATES` provenance:** currently a standalone constant (`["INTAKE"]`) in `adapters.py`, not derived from `TransitionRegistry` — flagged as a deviation from the single-source-of-truth principle. Pending explicit resolution: either promote to first-class `transition_templates.yaml`/`TransitionRegistry` data (e.g. a declared `initial_states` list), or keep as an approved, documented scoped exception. **Not yet decided — do not finalize this file's implementation without resolving it explicitly with the user first.**
   - **Cross-trigger cascade fix must be verified, not assumed**: the corrective `DELETE` inside `enforce_valid_initial_state` must not itself trigger anything unexpected (SQLite has no `AFTER DELETE` trigger declared on `tasks` in this schema, so this is expected to be inert, but confirm via the cascade-fix test in Step 4).
   - Add to `CURRENT_SCHEMA_VERSION` bump + `SCHEMA_MIGRATIONS` entries so existing DBs self-heal.
   - **Ordering constraint (finding #3):** no `SCHEMA_MIGRATIONS` entry may `UPDATE`/`INSERT` against `tasks` touching `state` before `valid_transitions` is resynced for the current schema version within the same `ensure_schema()` pass — verify this ordering explicitly when adding these triggers, since the triggers become active as soon as `SCHEMA_SQL` runs, ahead of the registry sync in Step 2 below.
2. **Registry sync** (`ensure_schema()`): after schema/migrations run, import
   `TransitionRegistry` from `control_plane.registry`, call `load_default().get_all_edges()`,
   and idempotently sync into `valid_transitions` using **parameterized INSERT statements**
   (`?` placeholders — finding #1, not string-formatted SQL) (`DELETE FROM valid_transitions;`
   then bulk parameterized `INSERT`, inside the same transaction as the rest of
   `ensure_schema()`). Also sync legal initial-state rows for the INSERT-side trigger.
3. **Prototype verification**: re-run the `/tmp` trigger experiment against the *actual*
   `SCHEMA_SQL` (not a toy schema) to confirm the trigger behaves identically once real
   columns/constraints are present (e.g. the `tasks.state` CHECK constraint firing alongside),
   and additionally with `PRAGMA recursive_triggers = ON` set explicitly (finding #2).
4. **Tests** — new file `plugins/agent-agentic-os/tests/test_control_plane_trigger_enforcement.py`:
   - `test_valid_transitions_table_matches_registry()`
   - `test_illegal_update_transition_via_raw_sql_is_reverted_and_logged()` (assert both `state`
     and `updated_at` are restored)
   - `test_illegal_insert_initial_state_via_raw_sql_is_deleted_and_logged()` (finding #5;
     assert the row is **deleted**, not coerced — revised)
   - `test_delete_then_reinsert_bypass_is_caught_by_insert_trigger()` (finding #5; assert the
     re-inserted row is deleted, task no longer exists)
   - `test_insert_trigger_cascade_does_not_fire_update_trigger()` (new — proves the
     cross-trigger cascade bug is fixed: illegal INSERT → row deleted → exactly one
     `transition_violations` row, not two → confirms `enforce_valid_transition` did not also
     fire as a side effect of the corrective `DELETE`)
   - `test_legal_transition_via_raw_sql_is_unaffected_and_unlogged()`
   - `test_trigger_survives_schema_rebuild()` (forces `_rebuild_schema_transactional()`, then
     repeats the illegal-transition check — both triggers must be explicitly dropped and
     recreated around the rebuild, not left to `CREATE TRIGGER IF NOT EXISTS` alone; see the
     ALTER TABLE RENAME trigger-orphaning bug found while writing this test)
   - `test_recursive_triggers_on_hits_recursion_limit_but_no_illegal_write_persists()`
     (finding #2, explicit `PRAGMA recursive_triggers = ON` — revised expectation: asserts
     `sqlite3.OperationalError` is raised, illegal write does not persist, but violation log
     is empty — documented accepted residual risk, not "no infinite loop, no duplicate rows"
     as originally worded)
5. **Run full control-plane suite**: `pytest plugins/agent-agentic-os/tests/ -k control_plane -v`
6. **Audits**: `audit.py` and `audit_plugin_structure.py` against `agent-agentic-os`.
7. **Reinstall plugin**: `plugin_add.py plugins/agent-agentic-os -y`.
8. **Update map-debt / issue #523**: comment on the issue documenting the partial fix and its
   explicit boundaries — adjacency-only (not full `policy.py` parity), silent revert on
   detected violations, and the three residual risks now documented in the spec: DROP
   TRIGGER/file-replace, `policy.py`/`valid_transitions` drift silently reverting a legitimate
   write (finding #4), and `transition_violations` itself having no tamper protection
   (finding #6).

## Verification (DoD mapping)

Each step above maps 1:1 to a DoD checkbox in the spec. No step is considered done until its
associated automated check (pytest, audit script) exits 0 — per TDW policy, tests for steps 4
are written and run failing (RED) before step 1-2's implementation, then implementation makes
them pass (GREEN).
