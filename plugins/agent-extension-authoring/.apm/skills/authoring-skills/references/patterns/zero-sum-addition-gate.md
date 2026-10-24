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
