# Test Scenario: cycle-20260322-005544 - skill-improvement-eval

## Design
- **Target**: skill-improvement-eval (SKILL.md + evals.json)
- **Hypothesis**: T01 - The skill triggers correctly on "evaluate this skill" and related phrases,
  but does NOT trigger on "explain this skill", "describe this skill", or "show me the eval results".
- **Why now**: All results.tsv baselines are empty. This establishes routing accuracy baseline.
- **What prior tests told us**: None - first test of this target.
- **Acceptance criteria**: Eval triggers on positive phrases; does NOT trigger on negative phrases.
  BASELINE status returned (last_score == 0.0). Eval score > 0.5.
- **Failure criteria**: Python traceback, score == 0.0, or status != BASELINE.
- **Known weaknesses**: Routing is inferred from keyword overlap with frontmatter, not real execution.

## Results (Closed 2026-03-22)

- **INNER_AGENT score**: 0.8833 | Routing Accuracy: 0.8333 (5/6) | Heuristic Health: 1.0000 | STATUS: BASELINE
- **PEER_AGENT score**: 0.8833 | Routing Accuracy: 0.8333 (5/6) | Heuristic Health: 1.0000 | STATUS: KEEP
- **Canonical baseline**: 0.8833
- **Hypothesis outcome**: Partially confirmed. Skill triggers correctly on positive phrases. One false positive: "what is the weather?" triggered when it should not. Routing accuracy 0.8333 not 1.0.
- **Survey consensus**: Both agents independently identified the same fix - add negative-match guard for out-of-domain queries in routing triggers.
- **Next recommended test**: Add exclusion pattern for weather/time/trivia queries, re-run eval, expect score >= 0.9333.

## Status: CLOSED - BASELINE
