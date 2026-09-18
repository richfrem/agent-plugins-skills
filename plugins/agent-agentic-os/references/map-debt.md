# Map Debt Registry

This registry tracks technical debt, process friction, and workarounds.
Entries must be resolved, aged, or escalated. 
Do not delete resolved items; set `Status: RESOLVED` to maintain history.

| 2026-09-18 | auth-ciba-poc-transition-mechanics | `IN_WORKTREE -> WORKTREE_REVIEW`'s `next_steps_hint` told the agent to run `record-verification-receipt` to satisfy `test_suite_or_deferred_to_review` before transitioning -- that command does not exist (the real CLI verb is `record-receipt`; `record-verification-receipt` is a garbled hybrid of that and the internal Python method name `record_verification_receipt()`). Discovered live: a real attempt to run `IN_WORKTREE -> WORKTREE_REVIEW` was denied by the check, and the only command the guidance offered to fix it does not exist. | Fixed live same session: corrected the hint to name the real `record-receipt --gate test_suite\|test_suite_deferred_to_review` command, and to explain the check must be satisfied by a receipt recorded BEFORE the transition call (see the sibling `interview_plan_route_complete` finding below for why -- same root architectural cause). | `plugins/agent-agentic-os/scripts/control_plane/transition_templates.yaml`, `in_worktree_to_worktree_review` template's `next_steps_hint`. | Tier 1 | 1 | RESOLVED |
| 2026-09-18 | auth-ciba-poc-transition-mechanics | `IN_WORKTREE -> WORKTREE_REVIEW`'s `confirm_test_suite_or_defer` human question is structurally unreachable in practice: the `test_suite_or_deferred_to_review` deterministic check runs at coordinator.py step 5 (before the human-questions loop at step 6 that would present this question), so a fresh attempt with no pre-existing `test_suite`/`test_suite_deferred_to_review` receipt is denied before the question is ever asked. Even if it were reached, `coordinator.py` has zero special-case handling converting a "Defer" answer into the `test_suite_deferred_to_review` receipt the check actually requires (confirmed via grep -- no reference to either string in coordinator.py). This is the same root-cause class as `DEBT-20260918-INTERVIEW-CHECK-DEFERRAL-STALE-NAME` (a deterministic check needing an answer collected in the same call, but not wired into the deferred-checks mechanism), but for a different check/edge. | Not fixed now -- the safe fix (adding `test_suite_or_deferred_to_review` to the deferral tuple, plus wiring `confirm_test_suite_or_defer`'s answer to auto-record the receipt) needs its own TDD cycle and full-suite re-verification, not a late-night live-pipeline-blocking patch. Worked around live by recording the receipt via `record-receipt` before calling `coordinate-transition`, per the corrected guidance text above. | Add `test_suite_or_deferred_to_review` to `coordinator.py`'s deferred-checks tuple; add handling so answering `confirm_test_suite_or_defer` with "Defer to later review/control step" auto-records the `test_suite_deferred_to_review` receipt before the deferred check re-evaluates, mirroring how `interview_plan_route_complete` was fixed. | Tier 2 | YES -- this is the second confirmed instance of "deterministic check runs too early to see this edge's own interactive answer"; recommend the CI cross-reference check proposed in the sibling entry be broadened to also flag any `deterministic_checks` entry whose gate/receipt name is only ever satisfied by that same edge's own `human_questions` answer. | OPEN |

| 2026-09-10 | WP-576 follow-up | Plan-to-diff completeness was previously inferred from green tests and could miss approved but unimplemented plan tasks. | Added the implementation ledger contract and fail-closed `implementation_completeness` gate before retrospective. | Verify every implementation-plan task has COMPLETE status, evidence, and existing artifacts before leaving VERIFY_EXIT. | Tier 1 | 1 | RESOLVED — full suite, simulator paths, audits, and symlink diagnosis pass |
| 2026-09-10 | autonomous implementation controller | Authorized work packages had no persistent bounded queue or watchdog-backed continuation owner after worktree entry. | Added JSON-backed queue/controller around the existing lifecycle-independent implementation loop, with heartbeat persistence, stale-runner blocking, and explicit exit-verification stop. | Add cross-process locking if multiple controller processes are ever supported. | Tier 1 | 1 | OPEN follow-up — single-writer controller only |
| 2026-09-17 | auth-ciba-poc-transition-mechanics | Live diagram review surfaced three edges converging on `VERIFY_EXIT` with weak or zero human authorization: `WORKTREE_REVIEW -> VERIFY_EXIT` and `MULTI_AGENT_CODE_REVIEW -> VERIFY_EXIT` both declared zero `human_questions` (reachable via `code_review_or_skip`'s own receipt check, which has no actor verification -- `record_review_skip`'s `actor` param is an unvalidated free-text string); `IN_WORKTREE -> VERIFY_EXIT` was worse still, zero `human_questions` AND zero `deterministic_checks`, a fully open backdoor skipping `WORKTREE_REVIEW` and code review entirely. | Fixed live same session. The two weak edges got real `human_questions` entries, trigger-enforced via the existing `required_transition_questions` mechanism. `IN_WORKTREE -> VERIFY_EXIT` was first mis-fixed the same way (a human question, "Gate 3d"), then corrected: removed entirely from `state_machine.py` and the YAML template, since a human answering a bypass question there would be approving skipping the one step (`WORKTREE_REVIEW`) whose purpose is to show them the diff first -- correctly attributed, not informed. | See `references/map-debt.md` DEBT-20260917-VERIFY-EXIT-GATE-HARDENING for full detail; `test_worktree_review_verify_exit_gate.py` has the regression coverage. | Tier 1 | 1 | RESOLVED |
| 2026-09-17 | auth-ciba-poc-transition-mechanics | `coordinator.py`'s `_resolve_artifact_path()` fallback (line ~731) and the `required_artifacts` patterns in `transition_templates.yaml`'s `DRAFT_PLAN -> PLAN_REVIEW`/`AWAITING_APPROVAL` templates are hardcoded to the flat `docs/plans/<task-id>-spec.md` / `docs/plans/<task-id>-implementation-plan.md` layout, with no awareness of the `docs/plans/work-tasks/<task-id>/` folder convention `write_plan_document.py`'s own destination validator already allows and `document-layout.md` documents. Writing plan documents only under `work-tasks/<task-id>/` (the documented-correct location) causes the `required_artifacts` check to report them missing and deny `DRAFT_PLAN -> PLAN_REVIEW`. Worked around live in `auth-ciba-poc-transition-mechanics` by writing duplicate flat-path copies; a real fix should make `_resolve_artifact_path()` check the `work-tasks/<task-id>/` location (or migrate `required_artifacts` patterns to it) so a second, always-stale flat copy isn't required going forward. | Not fixed now — found live while checking transition readiness; duplicate flat-path copies are a working, if inelegant, interim satisfaction of the current check. | Update `_resolve_artifact_path()`'s plan/spec fallback to try `docs/plans/work-tasks/<task-id>/<task-id>-*.md` before or instead of the flat path; update `required_artifacts` YAML patterns to match; remove the now-redundant flat-path copies once fixed. | Tier 1 | 1 | OPEN |
| 2026-09-17 | auth-ciba-poc-transition-mechanics (side finding, unrelated to task scope) | `agent_control.py`'s `_resolve_plan_outline_path()` (line ~496) falls back to `Path(repo_root or Path.cwd())` when a `ControlPlane` instance doesn't have `repo_root` explicitly set. Tests that construct `ControlPlane` without pointing `repo_root` at an isolated `tmp_path` silently write real `docs/plans/<task-id>-plan-outline.md` files into whatever directory `pytest` was invoked from. Reproduced live: running the full suite from `plugins/agent-agentic-os` (not the true repo root) wrote 4 stray outline files into `plugins/agent-agentic-os/docs/plans/` (`test-bundle-001`, `test-bundle-002`, `char-priorart-nonedge-001`, `p01-task`) from tests in `test_agent_control_gate_characterization.py`, `test_multi_agent_bundle_gate.py`, `test_p01_intake_persistence.py`. Removed as debris (confirmed test-only content) after discovery; not committed. | Not fixed now -- separate, pre-existing bug unrelated to this task's approved scope; found only because the full suite happened to be run from the wrong cwd. | Either fix the affected tests' fixtures to always set `repo_root` to `tmp_path`, or harden `_resolve_plan_outline_path()` itself to require an explicit `repo_root` (fail loud) rather than falling back to `Path.cwd()`. | Tier 1 | 1 | OPEN |
| 2026-09-17 | auth-ciba-poc-transition-mechanics | `agent_control.py` hardcodes the interview plan-outline artifact path at two call sites (lines ~383, ~442: `f"docs/plans/{task_id}-plan-outline.md"`), placing it directly under `docs/plans/` instead of `docs/plans/work-tasks/<task-id>/`, inconsistent with the task-artifact grouping convention documented in `docs/plans/document-layout.md`. Spec/implementation-plan documents written via `control_plane/wrappers/write_plan_document.py` correctly land inside the task's `work-tasks/<task-id>/` folder; the outline does not, so one task's artifacts are split across two locations. | Folded into `auth-ciba-poc-transition-mechanics`'s own implementation scope as ledger task T6 (2026-09-17), rather than filed as a fully separate task, since that task already touches `agent_control.py` for other reasons. | Update both hardcoded strings to `f"docs/plans/work-tasks/{task_id}/{task_id}-plan-outline.md"`. See `docs/plans/work-tasks/auth-ciba-poc-transition-mechanics/auth-ciba-poc-transition-mechanics-implementation-plan.md` task T6. | Tier 0 | 1 | RESOLVED — both call sites fixed 2026-09-18, `test_interview_plan_outline.py` updated and green |
| 2026-09-18 | auth-ciba-poc-transition-mechanics | `coordinator.py`'s deterministic-check deferral special-case still matched retired check-id names `interview_trivial_complete`/`interview_standard_complete` from before `policy.py` unified them behind `interview_plan_route_complete`. The check ran too early (before the interactive question-collection loop), against an empty `stage_answers` dict, denying every purely-interactive `INTERVIEW -> DRAFT_PLAN` transition with no pre-staged answers -- a real functional bug, not just test staleness, found only in the full-suite run via `test_draft_plan_interactive_outline_gap.py`. | Fixed live same session: added `interview_plan_route_complete` to the deferral tuple. | See `references/map-debt.md` DEBT-20260918-INTERVIEW-CHECK-DEFERRAL-STALE-NAME for full detail and the recommended CI cross-reference check to catch the next check-id rename before merge. | Tier 2 | 1 | RESOLVED — full suite 508 passed, 1 skipped, 0 failed |

---

## Tier 1 (Friction): Duplicated hardcoded domain literals across control-plane files

**Status: RESOLVED**
**Discovered:** 2026-09-14, external review (Gemini) of `control_plane/adapters.py` plus a
follow-up whole-plugin scan, during the `agentic-os-dedup-invariant-v2` work package.
- The mandatory `guidance_compliance_confirmation` question added earlier in this same
  work package broke 46 pre-existing tests because each had independently hardcoded its
  own literal answer sequence — the proximate trigger for a much broader scan.
- The broader scan found ~1,000 raw occurrences of task-lifecycle state-name literals
  (`"INTAKE"`, `"INTERVIEW"`, etc.) across 40 production and test files, plus a second
  wave of hardcoded domain values in `control_plane/adapters.py` specifically: decision
  types, actors, cost tiers, task types, worktree states, confirmation statuses, gate
  names, critic verdicts, delegation statuses, retrospective decision/completion-mode/
  follow-up statuses, and `ModelCatalogAdapter`'s tool-alias mapping and status
  denylist — each independently retyped at every call site instead of read from one
  authoritative source.
- Two live bugs were found and fixed as a direct consequence of this duplication: (1)
  three `adapters.py` methods embedded `'{DECISION_TYPE_APPROVAL}'` inside a **plain**
  (non-f) triple-quoted SQL string, so SQLite was literally comparing against the
  25-character text `{DECISION_TYPE_APPROVAL}` instead of `APPROVAL` — silently
  matching nothing; (2) `_rebuild_schema_transactional()` built and executed a ~40-line
  inline `CREATE TRIGGER` definition that was immediately dropped and replaced by the
  canonical one extracted from `SCHEMA_SQL` three lines later — dead code that had
  drifted from the canonical trigger it duplicated.
- **Fix applied:** created `control_plane/constants.py` as the single shared source for
  every cross-file domain constant (state names, decision types, actors, cost tiers,
  task types, worktree states — the exact 6-state vocabulary from
  `worktree-lifecycle-management.md` — gate names, critic verdicts, delegation
  statuses, retrospective/follow-up statuses, error codes, the guidance-compliance
  accepted answer, and test-only `REASON_*` free-text constants). `state_machine.py`
  imports the state names from it and owns only the derived adjacency DAG
  (`ALLOWED_TRANSITIONS`/`CANONICAL_STATES`); `adapters.py`'s `SCHEMA_SQL` (the
  fresh-create schema) now builds its `CHECK (... IN (...))` clauses from these
  constants via a new `sql_in_list()` helper. `SCHEMA_MIGRATIONS` (the immutable
  historical DDL record) was deliberately left untouched — rewriting a historical
  migration to reference current constants would misrepresent what was actually
  executed against real databases over time.
- Also fixed: runtime SQL queries that had been interpolating constants directly into
  the query text (`f"... WHERE actor = '{ACTOR_HUMAN}'"`) were converted to proper `?`
  bind parameters — f-string interpolation is now reserved for `SCHEMA_SQL`/trigger DDL
  at module-load time only, where SQLite triggers cannot accept bind parameters at all.
  Two repo-root-relative path resolutions using a fixed `Path(__file__).parent.parent...`
  chain were replaced with one `_resolve_repo_root()` helper (git-based, with a
  fixed-depth fallback only if git is unavailable).
- A follow-up 21-file audit checked the rest of `plugins/agent-agentic-os/scripts/` for
  the required `Key Input Dependencies`/`Key Functions` header sections
  (`coding-conventions.md`); 20 files were fixed, `evaluate.py` was correctly left
  untouched (its own header says "DO NOT MODIFY THIS FILE. It is the locked
  evaluator."). One further genuine duplication was found and fixed
  (`worktree_manager.py`'s `"native"`/`"portable"` strategy literals, duplicated into
  its test file) — a coincidental `"COMPLETE"` string shared across 4 unrelated domains
  (ledger status, session-event kind, install-classification state, simulation-result
  status) was deliberately NOT merged into one constant, since doing so would have been
  a false coupling between unrelated concepts (same mistake class caught earlier when a
  batch script wrongly imported `agent_control`'s `STATE_AWAITING_APPROVAL` into files
  that actually call the separately-governed `evolution_state.py`'s own `AWAITING_APPROVAL`).
- Canonical rule updated: `plugins/agent-agentic-os/rules/config-driven-constants-over-hardcoding.md`
  now documents the single-shared-file pattern, the SQL-parameterization rule, and the
  repo-root-resolution rule.
- **Regression test:** full suite green (475 passed) after all changes, including the
  two live bugs found and fixed above.

**Residual/deferred:** none — full-suite verified, retrospective recorded, task
transitioned to DONE.

---

## Tier 3 (Structural): Controller verifies and commits against the wrong directory

**Status: RESOLVED**
**Discovered:** 2026-08-31, live manual cycle `live-pass-1788153987` on `feature/evolution-memory-orchestration-hardening`, real repo (not the sandboxed e2e smoke test).
**Resolved:** 2026-08-31, commits `17813783` (worktree_path wiring + PASS-path commit inside worktree)
and `7ac0fe8a` (COMMIT-gate receipt recomputation, found live while re-verifying this exact fix — see
"Third occurrence" note below). Re-verified with a full real PASS cycle (`live-pass2-1788154733`,
merge commit `15cd7592`) and a full real ROLLBACK cycle (`live-rollback-1788154998`,
`knowledge/live-rollback-1788154998`) against this actual repo, not just the sandboxed suite.

**Evidence:**
- `plugins/agent-agentic-os/scripts/evolution_state.py` initializes `state["worktree_path"] = None` at `init` (line ~260) and reads it in `cmd_verify` (line ~450: `if state.get("worktree_path"): exec_dir = wt`) to decide where the verifier subprocess runs. Grep of the entire file confirms `worktree_path` is written **nowhere** — no CLI subcommand, no code path, ever sets it after `git worktree add`.
- Live repro: created worktree `../worktree-live-pass-1788153987` via `git worktree add -b evolution/<cid> ... HEAD`, applied a real Kelvin-broadening fix to `evo-smoketest/SKILL.md` inside that worktree only, then ran `python3 evolution_state.py verify`. Output: `Controller executing verifier: [...] in /Users/richardfremmerlid/Projects/agent-plugins-skills` — the **main checkout**, not the worktree. `evaluate.py --skill ... --decision-only` graded the unmodified main-checkout file (still missing Kelvin) and still returned exit 0 / `STATUS: KEEP`, because `--decision-only` gates on "no regression vs. baseline score" (0.7933 == 0.7933), not on "did the targeted eval case flip." A verify call that never sees the mutation cannot prove the mutation works.
- Second half of the same root cause, read (not yet independently repro'd live): the PASS-path COMMIT step in `self-evolution/SKILL.md` Stage 3 and in `smoke_test.py` runs `git add .` / `git write-tree` / `git commit` with `cwd` at the main repo root, never inside the worktree — so even if verify passed correctly, the worktree's mutation still would not be staged or committed from there.

**Impact:** The worktree-isolation/verifier-sovereignty invariant (the core safety claim of the V1/V2 hardening: "the controller runs the declared verifier itself so results can't be self-reported") does not currently hold in a real cycle. It holds only in the existing test suite (unit tests, `test_graph_state_machine.py`, `smoke_test.py`) because those tests' sandbox setups happen not to expose the worktree/main-checkout split. No test in the current suite asserts that the verifier reads the file the mutation actually wrote.

**Fix applied:**
1. `transition --to CREATE_WORKTREE` now accepts `--worktree-path`, persisted into state immediately (existence not required at transition time; caller may create the worktree right after). Deliberately NOT moved into the controller itself (considered, per the original directive's fork) — several existing tests and the real retry-loop path re-enter `CREATE_WORKTREE` for the same `cycle_id`, and auto-creating would collide with a branch that already exists on the second entry. The caller (SKILL.md prose / smoke_test.py / callers of the CLI) still owns worktree creation; it now tells the controller the truth about where it landed. `cmd_verify` hard-fails (does not silently fall back to main) if the declared `worktree_path` doesn't exist.
2. The PASS-path COMMIT step (`self-evolution/SKILL.md` Stage 3) now stages/writes-tree/commits inside the worktree (`git -C <worktree> add/write-tree/commit`) so the receipt binds the tree that actually contains the fix, then merges `evolution/<cid>` into the calling branch before cleanup.

**Third occurrence, found live while re-verifying fix #2 above, same commit `7ac0fe8a`:** the `COMMIT` transition guard's cryptographic re-verification called `verify_evolution_receipt.compute_receipt(repo_root, cycle_id)` with no `tree_sha`, so *it* also fell back to `git write-tree` against the main checkout — meaning a correctly-generated pre-commit token (bound to the worktree's tree) always mismatched on recomputation, and `COMMIT` was permanently unreachable for the very case it exists to allow. This was caught live: the gate correctly rejected the mismatched token rather than silently accepting it, but only because the recomputation was *also* wrong could the reject have been avoided by fixing this too. Fixed the same way: recompute against `state["worktree_path"]` when present.

**Regression tests (both currently green, both proven red beforehand):**
- `test_verify_reads_worktree_mutation_not_main_checkout` (`plugins/agent-agentic-os/tests/test_evolution_scripts.py`)
- `test_commit_receipt_recomputes_against_worktree_not_main` (same file) — manually confirmed red against the pre-fix code via `git stash`, reproducing the exact live mismatch error, before re-confirming green.

**Residual gap #1, RESOLVED same day (commit `50b8d758`):** `smoke_test.py` originally still passed 12/12 without ever passing `--worktree-path` or asserting on verified content, so it remained structurally blind to this entire class of defect. Hardened: `CREATE_WORKTREE` transitions (PASS + all 3 ROLLBACK attempts) now pass `--worktree-path`; Assertion 5 requires the controller's own stdout to name the worktree path; PASS-path commit sequence now stages/writes-tree/commits inside the worktree then merges, matching the real design; new Assertion 7b confirms the mutated content actually landed on main after merge. Verified the hardening is real (not decorative) by swapping in the pre-fix (`36500d2f`) and mid-fix (`17813783`) versions of `evolution_state.py` via `git show` and confirming the smoke test now hard-crashes against both, at the exact call each defect broke. 13/13 smoke test assertions green against the final fixed code.

**Residual gap #2, RESOLVED same day (commit `2fec57e2`):** `evo-smoketest`'s own documentation claimed the `kelvin_conversion` eval case was "the deliberate baseline gap that PASS closes" — but per-case `eval_runner.py --json` output showed that case already scored `correct: true` at baseline, because the query text ("Convert 300 Kelvin to Celsius") already contained the substring "celsius", which the keyword-matcher latches onto regardless of whether "Kelvin" appears in the skill description. The actually-failing case both before and after was the unrelated `celsius_shorthand` ("20c to f please"), which the 4+ char keyword matcher can never resolve regardless of description content. Fixed: `kelvin_conversion`'s query changed to "How warm is 300 Kelvin?" (zero keyword overlap with baseline description — verified f1 0.857 → 1.0, a genuine broken→fixed transition, not a coincidental pass); `celsius_shorthand` rephrased to a normal full-word true positive so it no longer pollutes the fixture with an unrelated permanent failure. `evo-smoketest/SKILL.md` and `evals.json` both updated with corrected narrative.

---

## Tier 0 (Friction): Missing domain query CLI primitives leading to ad-hoc inline SQL

**Status: RESOLVED**
**Discovered:** 2026-08-31, valuation triage in downstream investment toolkit.
**Resolved:** 2026-08-31.
- Updated `self-evolution-policy.md` across plugin source and downstream repositories with **Hard Gate 15: Single Source of Truth Verification First**.
- Mandated that analysis skills (`update-stock-analysis`) query canonical CLI utilities (`portfolio_io.py --ticker {TICKER}`) before assigning lifecycle status or actions, strictly forbidding inline Python/SQL.
- Added `--ticker`, `--pillars`, and `--json` CLI primitives to `portfolio_io.py` to eliminate inline query workarounds.
