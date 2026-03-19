---
name: cyclical-state-propagation-contract
description: A workflow where the output of execution cycle N acts as the structurally binding input constraint for execution cycle N+1, explicitly linking asynchronous workflows over time.
category: State / Knowledge Constraints
priority: Medium
---

# Cyclical State Propagation Contract (CSPC)

## Executive Summary
A workflow where the **output of execution cycle N becomes the structurally binding input constraint for execution cycle N+1**. The agent must simultaneously consume prior-cycle artifacts as evaluation evidence AND produce current-cycle artifacts in a schema forward-compatible with the next cycle's input requirements. This creates a closed-loop state chain across time-bounded workflow instances.

## Why This Pattern Matters
Without CSPC, cyclic workflows (performance reviews, OKR setting, multi-stage audits) become fragmented over time. The agent treats each execution as an isolated one-off event. By enforcing strict "input-from-past" and "output-for-future" contractual boundaries in the output schema, CSPC forces the agent to explicitly acknowledge workflow continuity across vast temporal gaps.

## Diagnostic Questions
- Does the workflow happen in recurring, time-bounded periods (e.g., quarterly, annually, per sprint)?
- Is the success of the current workflow dependent upon evaluating goals, targets, or schemas set in a preceding cycle?
- Does the output of the current workflow establish the baseline constraints for a future workflow?

## Core Mechanics
1. **Declare Cycle Position:** The agent explicitly labels its position in the cycle (e.g., Goal-Setting, Evaluation, or Both).
2. **Prior-Cycle Retrieval Mandate:** The output template structurally requires evidence from cycle `N-1`. If not present, the agent must explicitly raise a missing-context warning rather than hallucinating the past.
3. **Forward-Compatible Outputs:** Goals or metrics generated for cycle `N+1` use the exact schema that cycle `N+1` will expect as its input.

## Implementation Standard

```markdown
## [Workflow Title] — [Period Identifier]

> **Cycle Position:** [Evaluation | Planning | Hybrid]
> ⚠ **Prior cycle context:** [Found: [date] | Not found — manual input required]

### Phase 1: Prior Period Evaluation
*(Constraints imported from previous cycle)*
| Objective [from [prior period]] | Status | Evidence |
|---------------------------------|--------|----------|
| [Objective 1]                   | [Eval] | [Proof]  |

### Phase 2: Next Period Specification
*(These become binding constraints for the [next period] cycle)*
| Objective | Metric/Target | Owner |
|-----------|---------------|-------|
| [New Obj] | [Measurement] | [Who] |
```

## Anti-Patterns Avoided
- **Amnesic Continuity:** Setting goals in Q1 and hallucinating entirely new evaluation criteria in Q2 because the input-output schemas lacked a contractual handshake.
- **Divergent Schemas:** Changing the structure of goals every cycle, preventing programmatic data extraction over time.
