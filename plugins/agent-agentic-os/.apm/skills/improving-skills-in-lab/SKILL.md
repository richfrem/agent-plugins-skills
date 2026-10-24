---
name: improving-skills-in-lab
plugin: agent-agentic-os
description: >
  Runs the Skill Improvement Lab in the main session: plan, bootstrap an isolated lab repo, KEEP or
  DISCARD improvement loop with a locked scorer, log and chart runs, backport, close with memory.
  Use for "improve this skill", "evaluate this skill", "score this change", "KEEP or DISCARD", "skill is
  not triggering", "fix skill description", "improve skill routing", "run the improvement loop", "run the
  autoresearch loop", "optimize this skill for N iterations", "close the loop", "ORCHESTRATOR and
  PEER_AGENT", "claim_task on the kernel bus", "plan an improvement", "write a delegation prompt",
  "audit what exists before improving X", "should we update or create this skill", "bootstrap the eval
  repo", "backport the lab results", "improvement chart", "update memory", "capture
  learnings", "write a session log", "what should we record from this session", or when closing a session.
  Not for control-plane task intake (use running-control-plane) or project bootstrap (use setting-up-agentic-os).
allowed-tools: Bash, Read, Write, Edit
---

# Improving skills in the lab

One conversation takes a skill or agent from a plain-language goal to a scored, backported improvement. Each mode below was a separate skill; its full workflow is a reference loaded when that mode starts.

## Contents

- [Critical constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Handoff block](#handoff-block)
- [Verification](#verification)
- [References](#references)

## Critical constraints

1. **One question at a time.** Read the whole message first, never re-ask, and offer a default with each choice.
2. **Stay read-only until the user confirms the summary** (the interview, step 4).
3. **The scorer is locked.** Every change gets exit 0 (KEEP) or 1 (DISCARD, auto-reverted); never edit `evals/evals.json` or the scorer during a run.
4. **Never record an approval for the user.** Present the command and let them run it.
5. **Lab work stays in the isolated lab repo.** Master sources change only through the backport mode, and only after checking the target skill is installed.

## Quick start

Keep the user's own wording. Ask in this order, skipping what is known, then confirm before writing anything:

1. What to improve and why, and whether it exists or is new.
2. Read the target's source and look for overlap (skills, agents, earlier runs, the target skill's `program.md`, `evals/results.tsv`); report what was found.
3. Success definition, depth (about 10, 50 or 100+ runs; recommend 50), available tools (`which gh agy claude`), second-opinion check, known problems.
4. Restate and ask "Does this look right?". Then write the target skill's `program.md`, `improvement/run-config.json` and `improvement/session-brief.md`, asking before overwriting. Resume from `improvement/run-config.json` when it exists.

Full conversation script: [interview.md](references/interview.md).

## Workflow

| Mode | Use when | Run | Workflow |
|---|---|---|---|
| `plan` | Planning an improvement, writing a delegation prompt, auditing what already exists, deciding update vs create, a new pattern to generalize | agent work, no script | [planner](references/modes/plan.md) |
| `setup` | An isolated lab repo must be built and baselined | `scripts/generate_eval_instructions.py`, `scripts/init_autoresearch.py` | [setup](references/modes/setup.md) |
| `loop` | Running the improvement cycle (orient, mutate once, score, close); solo or ORCHESTRATOR with INNER_AGENT and PEER_AGENT; fan-out, event bus, claim_task, triple-loop; closing the cycle | solo, or ORCHESTRATOR with INNER_AGENT and PEER_AGENT | [loop](references/modes/loop.md) |
| `score` | Evaluating a skill; one change needs KEEP or DISCARD; skill routing or description is wrong; RED-GREEN-REFACTOR; measuring a gain; running tests on a skill | `scripts/evaluate.py`, `scripts/eval_runner.py` | [scorer](references/modes/score.md) |
| `log` | Persist a run, query past runs, render the trend chart | `scripts/experiment_log.py`, `scripts/generate_report.py`, `scripts/plot_eval_progress.py` | [log](references/modes/log.md) |
| `backport` | A completed lab run's diff must reach the master sources | agent review, ACCEPT, ADAPT, REJECT or REVIEW per file | [backport](references/modes/backport.md) |
| `memory` | Closing a session; "remember this", "update memory", session log, capture learnings; deciding what to record or promote | installed `context/kernel.py` | [memory](references/modes/memory.md) |

Order for a full run: plan, setup, loop (which calls score every change), backport, log, memory. Do not start the next mode until the user agrees.

**Routing rule:** the table above only routes. Before acting in a mode, read that mode's workflow file in full (the last column); open the detail references below only from inside it.

## Handoff block

End each mode with the `HANDOFF_BLOCK` defined in [interview.md](references/interview.md) (target, config, brief, program, next mode, status).

## Verification

Run `python3 -m pytest tests` from this skill's folder. Each mode's gates are in [acceptance-criteria.md](references/acceptance-criteria.md); on failure follow [fallback-tree.md](references/fallback-tree.md).

## References

Detail files, grouped by the mode that uses them. Read the mode workflow first.

- **planner**: [audit-lenses](references/audit-lenses.md) • [delegation](references/delegation.md) • [plan-templates](references/plan-templates.md) • [routing-taxonomy](references/routing-taxonomy.md)
- **setup**: [copilot_proposer_prompt](references/copilot_proposer_prompt.md) • [setup-detailed-reference](references/setup-detailed-reference.md)
- **loop**: [cheapest_models](references/cheapest_models.md) • [lab-limits](references/lab-limits.md) • [mutation-protocol](references/mutation-protocol.md) • [orchestrator-meta-survey](references/orchestrator-meta-survey.md) • [program-example](references/program-example.md) • [stage-0-orientation](references/stage-0-orientation.md) • [stage-1-execution](references/stage-1-execution.md) • [stage-2-verification](references/stage-2-verification.md) • [stage-3-decision](references/stage-3-decision.md) • [stage-4-close](references/stage-4-close.md) • [test-registry-protocol](references/test-registry-protocol.md)
- **scorer**: [check-protocol](references/check-protocol.md) • [overfitting-gate](references/overfitting-gate.md) • [red-green-refactor](references/red-green-refactor.md) • [score-troubleshooting](references/score-troubleshooting.md)
- **log**: [chart-reading-guide](references/chart-reading-guide.md) • [log-detailed-reference](references/log-detailed-reference.md) • [report-reference](references/report-reference.md) • [test-scenarios-seed](references/test-scenarios-seed.md)
- **backport**: [backport-detailed-reference](references/backport-detailed-reference.md) • [phase-guide](references/phase-guide.md)
- **memory**: [improvement-ledger-spec](references/improvement-ledger-spec.md) • [loop-metrics](references/loop-metrics.md) • [memory-detailed-reference](references/memory-detailed-reference.md) • [memory-promotion-guide](references/memory-promotion-guide.md) • [post_run_survey](references/post_run_survey.md)
- **shared**: [acceptance-criteria](references/acceptance-criteria.md) • [domain-patterns-routing-skill](references/domain-patterns-routing-skill.md) • [domain-patterns](references/domain-patterns.md) • [fallback-tree](references/fallback-tree.md) • [lab-space-protocol](references/lab-space-protocol.md) • [operating-protocols](references/operating-protocols.md) • [two-improvement-paths](references/two-improvement-paths.md)
