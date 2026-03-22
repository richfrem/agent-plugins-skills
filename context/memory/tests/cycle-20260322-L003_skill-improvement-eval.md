# Test Scenario: cycle-20260322-L003 - skill-improvement-eval

## Design
- **Target**: skill-improvement-eval (evals.json test coverage)
- **Hypothesis**: T03 - Adding a new positive trigger phrase "measure the performance gain" to evals.json expands adversarial test coverage. If the current frontmatter cannot satisfy it, the eval will DISCARD, proving the flywheel catches coverage gaps.
- **Why now**: PEER_AGENT L002 recommendation: expand with adversarial multi-category keyword cases. "measure the performance gain" uses domain-appropriate words (measure, performance, gain) that are NOT currently in the frontmatter keywords, so this tests whether the skill description is broad enough.
- **What prior tests told us**: After T02 fix, score is 1.0000 (6/6 routing, 1.0 heuristic). This cycle deliberately adds a harder test.
- **Acceptance criteria**: If routing 7/7 - KEEP. If 6/7 - DISCARD (expected, reveals gap in trigger coverage).
- **Failure criteria**: Python traceback or score drops below 0.5.
- **Known weaknesses**: "measure", "performance", "gain" are not in current frontmatter - this case will likely DISCARD, intentionally.
- **Change made**: Added {"prompt": "measure the performance gain", "should_trigger": true} to evals.json.

## Results (Closed 2026-03-22)
- **Score**: 0.9000 | Routing Accuracy: 0.8571 (6/7) | Heuristic Health: 1.0000 | STATUS: DISCARD
- **Hypothesis outcome**: Confirmed DISCARD. "measure the performance gain" has zero keyword overlap with frontmatter. Flywheel correctly detected the coverage gap.
- **Root cause**: "measure", "performance", "gain" not in frontmatter description.
- **Next test**: Add "measure the performance gain" to frontmatter trigger phrases, re-run eval, expect 7/7 KEEP.

## Status: CLOSED - DISCARD
