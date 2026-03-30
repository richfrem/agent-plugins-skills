# Improvement Ledger Specification

The improvement ledger is the longitudinal record of the flywheel. Individual loop
reports, surveys, and test registry entries are point-in-time snapshots. The ledger
is the accumulation — it answers the questions that per-cycle files cannot:

- Is eval score for `session-memory-manager` trending up or down over 10 cycles?
- Which survey friction item led to which skill change, and did the change improve the score?
- What is the Autonomous Workflow Completion Rate this month vs last month?

Without the ledger, every session starts from scratch on these questions. With it,
ORCHESTRATOR can read one file at orientation and know the full improvement trajectory.

---

## Location

```
context/memory/improvement-ledger.md
```

This file is runtime state (not committed). It is read at every ORCHESTRATOR orientation
(Stage 1) and written at every loop close (Stage 4.7). It is never deleted — only appended.

---

## Format: Three Sections

### Section 1: Eval Score Progression

One row per KEEP cycle per skill target. Written by ORCHESTRATOR at Stage 4.7.

```markdown
## Eval Score Progression

| Date | Cycle ID | Target | Baseline | After | Delta | Verdict | Sub-cycles to KEEP | Change Summary |
|------|----------|--------|----------|-------|-------|---------|-------------------|----------------|
| 2026-03-21 | cycle-20260321-001 | session-memory-manager | 0.00 (first run) | 0.72 | +0.72 | KEEP | 1 | Added Phase 3 test registry preservation |
| 2026-03-22 | cycle-20260322-001 | session-memory-manager | 0.72 | 0.78 | +0.06 | KEEP | 2 | Tightened dedup conflict detection wording |
| 2026-03-22 | cycle-20260322-002 | skill-improvement-eval | 0.00 (first run) | 0.65 | +0.65 | KEEP | 1 | Established baseline — no change made |
| 2026-03-23 | cycle-20260323-001 | session-memory-manager | 0.78 | 0.76 | -0.02 | DISCARD | 3 | Reverted — adversarial prompt change degraded routing |
```

**Rules:**
- **First run of any skill MUST use status `BASELINE`, not `KEEP`**. There is no prior score to
  beat on cycle 1, so a KEEP verdict is meaningless. Label it BASELINE so the step-line chart
  anchors correctly and does not show a false improvement signal.
- DISCARD cycles are also recorded (they show what did NOT work).
- `Baseline` for the first run of a skill is `0.00 (first run)` — it establishes the baseline.
- `Sub-cycles to KEEP` counts how many INNER_AGENT attempts before KEEP verdict in this loop.
- `Change Summary` is a 3-10 word description of what edit was applied (or "no change" if DISCARD).
- Do NOT summarize — record exactly what changed. "Tightened wording" is not enough. Write the actual section name or line changed.

---

### Section 2: Survey-to-Action Trace

The accountability chain from friction to fix to outcome. One row per survey finding
that resulted in a concrete change attempt (whether KEEP or DISCARD).

```markdown
## Survey-to-Action Trace

| Date | Survey ID | Agent | Friction Item | Action Taken | Target File | Change Made | Eval Delta | Outcome |
|------|-----------|-------|---------------|--------------|-------------|-------------|------------|---------|
| 2026-03-21 | survey_20260321_1030_INNER_AGENT | INNER_AGENT | "eval_runner.py --skill flag not documented" | Added --skill flag to skill-improvement-eval SKILL.md examples | skills/skill-improvement-eval/SKILL.md | Added code block with --skill flag | +0.06 | KEEP |
| 2026-03-22 | survey_20260322_1145_PEER_AGENT | PEER_AGENT | "dedup protocol ambiguous for paraphrased facts" | Rewrote Phase 4 dedup instruction in session-memory-manager | skills/session-memory-manager/SKILL.md | Phase 4 step 2 rewritten with example | +0.06 | KEEP |
| 2026-03-22 | survey_20260322_1500_ORCHESTRATOR | ORCHESTRATOR | "registry.md orientation step unclear" | Added registry-read checklist to Stage 1 | skills/concurrent-agent-loop/SKILL.md | Stage 1 steps 1-2 expanded | +0.00 | BASELINE (neutral) |
| 2026-03-23 | survey_20260323_0930_INNER_AGENT | INNER_AGENT | "DO NOT RE-TEST entries hard to find" | Moved DO NOT RE-TEST to top of registry.md | context/memory/tests/registry.md | Added pinned section at top | N/A | Not eval'd |
```

**Rules:**
- Only record friction items where an action was taken. Friction items that were noted
  but not yet acted on go in the session log Open Items, not in this ledger.
- **`Eval Delta` MUST be written as `"N/A — pending eval"` at the time of the change.**
  It is filled in only after the next eval run on the same target completes. Writing a
  forward-looking or estimated delta at change time is a protocol violation — it produces
  hallucinated trace entries that cannot be verified.
- `Outcome` is KEEP, DISCARD, BASELINE (neutral score), or "Not eval'd".
- One row per friction item that generated a change. One survey can generate multiple rows.
- This trace is how you prove the flywheel is working: friction -> change -> score delta -> keep.

---

### Section 3: North Star Metric Log

One row per session. Tracks the Autonomous Workflow Completion Rate over time.

```markdown
## North Star Metric: Autonomous Workflow Completion Rate

| Date | Session | Total Cycles | Completed Without Human Rescue | Completion Rate | Human Interventions | Friction Events Total | Trend |
|------|---------|-------------|-------------------------------|----------------|--------------------|-----------------------|-------|
| 2026-03-21 | session-001 | 2 | 1 | 50% | 3 | 7 | (baseline) |
| 2026-03-22 | session-002 | 3 | 2 | 67% | 2 | 4 | +17% |
| 2026-03-23 | session-003 | 3 | 3 | 100% | 0 | 1 | +33% |
```

**Rules:**
- `Completed Without Human Rescue` = cycles where `human_interventions` from `post_run_metrics.py` = 0.
- `Completion Rate` = Completed / Total Cycles (percentage).
- `Trend` = change from prior session (first session is "(baseline)").
- Goal: completion rate increases, friction events decrease, over sessions.
- If completion rate regresses 2 sessions in a row, ORCHESTRATOR MUST invoke os-learning-loop
  in Full Loop mode at the start of the next session — this is a mandatory auto-trigger.

---

## Writing Protocol

ORCHESTRATOR writes to all three sections at **Stage 4.7** of every loop close, immediately
after the test registry update (Stage 4.6) and before long-term memory promotion (Stage 4.8).

### Write procedure

1. Read the current `context/memory/improvement-ledger.md` (use `Read` tool).
2. Append new row(s) to the appropriate section(s) -- never rewrite existing rows.
3. For Section 1: add one row if verdict was KEEP or DISCARD.
4. For Section 2: add one row per survey friction item that resulted in an action this cycle.

   **Section 2 grep verification (mandatory before writing each row)**:
   The friction quote in the `Friction Quote` column must be a verbatim excerpt
   (under 15 words) from the cited survey file. Before writing the row, run:
   ```bash
   grep -F "[exact friction quote]" "context/memory/retrospectives/[survey_file].md"
   ```
   If no match is found, the row is a protocol violation -- do not write it.
   Paraphrases or invented quotes are not acceptable. If the survey used different
   words to describe the friction, quote those exact words.

5. For Section 3: add one row per session (written once at session close, not per cycle).
6. Verify the append with `Read` (Post-Write Verification protocol).

Emit ledger updated event:
```bash
python3 "$KERNEL_PY" emit_event \
  --agent ORCHESTRATOR --type learning --action ledger_updated \
  --correlation-id "$CYCLE_ID" \
  --summary "section:eval-score target:[TARGET] delta:[DELTA] survey-actions:[N]"
```

---

## Reading Protocol (ORCHESTRATOR Orientation)

At Stage 1 orientation, ORCHESTRATOR reads the improvement ledger BEFORE writing the strategy packet:

1. **Scan Section 1** (Eval Score Progression) for the target skill:
   - What is the current baseline? Is score trending up or flat?
   - Are there DISCARD rows for this target? What did NOT work?
   - How many sub-cycles to KEEP on average? (Informs time budget.)

2. **Scan Section 2** (Survey-to-Action Trace) for the target skill:
   - Which friction items have already been acted on?
   - Did those actions produce positive eval delta? Or neutral/negative?
   - Are there unresolved friction items from prior cycles that need follow-up?

3. **Scan Section 3** (North Star Metric) for session trend:
   - Is completion rate stable, improving, or regressing?
   - Two-session regression -> mandatory os-learning-loop at session start.

These answers must inform the strategy packet content. A strategy packet written without
reading the ledger is missing the core improvement context.

---

## Initialization

The ledger is initialized the first time ORCHESTRATOR runs a loop close on a new project.
Create the file with all three section headers and an empty table under each:

```bash
# First-run initialization
cat > context/memory/improvement-ledger.md << 'EOF'
# Improvement Ledger

> Longitudinal record of eval score progression, survey-to-action traceability,
> and autonomous completion rate. Updated every loop close. Read at every orientation.

## Eval Score Progression

| Date | Cycle ID | Target | Baseline | After | Delta | Verdict | Sub-cycles to KEEP | Change Summary |
|------|----------|--------|----------|-------|-------|---------|-------------------|----------------|

## Survey-to-Action Trace

| Date | Survey ID | Agent | Friction Item | Action Taken | Target File | Change Made | Eval Delta | Outcome |
|------|-----------|-------|---------------|--------------|-------------|-------------|------------|---------|

## North Star Metric: Autonomous Workflow Completion Rate

| Date | Session | Total Cycles | Completed Without Human Rescue | Completion Rate | Human Interventions | Friction Events Total | Trend |
|------|---------|-------------|-------------------------------|----------------|--------------------|-----------------------|-------|
EOF
```

---

## What the Ledger Enables

| Question | Without ledger | With ledger |
|----------|---------------|-------------|
| Is session-memory-manager improving? | Read 10 loop reports manually | Scan Section 1, one table |
| Did that survey fix actually help? | Read survey + loop report + test registry | Scan Section 2, one row |
| Are we completing more cycles autonomously? | Calculate from individual metric events | Scan Section 3, one table |
| What changes made things worse? | No record | Section 1 DISCARD rows with change summary |
| Which agent generates the most actionable friction items? | Impossible without aggregation | Section 2, group by Agent column |
| When should os-learning-loop auto-trigger on trend? | No signal | Section 3, two consecutive regression rows |

---

## Anti-Patterns

- **Rewriting rows**: Never modify a prior row. Append-only. If a finding changes, the new
  evidence is a new row in Section 2 with the outcome "supersedes [date] row".
- **Vague change summaries**: "Improved wording" is not a change summary. "Rewrote Phase 4
  step 2 dedup conflict detection instructions" is.
- **Not recording DISCARDs**: Negative results are as important as positive ones. A DISCARD
  row tells the next ORCHESTRATOR what NOT to try — preventing repeated wasted cycles.
- **Skipping Section 2**: Only writing Section 1 (eval scores) without Section 2 (survey trace)
  breaks the causal chain. You can see scores moving but not why.
- **Writing Section 3 per cycle instead of per session**: Section 3 is a session-level metric.
  Writing it per cycle inflates the row count and makes trend analysis harder.
