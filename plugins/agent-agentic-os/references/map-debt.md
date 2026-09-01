# Map Debt Registry

This registry tracks technical debt, process friction, and workarounds.
Entries must be resolved, aged, or escalated. 
Do not delete resolved items; set `Status: RESOLVED` to maintain history.

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

