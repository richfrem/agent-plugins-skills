# Improvement Ledger

> Longitudinal record of eval score progression, survey-to-action traceability,
> and autonomous completion rate. Updated every loop close. Read at every orientation.

## Eval Score Progression

| Date | Cycle ID | Target | Baseline | After | Delta | Verdict | Sub-cycles to KEEP | Change Summary |
|------|----------|--------|----------|-------|-------|---------|-------------------|----------------|
| 2026-03-22 | cycle-20260322-005544 | skill-improvement-eval | 0.00 (first run) | 0.8833 | +0.8833 | BASELINE | 1 | First run - no change made. Routing accuracy 5/6, heuristic health 1.0. One false positive: "what is the weather?" |
| 2026-03-22 | cycle-20260322-L002 | skill-improvement-eval | 0.8833 | 1.0000 | +0.1167 | KEEP | 1 | Rephrased frontmatter example 3 to remove "what" keyword - eliminated "what is the weather?" false positive. Routing 6/6. |
| 2026-03-22 | cycle-20260322-L003 | skill-improvement-eval | 1.0000 | 0.9000 | -0.1000 | DISCARD | 1 | Added "measure the performance gain" to evals.json as positive test - frontmatter lacks measure/performance/gain keywords, case 7 fails to trigger. No change applied. |
| 2026-03-22 | cycle-20260322-L004 | skill-improvement-eval | 0.9000 | 1.0000 | +0.1000 | KEEP | 1 | Added "measure the performance gain" to SKILL.md frontmatter trigger phrases - resolved L003 DISCARD. Routing 7/7. |

## Survey-to-Action Trace

| Date | Survey ID | Agent | Friction Item | Action Taken | Target File | Change Made | Eval Delta | Outcome |
|------|-----------|-------|---------------|--------------|-------------|-------------|------------|---------|
| 2026-03-22 | survey_20260322_INNER_AGENT | INNER_AGENT | "what is the weather? triggered as false positive - routing accuracy 0.8333" | Identified: add negative-match guard for out-of-domain queries (weather/time/trivia) | plugins/agent-agentic-os/skills/skill-improvement-eval/SKILL.md routing trigger section | N/A - pending eval | N/A - pending eval | Not yet applied - recommendation for next cycle |
| 2026-03-22 | survey_20260322_PEER_AGENT | PEER_AGENT | "no expected-failure annotation mechanism exists to distinguish known boundary failures from regressions" | Identified: add expected-failure annotation to eval fixtures | plugins/agent-agentic-os/skills/skill-improvement-eval/evals/evals.json | N/A - pending eval | N/A - pending eval | Not yet applied - recommendation for next cycle |

## North Star Metric: Autonomous Workflow Completion Rate

| Date | Session | Total Cycles | Completed Without Human Rescue | Completion Rate | Human Interventions | Friction Events Total | Trend |
|------|---------|-------------|-------------------------------|----------------|--------------------|-----------------------|-------|
| 2026-03-22 | session-20260322 | 1 | 1 | 100% | 0 | 0 | (baseline) |
