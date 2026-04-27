---
type: planner
result_type: qualitative
date: 2026-04-26 22:24
session_id: 0027-rsvp-speed-reader-lab
source: os-evolution-planner
target: rsvp-speed-reader
verdict: 0 workstreams, 4 gaps
---

## Experiment — 2026-04-26 22:24 | planner | rsvp-speed-reader

| Field | Value |
|-------|-------|
| Session ID | 0027-rsvp-speed-reader-lab |
| Source | os-evolution-planner |
| Target | rsvp-speed-reader |
| Result type | qualitative |
| Verdict | 0 workstreams, 4 gaps |

---

# 0027 — RSVP Speed Reader Eval Lab Setup

## Context
The user requested a full evaluation lab to autonomously improve the `rsvp-speed-reader` plugin using the Karpathy Autoresearch loop pattern. The execution must be isolated in a sibling repository, scored against a quantitative metric, constrained to 10 iterations of single-variable mutations, and concluded with a visual performance report.

## Approach Selected
**Option A — Full Karpathy Loop with ORP Metric:** We will define **ORP Calculation Accuracy** as the core metric. A headless Python script will benchmark the output of the existing `calculate_orp()` against a golden dataset of complex edge-case strings. This provides the most objective, deterministic quantitative measure for RSVP reading performance without requiring a human in the loop.

*(Options considered: Option B — Delay Variance Benchmarking (harder to establish objective truth), Option C — Token Stream Schema Fuzzing (tests stability, not performance) — Option A provides the best signal for the learning loop).*

## Gaps Identified
- No sibling eval lab repository exists yet for `rsvp-speed-reader` isolation.
- No `test_orp_engine.py` scoring script exists to measure ORP accuracy headlessly.
- No `evals.json` routing configuration exists for the scoring script.
- The `os-improvement-loop` requires a specific injection of constraints (10 iterations, 1-variable mutation).

## Workstreams
| WS | Scope | Delegate to |
|----|-------|-------------|
| WS-1 | Run `os-eval-lab-setup` for isolation | Copilot CLI (`claude-sonnet-4.6`) |
| WS-2 | Create `test_orp_engine.py` and configure `evals.json` for ORP Accuracy | Copilot CLI (`claude-sonnet-4.6`) |
| WS-3 | Run `os-improvement-loop` with 10 iterations and single-mutation constraint | Copilot CLI (`claude-sonnet-4.6`) |
| WS-4 | Run `os-improvement-report` to visualize experiment log results | Copilot CLI (`claude-sonnet-4.6`) |

## Delegation Plan
1. Delegation prompt at `tasks/todo/copilot_prompt_0027_rsvp_speed_reader_lab.md`
2. Dispatch via `run_agent.py` with `claude-sonnet-4.6`
3. Review output (experiment logs, charts)
4. Commit and PR

## Status
- [ ] WS-1: Lab Setup
- [ ] WS-2: Metric Scaffold
- [ ] WS-3: Loop Execution
- [ ] WS-4: Reporting

---

### Actions Taken
_[fill in: what was done in response to failures — spec fix, new eval, new skill]_
