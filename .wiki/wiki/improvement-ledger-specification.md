---
concept: improvement-ledger-specification
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/os-skill-improvement/references/memory/improvement-ledger-spec.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.184092+00:00
cluster: section
content_hash: 619fb81fbaaff595
---

# Improvement Ledger Specification

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Improvement Ledger Specification

The improvement ledger is the longitudinal record of the Triple-Loop. Individual loop
reports, surveys, and test registry entries are point-in-time snapshots. The ledger
is the accumulation — it answers the questions that per-cycle files cannot:

- Is eval score for `os-memory-manager` trending up or down over 10 cycles?
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
| 2026-03-21 | cycle-20260321-001 | os-memory-manager | 0.00 (first run) | 0.72 | +0.72 | KEEP | 1 | Added Phase 3 test registry preservation |
| 2026-03-22 | cycle-20260322-001 | os-memory-manager | 0.72 | 0.78 | +0.06 | KEEP | 2 | Tightened dedup conflict detection wording |
| 2026-03-22 | cycle-20260322-002 | os-eval-runner | 0.00 (first run) | 0.65 | +0.65 | KEEP | 1 | Established baseline — no change made |
| 2026-03-23 | cycle-20260323-001 | os-memory-manager | 0.78 | 0.76 | -0.02 | DISCARD | 3 | Reverted — adversarial prompt change degraded routing |
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
| 2026-03-21 | survey_20260321_1030_INNER_AGENT | INNER_AGENT | "eval_runner.py --skill flag not documented" | Added --skill flag to os-eval-runner SKILL.md examples | skills/os-eval-runner/SKILL.md | Added code block with --skill flag | +0.06 | KEEP |
| 2026-03-22 | survey_20260322_1145_PEER_AGENT | PEER_AGENT | "dedup protocol ambiguous for paraphrased facts" | Rewrote Phase 4 dedup instruction in os-memory-manager | skills/os-memory-manager/SKILL.md | Phase 4 step 2 rewritten with example | +0.06 | KEEP |
| 2026-03-22 | survey_20260322_1500_ORCHESTRATOR | ORCHESTRATOR | "registry.md orientation step unclear" | Added registry-read checklist to Stage 1 | skills/os-improvement-loop/SKILL.md | Stage 1 steps 1-2 expanded | +0.00 | BASELINE (neutral) |
| 2026-03-23 | survey_20260323_0930_INNER_AGENT | INNER_AGENT | "DO NOT RE-TEST entries hard to find" | Moved 

*(content truncated)*

## See Also

- [[improvement-ledger-spec]]
- [[improvement-ledger-spec]]
- [[improvement-ledger-spec]]
- [[improvement-ledger-spec]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[metrics-workflow-health-continuous-improvement]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/os-skill-improvement/references/memory/improvement-ledger-spec.md`
- **Indexed:** 2026-04-17T06:42:10.184092+00:00
