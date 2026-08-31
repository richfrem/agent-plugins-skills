# Map Debt Registry

This registry tracks technical debt, process friction, and workarounds.
Entries must be resolved, aged, or escalated. 
Do not delete resolved items; set `Status: RESOLVED` to maintain history.

---

## Tier 3 (Structural): Controller verifies and commits against the wrong directory

**Status: OPEN, Repeat: N/A (first occurrence, root cause)**
**Discovered:** 2026-08-31, live manual cycle `live-pass-1788153987` on `feature/evolution-memory-orchestration-hardening`, real repo (not the sandboxed e2e smoke test).

**Evidence:**
- `plugins/agent-agentic-os/scripts/evolution_state.py` initializes `state["worktree_path"] = None` at `init` (line ~260) and reads it in `cmd_verify` (line ~450: `if state.get("worktree_path"): exec_dir = wt`) to decide where the verifier subprocess runs. Grep of the entire file confirms `worktree_path` is written **nowhere** — no CLI subcommand, no code path, ever sets it after `git worktree add`.
- Live repro: created worktree `../worktree-live-pass-1788153987` via `git worktree add -b evolution/<cid> ... HEAD`, applied a real Kelvin-broadening fix to `evo-smoketest/SKILL.md` inside that worktree only, then ran `python3 evolution_state.py verify`. Output: `Controller executing verifier: [...] in /Users/richardfremmerlid/Projects/agent-plugins-skills` — the **main checkout**, not the worktree. `evaluate.py --skill ... --decision-only` graded the unmodified main-checkout file (still missing Kelvin) and still returned exit 0 / `STATUS: KEEP`, because `--decision-only` gates on "no regression vs. baseline score" (0.7933 == 0.7933), not on "did the targeted eval case flip." A verify call that never sees the mutation cannot prove the mutation works.
- Second half of the same root cause, read (not yet independently repro'd live): the PASS-path COMMIT step in `self-evolution/SKILL.md` Stage 3 and in `smoke_test.py` runs `git add .` / `git write-tree` / `git commit` with `cwd` at the main repo root, never inside the worktree — so even if verify passed correctly, the worktree's mutation still would not be staged or committed from there.

**Impact:** The worktree-isolation/verifier-sovereignty invariant (the core safety claim of the V1/V2 hardening: "the controller runs the declared verifier itself so results can't be self-reported") does not currently hold in a real cycle. It holds only in the existing test suite (unit tests, `test_graph_state_machine.py`, `smoke_test.py`) because those tests' sandbox setups happen not to expose the worktree/main-checkout split. No test in the current suite asserts that the verifier reads the file the mutation actually wrote.

**Root cause (both halves, not yet fixed — do not hot-patch mid-cycle, this needs a real design fix):**
1. `cmd_verify` must resolve `exec_dir`/`cwd` from the real worktree path used by `CREATE_WORKTREE`, not from a `state["worktree_path"]` field nothing ever populates. Either add a `--worktree-path` argument to the `transition --to CREATE_WORKTREE` (or a dedicated `set-worktree` subcommand) that persists it into state, or derive it deterministically from `cycle_id` at verify time.
2. The PASS-path COMMIT step (`self-evolution/SKILL.md` Stage 3, and mirrored in `smoke_test.py`) must operate with `cwd` inside the worktree, then merge/export that commit back to the branch it started from — not run `git add`/`git commit` against the main checkout directly.

**Missing regression test:** no test in the suite currently asserts "the file the verifier reads is the file the mutation wrote." See `test_verify_reads_worktree_mutation_not_main_checkout` added to `plugins/agent-agentic-os/tests/test_evolution_scripts.py` — it currently FAILS (red), demonstrating the defect precisely; it should not be made to pass by weakening the assertion, only by fixing `cmd_verify`.
