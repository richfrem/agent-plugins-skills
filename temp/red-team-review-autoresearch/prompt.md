# Red Team Review v4: Karpathy 3-File Autoresearch — Post Round-3 Hardening

## Role & Mission
Act as a senior AI architecture and security auditor. Your mission is to evaluate whether this v4 implementation of the Karpathy autoresearch loop is robust, correctly enforced, and safe for autonomous overnight execution.

## Priority Matrix — Where to Focus

### RED (Critical — verify these first)

| # | Area | File | What to look for |
|---|---|---|---|
| R1 | **Keyword-overlap is a proxy metric, not real routing** | `eval_runner.py` | The scorer measures keyword overlap between prompts and SKILL.md frontmatter. It does NOT simulate actual agent routing. A skill can score 1.0 here and still be mis-triggered by a real agent. Is this limitation clearly documented in program.md and autoresearch-overview.md? Could the loop optimize toward a metric that diverges from actual routing quality? |
| R2 | **SHA256 lock check — correctness and coverage** | `evaluate.py` | Round 3 added `save_lock_hashes()` (at baseline) and `check_sha256_hashes()` (on every run). Verify: (a) hashes are saved AFTER the baseline row is written (not before); (b) the check runs before eval_runner.py is called (so a tampered scorer never runs); (c) `.lock.hashes` is placed in `<target-skill>/evals/` not in `scripts/`; (d) a committed-then-restored attack (modify → commit → restore → commit) still gets caught. What does it miss? |
| R3 | **TSV baseline column records the wrong value** | `evaluate.py`, `results.tsv` | In `write_row()`, the `baseline` column is written as `baseline_score` — the value loaded from the last BASELINE row. For the BASELINE row itself, `load_baseline()` returns `(0.0, 0.0)` before the row is written, so the BASELINE row's own `baseline` column records `0.0000` instead of the score it just computed. Verify whether this causes any downstream corruption in the `load_baseline()` read path (it reads `score`, not `baseline` column — but confirm). |
| R4 | **Phase 4 missing — now added, verify correctness** | `SKILL.md` | Round 3 added Phase 4 (Commit & Report) between Phase 3 (Revert/Reset) and Phase 5 (Self-Assessment). Verify: (a) the commit format matches what `evaluate.py` prints; (b) the threshold-stop logic in Phase 4 step 4 is reachable and correct; (c) Phase 4 doesn't re-run git checkout on DISCARD (evaluate.py already did it — double revert could corrupt if there are uncommitted changes to other files). |

### YELLOW (Important — verify after reds)

| # | Area | File | What to look for |
|---|---|---|---|
| Y1 | **Meta-circular risk** | `SKILL.md`, `program.md` | This skill is used to improve itself. The lock check and frontmatter guard reduce this but a sufficiently creative agent could modify non-SKILL.md files in the skill's own directory (e.g., evals/evals.json via a path-traversal in the --skill argument, or program.md). Is there a guard preventing `--skill` from pointing to a path that modifies its own scorer? |
| Y2 | **No iteration cost ceiling** | `program.md`, `SKILL.md` | NEVER STOP means the loop runs forever. Without a token budget or wall-clock ceiling, an overnight run can consume unbounded API spend. Is there any guidance in program.md for setting a default cap? Is `--max-iterations` documented anywhere? |
| Y3 | **git checkout scope on DISCARD** | `evaluate.py` | `git checkout -- SKILL.md` reverts only `SKILL.md`. If the agent made changes to other files in the same iteration (e.g., references/program.md or evals/evals.json), those are NOT reverted. Does the current lock check prevent this, or is there still an unguarded window? |
| Y4 | **evals.json test case quality** | `evals/evals.json` | The dual guard (score + F1) prevents keyword-stuffing, but adversarial negative cases that share partial vocabulary with eval-related prompts (e.g. "what score did we get?", "write a skill for session memory") may still produce false positives. Are negative cases hard enough? |
| Y5 | **Baseline established with score=0.0 path** | `evaluate.py` | `if args.baseline or baseline_score == 0.0: status = "BASELINE"` — if an early non-baseline run returns score=0.0 (e.g. malformed frontmatter → hard fail), it auto-promotes itself to BASELINE. This could set an artificially low baseline. Is this the intended behavior? |

## What Changed Since Last Review (v3 -> v4)

| Finding | Fix Applied |
|---|---|
| SHA256 lock gap (all 4 reviewers flagged) | `evaluate.py` now saves `.lock.hashes` at baseline time; `check_sha256_hashes()` runs before eval on every iteration — catches committed modifications to locked files |
| Phase 4 missing (SKILL.md jumped 3→5) | Phase 4 (Commit & Report) added: KEEP commits with standard format, DISCARD reports score delta, loop-ledger summary line, threshold-stop check |
| Phase 3 still told agent to run `git checkout` | Phase 3 updated to clarify `evaluate.py` already ran the revert automatically — agent only verifies, does not re-run |

## Two Known Risks Still Open

1. **Keyword-overlap is a proxy** — The metric is technically sound (keyword overlap with frontmatter only, F1 guard, hard-fail on malformed frontmatter) but it does not measure actual agent routing. A high score does not guarantee the skill is correctly triggered in production.
2. **Meta-circular risk** — This skill is used to improve itself. The SHA256 check and frontmatter guard reduce this but cannot fully prevent an agent from modifying non-SKILL.md files in clever ways.

## Core Questions for the Reviewer

1. **SHA256 correctness (R2):** Is the hash snapshot taken at the right moment, covering the right files? What committed-modification attack does it still miss?
2. **Proxy metric gap (R1):** Given keyword-overlap is only a proxy for real routing, how far can the loop's optimized SKILL.md diverge from actual agent behavior before the eval score becomes meaningless?
3. **TSV baseline column (R3):** Does the `baseline=0.0000` value in the BASELINE row's own `baseline` column cause any actual bug, or is it cosmetic? Trace the read path.
4. **Phase 4 correctness (R4):** Is the commit-and-report phase safe? Any scenarios where it double-reverts or races with evaluate.py's own revert?
5. **Remaining attack surface:** Given R2 (SHA256) and Y1 (meta-circular), what is the next most-exploitable path an overnight agent would take?

## Context Provided
The bundle contains:
- The research reference (`karpathy-autoresearch-3-file-eval.md`)
- The core evaluation skill (`skill-improvement-eval/`) including `SKILL.md`, `README.md`, `references/`, `evals/`
- The shared evaluation scripts (`scripts/evaluate.py`, `scripts/eval_runner.py`)
- The mapping and sequence diagrams (`references/diagrams/`)
- The candidate analysis skill (`eval-autoresearch-fit/`)

**Focus on R1-R4 first. High-signal findings only. Call out anything the fixes introduced as new attack surface.**
