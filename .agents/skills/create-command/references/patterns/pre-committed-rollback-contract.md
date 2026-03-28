# Pattern: Pre-Committed Rollback Contract

## Overview
A structural mechanic used for high-stakes, irreversible workflows (e.g., deployments, migrations, bulk edits) that forces the user to declare explicit abort criteria *before* the action begins.

## Core Mechanic
Before starting the primary execution loop, the agent generates a mandatory `### Rollback Triggers` block in the artifact. This block contains explicit placeholder thresholds (`[X]`) that the user must fill in, or that the agent auto-fills by querying baseline metrics.

```markdown
### Rollback Triggers
- Error rate exceeds [X]%
- P50 latency exceeds [X]ms
- [Critical user flow] fails
```
The agent establishes a behavioral rule: "Decide when to roll back before you act, not during."

## Use Case
Any command where failure carries high consequences and human operators will be under stress, making real-time judgment dangerous.
