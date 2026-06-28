# Stage 4: Mandatory Loop Close

## 4.0 Friction Resolution Gate

Before `loop.close` may be emitted, ORCHESTRATOR must verify all friction events from this
cycle are resolved. A loop cannot close with unhandled friction.

```bash
# Count friction encounters vs resolutions for this cycle
OPEN=$(python "$KERNEL_PY" read_events --type friction --correlation-id "$CYCLE_ID" | python -c "import sys,json; print(len(json.load(sys.stdin)))")
CLOSED=$(python "$KERNEL_PY" read_events --type friction.resolved --correlation-id "$CYCLE_ID" | python -c "import sys,json; print(len(json.load(sys.stdin)))")
# Pass only if OPEN == CLOSED
```

For each `friction` event, verify exactly one `friction.resolved` event exists with matching
`correlation-id`. Valid resolutions: `outcome: FIX`, `MAP_DEBT`, or `ESCALATE`.

If `OPEN != CLOSED`, do **not** emit `loop.close`. Resolve or escalate before proceeding to 4.1.

## 4.1 Emit loop.close

```bash
python "$KERNEL_PY" emit_event \
  --agent ORCHESTRATOR --type result --action loop.close \
  --status success --correlation-id "$CYCLE_ID" \
  --summary "improvements-applied:N friction-events:N"
```

## 4.2 Agent Self-Assessment Survey (Each Agent)

Every agent that performed work this cycle MUST complete the Post-Run Self-Assessment Survey
(`references/memory/post_run_survey.md`). Answer every section — do not skip.

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
python "$KERNEL_PY" emit_event \
  --agent PEER_AGENT --type learning --action survey_completed \
  --summary "retrospectives/survey_${DATE}_${TIME}_PEER_AGENT.md"
```

## 4.3 Run Post-Run Metrics

```bash
python "${CLAUDE_PROJECT_DIR}/context/kernel.py" emit_event \
  --agent post_run_hook --type intent --action session_summary

python ./scripts/post_run_metrics.py
```

This emits a `type: metric` event with:
- `human_interventions` — count of human rescues this cycle
- `workflow_uncertainty` — count of uncertainty friction events
- `missed_steps` — count of skipped required steps
- `cli_errors` — count of wrong CLI syntax errors
- `friction_events_total` — total friction events
- `hook_errors` — count from `context/memory/hook-errors.log`

## 4.4 Write Session Log

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

## 4.5 Loop Report (Every Cycle — Published Before Memory Close)

ORCHESTRATOR writes a Loop Report before running `os-memory-manager`. This is the
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
- [ ] Triple-Loop Retrospective triggered: YES (cause: [friction pattern]) / NO
```

Emit loop report written event:
```bash
python "$KERNEL_PY" emit_event \
  --agent ORCHESTRATOR --type result --action loop.report \
  --correlation-id "$CYCLE_ID" \
  --summary "report:loop-reports/report_${CYCLE_ID}.md"
```

## 4.6 Test Registry Update (MANDATORY — Every Cycle)

After the loop report is written, update the test scenario record per
`references/testing/test-registry-protocol.md`:

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
python "$KERNEL_PY" emit_event \
  --agent ORCHESTRATOR --type learning --action test_registry_updated \
  --correlation-id "$CYCLE_ID" \
  --summary "scenario:tests/${CYCLE_ID}_[TARGET_SLUG].md verdict:[KEEP/DISCARD] next-hypothesis:[one-line]"
```

## 4.7 Update Improvement Ledger (Every Cycle — No Exceptions)

After the test registry update, ORCHESTRATOR appends to `context/memory/improvement-ledger.md`.
This is the longitudinal record that makes the cycle of improvement visible over time.

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
python "$KERNEL_PY" emit_event \
  --agent ORCHESTRATOR --type learning --action ledger_updated \
  --correlation-id "$CYCLE_ID" \
  --summary "target:[TARGET] delta:[DELTA] verdict:[VERDICT] survey-actions:[N rows added to section 2]"
```

## 4.8 Promote to Long-Term Memory

Run `os-memory-manager` to evaluate session log entries for L3 promotion:
- Ephemeral state -> SKIP
- System facts, architectural decisions, new conventions -> PROMOTE with dedup ID
- Use `<SUPERSEDE old_id=NNN>` if overwriting a prior fact

## 4.9 Update Claude Auto-Memory (MEMORY.md)

After `os-memory-manager` runs, review the session for facts worth persisting in Claude's
**cross-session auto-memory** (`memory/MEMORY.md` in the project memory directory).

This is distinct from `os-memory-manager` (which promotes facts into `context/memory.md`
inside the lab). Auto-memory persists across all future conversations — it is the agent's
durable long-term knowledge about the user, project, and working patterns.

**What belongs here** (not in os-memory-manager):
- New non-obvious user preferences or feedback on how to collaborate
- Structural decisions made this session (e.g. skill moved, plugin renamed, pattern adopted)
- Surprising findings that should inform future sessions (e.g. sweep results, failed approaches)
- Project state changes that will be non-obvious next session

**What does NOT belong here** (use os-memory-manager instead, or skip):
- Code patterns, file paths, architecture derivable by reading the repo
- Temporary/ephemeral task state
- Anything already in CLAUDE.md

**Procedure:**
1. Read `memory/MEMORY.md` — check for stale entries that need updating
2. For each non-obvious fact worth preserving: write a new memory file or update an existing one
3. Add/update pointer in `memory/MEMORY.md`

## 4.10 Triple-Loop Retrospective Trigger Check

After metrics are collected, ORCHESTRATOR checks the friction threshold:

```bash
FRICTION=$(python -c "
import json
events = [json.loads(l) for l in open('${CLAUDE_PROJECT_DIR}/context/events.jsonl') if l.strip()]
# Count friction events by cause this cycle
from collections import Counter
causes = Counter(e.get('summary','').split('cause:')[-1].split()[0]
                 for e in events if e.get('type') == 'friction' and e.get('correlation_id') == '$CYCLE_ID')
print(max(causes.values()) if causes else 0, list(causes.most_common(1)))
")
```

If any single friction cause appears 3+ times this cycle: invoke `Triple-Loop Retrospective` in
**Full Loop mode** automatically. Pass the friction pattern and relevant survey excerpts.

## 4.11 Release Locks and Shutdown

```bash
python "$KERNEL_PY" release_lock memory
# Each agent:
python "$KERNEL_PY" emit_event --agent <ROLE> --type agent_stop --action shutdown \
  --summary "surveys:saved metrics:emitted memory:written"
```
