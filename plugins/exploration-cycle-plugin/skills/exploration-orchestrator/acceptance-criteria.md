# Acceptance Criteria: exploration-orchestrator

## Purpose

The orchestrator is successful when it coordinates the exploration loop in a way that improves clarity, reduces waste, and produces useful downstream artifacts without forcing premature convergence.

## Core Acceptance Criteria

1. The orchestrator selects an appropriate next action.

Correct behavior:
- starts broad exploration when the problem or solution is still unclear
- routes work to the right specialized agent when a specific artifact or question is needed
- triggers narrowing only when confidence appears sufficient
- reopens exploration when engineering ambiguity is real

Incorrect behavior:
- jumps straight to formal spec generation too early
- keeps the loop broad when the work is clearly ready to narrow
- invokes too many overlapping agents without a clear reason

2. The orchestrator produces a usable loop trace.

Correct behavior:
- records which agents were invoked
- records which artifacts were created or updated
- records whether the loop broadened, narrowed, or re-entered
- records why the next step was chosen

Incorrect behavior:
- leaves no useful explanation of why the loop advanced or reopened
- makes coordination decisions that cannot be inspected after the run

3. The orchestrator improves downstream usefulness.

Correct behavior:
- exploration outputs are strong enough to feed formal spec generation, planning updates, or work-package definition
- handoff is neither obviously premature nor unnecessarily delayed

Incorrect behavior:
- artifacts are generated but not useful to the next stage
- handoff repeatedly causes immediate reframing because convergence was weak

4. The orchestrator supports repeated-run optimization.

Correct behavior:
- baseline run data can be captured
- post-run survey data can be attached
- keep, discard, or crash outcomes can be compared across iterations

Incorrect behavior:
- no stable telemetry or survey signal exists to compare runs
- improvements cannot be evaluated without rereading full transcripts

## Suggested Scoring Dimensions

- routing quality
- convergence quality
- handoff timing quality
- artifact usefulness
- re-entry decision quality
- human intervention burden