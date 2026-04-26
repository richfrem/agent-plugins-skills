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
| WS-A | Smoke | Agent smoke tests (4 user-facing agents) | agentic-os-setup, os-health-check, triple-loop-architect, triple-loop-orchestrator | Copilot CLI |
| WS-B | Smoke | Skill smoke tests — Setup & Environment group | os-init, os-environment-probe, os-guide | Copilot CLI |
| WS-C | Smoke | Skill smoke tests — Planning & Evolution group | os-architect (skill), os-evolution-planner, os-evolution-verifier, os-experiment-log | Copilot CLI |
| WS-D | Smoke | Skill smoke tests — Eval & Improvement group | os-eval-lab-setup, os-eval-runner, os-eval-backport, os-improvement-loop, os-skill-improvement, os-improvement-report | Copilot CLI |
| WS-E | Smoke | Skill smoke tests — Memory & Utilities group | os-memory-manager, os-clean-locks, todo-check, optimize-agent-instructions | Copilot CLI |
| WS-F | Integration | Full architect pipeline end-to-end | os-architect (agent), os-evolution-planner, os-evolution-verifier, os-experiment-log, improvement-intake-agent | Copilot CLI |
| WS-G | Integration | Setup + memory chain | agentic-os-setup, os-init, os-memory-manager, os-health-check | Copilot CLI |
| WS-H | Eval Lab | 10-iteration eval loop on todo-check | os-eval-lab-setup, os-eval-runner, os-eval-backport, todo-check | Copilot CLI |
| WS-I | Eval Lab | 10-iteration eval loop on os-clean-locks | os-eval-lab-setup, os-eval-runner, os-eval-backport, os-clean-locks | Copilot CLI |
| WS-J | Eval Lab | 10-iteration eval loop on optimize-agent-instructions | os-eval-lab-setup, os-eval-runner, os-eval-backport, optimize-agent-instructions | Copilot CLI |
| WS-K | Assessment | Value overlap: os-skill-improvement vs os-improvement-loop | os-skill-improvement, os-improvement-loop | Manual review |
| WS-L | Assessment | os-architect-tester 8-scenario run + EXP-16 crashed/paused distinction | os-architect-tester, improvement-intake-agent, os-evolution-verifier | Copilot CLI |
| WS-M | Report | os-improvement-report on all logged numeric results | os-improvement-report, experiment_log.py | Direct script |

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

**Validation:** `grep -c "Event Bus\|Lock\|Memory" output` ≥ 3 matches.
**Pass condition:** All 3 sections present, no ERROR lines in output.
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

**Test sequence:**
1. Append a test verifier entry with session ID `test-idempotency-01`
2. Append the same entry again — expect sys.exit(1) with WARNING
3. Run `query test-idempotency-01` — expect exactly 1 result
4. Run `summary` — count matches

**Validation:**
```bash
python3 scripts/experiment_log.py append ... --session-id test-idempotency-01
# second call should print WARNING and exit 1
python3 scripts/experiment_log.py query test-idempotency-01 | grep -c "###"  # expect 1
```
**Pass condition:** Duplicate blocked, query returns 1 result, summary count correct.
**Result type:** qualitative

---

### EXP-08 — os-eval-runner 10-Iteration Lab: todo-check (WS-H)

**Hypothesis:** Running 10 eval iterations on todo-check produces at least 1 KEEP and
no regression below baseline. The eval gate correctly rejects regressions.

**Setup:** os-eval-lab-setup creates sibling lab at `../agent-plugins-skills-lab-todo-check/`

**Metric:** eval score (0.0–1.0), KEEP/DISCARD count, delta from baseline.
**Single change per iteration:** One SKILL.md mutation proposed by Copilot free model.
**Baseline:** Run evaluate.py before first iteration; record score.

**Expected outcome:** delta ≥ 0.0 after 10 iterations (no regression); at least 1 KEEP.

**Validation:**
```bash
python3 scripts/experiment_log.py query todo-check  # numeric entry with delta
cat results.tsv  # 10 rows, each KEEP or DISCARD
```
**Pass condition:** 10 iterations complete, delta ≥ 0, experiment log numeric entry written.
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

**Hypothesis:** optimize-agent-instructions has room for improvement; 10 iterations
find at least 2 KEEPs.

Same structure as EXP-08 with target = optimize-agent-instructions.
**Expected:** ≥ 2 KEEPs in 10 iterations.
**Result type:** numeric

---

### EXP-11 — Full Architect Pipeline Integration (WS-F)

**Hypothesis:** Given input "I want to add environment-awareness to os-guide so it
references the environment profile", os-architect correctly classifies as Path B (Update),
calls os-evolution-planner which generates 3 options, planner writes a valid plan and
delegation prompt, verifier runs and passes, log records a qualitative entry.

**Skills/agents exercised:** os-architect (agent + skill), improvement-intake-agent (if
Category 3 is triggered), os-evolution-planner, os-evolution-verifier, os-experiment-log.

**Validation chain:**
1. Architect output contains intent classification + path selection
2. Plan file exists at tasks/todo/ with Approach Selected section
3. Verifier produces EVOLUTION_VERIFICATION block with at least PARTIAL verdict
4. experiment_log.py summary shows new planner + verifier entries

**Pass condition:** All 4 validation points pass.
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

**Criteria for "distinct value":**
- Different setup overhead? (os-improvement-loop requires lab setup; os-skill-improvement does not)
- Different output quality?
- Different use case (single session vs multi-session)?

**Decision:** If both produce identical outputs with the same setup, deprecate os-skill-improvement.
**Result type:** qualitative (assessment)

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
  python3 plugins/agent-agentic-os/scripts/experiment_log.py append \
    --source-type verifier \
    --report /dev/stdin \
    --session-id "2026-04-26-<WS>-guard-fail" \
    --target "<skill-or-agent>" \
    --triggered-by dispatch-guard <<'EOF'
## EVOLUTION_VERIFICATION
SESSION_COMPLETE: false
STATUS: crashed
VERDICT: FAIL
NOTES: Dispatch output missing or < 20 lines — silent crash or timeout
EOF
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
```

Stop after each phase, review experiment log, proceed if no critical failures.

---

## Coverage Matrix

| Component | EXP | Phase | Exercised by |
|-----------|-----|-------|-------------|
| agentic-os-setup (agent) | EXP-01, EXP-12 | Smoke, Integration | WS-A, WS-G |
| os-health-check (agent) | EXP-02, EXP-12 | Smoke, Integration | WS-A, WS-G |
| triple-loop-architect (agent) | WS-A smoke | Smoke | WS-A |
| triple-loop-orchestrator (agent) | WS-A smoke | Smoke | WS-A |
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
