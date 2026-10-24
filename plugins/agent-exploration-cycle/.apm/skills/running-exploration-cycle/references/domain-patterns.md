# Domain Patterns: Known Failures and Escapes (Exploration Cycle)

Curated library of known failure types and the escape that resolved each. Moved up from the `domain-patterns/` folder and reviewed against the consolidated skills; the stale paths and the partly implemented fixes are called out in the pattern file.

## What they are

When an improvement loop (the `os-lab-*` skills in `agent-agentic-os`) meets a failure type it has seen before, it can apply a proven escape instead of inventing a new hypothesis. A person fixing the workflow by hand can use them the same way.

## When to read them

Before formulating an improvement hypothesis for this plugin. If the failure matches a known pattern, apply that pattern's escape first.

## How to add a pattern

1. A novel friction point occurs and is resolved by a confirmed improvement.
2. After a **second confirmation** of the same failure type, promote it to `## Known Patterns`.
3. Record: failure type, root cause, escape steps, confirmation count.

## Files

Named `domain-patterns-<stage>.md`, one per workflow stage:

| File | Covers | State |
|:-----|:-------|:------|
| [domain-patterns-exploration-session.md](domain-patterns-exploration-session.md) | Session misclassification, HARD-GATE bypass, premature handoff | exists, reviewed |
| `domain-patterns-requirements-capture.md` | BRD quality, gap-marker inconsistency, coverage failures | listed in the original README, never written |
| `domain-patterns-prototype-build.md` | Component decomposition, brownfield conflicts, plugin-mode detection | listed in the original README, never written |

The confirmation counts in the pattern file were recorded by the retired optimizer loop; the plugin's evolution log is empty, so they cannot be re-verified.
