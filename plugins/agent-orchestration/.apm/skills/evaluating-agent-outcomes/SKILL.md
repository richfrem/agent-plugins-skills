---
name: evaluating-agent-outcomes
plugin: agent-orchestration
description: >
  Repository-independent evaluation of delegated agent work: assesses a delivery against a work contract
  (criterion-level pass/fail/unverified, failure conditions, budget, authorization), checks evidence validity,
  selects proportionate verification, measures cost with missing data kept unknown, classifies human
  interventions, and records and retrieves specific lessons. Use when orchestrating-agent-work needs findings
  after a worker returns, or to gate a benchmark before model calls. Not an orchestrator and never grants authority.
allowed-tools: Bash, Read, Write
---

# Evaluating Agent Outcomes (`evaluating-agent-outcomes`)

The evaluator supplies **findings**; the orchestrator decides. Scores and passing checks never expand authorization.

## Contents

- [Constraints](#constraints) • [Quick Start](#quick-start) • [Defaults](#defaults) • [References](#references)

## Constraints

- **Findings only**: `complete` is true only when every required criterion passes and no failure condition fired. A numeric score cannot change it.
- **Unknown is not zero**: missing usage, interventions or telemetry are reported as unknown with coverage.
- **Bounded storage**: records go to an explicit store inside a declared root (default `<root>/.agent-work/records.jsonl`); never to a global ledger.
- **One implementation**: reusable logic lives in `scripts/` (`eval_core.py` gates and records, `scoring.py`, `accounting.py`, `usage_measure.py`, `outcome_eval.py`, `lessons.py`); consumers supply profiles, policy and storage and import it (Sanctuary does). Do not re-implement scoring or accounting in a consumer.
- **Scope**: this skill evaluates ordinary work. Project policy (research verdicts, governance, budgets, dashboards) belongs to the consuming repository's own skill.

## Quick Start

```bash
python3 scripts/outcome_eval.py validate contract.json
python3 scripts/outcome_eval.py assess contract.json --root . [--evidence evidence.json]   # exit 0 only if complete
python3 scripts/lessons.py --root . find "restricted PATH worker launch"                   # before dispatch
python3 scripts/lessons.py --root . add --trigger ... --failure ... --evidence ... --action ... --verification ... --limits ...
python3 scripts/outcome_eval.py assess contract.json   # optional rubric scores via scoring.py (assets/rubrics/pr-review.json)
python3 scripts/eval_cli.py --root . validity benchmark.json   # include a "claim" object for claim-specific validity   # fixtures | pilot | validity | intervention | repair | invest | summary
```

## Workflow

1. Before dispatch: `lessons.py find`. 2. After a worker returns: `outcome_eval.py assess` and hand findings to the orchestrator. 3. Before model benchmarks: `eval_cli.py fixtures|pilot`; after: `validity`. 4. Record `intervention` / `repair` / `lessons.py add|use` from observed events.

## Verification

```bash
python3 -m pytest tests -q
```

## Defaults

Small by default: acceptance, evidence, resource use, blockers. A rubric is optional (`assets/rubrics/pr-review.json` is an example profile). Deterministic checks first; bounded model review only where assertions cannot settle the question.

## References

- [work-contract.md](references/work-contract.md) — contract, findings and record formats, storage rules.
- [scoring-and-accounting.md](references/scoring-and-accounting.md) — Profile-driven scoring, cost tiers, usage ledger folding, usage measurement; what consumers keep.
- [gates.md](references/gates.md) — fixtures, output-contract pilot, benchmark validity cap, interventions, repair recurrence, investment accounting.
