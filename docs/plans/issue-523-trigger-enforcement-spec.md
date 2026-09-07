# TASK SPEC: SQLite trigger-based transition enforcement + violation audit log

**Task ID:** `issue-523-trigger-enforcement`
**Status:** DRAFT
**Related:** GitHub Issue #523

## 1. The Job

- **Objective:** Add a database-level backstop that rejects illegal `tasks.state` transitions
  (per the existing `transition_templates.yaml` / `TransitionRegistry` adjacency graph) on
  *any* write to `context/control_plane.db` — not just writes that go through
  `ControlPlane`/`PersistencePort`/`SqlitePersistenceAdapter`, and not just `UPDATE` statements
  — and logs every rejected attempt to a new audit table for monitoring.
- **Target Subsystems:**
  - `plugins/agent-agentic-os/scripts/control_plane/adapters.py` (`SCHEMA_SQL`,
    `SCHEMA_MIGRATIONS`, `ensure_schema()`)
  - `plugins/agent-agentic-os/scripts/control_plane/registry.py` (read-only: `get_all_edges()`)
  - `plugins/agent-agentic-os/tests/test_control_plane_sqlite_persistence_adapter.py` (new
    trigger tests) or a new sibling test file
    `plugins/agent-agentic-os/tests/test_control_plane_trigger_enforcement.py`

## 2. The Why (Rationale & Context)

- **Problem Statement:** Today, `policy.py`'s `CHECK_REGISTRY`/`evaluate_check()` and
  `registry.py`'s `TransitionRegistry` enforce phase-transition legality only in the Python
  application layer. Any actor with filesystem access — including the exact class of
  autonomous agent this system is built to constrain — can bypass every gate with a single
  raw `sqlite3 context/control_plane.db "UPDATE tasks SET state='DONE' WHERE task_id='X'"`,
  with zero enforcement and no audit trail (GitHub Issue #523).
- **User / System Impact:** Every safety property claimed by the control-plane pipeline (no
  DONE without a passing verifier, no advancing past review without a receipt, the Supreme
  Law Human Gate) is only true if every caller is cooperative. This closes the specific
  "arbitrary state teleport via raw SQL" exploit at the database engine level, independent of
  which tool or language touches the file, and gives operators a way to detect when someone
  tried.

## 3. Semantic Guardrails & Operational Reasons

| Guardrail Boundary | Operational Reason ("Why") |
| :--- | :--- |
| Scope is adjacency-legality only (`(from_state, to_state)` must exist in the registry) — **not** a reimplementation of `policy.py`'s dynamic gate checks (receipt existence, critic-review pass, prior-art scans) | Those checks depend on data/logic outside SQL's reach or require duplicating business logic in two places; full parity was explicitly rejected as too costly in #523's original disposition. This is a deliberate partial fix, and must be documented as such — not presented as closing the whole gap. |
| Enforcement uses the tested AFTER-UPDATE revert+log pattern, NOT `RAISE(ABORT)`/`FAIL`/`IGNORE` | Empirically verified (see Evidence) that SQLite's conflict-resolution RAISE mechanisms roll back the entire statement, including any earlier trigger's `INSERT` into the violation log — so a log-then-abort design silently loses every log entry. The AFTER-trigger revert pattern is the only tested mechanism that both blocks the illegal state change and preserves the audit log row. |
| No SQL error surfaces to the caller on a rejected write | A direct, accepted consequence of the AFTER-trigger revert pattern — the statement reports success, but `state` is silently reverted. Legitimate application-layer callers **should not** hit this path under `policy.py`'s current behavior (they only submit legal transitions vetted by `policy.py` first), so this only affects bypass attempts today, for whom "no useful negative feedback, but the attempt is durably logged" satisfies the actual goal. This is a current-behavior assumption, not an enforced invariant of this design — see the residual-risk row below for what happens if that assumption ever breaks. |
| `valid_transitions` lookup table (not hardcoded edges in trigger SQL) sourced from `TransitionRegistry.get_all_edges()`, resynced on every `ensure_schema()` call | Directly answers the "two enforcement layers drift" risk raised during review: a data-table sync is far more testable and lower-risk than hand-maintained trigger SQL, and tying the resync into the existing self-healing `ensure_schema()` flow (which already reruns on every `init_db()`) makes it self-maintaining with zero manual migration step per DAG change. **Implementation requirement:** the sync must use parameterized `INSERT` statements (`?` placeholders for `from_state`/`to_state`), not string-formatted SQL — state names originate from YAML today (low risk), but a future typo/edited value with an embedded quote must not produce a malformed statement (external security review, finding #1). |
| `transition_violations` audit table schema is deliberately minimal: `task_id, attempted_from_state, attempted_to_state, timestamp` — no actor/context/raw-SQL column | A SQL trigger has no access to the OS user, calling process, or original SQL statement text — anything beyond the state pair would just be a redundant re-encoding of `OLD`/`NEW`, not real information. Confirmed during interview; rejected the richer-schema option as adding no signal. |
| Trigger DDL lives in `SCHEMA_SQL` / is applied via `ensure_schema()`, not a one-time manual step | The self-healing schema-rebuild path (`_rebuild_schema_transactional()`) rebuilds `tasks` by rename→recreate→copy; a trigger not re-declared in `SCHEMA_SQL` would silently vanish on the next rebuild. |
| Enforcement covers `INSERT` and `DELETE` on `tasks`, not just `UPDATE` | External security review (finding #5) identified that an `AFTER UPDATE`-only trigger leaves a cheaper bypass than either residual risk originally documented: `INSERT INTO tasks (...) VALUES ('X', 'DONE', ...)` for a new/reused `task_id`, or `DELETE` + re-`INSERT`, achieves the same illegal state-teleport using ordinary SQL, with no elevated technique required — actually *less* effort than `DROP TRIGGER` or file replacement. An `AFTER INSERT ON tasks` trigger enforcing that a newly inserted row's `state` is a legal *initial* state (per the registry's edges from an implicit "does not exist" state) closes this at the same cost tier as the UPDATE trigger; combined with the UPDATE trigger, `DELETE`+re-`INSERT` is also covered since the re-`INSERT` is itself checked. |
| **Revised (superseded below):** the two enforcement triggers use deliberately *different* revert mechanisms — the UPDATE trigger coerces/reverts state (never destroys), the INSERT trigger deletes the row. This is a principled distinction, not an inconsistency — see the next two rows. |
| UPDATE trigger reverts by coercing `state` (and `updated_at`) back to `OLD.*` — never deletes the row | Unchanged from the original decision: consistent with revert-never-destroy, and lower blast radius under the Finding #4 drift scenario — if a legitimate caller's *transition* is ever misclassified due to future `policy.py`/`valid_transitions` drift, coercing back to `OLD.state` keeps their task record recoverable and visible, since the row already existed with real accumulated history (transitions, receipts, decisions) worth protecting. |
| INSERT trigger reverts by **deleting** the illegally-inserted row, not coercing it to `INTAKE` | **Revised after implementation discovered a cross-trigger cascade bug** (see below): coercing the INSERT trigger's illegal row to `INTAKE` via a corrective `UPDATE` unavoidably fires the *separate* `enforce_valid_transition` (UPDATE) trigger, which then sees the coercion itself as an illegal edge (e.g. `DONE → INTAKE` is not a legal transition) and reverts it right back to the illegal state — silently defeating the INSERT trigger's own fix and logging a confusing second violation row. **This does not reverse the original coerce-not-delete decision for the UPDATE trigger** — the reasoning behind "coerce, don't delete" was protecting *accumulated real work* on an existing task record, and that reasoning does not apply at INSERT time: a freshly-inserted illegal row has no accumulated transitions, receipts, or decisions to protect, so deleting it loses nothing a legitimate caller would ever have accrued. The two triggers reverting differently is a principled distinction driven by what each is protecting, not an inconsistency. |
| Cross-trigger cascade explicitly tested, not just fixed | A dedicated test proves the cascade is closed: an illegal `INSERT` results in the row being deleted, **zero** rows firing `enforce_valid_transition` as a side effect, and exactly **one** violation row logged (not two, from the old cascade). |
| Both enforcement triggers are explicitly dropped before `_rebuild_schema_transactional()`'s table-rename step and explicitly recreated after the row-copy completes — not left to `CREATE TRIGGER IF NOT EXISTS` inside `SCHEMA_SQL` alone | **Second implementation-time bug found empirically** (2026-09-07): `ALTER TABLE "tasks" RENAME TO "_tasks_migrating"` re-points *existing* triggers on `tasks` to follow the rename rather than dropping them. Left unhandled, this silently orphans `enforce_valid_transition` — it survives the rename bound to the wrong table, the mid-script `CREATE TRIGGER IF NOT EXISTS` no-ops (a trigger of that name already exists, just misdirected), and it is then permanently destroyed when `_tasks_migrating` is dropped at the end of the copy loop (SQLite drops a table's triggers along with it). This means **every schema rebuild — including this very migration's own first run on an existing DB — would have silently disabled all UPDATE-side enforcement** without an explicit drop-and-recreate step. `enforce_valid_initial_state` needed the same drop/recreate for a different reason (its own cascade with the copy INSERTs, above); this row documents that `enforce_valid_transition` needed it too, for a different reason, and both are now handled together in one place. |
| `recursive_triggers = ON` is a documented, accepted residual risk, not a silent bypass | **Revised from the original DoD wording** ("no infinite loop, no duplicate violation rows") after empirical testing: with this non-default pragma explicitly set, the UPDATE trigger's corrective `UPDATE` re-fires itself (the correction itself looks like a fresh, non-adjacent transition, e.g. `IN_WORKTREE → INTAKE` isn't a legal edge either), oscillating until SQLite's built-in recursion-depth cap aborts the *entire statement* — the same all-or-nothing rollback semantics as `RAISE(ABORT)` (see the earlier guardrail row on why abort-based designs were rejected). **Net effect, verified:** the illegal write never persists (no security regression — confirmed by test), but the violation goes unlogged in this mode, and the caller receives an unhandled `sqlite3.OperationalError` instead of a clean silent revert. `recursive_triggers` is OFF by default in SQLite; this residual risk only matters if some other code path touching `context/control_plane.db` explicitly turns it on. Accepted rather than fixed — no lock/sentinel mechanism was designed for this, scoped out as open-ended effort for a non-default configuration. |
| Corrective revert restores `updated_at` in addition to `state` | External security review (finding #7) flagged that a revert touching only `state` would be partial if other columns are modified in the same statement. Verified directly against `adapters.py`: **all three** legitimate transition-write call sites (`apply_transition`, `apply_transition_with_receipts` ×2) always set `state` and `updated_at` together in one `UPDATE` — this is not a hypothetical, it is the universal pattern. The corrective `UPDATE` therefore reverts both columns to `OLD.state`/`OLD.updated_at`, at no added cost. |
| A new automated pytest asserts `valid_transitions` (as materialized in a live/temp DB) matches `TransitionRegistry.load_default().get_all_edges()` exactly | Requested explicitly: makes drift between the YAML-driven registry and the SQL-layer enforcement fail loudly in CI/pre-push, sibling to the existing `test_registry_covers_every_allowed_edge` parity test, rather than relying on eyeballing. |
| `SCHEMA_MIGRATIONS` entries must never `UPDATE`/`INSERT`/`DELETE` against `tasks` in a way that touches `state` before `valid_transitions` has been resynced for the current schema version, within the same `ensure_schema()` pass | External security review (finding #3): if a future migration needs to backfill/normalize `tasks.state` directly (e.g. merging two deprecated state names), and the trigger + an empty/stale `valid_transitions` table are both already active, that legitimate administrative write would be misclassified as illegal, silently reverted, and logged as a false-positive violation. Ordering requirement, not a code change today — documented so a future migration author doesn't discover this by accident. |
| Recursive-trigger behavior must be tested with `PRAGMA recursive_triggers = ON`, not just the default (typically OFF) | External security review (finding #2): the corrective `UPDATE` inside the trigger body is itself an `UPDATE` on `tasks`. The `WHEN NEW.state != OLD.state` guard should make a recursive re-firing self-terminating, but this was only empirically verified under the default setting during the `/tmp` prototype — an environment where something upstream forces `recursive_triggers` ON was never exercised. Must be an explicit test case, not an assumption. |
| Consult ADR-007 and any control-plane security docs before editing `control_plane/*.py` | Per CLAUDE.md's standing rule for this security-sensitive control-plane code — must happen before implementation, not skipped because the change is "just SQL." |
| Known residual risk, explicitly out of scope: `DROP TRIGGER` or wholesale `.db` file replacement bypasses this entirely | Both require the same filesystem write access the actor already has today; closing this is not claimed and was explicitly accepted as unavoidable at this layer during interview. |
| Known residual risk, explicitly out of scope: silent revert of a *legitimate* write if `policy.py` and `valid_transitions` ever drift out of sync (e.g. a future `policy.py` override path approves an edge not present in the static registry) | External security review (finding #4). If this ever happens, `SqlitePersistenceAdapter` would observe apparent success (SQLite reports the `UPDATE` succeeded) while the trigger silently reverts the row underneath it — an application/database state desync for a *trusted* caller, not just a logged bypass attempt. This is accepted as an inherent tradeoff of enforcing at the SQL layer independent of application logic, at the same tier as the DROP TRIGGER/file-replacement risks above — not a bug introduced by this design, and not fixed by adding more code here. |
| Known residual risk, explicitly out of scope: `transition_violations` itself has no tamper protection — `DELETE FROM transition_violations` or `DROP TABLE transition_violations` erases the audit trail while leaving enforcement fully intact | External security review (finding #6). This is a more surgical compromise than `DROP TRIGGER` (enforcement keeps working, only the evidence disappears) and defeats the "gives operators a way to detect when someone tried" goal in §2. Accepted at the same tier as the other residual risks — protecting the audit table itself (permissions, triggers-on-the-trigger-table, etc.) is an infinite regress the auditor correctly flagged; a line has to be drawn somewhere, and it's drawn here for this iteration. |
| `_sync_valid_transitions()`'s `DELETE`+`INSERT` is wrapped in an explicit `BEGIN IMMEDIATE`/`COMMIT`/`ROLLBACK`, not left as two bare statements | **Code-review finding, fixed** (2026-09-07, single-agent code review dispatch): the original implementation issued a bare `DELETE FROM valid_transitions;` followed by a bare `executemany(INSERT...)` with no transaction wrapper — on the DB this spec itself describes as shared across concurrent worktrees/agents, a failure (or a concurrent reader) between the two could observe `valid_transitions` as empty or partially populated, during which *every* legitimate transition would be misclassified as illegal and reverted/deleted. Not previously disclosed as a residual risk — this is genuinely new code #523 introduced, unlike `_rebuild_schema_transactional()`'s separate, pre-existing atomicity bug (filed as #552, explicitly not fixed here — see below). Regression test forces a real mid-batch constraint violation and proves the table retains its full prior set afterward, never left empty or partial. |
| `_rebuild_schema_transactional()`'s own `BEGIN IMMEDIATE`/`COMMIT` wrapper does not actually protect against partial migration on exception (`conn.executescript()` silently commits mid-transaction) | **Found during the same code-review pass, explicitly NOT fixed here** — filed as GitHub Issue #552 instead. This is a pre-existing bug in the schema-migration engine (dating to issue-524's Step 5 extraction), not something #523's own new trigger-drop/recreate logic caused; #523 only ever claimed its triggers survive a *successful* rebuild (tested), never atomicity-under-failure. Fixing the general rebuild-atomicity engine is out of scope for a security-trigger PR — same "pre-existing, unrelated, file separately" discipline applied to `audit.py`'s findings (#551) and other out-of-scope discoveries this session. |

## 3a. External Review Record

Single-agent security review (`cli-agents:security-auditor`) dispatched against this spec +
implementation plan on 2026-09-07, prior to implementation. Verdict: **REVISE**. Two findings
(#5: INSERT/DELETE+INSERT bypass; #4: legitimate-caller drift desync) were assessed as
significant and addressed above (finding #5 closed via new INSERT-trigger scope; finding #4
corrected from an asserted fact to a documented residual risk). Five smaller findings (#1, #2,
#3, #6, #7) were incorporated as one-line guardrails/DoD items above; #7 was upgraded from
"disclose if theoretical" to "fix" after verifying against `adapters.py` that the condition it
warned about (another column changing alongside `state` in the same statement) is universally
true in this codebase, not hypothetical. No second review round was dispatched for these
fixes — the user reviewed and directed each disposition directly; this document reflects that
decision.

**Post-approval implementation finding (2026-09-07):** during TDD implementation in the
worktree, empirical testing surfaced a cross-trigger cascade bug not caught by external review
or the `/tmp` prototype (which only ever exercised one trigger in isolation): the INSERT
trigger's original coerce-to-`INTAKE` corrective action unavoidably fired the separate UPDATE
trigger, which then reverted the coercion itself (since e.g. `DONE → INTAKE` is not a legal
edge), silently defeating the fix. Resolved by having the INSERT trigger delete the illegal
row instead of coercing it — see the guardrail table's revised rows for why this doesn't
reverse the UPDATE trigger's coerce-not-delete decision. Flagged to the user before continuing
implementation, per this session's established discipline of surfacing design deviations
rather than silently resolving them.

**Two further post-approval implementation findings (2026-09-07),** surfaced while writing the
`test_trigger_survives_schema_rebuild` and `test_recursive_triggers_on_*` tests — again, not
caught by external review or the single-trigger `/tmp` prototype:
1. `_rebuild_schema_transactional()`'s table-rename step silently orphans `enforce_valid_transition`
   (it survives the rename bound to the wrong table, then is destroyed when the migrating table
   is dropped) — fixed by explicitly dropping and recreating both triggers around the rebuild,
   not relying on `CREATE TRIGGER IF NOT EXISTS` alone.
2. `PRAGMA recursive_triggers = ON` causes the UPDATE trigger's corrective action to oscillate
   until SQLite's recursion cap aborts the statement — the illegal write still never persists,
   but the violation goes unlogged and the caller sees an unhandled exception. Decided: accept
   as a documented residual risk (not SQLite's default setting) rather than design a lock/
   sentinel mechanism now.

Both flagged to the user with empirical evidence before any fix was applied; both resolutions
were the user's explicit direction, not unilateral choices.

**Post-commit code review (2026-09-07):** a second single-agent `cli-agents:security-auditor`
dispatch reviewed the actual committed implementation (commit `c9019f5b`) against this spec.
Verdict: **Proceed with changes**. Confirmed the trigger/table DDL is byte-identical across
all three copies (`SCHEMA_SQL`, `SCHEMA_MIGRATIONS`, the rebuild-path recreation) — no drift.
Two new findings, resolved differently based on whether the code was #523's own or pre-existing:
`_sync_valid_transitions()`'s unguarded `DELETE`+`INSERT` (genuinely new code #523 wrote) was
fixed with a TDD regression test proving atomicity; `_rebuild_schema_transactional()`'s broken
transaction wrapper (pre-existing, predates #523) was filed separately as #552, not fixed here.

## 4. Objective Definition of Done (DoD)

- [ ] `valid_transitions` table added to `SCHEMA_SQL`, populated/resynced from
      `TransitionRegistry.load_default().get_all_edges()` inside `ensure_schema()` (idempotent:
      safe to rerun every process start).
- [ ] `transition_violations` table added to `SCHEMA_SQL`
      (`task_id, attempted_from_state, attempted_to_state, timestamp`).
- [ ] `AFTER UPDATE ON tasks` trigger added to `SCHEMA_SQL`: on an illegal
      `(OLD.state, NEW.state)` pair (no match in `valid_transitions` and `NEW.state !=
      OLD.state`), inserts a row into `transition_violations` and reverts `tasks.state` AND
      `tasks.updated_at` back to `OLD.state`/`OLD.updated_at` via a corrective `UPDATE`.
- [ ] `AFTER INSERT ON tasks` trigger added to `SCHEMA_SQL`: on a newly inserted row whose
      `state` is not a legal initial state per the registry, inserts a row into
      `transition_violations` (with `attempted_from_state` representing the implicit
      "does not exist" origin) and **deletes** the illegally-inserted row (revised: not
      coerced to `INTAKE` — see guardrail table for the cross-trigger cascade bug that
      necessitated this and why it doesn't reverse the UPDATE trigger's coerce-not-delete
      decision).
- [ ] Cascade-fix test proves: an illegal `INSERT` results in the row being deleted, exactly
      one `transition_violations` row logged (not two), and `enforce_valid_transition` does
      not fire as a side effect of the INSERT trigger's corrective action.
- [ ] `valid_transitions` sync (`ensure_schema()`) uses parameterized `INSERT` statements
      (`?` placeholders), not string-formatted SQL.
- [ ] Manual empirical verification repeated against the real schema (not just the `/tmp`
      prototype) confirming: (a) an illegal raw `sqlite3` UPDATE reverts (state + updated_at)
      and is logged; (b) a legal transition via the existing adapter path is unaffected and
      unlogged; (c) **both** triggers survive a forced `_rebuild_schema_transactional()` pass
      (both explicitly dropped before the rename step and recreated after copy — see guardrail
      table for the second implementation-time bug this required fixing); (d) with `PRAGMA
      recursive_triggers = ON` explicitly set, the illegal write does not persist, but (revised
      from original wording) the violation goes unlogged and the caller receives an unhandled
      `sqlite3.OperationalError` — documented accepted residual risk, not a silent bypass.
- [ ] New test `test_valid_transitions_table_matches_registry()` (or equivalent), passing,
      asserting exact set-equality between the DB table and `TransitionRegistry.get_all_edges()`.
- [ ] New tests covering: illegal `UPDATE` transition is reverted + logged (state and
      updated_at both restored); illegal `INSERT` (new/reused task_id with an illegal initial
      state) is caught and logged; `DELETE` + re-`INSERT` bypass is caught by the INSERT-side
      trigger; legal transition via the existing adapter path is unaffected and unlogged;
      violation log row shape matches spec exactly; `recursive_triggers = ON` case (finding #2)
      produces no infinite loop or duplicate rows.
- [ ] Full existing control-plane test suite still green:
      `pytest plugins/agent-agentic-os/tests/ -k control_plane` exits 0.
- [ ] `python3 plugins/agent-scaffolders/scripts/audit.py --path plugins/agent-agentic-os` and
      `python3 plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/agent-agentic-os`
      both pass.
- [ ] ADR-007 and any control-plane security spec/doc reviewed before implementation; any
      conflicts surfaced to the user before proceeding, not silently resolved.
- [ ] Plugin reinstalled (`python3 plugins/plugin-manager/scripts/plugin_add.py
      plugins/agent-agentic-os -y`) so `.agents/` reflects the change.
