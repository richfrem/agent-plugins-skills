---
name: population-normative-distribution-constraint
description: Embedding top-down institutional distribution curves alongside localized decision tables to enforce population-level reality checks against human inflation/deflation biases.
category: Output / Formatting Constraints
priority: High
---

# Population-Normative Distribution Constraint (PNDC)

## Executive Summary
An output template embeds **statistical population-level distribution targets as a structural column** alongside agent-generated or user-provided data. The target distribution is not a suggestion — it appears in the same table as the actual data, creating a visual comparison that forces the user to reconcile their individual decisions against organizational-level normative expectations. The agent is not just displaying data; it is constructing a **normative calibration moment**.

## Why This Pattern Matters
Individual human evaluators suffer from local bias (e.g., grade inflation in performance reviews, overly optimistic story-point estimation). While the agent cannot evaluate *everyone*, it can hold the evaluator accountable to the *expected statistical distribution*. PNDC prevents localized micro-optimizations from violating macro-organizational budgets or curves by structurally forcing a comparison before a final decision is locked.

## Diagnostic Questions
- Does the workflow aggregate the scores, ratings, or resource allocations of multiple independent entities?
- Does the organization have an expected statistical distribution (e.g., bell curves, specific pass/fail target rates, budget caps) for this data?
- Does human judgment typically skew optimistically or pessimistically away from those targets if left unchecked?

## Core Mechanics
1. **Structural Calibration Table:** Create a summary table that tracks `# Evaluated` and calculates the actual percentage of the whole for each category.
2. **Embedded Target Curve:** Add a hardcoded or configured "Expected % Target" column natively to the summary table.
3. **Delta Flagging:** Use conditionals to explicitly flag structural discrepancies when actual values deviate from the target range by `>X%`.

## Implementation Standard

```markdown
### Normative Calibration Summary

| Category/Rating | Actual Count | Actual % | Target Distribution | Calibration Status |
|-----------------|--------------|----------|---------------------|--------------------|
| Exceptional     | [Count]      | [X]%     | 10–15%              | ✅ / ⚠             |
| Expected        | [Count]      | [Y]%     | 70–80%              | ✅ / ⚠             |
| Needs Improv.   | [Count]      | [Z]%     | 5–10%               | ✅ / ⚠             |

> **Calibration Warnings:**
> [If Actual > Target: ⚠ Your Exceptional rating count currently sits at 35%, significantly above the organizational normative band of 10-15%. Please review evaluations for inflation prior to final submission.]
```

## Anti-Patterns Avoided
- **Micro-Macro Divergence:** Creating localized plans that look perfectly reasonable in isolation but bankrupt a system's capacity, budget, or standards curve when aggregated across the population.
- **Siloed Judgment Validation:** Depending on a human committee meeting 3 weeks later to catch grading inflation, instead of catching it at generation-time.
