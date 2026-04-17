---
concept: pattern-zero-sum-addition-gate
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/zero-sum-addition-gate.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.017346+00:00
cluster: planning
content_hash: 2540f8b79912581a
---

# Pattern: Zero-Sum Addition Gate

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Pattern: Zero-Sum Addition Gate

## Overview
A pre-action capacity constraint used in planning domains that forbids the agent from blindly executing an additive operation without forcing a subtractive trade-off.

## Core Mechanic
At execution time, if the user requests adding an item to a constrained resource (a sprint, a roadmap, a budget), the agent pauses and asks what is being removed or deferred to make room.

```markdown
## Capacity Gate
Before adding any item to the roadmap:
1. If current + new item > capacity threshold:
   - Do NOT add the item yet.
   - Wait for the user to identify a trade-off: "Adding X exceeds capacity. What moves?"
2. Document the trade-off explicitly in the output.
```

## Use Case
Sprint planning, roadmap management, staffing changes, or any system where resources are finite and silent addition generates hidden debt.


## See Also

- [[zero-sum-addition-gate]]
- [[zero-sum-addition-gate]]
- [[zero-sum-addition-gate]]
- [[zero-sum-addition-gate]]
- [[zero-sum-addition-gate]]
- [[zero-sum-addition-gate]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/patterns/zero-sum-addition-gate.md`
- **Indexed:** 2026-04-17T06:42:10.017346+00:00
