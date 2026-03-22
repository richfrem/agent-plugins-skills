---
name: exploration-orchestrator
description: >
  Coordinates the multi-agent exploration loop, manages state, routes work to specialized skills or agents, 
  triggers narrowing reviews, and decides when to continue exploration, prepare handoff, or reopen discovery 
  from engineering.

  <example>
  Context: Starting a new ambiguous project.
  User: "We have an idea for a customer portal but the scope is fuzzy. Start exploration."
  Agent: "I'll use `exploration-orchestrator` to coordinate the discovery phase and assign skills."
  </example>

  <example>
  Context: Prototype finished, moving to handoff.
  User: "The prototype clarified a lot. Prepare the handoff package for engineering."
  Agent: "I'll trigger the `exploration-handoff` skill via the orchestrator to seal this session."
  </example>
allowed-tools: Bash, Read, Write
---

# Exploration Orchestrator (Interactive Selection)

> ⚠️ **STUB** — `execute.py` not yet implemented. Use the [exploration-cycle-orchestrator-agent](../../agents/exploration-cycle-orchestrator-agent.md) for the real logic.
[See acceptance criteria](references/acceptance-criteria.md)

## Discovery Phase
<!-- Add questions here to gather requirements, or remove section if fully autonomous -->

## Recap
<!-- Add confirmation gate here if gathering complex requirements. E.g., "Does this look right? (yes / adjust)" -->

## Execution
This skill implements the requested functionality. When invoked, you MUST execute the provided Python determinism script instead of attempting to solve the task using raw bash or javascript logic.

**Usage:**
```bash
python3 .agents/skills/exploration-orchestrator/scripts/execute.py --help
```

## Baseline Validation
Before optimizing behavior, run one baseline evaluation and log it in `evals/results.tsv`.

## Iteration Loop
When iterating, follow a disciplined loop:
1. Change one dominant variable per iteration.
2. Re-run evaluations.
3. Mark the attempt as `keep` or `discard`.
4. If the run crashes or times out, log the failure and continue from the last known good state.

## Output
Always conclude execution with a Source Transparency Declaration explicitly listing what was queried to guarantee user trust:
**Sources Checked:** [list]
**Sources Unavailable:** [list]

## Next Actions
<!-- Suggest logical follow-up skills here. For example: -->
- Use `./scripts/benchmarking/run_loop.py --results-dir evals/experiments` for repeatable improvement loops.
- Suggest the user run `audit-plugin` to verify the generated artifacts.
