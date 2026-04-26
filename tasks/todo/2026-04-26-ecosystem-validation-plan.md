# 0024 — Ecosystem Validation & Experiment Plan

## Context

Complete coverage test of the agent-agentic-os plugin — every skill and agent exercised
at least once, eval loops run to test the improvement lifecycle, and value assessments
on skills that may overlap. This plan doubles as the first real use of the experiment log
as a scientific record: each experiment is a hypothesis with a stated outcome, a
single-change constraint, and a measurable pass/fail criterion.

Execution model: os-architect dispatches each workstream via Copilot CLI to
claude-sonnet-4.6. Results logged to `context/experiment-log/` after each run.

**Pre-execution fixes applied (v2 — 2026-04-26):**
- `os-improvement-report` updated with Phase 0 to read `context/experiment-log/index.md`
  for `result_type: numeric` entries — EXP-13 (WS-M) no longer depends on legacy ledger
- `os-evolution-verifier` schema updated with `STATUS: complete | intentional_pause | crashed`
  field to disambiguate deliberate gates from silent crashes — resolves round5 Gemini gap
- EXP-16 added to WS-L: explicit crashed-vs-paused scenario for os-architect-tester
- Dispatch guard added to all delegation commands: hard FAIL on missing/empty output file

**Additional fixes applied (v3 — 2026-04-26, post multi-reviewer feedback):**
- Confirmed: EXP-07 idempotency guard is shipped — `_session_already_logged()` + `sys.exit(1)` present in `experiment_log.py` since round5 commit c268d081
- Bug fix: dispatch guard replaced `/dev/stdin` (unreliable as Path) with temp file `temp/crash_guard_<WS>_<ts>.md`
- EXP-01b added: triple-loop-architect + triple-loop-orchestrator now have a defined hypothesis and pass condition (were "WS-A smoke" with no EXP number)
- WS-D os-improvement-report smoke clarified: checks clean-exit on empty log, not chart generation
- EXP-10 pass condition lowered to ≥1 KEEP (same as EXP-08/09) — ≥2 was unjustified
- EXP-11 Category 3 fallback defined: alternate validation chain if architect routes to improvement-intake-agent
- Phase gate enforcement added: explicit `experiment_log.py query FAIL` check + human checkpoint between phases
- WS-K decision matrix added: 5-dimension comparison table replaces "if identical → deprecate"
- WS-N (Failure Injection) added: 6 adversarial experiments testing graceful degradation
- EXP-17 (Baseline Stability) added: run same eval 3× before Phase 3, verify variance ≤ 0.03
- EXP-08+ upgrade: holdout + adversarial eval split added; overfit detection rule added
- Stop conditions added: 3 consecutive FAILs in same WS triggers pause; critical path failures halt downstream
- "Unexpected behaviors" capture field added to each WS log entry

---

## Approach Selected

Option B — Phased Coverage: Phase 1 smoke-tests every component (fast, establishes
baseline), Phase 2 runs integration chains (architect → planner → verifier → log),
Phase 3 runs 3 short eval labs (10 iterations each), Phase 4 does value assessment
on potentially overlapping skills.

(Alternatives: Option A = parallel all-at-once, too noisy to attribute failures;
Option C = deep single-skill focus, misses the coverage goal.)

---

## Gaps Identified

- No existing baseline for 16 of 17 skills (only verifier has a logged run)
- No integration test covering the full architect → planner → verifier → log chain end-to-end
- os-skill-improvement and os-improvement-loop have overlapping descriptions — unclear if both are needed
- os-guide content accuracy unverified since plugin evolved in rounds 1-5
- agentic-os-setup not tested since template set was added
- os-improvement-report not tested against real numeric experiment log entries

---

## Workstreams

| WS | Phase | Scope | Skills/Agents Tested | Runs via |
|----|-------|-------|---------------------|---------|
| WS-A | Smoke | Agent smoke tests — 4 user-facing + EXP-01b for triple-loop agents | agentic-os-setup, os-health-check, triple-loop-architect, triple-loop-orchestrator | Copilot CLI |
| WS-B | Smoke | Skill smoke tests — Setup & Environment group | os-init, os-environment-probe, os-guide | Copilot CLI |
| WS-C | Smoke | Skill smoke tests — Planning & Evolution group | os-architect (skill), os-evolution-planner, os-evolution-verifier, os-experiment-log | Copilot CLI |
| WS-D | Smoke | Skill smoke tests — Eval & Improvement group (os-improvement-report: clean-exit only, no chart expected) | os-eval-lab-setup, os-eval-runner, os-eval-backport, os-improvement-loop, os-skill-improvement, os-improvement-report | Copilot CLI |
| WS-E | Smoke | Skill smoke tests — Memory & Utilities group | os-memory-manager, os-clean-locks, todo-check, optimize-agent-instructions | Copilot CLI |
| WS-F | Integration | Full architect pipeline end-to-end | os-architect (agent), os-evolution-planner, os-evolution-verifier, os-experiment-log, improvement-intake-agent | Copilot CLI |
| WS-G | Integration | Setup + memory chain | agentic-os-setup, os-init, os-memory-manager, os-health-check | Copilot CLI |
| WS-H | Eval Lab | 10-iteration eval loop on todo-check | os-eval-lab-setup, os-eval-runner, os-eval-backport, todo-check | Copilot CLI |
| WS-I | Eval Lab | 10-iteration eval loop on os-clean-locks | os-eval-lab-setup, os-eval-runner, os-eval-backport, os-clean-locks | Copilot CLI |
| WS-J | Eval Lab | 10-iteration eval loop on optimize-agent-instructions | os-eval-lab-setup, os-eval-runner, os-eval-backport, optimize-agent-instructions | Copilot CLI |
| WS-K | Assessment | Value overlap: os-skill-improvement vs os-improvement-loop | os-skill-improvement, os-improvement-loop | Manual review |
| WS-L | Assessment | os-architect-tester 8-scenario run + EXP-16 crashed/paused distinction | os-architect-tester, improvement-intake-agent, os-evolution-verifier | Copilot CLI |
| WS-M | Report | os-improvement-report on all logged numeric results | os-improvement-report, experiment_log.py | Direct script |
| WS-N | Failure Injection | Adversarial degradation tests — corrupted state, missing files, partial outputs | os-init, os-experiment-log, os-memory-manager, os-clean-locks, os-eval-runner | Copilot CLI |

---

## Experiment Specifications

### EXP-01 — agentic-os-setup Scaffold (WS-A)

**Hypothesis:** Running agentic-os-setup in a fresh temp directory produces all 12
template files and a wired hooks.json.

**Single change measured:** None (baseline establishment).

**Inputs:** Empty temp directory at `temp/validation/setup-test/`

**Expected outputs:**
- 12 template files present (MEMORY_MD.md, OS_STATE_JSON.json, etc.)
- hooks.json contains SessionStart, PostToolUse, Stop entries
- No interactive prompt left unanswered

**Validation:**
```bash
ls temp/validation/setup-test/ | wc -l  # expect >= 12
grep -c "SessionStart" temp/validation/setup-test/hooks.json  # expect >= 1
```
**Pass condition:** All 12 files present, hooks wired.
**Result type:** qualitative
**Logged as:** verifier source type (PASS/FAIL output)

---

### EXP-02 — os-health-check Output Coverage (WS-A)

**Hypothesis:** os-health-check surfaces event log status, lock directory status, and
memory state in a single structured report.

**Expected outputs:** Report containing sections: Event Bus, Locks, Memory State.

**Validation (semantic, not just presence):**
```bash
# Section presence
grep -c "Event Bus\|Lock\|Memory" output  # expect >= 3
# Cross-check event count against actual file
ACTUAL_EVENTS=$(wc -l < context/events.jsonl)
grep "events" output | grep -o "[0-9]+" | head -1  # should match ACTUAL_EVENTS ± 1
```
**Pass condition:** All 3 sections present; event count in report matches actual `events.jsonl` line count.
**Note:** Presence grep is necessary but not sufficient — count must match reality.
**Result type:** qualitative

---

### EXP-01b — triple-loop-architect + triple-loop-orchestrator Dry Run (WS-A)

**Hypothesis:** triple-loop-architect accepts a dry-run invocation for `todo-check` skill
and produces a readable lab setup plan without crashing. triple-loop-orchestrator accepts
a 1-iteration dry-run invocation and emits a LOG_PROGRESS entry.

**Single change measured:** None (baseline smoke test for both agents).

**Inputs:**
- triple-loop-architect: `"Set up a triple-loop eval lab for todo-check — dry run only, do not dispatch"`
- triple-loop-orchestrator: `"Run 1 iteration of the triple-loop on todo-check lab — dry run only"`

**Expected outputs:**
- triple-loop-architect: output ≥ 50 lines, contains "lab" and "todo-check", no ERROR
- triple-loop-orchestrator: output ≥ 30 lines, contains "LOG_PROGRESS" or "KEEP\|DISCARD" reference

**Validation:**
```bash
wc -l temp/validation/triple-loop-architect-smoke.md  # expect >= 50
grep -i "log_progress\|KEEP\|DISCARD" temp/validation/triple-loop-orchestrator-smoke.md
```
**Pass condition:** Both outputs meet line thresholds; no crash or empty output.
**Result type:** qualitative

---

### EXP-03 — os-environment-probe Verification (WS-B)

**Hypothesis:** Running os-environment-probe on this machine detects Claude Code as
active, attempts Copilot CLI probe, writes a valid environment.md with Delegation Strategy.

**Expected outputs:** `context/memory/environment.md` with populated table and
`## Delegation Strategy` section naming cheapest brainstorm model.

**Validation:**
```bash
grep -c "Cheapest brainstorm" context/memory/environment.md  # expect >= 1
grep "active" context/memory/environment.md  # expect at least 1 active row
```
**Pass condition:** environment.md created, Delegation Strategy populated.
**Result type:** qualitative

---

### EXP-04 — os-guide Accuracy Spot-Check (WS-B)

**Hypothesis:** os-guide answers 3 targeted questions accurately based on the current
plugin state (post-round5 changes included).

**Test questions:**
1. "What source types does the experiment log support?"
2. "What is the difference between os-skill-improvement and os-improvement-loop?"
3. "What does os-evolution-verifier check for?"

**Validation:** Answers cross-checked against SKILL.md source files.
**Pass condition:** All 3 answers match source content; no hallucinated capabilities.
**Result type:** qualitative

---

### EXP-05 — os-evolution-planner Multi-Option Generation (WS-C)

**Hypothesis:** Given target = os-guide skill and goal = "add Gotchas section and
SESSION_COMPLETE field awareness", os-evolution-planner generates 3 named approach
options with effort estimates before writing any plan file.

**Single change measured:** Phase 1 brainstorm present/absent.

**Expected outputs:**
- Console presents 3 named options before plan file is written
- Plan file contains `## Approach Selected` section
- Plan file written to `tasks/todo/`

**Validation:**
```bash
grep "Approach Selected" tasks/todo/*os-guide*.md  # expect 1 match
```
**Pass condition:** 3 options presented, Approach Selected in plan, plan file written.
**Result type:** qualitative

---

### EXP-06 — os-evolution-verifier 8-Scenario Re-run (WS-C)

**Hypothesis:** os-architect still passes all 8 scenario tests after the round5 changes
(multi-option planning, environment probe awareness added to embedded knowledge).

**Baseline:** 8/8 PASS from session 2026-04-25-round1.
**Expected:** 8/8 PASS. Any FAIL triggers root cause analysis before proceeding.

**Validation:** EVOLUTION_VERIFICATION blocks; `experiment_log.py summary` shows new entry.
**Pass condition:** 8/8 PASS.
**Result type:** qualitative
**Logged as:** verifier source type

---

### EXP-07 — os-experiment-log Idempotency & Query (WS-C)

**Hypothesis:** Calling `append` twice for the same session ID aborts with WARNING and
does not create a duplicate row; `query` returns correct results; `summary` counts match.

**Confirmed shipped:** `_session_already_logged()` + `sys.exit(1)` present in
`experiment_log.py` since round5 commit `c268d081`. This EXP verifies behavior, not presence.

**Test sequence:**
1. Append a test verifier entry with session ID `test-idempotency-01`
2. Append the same entry again — expect sys.exit(1) with WARNING
3. Run `query test-idempotency-01` — expect exactly 1 result
4. Run `summary` — count before and after must match

**Validation:**
```bash
python3 scripts/experiment_log.py append ... --session-id test-idempotency-01
EXIT_CODE=$?
# second call
python3 scripts/experiment_log.py append ... --session-id test-idempotency-01 2>&1 | grep "WARNING"
SECOND_EXIT=$?
[ $SECOND_EXIT -eq 0 ]  # grep found WARNING → guard fired
python3 scripts/experiment_log.py query test-idempotency-01 | grep -c "###"  # expect exactly 1
```
**Pass condition:** Second append exits 1 with WARNING; query returns exactly 1 result; summary unchanged.
**Result type:** qualitative

---

### EXP-08+ — os-eval-runner 10-Iteration Lab: todo-check (WS-H) [Upgraded]

**Hypothesis:** Improvements to todo-check increase accuracy on both the base eval set
AND an unseen holdout set, without overfitting. The eval gate correctly rejects regressions
and any iteration that improves base score while degrading holdout is force-discarded.

**Setup:** os-eval-lab-setup creates sibling lab at `../agent-plugins-skills-lab-todo-check/`

**Three eval datasets (create before running):**
- `evals/evals.json` — base set (existing, 10 cases) — drives KEEP/DISCARD gate
- `evals/evals_holdout.json` — holdout set (5 new cases, not seen during iterations) — generalization check
- `evals/evals_adversarial.json` — adversarial set (5 edge cases: ambiguous TODOs, conflicting tasks, noise injection) — robustness check

**Single change per iteration:** One SKILL.md mutation proposed by cheapest available model.

**Baseline (run 3× before first mutation — EXP-17 prerequisite):**
```bash
for i in 1 2 3; do python3 scripts/evaluate.py; done  # record variance
```
Variance > 0.03 → baseline is unstable → stop, investigate before running iterations.

**Metrics tracked per iteration:**
| Metric | Source | Notes |
|--------|--------|-------|
| `base_score` | evals.json | Drives KEEP/DISCARD |
| `holdout_score` | evals_holdout.json | Not used for gate; logged only |
| `adversarial_score` | evals_adversarial.json | Not used for gate; logged only |
| `overfit_flag` | base↑ && holdout↓ | Forces DISCARD even if base improves |

**Overfit detection rule:**
```
IF base_score > prev_base AND holdout_score < prev_holdout → OVERFIT → DISCARD
```

**Pass conditions:**
- 10 iterations complete
- `final_base_score ≥ baseline_base` (no regression)
- `final_holdout_score ≥ baseline_holdout` (no overfitting)
- At least 1 KEEP with positive holdout impact
- Variance across 3 baseline runs ≤ 0.03

**Validation:**
```bash
python3 scripts/experiment_log.py query todo-check  # numeric entry
cat results.tsv  # 10 rows; check OVERFIT column if present
```
**Result type:** numeric
**Logged as:** orchestrator source type

---

### EXP-09 — os-eval-runner 10-Iteration Lab: os-clean-locks (WS-I)

**Hypothesis:** os-clean-locks evals are stable; 10 iterations produce δ ≥ 0.

Same structure as EXP-08 with target = os-clean-locks.

**Expected outcome:** 10 rows in results.tsv, at least 1 KEEP, no score below baseline.
**Result type:** numeric

---

### EXP-10 — os-eval-runner 10-Iteration Lab: optimize-agent-instructions (WS-J)

**Hypothesis:** optimize-agent-instructions improves with 10 iterations; eval gate
functions correctly; no regression below baseline.

Same structure as EXP-08+ with target = optimize-agent-instructions.
**Pass condition:** ≥ 1 KEEP (same bar as EXP-08/09), delta ≥ 0, holdout ≥ baseline_holdout.
**Note (v3 fix):** Previous ≥ 2 KEEP requirement was unjustified — lowered to match other labs.
**Result type:** numeric

---

### EXP-11 — Full Architect Pipeline Integration (WS-F)

**Hypothesis:** Given input "I want to add environment-awareness to os-guide so it
references the environment profile", os-architect correctly classifies as Path B (Update),
calls os-evolution-planner which generates 3 options, planner writes a valid plan and
delegation prompt, verifier runs and passes, log records a qualitative entry.

**Skills/agents exercised:** os-architect (agent + skill), improvement-intake-agent (if
Category 3 is triggered), os-evolution-planner, os-evolution-verifier, os-experiment-log.

**Path B validation chain (primary):**
1. Architect output contains `PATH: B` and intent classification
2. Plan file at tasks/todo/ with `## Approach Selected` section
3. Verifier EVOLUTION_VERIFICATION block with VERDICT ≥ PARTIAL
4. `experiment_log.py summary` shows new planner + verifier entries

**Category 3 fallback chain (if architect routes to improvement-intake-agent instead):**
- NOT an automatic FAIL — Category 3 is a legitimate classification for this input
- Check: `improvement-intake-agent` produces `improvement/run-config.json`
- Check: HANDOFF_BLOCK contains `PATH: C` or `PATH: B` with `improvement-intake-agent` as next agent
- Substitute validation points 2-4 with run-config.json existence check

**Pass condition (Path B):** All 4 validation points pass.
**Pass condition (Category 3 route):** run-config.json written, HANDOFF_BLOCK valid. Not a FAIL.
**Result type:** qualitative

---

### EXP-12 — Setup + Memory Chain Integration (WS-G)

**Hypothesis:** agentic-os-setup in a temp dir → os-memory-manager on 5 injected facts →
os-health-check correctly reports memory state.

**Steps:**
1. Run agentic-os-setup in temp dir
2. Manually inject 5 facts into events.jsonl (3 unique, 2 duplicates)
3. Run os-memory-manager — expect 3 facts in memory.md, 2 deduplicated
4. Run os-health-check — expect memory state section shows correct count

**Validation:**
```bash
grep -c "^- " context/memory.md  # count promoted facts
```
**Pass condition:** 3 facts in memory.md (duplicates removed), health-check shows correct state.
**Result type:** qualitative

---

### EXP-13 — os-improvement-report on Numeric Results (WS-M)

**Hypothesis:** After EXP-08/09/10 complete (numeric entries in log), os-improvement-report
generates a chart showing KEEP/DISCARD counts and score delta by target skill.

**Prerequisite:** At least 3 numeric entries in experiment log.

**Expected:** Chart/report generated, numbers match `experiment_log.py summary` counts.

**Validation:** Report output compared against `experiment_log.py summary` manually.
**Pass condition:** Chart generated, numbers accurate.
**Result type:** qualitative (report validation)

---

### EXP-14 — os-architect-tester + Internal Agents (WS-L)

**Hypothesis:** After all changes in this session (multi-option planner, env probe,
README), os-architect still passes all 8 tester scenarios including the new
environment-probe-aware embedded knowledge.

**Agents exercised:** os-architect-tester (primary), improvement-intake-agent (invoked by
Category 3 scenario), os-evolution-verifier (invoked via tester pipeline).

**Baseline:** 8/8 PASS.
**Pass condition:** 8/8 PASS. Any FAIL triggers root cause before claiming done.
**Result type:** qualitative

---

### EXP-16 — Crashed vs Paused Distinction (WS-L)

**Hypothesis:** When os-architect receives a prompt that causes it to halt unexpectedly
before Phase 2 (simulated via a malformed or token-limit-triggering input), the verifier
correctly sets `STATUS: crashed` and `VERDICT: FAIL` — NOT `SESSION_COMPLETE: false` with
`VERDICT: PARTIAL`.

**Single change measured:** Presence/absence of the `STATUS` field in EVOLUTION_VERIFICATION.

**Test inputs:**
- Input A: A prompt that triggers a legitimate clarifying question (expected: `STATUS: intentional_pause`)
- Input B: A malformed prompt designed to produce < 50 lines of output with no HANDOFF_BLOCK
  and no clarifying question (expected: `STATUS: crashed`, `VERDICT: FAIL`)

**Validation:**
```bash
grep "STATUS:" temp/os-evolution-verifier/output_exp16a.md  # expect: intentional_pause
grep "STATUS:" temp/os-evolution-verifier/output_exp16b.md  # expect: crashed
grep "VERDICT:" temp/os-evolution-verifier/output_exp16b.md  # expect: FAIL
```

**Pass condition:** Input A → `STATUS: intentional_pause`, Input B → `STATUS: crashed` + `VERDICT: FAIL`.
Any output that reports `STATUS: crashed` as PARTIAL fails this test.
**Result type:** qualitative

---

### EXP-15 — Value Assessment: os-skill-improvement vs os-improvement-loop (WS-K)

**Hypothesis:** os-skill-improvement is a lighter-weight subset of os-improvement-loop
appropriate for single-session targeted work; both have distinct value. Alternative:
one is redundant and should be deprecated.

**Test:**
1. Run os-skill-improvement on os-clean-locks for 3 iterations
2. Run os-improvement-loop on the same target for 3 iterations
3. Compare: outputs, token cost, setup overhead, distinctness

**5-dimension decision matrix:**

| Dimension | os-skill-improvement | os-improvement-loop |
|-----------|---------------------|---------------------|
| Setup cost | Low — no lab, runs inline | High — requires sibling lab |
| Iteration depth | Single session, SME reviews each mutation | Multi-session, autonomous; evaluate.py gates all |
| Automation level | Semi-manual | Fully automated KEEP/DISCARD gate |
| Failure containment | Changes land in main repo immediately | Changes isolated to lab — zero contamination risk |
| Best use case | Quick targeted single-session tweak | Sustained improvement campaign over days/weeks |

**Decision criteria:**
- If outputs from the same target are *functionally identical* → deprecate os-skill-improvement
- If setup overhead is the *only* difference → merge into os-improvement-loop with a `--no-lab` flag
- If distinct use case is confirmed → document it and keep both, update README to clarify routing

**Result type:** qualitative (assessment)

---

### EXP-17 — Baseline Stability Check (prerequisite for WS-H/I/J)

**Hypothesis:** The eval score for each lab target is stable across 3 identical runs before
any mutations are applied. Variance > 0.03 indicates the eval itself is flawed (non-determinism,
prompt sensitivity) and the lab should not proceed.

**Run for each eval lab target before starting iterations:**
```bash
for TARGET in todo-check os-clean-locks optimize-agent-instructions; do
  for i in 1 2 3; do
    python3 scripts/evaluate.py --target "$TARGET" >> "temp/baseline_variance_$TARGET.txt"
  done
  # Check variance
  python3 -c "
import statistics, re
scores = [float(s) for s in re.findall(r'Score: ([0-9.]+)', open('temp/baseline_variance_$TARGET.txt').read())]
v = statistics.variance(scores) if len(scores) > 1 else 0
print(f'{TARGET}: scores={scores}, variance={v:.4f}, stable={v <= 0.03}')
"
done
```

**Pass condition:** Variance ≤ 0.03 for all 3 targets. If any target fails, halt that lab,
log the instability to experiment log, investigate eval design before running iterations.
**Result type:** qualitative (gate check, not an improvement run)

---

### WS-N — Failure Injection Experiments

Six adversarial tests verifying graceful degradation when components receive corrupted or
partial state. These test error detection and recovery messaging, not happy-path behavior.

---

#### N-01 — Corrupted events.jsonl

**Input:** Inject 3 malformed JSON lines into `context/events.jsonl` (invalid JSON, missing
required fields, truncated record).
**Expected:** os-health-check detects and reports the malformed lines; does not crash;
includes "malformed" or "corrupt" in output. os-memory-manager skips bad lines without
silent data loss.
**Validation:**
```bash
grep -i "malformed\|corrupt\|invalid\|error" temp/ws-n-01-output.md  # expect >= 1
wc -l temp/ws-n-01-output.md  # expect >= 30 (full report, not just stack trace)
```
**Pass condition:** Health-check reports issue, does not crash. Memory manager skips bad lines.

---

#### N-02 — Missing context/memory.md

**Input:** Rename `context/memory.md` to `context/memory.md.bak` before running
os-memory-manager and os-health-check.
**Expected:** Both tools report missing memory gracefully (error message, not crash);
os-memory-manager offers to create fresh memory.md rather than exiting with exception.
**Pass condition:** No unhandled exception; both tools describe the missing state in output.

---

#### N-03 — Conflicting stale lock files

**Input:** Create 3 stale lock files in `context/.locks/` (files with timestamps > 30 min old).
**Expected:** os-health-check flags stale locks; os-clean-locks removes them successfully;
post-clean health-check shows 0 locks.
```bash
touch -t $(date -v-1H +%Y%m%d%H%M) context/.locks/test-stale-{1,2,3}.lock
```
**Pass condition:** Stale locks detected and removed; no false-positive on active locks.

---

#### N-04 — Malformed improvement/run-config.json

**Input:** Write a `improvement/run-config.json` missing the required `target` field.
**Expected:** os-improvement-loop detects missing field, emits a clear validation error,
does not attempt to run with incomplete config.
**Validation:**
```bash
grep -i "missing\|required\|invalid config" temp/ws-n-04-output.md  # expect >= 1
```
**Pass condition:** Validation error surfaced; no partial run started.

---

#### N-05 — Truncated task plan file

**Input:** Write a `tasks/todo/test-truncated-plan.md` that starts correctly but is cut
off mid-section (no `## Validation` or `## Pass Conditions` section).
**Expected:** os-evolution-planner detects missing sections and reports a schema validation
error rather than dispatching on incomplete instructions.
**Pass condition:** "missing section" or similar error surfaced; no Copilot CLI dispatch fired.

---

#### N-06 — Partial evals.json (missing should_trigger field)

**Input:** Write an `evals/evals.json` with 5 cases where `should_trigger` is absent on
2 of them (legacy `expected_behavior` format instead).
**Expected:** os-eval-runner detects the schema mismatch, reports "0% accuracy warning" or
similar for the malformed cases, does not use them in KEEP/DISCARD gate.
**Validation:**
```bash
grep -i "schema\|missing.*should_trigger\|0%\|legacy" temp/ws-n-06-output.md  # expect >= 1
```
**Pass condition:** Malformed evals detected and skipped; gate uses only valid cases.

---

## Delegation Plan

Each workstream dispatched via:

```bash
# Heartbeat (free model — always first)
python3 plugins/copilot-cli/scripts/run_agent.py \
  /dev/null /dev/null temp/heartbeat_val.md \
  "HEARTBEAT CHECK: Respond HEARTBEAT_OK only."
grep -q "HEARTBEAT_OK" temp/heartbeat_val.md || { echo "HEARTBEAT FAIL — aborting"; exit 1; }

# Dispatch one WS at a time (premium)
python3 plugins/copilot-cli/scripts/run_agent.py \
  /dev/null \
  tasks/todo/copilot_prompt_<WS>.md \
  temp/copilot_output_<WS>.md \
  "Execute exactly as specified. Use Write tool for all file outputs." \
  claude-sonnet-4.6

# DISPATCH GUARD — hard abort on empty or missing output (do not pass to experiment log)
OUTPUT="temp/copilot_output_<WS>.md"
if [ ! -f "$OUTPUT" ] || [ "$(wc -l < "$OUTPUT")" -lt 20 ]; then
  echo "DISPATCH GUARD FAIL: $OUTPUT missing or < 20 lines — logging FAIL to experiment log"
  # Write crash report to temp file (NOT /dev/stdin — Path.read_text() cannot read stdin)
  CRASH_REPORT="temp/crash_guard_<WS>_$(date +%s).md"
  cat > "$CRASH_REPORT" <<'CRASHEOF'
## os-evolution-verifier Test Report
## EVOLUTION_VERIFICATION
SESSION_COMPLETE: false
STATUS: crashed
VERDICT: FAIL
NOTES: Dispatch output missing or < 20 lines — silent crash or timeout
CRASHEOF
  python3 plugins/agent-agentic-os/scripts/experiment_log.py append \
    --source-type verifier \
    --report "$CRASH_REPORT" \
    --session-id "2026-04-26-<WS>-guard-fail" \
    --target "<skill-or-agent>" \
    --triggered-by dispatch-guard
  exit 1
fi
```

After each WS passes the guard:
```bash
python3 plugins/agent-agentic-os/scripts/experiment_log.py append \
  --source-type <type> \
  --report temp/copilot_output_<WS>.md \
  --session-id "2026-04-26-<WS>" \
  --target "<skill-or-agent>" \
  --triggered-by os-architect
```

---

## Execution Order

Run in this sequence — each phase builds on the previous:

```
Phase 1 (Smoke):     WS-A → WS-B → WS-C → WS-D → WS-E   [all qualitative, fast]
Phase 2 (Integration): WS-F → WS-G                         [qualitative, medium]
Phase 3 (Eval Labs):  WS-H → WS-I → WS-J                  [numeric, ~10 iterations each]
Phase 4 (Assessment): WS-K → WS-L → WS-M                  [qualitative + report]
Phase 5 (Failure Injection): WS-N                           [adversarial, qualitative]
```

**Phase gate — run between each phase (human checkpoint required):**

```bash
# Query all FAILs accumulated so far
python3 plugins/agent-agentic-os/scripts/experiment_log.py query FAIL

# Count FAILs in the just-completed phase
FAIL_COUNT=$(python3 plugins/agent-agentic-os/scripts/experiment_log.py query FAIL | grep -c "###")
echo "Phase FAIL count: $FAIL_COUNT"

# Rule: any critical-path FAIL halts downstream WS; 3 consecutive FAILs in same WS triggers pause
# Critical path: WS-A, WS-C, WS-F. A FAIL in these halts the phase that depends on them.
# Non-critical: WS-B, WS-D, WS-E, WS-G. Log and continue.
```

Human checkpoint: review query output. Investigate root causes before proceeding. Record decision in `temp/phase-gate-notes.md`.

**Stop conditions:**
- 3 consecutive FAILs in the same WS → pause that WS, open a root-cause task before continuing
- Any FAIL in WS-A (agent smoke), WS-C (evolution planner/verifier), or WS-F (integration) → halt all downstream WS in that phase until resolved
- WS-H/I/J: if baseline variance > 0.03 (EXP-17) → halt that eval lab, investigate eval stability before iterating

---

## Coverage Matrix

| Component | EXP | Phase | Exercised by |
|-----------|-----|-------|-------------|
| agentic-os-setup (agent) | EXP-01, EXP-12 | Smoke, Integration | WS-A, WS-G |
| os-health-check (agent) | EXP-02, EXP-12 | Smoke, Integration | WS-A, WS-G |
| triple-loop-architect (agent) | EXP-01b | Smoke | WS-A |
| triple-loop-orchestrator (agent) | EXP-01b | Smoke | WS-A |
| improvement-intake-agent (internal) | EXP-11, EXP-14 | Integration, Validation | WS-F, WS-L |
| os-architect-tester (internal) | EXP-14 | Validation | WS-L |
| os-init (skill) | EXP-12 | Integration | WS-G |
| os-environment-probe (skill) | EXP-03 | Smoke | WS-B |
| os-guide (skill) | EXP-04, EXP-05 | Smoke, Evolution | WS-B, WS-C |
| os-architect (skill + agent) | EXP-11 | Integration | WS-F |
| os-evolution-planner (skill) | EXP-05, EXP-11 | Smoke, Integration | WS-C, WS-F |
| os-evolution-verifier (skill) | EXP-06, EXP-11, EXP-14 | Smoke, Integration, Validation | WS-C, WS-F, WS-L |
| os-experiment-log (skill) | EXP-07 | Smoke | WS-C |
| os-eval-lab-setup (skill) | EXP-08/09/10 | Eval Lab | WS-H, WS-I, WS-J |
| os-eval-runner (skill) | EXP-08/09/10 | Eval Lab | WS-H, WS-I, WS-J |
| os-eval-backport (skill) | EXP-08/09/10 | Eval Lab | WS-H, WS-I, WS-J |
| os-improvement-loop (skill) | EXP-15 | Assessment | WS-K |
| os-skill-improvement (skill) | EXP-15 | Assessment | WS-K |
| os-improvement-report (skill) | EXP-13 | Report | WS-M |
| os-memory-manager (skill) | EXP-12 | Integration | WS-G |
| os-clean-locks (skill) | EXP-09 | Eval Lab | WS-I |
| todo-check (skill) | EXP-08 | Eval Lab | WS-H |
| optimize-agent-instructions (skill) | EXP-10 | Eval Lab | WS-J |

| os-init (skill) | N-02 (memory missing) | Failure Injection | WS-N |
| os-experiment-log (skill) | N-01 (corrupt events) | Failure Injection | WS-N |
| os-memory-manager (skill) | N-01, N-02 | Failure Injection | WS-N |
| os-clean-locks (skill) | N-03 | Failure Injection | WS-N |
| os-eval-runner (skill) | N-06 | Failure Injection | WS-N |

**Coverage:** 17/17 skills ✓ — 7/7 agents (4 user-facing + 3 internal) ✓

---

## Status

- [ ] WS-A: Agent smoke tests (agentic-os-setup, os-health-check, triple-loop-architect, triple-loop-orchestrator)
- [ ] WS-B: Skill smoke tests — Setup & Environment (os-init, os-environment-probe, os-guide)
- [ ] WS-C: Skill smoke tests — Planning & Evolution (os-architect, os-evolution-planner, os-evolution-verifier, os-experiment-log)
- [ ] WS-D: Skill smoke tests — Eval & Improvement (os-eval-lab-setup, os-eval-runner, os-eval-backport, os-improvement-loop, os-skill-improvement, os-improvement-report)
- [ ] WS-E: Skill smoke tests — Memory & Utilities (os-memory-manager, os-clean-locks, todo-check, optimize-agent-instructions)
- [ ] WS-F: Full architect pipeline integration test
- [ ] WS-G: Setup + memory chain integration test
- [ ] WS-H: 10-iteration eval lab — todo-check
- [ ] WS-I: 10-iteration eval lab — os-clean-locks
- [ ] WS-J: 10-iteration eval lab — optimize-agent-instructions
- [ ] WS-K: Value assessment — os-skill-improvement vs os-improvement-loop
- [ ] WS-L: os-architect-tester 8-scenario run + EXP-16 crashed/paused distinction (internal agents: improvement-intake-agent, os-architect-tester, os-evolution-verifier)
- [ ] WS-M: os-improvement-report on all logged numeric results
- [ ] WS-N: Failure injection — 6 adversarial experiments (N-01 through N-06)
