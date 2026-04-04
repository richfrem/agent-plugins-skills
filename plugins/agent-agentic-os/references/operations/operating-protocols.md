# Operating Protocols

This document defines the canonical, mandatory protocols for setting up and running Agentic OS evaluations. To maximize repository safety and execution efficiency, several legacy approaches have been deprecated.

## The Two Unified Operating Protocols

Rather than offering multiple overlapping options for testing, we rely on **One Core Architecture (The Triple-Loop Learning System)** operating in two distinct phases, each mapped to a specific agent:

| Phase / Protocol | Managing Agent | How It Works | Deprecated Legacy Alternatives |
|------------------|----------------|--------------|--------------------------------|
| **1. Interactive Lab Setup** <br>*(Test Environment)* | `triple-loop-architect` | **Sibling Repo Labs** <br> The architect creates isolated test repos alongside the main project folder (`../test-target-skill`). <br>*(See: `assets/diagrams/sibling-repo-labs.mmd`)* | ❌ Subfolder tests within repo <br> ❌ Manual Copilot CLI project generation |
| **2. Unattended Execution** <br>*(Run Mechanism)* | `triple-loop-orchestrator` | **Headless Overnight Orchestrator** <br> The orchestrator runs the full Triple-Loop System headlessly overnight (e.g. via Gemini/Copilot CLI), using `evaluate.py` as an objective gate. <br>*(See: `assets/diagrams/headless-overnight-orchestrator.mmd`)* | ❌ Interactive Step-by-Step Confirmation Loops <br> ❌ Single/Double/Dual loops presented as separate, disjoint options |

## The Golden Path (End-to-End)

1. **Bootstrap** a pristine, risk-free sibling evaluation repo guided by the `triple-loop-architect` agent.
2. **Execute** iterations headlessly using the `triple-loop-orchestrator` agent.
3. **Review & Backport** only the successful, evaluated changes back to the canonical sources using the `os-eval-backport` skill.

## Critical Rule: The Re-Baseline Protocol

Whenever you manually update a plugin's underlying structure—such as fixing a bug in an associated `plugin/scripts/*.py` script, or refactoring the test inputs in `evals.json`—the previously recorded baseline metrics and the `.lock.hashes` cryptographic snapshot become instantly invalid.

**You must always recapture the baseline:**
If you change the mechanics of a skill outside of an active automated loop, you must clear the old lock and recapture the baseline mapping *before* initiating the next loop session. Failing to respect the Re-Baseline Protocol will either cause the loop to fail with a tampering error (Exit 3) or optimize against corrupted metrics.
