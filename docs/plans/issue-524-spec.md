# TASK_SPEC — issue-524: ControlPlane God-Object Decomposition

**Task ID:** `issue-524` · **GitHub Issue:** [#524](https://github.com/richfrem/agent-plugins-skills/issues/524)
**Control-plane state at draft time:** `DRAFT_PLAN`
**Related issues:** [#519](https://github.com/richfrem/agent-plugins-skills/issues/519) (excluded, separate design pass), [#523](https://github.com/richfrem/agent-plugins-skills/issues/523) (assessed post-implementation only, not implemented here), [#529](https://github.com/richfrem/agent-plugins-skills/issues/529) (process/architecture finding from this task's own interview, carried into guardrails below, not implemented here)

---

## 1. The Job

`plugins/agent-agentic-os/scripts/agent_control.py` (1114 lines, single `ControlPlane` class) currently mixes 7 responsibilities:

1. Connection/pool management (`_get_connection`, `_discover_shared_db_path`)
2. Schema migration engine (`init_db`, `_schema_needs_rebuild`, `_rebuild_schema_transactional`, `_copy_common_columns`, `_merge_orphaned_tasks_old`, `_log_orphan_merge_conflicts`, `SCHEMA_SQL`, `SCHEMA_MIGRATIONS`)
3. State-machine validation (`transition`, `ALLOWED_TRANSITIONS`, `_read_current_state_for_update`)
4. Gate policy enforcement — **scattered across 4 mechanisms**: `GATE_REQUIREMENTS` registry + `_check_gate_requirement`/`_gate_any_of`/`_gate_receipt_exists`/`_gate_critic_review_pass_exists`, plus 3 hardcoded guards (`_check_prior_art_guard`, `_check_done_guard`, `_check_rolled_back_guard`), plus `update_worktree()`'s own independent `pushed_to_origin` barrier (lines 916-926)
5. Cryptographic receipts (`record_verification_receipt`, `_sha256_file`, `lock_verifiers`, `verify_sovereignty`)
6. Filesystem side-effects (`_log_orphan_merge_conflicts` writing to `references/map-debt.md`)
7. Model-catalog resolution (`resolve_recommended_model`, `_resolve_tool_catalog`, `_pick_tier_model`)

**Job:** Introduce a hexagonal ports/adapters decomposition that separates these 7 responsibilities into distinct, independently testable components, with all 4 gate-policy mechanisms unified into the single `GATE_REQUIREMENTS`-driven path — delivered as a sequence of small, independently-verified, behavior-preserving steps in one worktree, landing as one PR at the end.

**Target subsystem paths:**
- `plugins/agent-agentic-os/scripts/agent_control.py` (becomes a thin facade)
- New: `plugins/agent-agentic-os/scripts/control_plane/` (domain/ports/adapters/application layers — exact submodule layout is an implementation decision, not fixed here)
- `plugins/agent-agentic-os/tests/test_agent_control.py` (existing 880-line suite — must stay green throughout; new unit tests added alongside)
- `plugins/agent-agentic-os/scripts/init_agentic_os.py` and `plugins/agent-agentic-os/tests/test_pre_push_review_guard.py`, `test_multi_agent_bundle_gate.py`, `test_init_agentic_os_scaffolding.py`, `test_control_plane_worktree_sharing.py` (direct `ControlPlane` consumers — updated only if the facade's public surface changes, which this task does not intend)

---

## 2. The Why

Confirmed via direct source read (not just the issue's claim): the 3 `_check_*_guard` methods (lines 617-696) are imperative conditionals structurally identical in purpose to what `GATE_REQUIREMENTS` (lines 242-305) already declaratively encodes for other edges, but implemented as a separate, inconsistent mechanism. `update_worktree()`'s `pushed_to_origin` barrier (lines 916-926) is a fourth, independent gate location with its own ad-hoc state-list check. A maintainer adding a new gate rule has to know which of 4 places applies — the exact drift class that produced the FK-corruption bug (PR #521) and the DONE-guard/schema_version bugs from the round-1 review follow-up.

The class also depends directly on concretions (`sqlite3`, `subprocess`, `hashlib`, `time`, filesystem) with no ports/interfaces, so `test_agent_control.py` has to use real SQLite fixtures and monkeypatch private methods (`_read_current_state_for_update`) to simulate scenarios a clean seam would let run in-memory.

This is a maintainability refactor, not a functional bug fix — the pipeline logic itself is sound and already well-tested (`test_agent_control.py`, `test_graph_state_machine.py`, `test_control_plane_worktree_sharing.py`).

---

## 3. Semantic Guardrails & Operational Reasons

| Guardrail | Operational Reason |
|---|---|
| **Behavior-preserving, not a rewrite.** External CLI behavior and exit codes (see `_map_exception_to_exit_code`) must not change unless a later plan-review round explicitly identifies and justifies a necessary change. | Confirmed human decision (interview, Option B + facade). No functional bug exists to justify behavior changes; changing behavior here would conflate this maintainability refactor with unrelated risk. |
| **`ControlPlane` remains a public compatibility facade** — existing constructor signature, method names, and semantics stay callable exactly as today. | `init_agentic_os.py` and 4 test files are direct Python-level consumers (confirmed via repo-wide grep during interview), not just CLI users. The Python surface is part of the compatibility contract even though never formally declared "public." User explicitly rejected renaming these to "look architecturally clean" (Option 2 over Option 1). |
| **Incremental TDD steps, each independently green** — not a single big-bang commit replacing the whole file. | Explicit user instruction: "full scope does not mean one giant rewrite... a sequence of small, behavior-preserving TDD changes with clear intermediate verification points." Also required by this repo's `test-driven-development.md` Iron Law and `graph-planning-superpowers-policy.md` Phase 2 Red-Green-Refactor. |
| **Gate-policy unification is mandatory within this task's scope**, not deferred to "future work." | This is the issue's headline, most concrete finding (4 scattered mechanisms) — descoping it would leave the primary reported problem unfixed inside an issue that claims to fix it. |
| **All 7 responsibilities get separated behind ports/interfaces** (persistence, migration, domain/state-machine, gate policy, crypto/receipts, filesystem side-effects, model-catalog resolution). | Explicit user decision (Option B, full decomposition) — avoids repeatedly reopening issues for remaining symptoms of the same god-object structure. |
| **#519 (durable audit export) stays entirely out of scope.** | Confirmed orthogonal — different design pass, no code overlap identified. |
| **#523 (raw sqlite3 CLI bypass) is assessed, not implemented, after this task completes.** | Confirmed orthogonal — a DB-layer enforcement gap that unifying Python-layer gate policy does not close (no SQLite triggers/constraints are in scope here). Comment already posted to #523 confirming it stays open independently ([#529](https://github.com/richfrem/agent-plugins-skills/issues/529) intake comment thread references this). |
| **Single worktree, single PR at the end.** | Explicit user delivery decision. |
| **Plain-language framing for any further human-facing decision points in this task.** | Process finding recorded during this task's own interview (also filed as issue #529) — jargon-first questions ("hexagonal ports/adapters") required a translation round-trip before the human could decide. |
| **No implementation of the #529 finding itself** (state/behavior divergence detection, transition-authority separation) inside this task. | User explicitly deferred it: "include the finding in the draft plan or map-debt so it can be reviewed before we decide whether it belongs in #524" — carried forward to Section 6 (Open Items) below, not built. |

---

## 4. Definition of Done (DoD)

All of the following must pass with `exit 0` before this task can leave `WORKTREE_REVIEW`:

1. **Existing test suite green, unchanged assertions:** `python3 -m pytest plugins/agent-agentic-os/tests/test_agent_control.py plugins/agent-agentic-os/tests/test_control_plane_worktree_sharing.py plugins/agent-agentic-os/tests/test_graph_state_machine.py plugins/agent-agentic-os/tests/test_multi_agent_bundle_gate.py plugins/agent-agentic-os/tests/test_pre_push_review_guard.py plugins/agent-agentic-os/tests/test_init_agentic_os_scaffolding.py -v` — zero regressions, no test deleted or weakened to make this pass.
2. **Characterization matrix complete and green BEFORE any gate-policy code is touched** (see Section 5, Step 1). Every currently-permitted branch of the 4 scattered gate mechanisms must have an explicit, passing characterization test capturing today's exact behavior:
   - `_check_prior_art_guard`: EVOLUTION task without prior-art scan (blocked), EVOLUTION task with prior-art scan logged (allowed), GENERAL task (guard not applicable), non-`INTAKE→INTERVIEW` edge (guard not applicable).
   - `_check_done_guard`: missing `test_suite` receipt (blocked), passing receipt but no asymmetric-persistence log (blocked), passing receipt + persistence log but failing/missing `leak_check` (blocked), all three present (allowed), locked verifiers present and intact vs. tampered (sovereignty check branch).
   - `_check_rolled_back_guard`: no asymmetric-persistence entry (blocked), entry present (allowed).
   - `update_worktree()`'s push barrier: each of the three currently-permitted states individually — `WORKTREE_REVIEW` (allowed), `MULTI_AGENT_CODE_REVIEW` (allowed), `VERIFY_EXIT` (allowed) — plus the blocked case (any other state, e.g. `IN_WORKTREE`).

   This matrix is the regression oracle for Step 3 (gate-policy unification) — Step 3 is not permitted to start until every row above has a passing test tied to it.
3. **New unit tests added and green** for each extracted responsibility (domain state-machine testable without SQLite fixtures; gate policy testable without a live DB where feasible) — added, not replacing, existing coverage.
4. **Gate-policy unification verified structurally, across both mechanisms it must now cover:** a single code search confirms `_check_prior_art_guard`, `_check_done_guard`, `_check_rolled_back_guard`, and `update_worktree()`'s `pushed_to_origin` barrier no longer exist as separate ad-hoc mechanisms — all gate logic (both lifecycle `(from_state, to_state)` transitions AND the worktree-push operation guard) resolves through the one declarative policy-evaluation mechanism described in Section 5, Step 3.
5. **Dependency-direction invariant verified:** a static check (import-graph inspection or equivalent) confirms the domain/state-machine and policy modules contain no direct imports of `sqlite3`, `subprocess`, `hashlib`, `time`-based I/O, or filesystem/model-catalog-storage APIs — those only appear in adapter modules.
6. **CLI compatibility check:** every `agent_control.py <subcommand> --help` output and every exit code path (`_map_exception_to_exit_code`) is unchanged — verified by re-running the existing CLI-level tests plus a manual diff of `--help` output before/after.
7. **Python-consumer compatibility check:** `init_agentic_os.py` and all 4 dependent test files run unmodified (or, if the interview's facade decision requires it, modified only to the extent the plan-review round explicitly approves) — `python3 -m pytest plugins/agent-agentic-os/tests/test_init_agentic_os_scaffolding.py -v` green.
8. **Structural audits pass:**
   ```
   python3 plugins/agent-scaffolders/scripts/audit.py --path plugins/agent-agentic-os
   python3 plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/agent-agentic-os
   ```
9. **Symlink diagnostics clean:** `python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose` — zero broken/imposter entries (relevant only if new shared scripts are added under the plugin's hub `scripts/` tree).
10. **Map-debt / wiki update:** an entry recorded per `self-evolution-policy.md` Rule 3, documenting the new gate-policy invariant and the deferred #529 finding (Section 6).
11. **Plugin reinstalled:** `python3 plugins/plugin-manager/scripts/plugin_add.py plugins/agent-agentic-os -y` run after implementation, before PR, so `.agents/` reflects the change.

---

## 5. Delivery Plan (destination fixed, execution incremental)

One issue, one complete architectural destination, incremental TDD steps — not a single rewrite commit. Order revised per external plan review (round 1) to fix a real extraction-order dependency and to generalize the gate-policy destination — see notes after the sequence.

```
issue-524 (single worktree, single PR)
  1. Characterize existing behavior — build the explicit characterization matrix (DoD item 2)
     covering every branch of _check_prior_art_guard, _check_done_guard, _check_rolled_back_guard,
     and update_worktree()'s push barrier (including each of the three permitted push states —
     WORKTREE_REVIEW, MULTI_AGENT_CODE_REVIEW, VERIFY_EXIT — proven individually, plus the
     blocked case). This matrix must be green before Step 3 (gate-policy unification) starts;
     it is the regression oracle for that step, not a nice-to-have.
  2. Define ports/contracts — introduce interfaces for Persistence, Clock/Time, Filesystem,
     Crypto, ModelCatalog, and Policy (exact names/module layout: implementation judgment, not
     an interview decision). Dependency-direction invariant (DoD item 5) is fixed here: domain/
     state-machine and policy code depend only on these interfaces, never on sqlite3, subprocess,
     hashlib, time-based I/O, or concrete filesystem/model-catalog storage. Adapters depend on
     the ports; the application layer composes policy with ports. ControlPlane (Step 8) composes
     the application layer — it must not become a replacement god-service that everything still
     funnels through.
  3. Extract the filesystem seam FIRST, ahead of migration/persistence. Reordered per external
     review: _log_orphan_merge_conflicts() (part of the migration path) already writes to
     references/map-debt.md, so migration has a real, current dependency on a filesystem side
     effect. Extracting migration before the filesystem port exists would require repairing this
     dependency immediately afterward. Introduce the Filesystem port/adapter now so Step 5's
     migration extraction can depend on the port from the start, not on a follow-up patch.
  4. Centralize gate policy behind ONE declarative policy-evaluation mechanism — not two.
     Reordered/generalized per external review: update_worktree()'s pushed_to_origin barrier is
     an operation guard (is this specific worktree-state-write operation currently permitted?),
     not a lifecycle (from_state, to_state) transition, so it cannot be forced into the existing
     transition-keyed GATE_REQUIREMENTS dict without distorting that model. The unified mechanism
     must be able to evaluate both:
       (a) lifecycle transitions — today's GATE_REQUIREMENTS-keyed (from_state, to_state) checks,
           plus _check_prior_art_guard, _check_done_guard, _check_rolled_back_guard folded in as
           declarative entries in the same registry shape; and
       (b) controlled operations — today's update_worktree() push barrier, expressed as a
           declarative policy entry keyed on the operation (e.g. "write worktree_state=
           pushed_to_origin") and its own required-context check (task must be in one of
           WORKTREE_REVIEW / MULTI_AGENT_CODE_REVIEW / VERIFY_EXIT), evaluated through the same
           engine and the same PersistenceInvariantViolation error path as (a).
     One policy-evaluation entry point, two kinds of declarative rules it can evaluate — not a
     second independent gate engine. This step is verified directly against the Step 1
     characterization matrix and alone resolves the issue's headline finding.
  5. Extract persistence/migration — move connection management and schema migration behind the
     Persistence port/adapter (established after Step 3, so migration's existing filesystem
     dependency is already satisfied through a port, not a raw file write).
  6. Extract receipts/crypto — move SHA256/receipt-token logic behind the Crypto port/adapter.
  7. Extract model-catalog resolution — move resolve_recommended_model and helpers behind the
     ModelCatalog port/adapter.
  8. Thin the ControlPlane facade — remaining ControlPlane class composes the application layer
     (policy + ports) and delegates; public method signatures unchanged. Verify against DoD item
     5 (dependency-direction invariant) that ControlPlane itself is the only place allowed to
     wire concrete adapters to ports — it must not itself contain business logic moved out of
     the original class in disguise.
  9. Regression + structural verification — full DoD checklist (Section 4).
```

Each step ends with the full existing test suite green (plus the Step 1 characterization matrix, once it exists) before the next step starts — Red-Green-Refactor per step, not per file.

---

## 6. Open Items — Explicitly Deferred, Not In Scope Here

- **Issue #529 finding (state/behavior divergence + transition-authority separation):** noted for plan-review consideration; not implemented in this task. If the reviewers judge it belongs in this refactor's ports design (e.g., a port boundary that would make future enforcement easier), that is a plan-review recommendation to bring back to the human for a scope decision — not something to fold in unilaterally.
- **Issue #523 (raw sqlite3 CLI bypass):** to be assessed against the completed refactor once merged. If gate-policy unification happens to close it as a side effect (unlikely, per the interview's own analysis — it's a DB-layer gap, not a Python-layer one), comment on #523 with evidence rather than assuming closure.
- **Issue #519 (durable audit export):** entirely separate design pass, not touched.
