# Test Scenario: cycle-20260322-L002 - skill-improvement-eval

## Design
- **Target**: skill-improvement-eval (SKILL.md routing triggers)
- **Hypothesis**: T02 - Removing "what" keyword from SKILL.md frontmatter (by rephrasing the negative example) eliminates the "what is the weather?" false positive and raises routing accuracy from 5/6 to 6/6.
- **Why now**: INNER_AGENT and PEER_AGENT both independently identified this fix in cycle L001 surveys. The "what" keyword leaks from example 3 in the frontmatter: `"Can someone tell me what the os-clean-locks skill does?"`. Rephrasing removes the leak.
- **What prior tests told us**: Baseline 0.8833 (routing 5/6). Sole failure: "what is the weather?" triggers due to "what" keyword overlap.
- **Acceptance criteria**: Routing accuracy 6/6 = 1.0000. Final score > 0.9. STATUS: KEEP.
- **Failure criteria**: Score < 0.8833 (regression), or "what is the weather?" still triggers.
- **Known weaknesses**: Keyword-based routing - any 4+ char word in frontmatter can cause overlap.
- **Change made**: Rephrase example 3 from `"Can someone tell me what the os-clean-locks skill does?"` to `"Tell me about the os-clean-locks skill."` — removes "what" from frontmatter keyword set.

## Results (Closed 2026-03-22)
- **Score**: 1.0000 | Routing Accuracy: 1.0000 (6/6) | Heuristic Health: 1.0000 | STATUS: KEEP
- **Hypothesis outcome**: Confirmed. Removing "what" from frontmatter example 3 fixed the false positive completely.
- **Next test**: Expand coverage with adversarial multi-category keyword cases.

## Status: CLOSED - KEEP
