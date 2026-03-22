---
name: concurrent-agent-loop
version: 0.5.0
description: >
  Pattern 5: Concurrent Event-Driven Multi-Agent Loop. Coordinates multiple Claude sessions
  as OS threads sharing a common event bus and memory address space. Every loop cycle is a
  full improvement cycle: execute, eval against benchmark (KEEP/DISCARD), emit friction events
  during work, close with post_run_metrics, agent self-assessment survey saved to retrospectives,
  memory persistence, and os-learning-loop trigger if friction threshold crossed.
  Four coordination topologies: turn-signal, fan-out, request-reply, dual-loop (Pattern D).
status: active
trigger: concurrent agents, shared event bus, multi-agent coordination, turn signal, fan-out,
  parallel agents shared state, event-driven agents, agent threads, kernel event bus,
  cross-session coordination, replace AGENT_COMMS, concurrent skill audit, claim task,
  inner agent, orchestrator peer agent, worker agent, continuous improvement loop,
  eval benchmark, self-assessment survey, post-run survey, friction events, metrics,
  os-learning-loop, skill improvement, memory persistence, retrospective
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Concurrent Agent Loop

> Pattern 5 in the agent-loops taxonomy. Treats concurrent Claude sessions as OS threads
> sharing a filesystem address space. The kernel event bus coordinates signals. Every cycle
> includes real work, eval against benchmark, friction tracking, agent self-assessment survey,
> post-run metrics, and memory persistence. The OS learns from every run.

## CRITICAL: What a Loop Is

The kernel (`kernel.py`) handles event routing, locks, and cursors. A loop is NOT a signal
exchange. A complete loop cycle requires all of the following, in order:

1. **Orientation** — ORCHESTRATOR reads `context/memory/improvement-ledger.md` (score trajectory, survey-to-action trace, north star trend), test registry, last session log, last surveys
2. **Test scenario documented** — ORCHESTRATOR writes scenario record to `context/memory/tests/` BEFORE emitting `task.assigned`
3. **Execution** — INNER_AGENT reads strategy packet, does real work
4. **Friction tracking** — agents emit `type: friction` events whenever they hit uncertainty, ambiguity, wrong CLI, or need human rescue
5. **Eval against benchmark** — `eval_runner.py` run, score compared to `results.tsv` baseline
6. **KEEP/DISCARD verdict** — PEER_AGENT runs `skill-improvement-eval` independently
7. **PEER_AGENT self-assessment survey** — answered in full, saved to `context/memory/retrospectives/`
8. **Apply improvement or correction packet** — ORCHESTRATOR acts on verdict
9. **ORCHESTRATOR self-assessment survey** — answered in full, saved to retrospectives
10. **Post-run metrics** — `post_run_metrics.py` run, metric event emitted to bus
11. **Loop report written** — before/after scores, metrics, survey summaries, artifacts updated
12. **Test registry updated** — scenario file closed with results, `registry.md` row updated, recommended next test written
13. **Improvement ledger updated** — Section 1 eval row + Section 2 survey-action rows appended; optional chart regenerated
14. **L2/L3 memory promotion** — `session-memory-manager` runs, facts promoted with dedup IDs
15. **os-learning-loop trigger check** — if 3+ friction events of same type OR north star regressing 2+ sessions, trigger Full Loop

Emitting `eval.result` with `score:0.9` is not a completed loop. The survey, the metrics, and
the memory write are the loop. The signal is just coordination glue.

---

## When to Use This Pattern

Use when:
- Two or more Claude sessions coordinating continuous improvement work
- N skills, workflows, or artifacts to eval and improve in parallel
- You want every cycle to produce measurable improvement and persistent memory

Do NOT use for:
- Single-session work (use `learning-loop` or `dual-loop` instead)
- Signal-only coordination with no eval, survey, or memory steps

---

## Agent Roles

| Role | Responsibility |
|------|---------------|
| ORCHESTRATOR | Orients, writes strategy packets, applies improvements on KEEP, owns git, runs metrics, closes memory |
| PEER_AGENT | Runs `skill-improvement-eval` independently, produces KEEP/DISCARD verdict, completes self-assessment survey |
| INNER_AGENT | Reads strategy packet, executes work, runs `eval_runner.py`, emits friction events during work, completes self-assessment survey |
| WORKER | Stateless subprocess, no bus, returns result via file/stdout, no survey required |

---

## Architecture

```
${CLAUDE_PROJECT_DIR}/context/
  events.jsonl                         <- shared event bus (append-only, atomic)
  agents.json                          <- permitted agent registry
  os-state.json                        <- shared counters and state
  agents/<id>.cursor                   <- per-agent read cursor (line-count)
  .locks/                              <- per-resource mutex directories
  memory/YYYY-MM-DD.md                 <- session log written at every loop close
  memory/retrospectives/               <- per-agent self-assessment surveys
    survey_[DATE]_[TIME]_[AGENT].md    <- one file per agent per cycle
  memory.md                            <- L3 long-term facts (promoted from session logs)
  memory/hook-errors.log               <- hook failures (read by post_run_metrics.py)
```

Companion skills (all required for a complete loop):
- `dual-loop` — strategy packet format, correction packet protocol, verification
- `skill-improvement-eval` — eval_runner.py, KEEP/DISCARD logic, results.tsv baseline
- `session-memory-manager` — session log template, L2/L3 promotion, deduplication
- `os-learning-loop` — root cause analysis, Full Loop improvement, auto-patching skills

---

## Friction Event Protocol

Agents MUST emit a `type: friction` event immediately whenever they encounter:
- Uncertainty about what to do next
- An ambiguous or underspecified instruction, rule, or workflow step
- A wrong CLI command or tool syntax
- Being redirected or corrected by a human
- A `<WRITE_FAILED>` or tool error requiring retry

```bash
python3 "$KERNEL_PY" emit_event \
  --agent INNER_AGENT --type friction --action encountered \
  --correlation-id "$CID" \
  --summary "step:eval-runner cause:wrong-flag-name"
```

These events are counted by `post_run_metrics.py` at close and drive the os-learning-loop
auto-trigger (3+ friction events of same type = Full Loop improvement automatically).

---

## Bash Polling Pattern

```bash
poll_for_event() {
  local AGENT=$1 ACTION=$2 CID=$3
  for i in $(seq 1 30); do
    EVENTS=$(python3 "$KERNEL_PY" read_events --agent "$AGENT")
    MATCH=$(echo "$EVENTS" | python3 -c "
import sys, json
evs = json.load(sys.stdin)
hits = [e for e in evs if e.get('action') == '$ACTION'
        and (not '$CID' or e.get('correlation_id') == '$CID')]
print(json.dumps(hits[0]) if hits else '')
")
    if [ -n "$MATCH" ]; then echo "$MATCH"; return 0; fi
    sleep 2
  done
  echo ""; return 1
}
```

---

## Stage 1: Setup and Orientation

**Goal**: Every agent orients before any work begins. No agent starts cold.

1. **ORCHESTRATOR reads (in order):**
   - `context/memory/improvement-ledger.md` — eval score trajectory per skill, survey-to-action trace, north star trend
   - `context/memory/tests/registry.md` — what has been tested, what was recommended next
   - `context/memory.md` (L3 long-term facts)
   - Last session log: `context/memory/YYYY-MM-DD.md`
   - Last retrospective surveys: `context/memory/retrospectives/` (most recent per agent)
   - `context/events.jsonl` last 100 lines for friction patterns from prior cycle
2. **ORCHESTRATOR answers before writing any strategy packet:**
   - What does the improvement ledger show for this target's score trajectory? (flat = try a different approach; declining = revert last change)
   - Is the north star completion rate regressing 2+ sessions in a row? (if yes, trigger os-learning-loop before this cycle)
   - What does the test registry say was the recommended next test?
   - Has this hypothesis already been confirmed or falsified? (check registry — do not re-run)
   - Which survey friction items from prior cycles have not been acted on yet? (Section 2 gaps)
3. Confirm `agents.json` lists all participating agents.
4. Each agent emits `agent_start`:
   ```bash
   python3 "$KERNEL_PY" emit_event \
     --agent ORCHESTRATOR --type agent_start --action registered \
     --summary "ORCHESTRATOR online — registry read, designing test from prior results"
   ```
5. **ORCHESTRATOR documents the test scenario** in `context/memory/tests/[CYCLE_ID]_[TARGET_SLUG].md`
   per `references/test-registry-protocol.md` — hypothesis, acceptance criteria, failure criteria,
   prior results consulted, known weaknesses — BEFORE emitting `loop.start`.
6. Add row to `context/memory/tests/registry.md` with status IN PROGRESS.
7. ORCHESTRATOR emits `loop.start`:
   ```bash
   CYCLE_ID="cycle-$(date +%Y%m%d-%H%M%S)"
   python3 "$KERNEL_PY" emit_event \
     --agent ORCHESTRATOR --type intent --action loop.start \
     --correlation-id "$CYCLE_ID" \
     --summary "target:[TARGET_SLUG] hypothesis:[one-line] scenario:tests/${CYCLE_ID}_[TARGET_SLUG].md"
   ```
8. ORCHESTRATOR writes strategy packet informed by the test scenario, prior survey
   recommendations, and friction patterns from the last cycle.

---

## Stage 2: Coordinate

### Pattern A: Turn Signal (Sequential Handoff)

```bash
# ORCHESTRATOR: apply fix, signal PEER_AGENT to eval
python3 "$KERNEL_PY" emit_event \
  --agent ORCHESTRATOR --type signal --action signal.wakeup \
  --to PEER_AGENT --correlation-id "$CID" \
  --summary "target:skills/skill-A/SKILL.md change:updated-triggers"

# PEER_AGENT: poll, run full eval cycle (Stage 3), emit verdict
RESULT=$(poll_for_event ORCHESTRATOR eval.result "$CID")
# ORCHESTRATOR: act on verdict (Stage 3 and Stage 4)
```

### Pattern B: Fan-Out (N Skills in Parallel)

```bash
for partition in 1 2 3; do
  (
    CLAIM=$(python3 "$KERNEL_PY" claim_task \
      --task-id "$CYCLE_ID" --partition $partition --agent INNER_AGENT --ttl 600)
    if [ "$CLAIM" = "claimed" ]; then
      # INNER_AGENT: full execution obligation (Stage 3)
      python3 "$KERNEL_PY" emit_event \
        --agent INNER_AGENT --type result --action task.complete \
        --status success --to ORCHESTRATOR --correlation-id "$CYCLE_ID" \
        --summary "partition:$partition score:0.88 verdict:KEEP survey:saved"
      python3 "$KERNEL_PY" release_lock "task_${CYCLE_ID}_p${partition}"
    fi
  ) &
done
wait
python3 "$KERNEL_PY" read_events --agent ORCHESTRATOR
```

### Pattern C: Request-Reply (Delegated Subtask)

```bash
CID=$(python3 -c "import uuid; print(uuid.uuid4().hex[:8])")
python3 "$KERNEL_PY" emit_event \
  --agent ORCHESTRATOR --type intent --action task.assigned \
  --to INNER_AGENT --correlation-id "$CID" \
  --summary "packet:handoffs/packet-${CID}.md target:skill-B"

# INNER_AGENT: poll, execute, eval, survey, reply (Stage 3)
REPLY=$(poll_for_event ORCHESTRATOR task.complete "$CID")
```

### Pattern D: Dual-Loop as Event-Native (Primary Improvement Pattern)

**Mandatory event chain:**
```
loop.start -> task.assigned -> task.complete -> eval.result -> orchestrator.decision -> loop.close
```

> **MANDATORY GATE: ORCHESTRATOR must receive `eval.result` with KEEP/DISCARD verdict from
> PEER_AGENT before applying any improvement or emitting `orchestrator.decision`. The
> eval.result event carries the verdict AND the PEER_AGENT self-assessment reference.
> Merging on `task.complete` alone is a protocol violation.**

```bash
# ORCHESTRATOR assigns task
python3 "$KERNEL_PY" emit_event \
  --agent ORCHESTRATOR --type intent --action task.assigned \
  --to INNER_AGENT --correlation-id "$CID" \
  --summary "packet:handoffs/packet-${CID}.md target:skills/skill-A/SKILL.md"

# Wait for task.complete
TC=$(poll_for_event ORCHESTRATOR task.complete "$CID")

# Signal PEER_AGENT to eval
python3 "$KERNEL_PY" emit_event \
  --agent ORCHESTRATOR --type signal --action signal.wakeup \
  --to PEER_AGENT --correlation-id "$CID" \
  --summary "eval-target:skills/skill-A/SKILL.md output:handoffs/out-${CID}.md"

# Wait for eval.result — MANDATORY before any decision
ER=$(poll_for_event ORCHESTRATOR eval.result "$CID")

# Emit decision
python3 "$KERNEL_PY" emit_event \
  --agent ORCHESTRATOR --type result --action orchestrator.decision \
  --status success --correlation-id "$CID" \
  --summary "verdict:KEEP improvements-applied:yes"
```

---

## Stage 3: Mandatory Loop Content (Every Agent, Every Cycle)

### INNER_AGENT Execution Obligation

Every time INNER_AGENT receives `task.assigned`, it MUST:

1. **Read the strategy packet** at the path in the event summary.
2. **Execute the assigned work** — edit target skill, workflow doc, or artifact.
3. **Emit friction events immediately** when hitting uncertainty, wrong syntax, or needing help.
4. **Run eval_runner.py:**
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/skill-improvement-eval/scripts/eval_runner.py" \
     --skill path/to/target/SKILL.md
   ```
5. If DISCARD: revert edit, note failure in output file, emit `task.complete --status fail`.
6. Write output to `handoffs/out-${CID}.md`.
7. **Complete the Post-Run Self-Assessment Survey** (see Stage 4.2).
8. Emit `task.complete` including score, output path, and survey path in summary.

### PEER_AGENT Eval Obligation

Every time PEER_AGENT receives `signal.wakeup` for eval, it MUST:

1. **Read the INNER_AGENT output file** at the path in the wakeup summary.
2. **Run `skill-improvement-eval`** independently — not read the score from the event.
3. Compare score to baseline in `results.tsv`. DISCARD if same or lower.
4. **Complete the Post-Run Self-Assessment Survey** (see Stage 4.2).
5. Emit `eval.result` with KEEP/DISCARD verdict, score delta, and survey path:
   ```bash
   python3 "$KERNEL_PY" emit_event \
     --agent PEER_AGENT --type result --action eval.result \
     --status success --to ORCHESTRATOR --correlation-id "$CID" \
     --summary "verdict:KEEP score-before:0.82 score-after:0.89 gaps:adversarial survey:retrospectives/survey_DATE_PEER_AGENT.md"
   ```

### ORCHESTRATOR Improvement Obligation

On **KEEP** verdict:
1. Apply the approved changes to the canonical skill or workflow doc.
2. Emit `orchestrator.decision`.
3. Update task tracking to Done.

On **DISCARD** verdict:
1. Write a correction packet to `handoffs/correction-${CID}.md` using severity schema:
   - CRITICAL: feature missing or tests fail
   - MODERATE: works but violates architecture or standards
   - MINOR: works, style issues only
2. Re-signal INNER_AGENT with correction packet for next sub-cycle.
3. Do NOT emit `orchestrator.decision` until KEEP is received.

---

## Stage 4: Mandatory Loop Close (Every Cycle — No Exceptions)

### 4.1 Emit loop.close

```bash
python3 "$KERNEL_PY" emit_event \
  --agent ORCHESTRATOR --type result --action loop.close \
  --status success --correlation-id "$CYCLE_ID" \
  --summary "improvements-applied:N friction-events:N"
```

### 4.2 Agent Self-Assessment Survey (Each Agent)

Every agent that performed work this cycle MUST complete the Post-Run Self-Assessment Survey
(`references/post_run_survey.md`). Answer every section — do not skip.

Save completed survey to:
```
context/memory/retrospectives/survey_[YYYYMMDD]_[HHMM]_[AGENT].md
```

Survey sections (all mandatory):

**Run Metadata**: date, task type, task complexity, skill under test

**Completion Outcome**:
- Did you complete the full intended workflow end to end? (Yes/No)
- Did the run require major human rescue? (Yes/No)

**Count-Based Signals (Karpathy Parity)**:
- How many times did you not know what to do next?
- How many times did you miss or skip a required step?
- How many times did you use the wrong CLI syntax?
- How many times were you redirected by a human?
- Total Friction Events

**Qualitative Friction**:
1. At what point were you most uncertain about what to do next?
2. Which instruction, rule, or workflow step felt ambiguous or underspecified?
3. Which command, tool, or template was most confusing in practice?
4. What was the single biggest source of friction in this run?
5. Which failure felt avoidable with a better prompt, skill, or rule?
6. What is the smallest workflow change that would have improved this run the most?

**Improvement Recommendation**:
- What one change should be tested before the next run?
- What evidence from this run supports that change?
- Target (Skill/Prompt/Script/Rule)?

After saving, emit survey_completed event:
```bash
python3 "$KERNEL_PY" emit_event \
  --agent PEER_AGENT --type learning --action survey_completed \
  --summary "retrospectives/survey_${DATE}_${TIME}_PEER_AGENT.md"
```

### 4.3 Run Post-Run Metrics

```bash
python3 "${CLAUDE_PROJECT_DIR}/context/kernel.py" emit_event \
  --agent post_run_hook --type intent --action session_summary

python3 "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/post_run_metrics.py"
```

This emits a `type: metric` event with:
- `human_interventions` — count of human rescues this cycle
- `workflow_uncertainty` — count of uncertainty friction events
- `missed_steps` — count of skipped required steps
- `cli_errors` — count of wrong CLI syntax errors
- `friction_events_total` — total friction events
- `hook_errors` — count from `context/memory/hook-errors.log`

### 4.4 Write Session Log

ORCHESTRATOR writes `context/memory/YYYY-MM-DD.md`:

```markdown
# Session Log: YYYY-MM-DD (Cycle: CYCLE_ID)

## Summary
[What was improved, which skills/workflows were modified]

## Eval Results
- Target: [skill or artifact]
- Score before: [baseline from results.tsv]
- Score after: [new score]
- Verdict: KEEP / DISCARD
- Gaps remaining: [from PEER_AGENT survey]

## Metrics (from post_run_metrics.py)
- Human interventions: N
- Friction events: N
- CLI errors: N
- Hook errors: N

## Agent Surveys
- INNER_AGENT: retrospectives/survey_DATE_TIME_INNER_AGENT.md
- PEER_AGENT: retrospectives/survey_DATE_TIME_PEER_AGENT.md
- Top recommendation: [single most impactful change from surveys]

## Skills / Workflows Updated
- [skill name]: [what changed and why]

## Open Items
- [ ] [Gaps flagged CRITICAL or MODERATE in surveys for next cycle]
```

### 4.5 Loop Report (Every Cycle — Published Before Memory Close)

ORCHESTRATOR writes a Loop Report before running `session-memory-manager`. This is the
cycle's official record. Save to `context/memory/loop-reports/report_[CYCLE_ID].md`:

```markdown
# Loop Report: [CYCLE_ID] — [YYYY-MM-DD HH:MM]

## Agent Summaries
### ORCHESTRATOR
[2-3 sentence summary: what was assigned, what decision was made, what was applied]

### INNER_AGENT
[2-3 sentence summary: what was executed, what score was produced, what friction was hit]

### PEER_AGENT
[2-3 sentence summary: eval run, verdict, gaps identified, self-assessment headline]

## Baseline vs Result
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Eval score | [results.tsv baseline] | [new score] | [+/-] |
| Friction events | [prior cycle count] | [this cycle count] | [+/-] |
| Human interventions | [prior] | [this cycle] | [+/-] |

## Survey Response Summary
- INNER_AGENT biggest friction: [one line from survey qualitative section]
- PEER_AGENT biggest friction: [one line from survey qualitative section]
- ORCHESTRATOR biggest friction: [one line from survey qualitative section]
- Top improvement recommendation: [the single most impactful change cited across surveys]

## Artifacts Updated This Cycle
- [ ] Skill updated: [path] — [what changed]
- [ ] Script updated: [path] — [what changed]
- [ ] Hook updated: [path] — [what changed]
- [ ] Memory updated: context/memory/YYYY-MM-DD.md
- [ ] L3 promoted: [N facts to context/memory.md]
- [ ] Survey saved: retrospectives/survey_[DATE]_[AGENT].md (each agent)

## Status
- [ ] Results saved to memory: YES / NO
- [ ] os-learning-loop triggered: YES (cause: [friction pattern]) / NO
```

Emit loop report written event:
```bash
python3 "$KERNEL_PY" emit_event \
  --agent ORCHESTRATOR --type result --action loop.report \
  --correlation-id "$CYCLE_ID" \
  --summary "report:loop-reports/report_${CYCLE_ID}.md"
```

**The loop report is always written to disk.** After writing, ask the user:
> "Loop report saved to `context/memory/loop-reports/report_[CYCLE_ID].md`. Would you like me to surface the summary now?"

Only display the report content if the user says yes. Never display it automatically.

### 4.6 Test Registry Update (MANDATORY — Every Cycle)

After the loop report is written, update the test scenario record per
`references/test-registry-protocol.md`:

1. Open `context/memory/tests/[CYCLE_ID]_[TARGET_SLUG].md` and fill in the Results section:
   - Eval scores (baseline vs after, delta, verdict)
   - Metrics (friction count, human interventions, cycles to KEEP)
   - Survey findings (headline friction per agent, shared patterns)
   - Hypothesis outcome: Confirmed / Falsified / Inconclusive
   - What this test did NOT cover
   - **Recommended next test** (hypothesis, target, design improvement)

2. Update `context/memory/tests/registry.md` row from IN PROGRESS to CLOSED with verdict.

3. If the hypothesis was **Confirmed**: promote the finding to `context/memory.md` L3 with
   a dedup ID and a reference to the cycle ID as evidence.

4. If the hypothesis was **Falsified**: add a "DO NOT RE-TEST" entry to `context/memory.md`
   with the cycle ID, so future cycles do not waste time re-running it.

5. If **Inconclusive**: note what additional data would be needed and what to change in
   the test design before retrying.

Emit registry updated event:
```bash
python3 "$KERNEL_PY" emit_event \
  --agent ORCHESTRATOR --type learning --action test_registry_updated \
  --correlation-id "$CYCLE_ID" \
  --summary "scenario:tests/${CYCLE_ID}_[TARGET_SLUG].md verdict:[KEEP/DISCARD] next-hypothesis:[one-line]"
```

### 4.7 Update Improvement Ledger (Every Cycle — No Exceptions)

After the test registry update, ORCHESTRATOR appends to `context/memory/improvement-ledger.md`.
This is the longitudinal record that makes the cycle of improvement visible over time.
See `references/improvement-ledger-spec.md` for the full format and writing protocol.

**Section 1 — Eval Score Progression** (one row, every cycle):
```
| [DATE] | [CYCLE_ID] | [TARGET] | [baseline score] | [after score] | [+/-delta] | KEEP/DISCARD | [N sub-cycles] | [what changed in 5-10 words] |
```

**Section 2 — Survey-to-Action Trace** (one row per friction item that generated a change):
```
| [DATE] | [survey file name] | [AGENT] | [friction item — exact quote from survey] | [action taken] | [target file] | [what changed] | [eval delta after change] | KEEP/DISCARD/pending |
```

**Section 3 — North Star Metric** (one row per session, written ONCE at session close):
```
| [DATE] | [session ID] | [total cycles] | [cycles without human rescue] | [completion %] | [human interventions total] | [friction events total] | [trend vs prior session] |
```

After appending, emit:
```bash
python3 "$KERNEL_PY" emit_event \
  --agent ORCHESTRATOR --type learning --action ledger_updated \
  --correlation-id "$CYCLE_ID" \
  --summary "target:[TARGET] delta:[DELTA] verdict:[VERDICT] survey-actions:[N rows added to section 2]"
```

**Optional: update progress chart** (run after every KEEP cycle, or on user request):
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/loop-progress-report/scripts/generate_report.py" \
  --project-dir "${CLAUDE_PROJECT_DIR}" \
  --plugin-dir "${CLAUDE_PLUGIN_ROOT}"
```

After running: "Progress chart updated at `context/memory/reports/progress_[TIMESTAMP].png`. Want to see the summary?"
Only display the chart/summary if the user says yes — never auto-display.

**If north star regresses 2 consecutive sessions**: log a warning in the ledger and invoke
`os-learning-loop` in Full Loop mode at the start of the next session. Do not wait for the
friction event threshold — a completion rate decline is a systemic signal.

### 4.8 Promote to Long-Term Memory

Run `session-memory-manager` to evaluate session log entries for L3 promotion:
- Ephemeral state -> SKIP
- System facts, architectural decisions, new conventions -> PROMOTE with dedup ID
- Use `<SUPERSEDE old_id=NNN>` if overwriting a prior fact

### 4.10 os-learning-loop Trigger Check

After metrics are collected, ORCHESTRATOR checks the friction threshold:

```bash
FRICTION=$(python3 -c "
import json
events = [json.loads(l) for l in open('${CLAUDE_PROJECT_DIR}/context/events.jsonl') if l.strip()]
# Count friction events by cause this cycle
from collections import Counter
causes = Counter(e.get('summary','').split('cause:')[-1].split()[0]
                 for e in events if e.get('type') == 'friction' and e.get('correlation_id') == '$CYCLE_ID')
print(max(causes.values()) if causes else 0, list(causes.most_common(1)))
")
```

If any single friction cause appears 3+ times this cycle: invoke `os-learning-loop` in
**Full Loop mode** automatically. Pass the friction pattern and relevant survey excerpts.
The learning loop will run root cause analysis (Kernel/RAM/Stdlib layer), propose a fix,
run the eval-gate, and apply the improvement before the next cycle begins.

### 4.11 Release Locks and Shutdown

```bash
python3 "$KERNEL_PY" release_lock memory
# Each agent:
python3 "$KERNEL_PY" emit_event --agent <ROLE> --type agent_stop --action shutdown \
  --summary "surveys:saved metrics:emitted memory:written"
```

Invoke `os-clean-locks` if any `.lock` dirs remain.

---

## North Star Metric

**Autonomous Workflow Completion Rate**: percentage of cycles that complete the full
`loop.start -> task.complete -> eval.result -> orchestrator.decision -> loop.close`
chain without human rescue. Track this in the session log. Goal: increase every cycle.

Supporting metrics (all tracked by `post_run_metrics.py`, goal: decrease every cycle):
- Human Interventions
- Workflow Uncertainty events
- Missed Step Rate
- CLI Error Rate
- Friction Events Total

---

<example>
User: "run a continuous improvement loop on the skill-improvement-eval skill"
ORCHESTRATOR reads last survey (notes INNER_AGENT flagged eval_runner.py flag confusion as
biggest friction). Writes strategy packet incorporating that fix. INNER_AGENT runs, emits
friction event when hitting the confusing flag, completes eval, saves survey noting the fix
worked. PEER_AGENT runs skill-improvement-eval independently, produces KEEP verdict with
score delta, saves survey noting zero friction. ORCHESTRATOR applies edit, runs post_run_metrics
(friction count dropped from 3 to 0), writes session log with before/after scores, promotes
fix to memory.md. No os-learning-loop trigger needed — friction threshold not crossed.
</example>

<example>
User: "audit 3 skills in parallel"
ORCHESTRATOR dispatches 3 INNER_AGENTs via claim_task. Each emits friction events during work,
runs eval_runner.py, saves survey. ORCHESTRATOR collects all results, identifies lowest scorer,
writes correction packet. After correction cycle, runs post_run_metrics — 4 friction events
for same cause (wrong CLI syntax in eval_runner). Triggers os-learning-loop Full Loop to patch
eval_runner documentation in the skill. Closes with session log and memory promotion.
</example>

<example>
User: "replace AGENT_COMMS.md with the event bus and track whether it's faster"
ORCHESTRATOR establishes bus, runs Pattern A turn-signal cycle, records round-trip latency.
INNER_AGENT and PEER_AGENT both complete post-run surveys noting any friction with polling syntax.
post_run_metrics emitted. Session log records latency delta vs AGENT_COMMS baseline.
Surveys compared — if both agents report same confusion point, os-learning-loop patches SKILL.md.
</example>

---

## References

- [dual-loop protocol](references/dual-loop.md) - strategy packet format, correction packets, verification (inlined from agent-loops)
- [skill-improvement-eval SKILL](../skill-improvement-eval/SKILL.md) - eval_runner.py, KEEP/DISCARD, results.tsv
- [session-memory-manager SKILL](../session-memory-manager/SKILL.md) - session log template, L2/L3 promotion
- [os-learning-loop agent](../../agents/os-learning-loop.md) - root cause analysis, Full Loop patching
- [loop-progress-report SKILL](../loop-progress-report/SKILL.md) - generate progress chart from improvement ledger
- [improvement-ledger-spec.md](../../references/improvement-ledger-spec.md) - ledger format, Section 1/2/3 writing protocol
- [post_run_survey.md](../../references/post_run_survey.md) - self-assessment survey template (all sections mandatory)
- [post_run_metrics.py](../../hooks/scripts/post_run_metrics.py) - automated metric collection script
- [metrics.md](../../references/metrics.md) - North Star metric definition and review cadence
- [kernel.py](../agentic-os-init/runtime/kernel.py) - v3 kernel: seven commands, ~200 lines
