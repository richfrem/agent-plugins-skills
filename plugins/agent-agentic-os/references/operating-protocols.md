# Operating Protocols

This document defines the canonical, mandatory protocols for setting up and running Agentic OS evaluations. To maximize repository safety and execution efficiency, several legacy approaches have been deprecated.

## Canonical Setup & Execution Matrix

| Architecture Component | Golden Protocol | Deprecated Legacy Protocols | Why Deprecated? |
|-------------------------|----------------|-----------------------------|-----------------|
| **Test Environment** | **Sibling Repo Labs** <br> Creates isolated test repos alongside the main project folder (`../test-target-skill`). Facilitated by `os-eval-lab-setup`.<br>*(See: `assets/diagrams/sibling-repo-labs.mmd`)* | ❌ Subfolder within repo <br> ❌ Manual Copilot CLI project generation | Subfolders pollute git index and tangle lab artifacts with master. Manual generation is brittle. |
| **Execution Loop** | **Triple-Loop Learning System** <br> Unified model: Orchestrator (Meta-learning) → Strat Planner → Tactical Executor.<br>*(See: `assets/diagrams/triple-loop-learning-system.mmd`)* | ❌ Presenting Single, Double, or Dual loops as separate choices. | Creates confusion. They are nested rings of the *same* system, not distinct alternative operational models. |
| **Run Mechanism** | **Headless Overnight Orchestrator** <br> External agent (e.g. Gemini/Copilot CLI) runs the triple-loop iterations headlessly.<br>*(See: `assets/diagrams/headless-overnight-orchestrator.mmd`)* | ❌ Manual step-by-step confirmation loops | Human latency blocks large-scale iteration testing. Objective gating runs securely in the background. |

## The Golden Path (End-to-End)

1. **Bootstrap** a pristine, risk-free sibling evaluation repo using `os-eval-lab-setup`.
2. **Execute** iterations headlessly using the **Triple-Loop Orchestrator** pattern.
3. **Review & Backport** only the successful, evaluated changes back to the canonical sources using `os-eval-backport`.

## Critical Rule: The Re-Baseline Protocol

Whenever you manually update a plugin's underlying structure—such as fixing a bug in an associated `plugin/scripts/*.py` script, or refactoring the test inputs in `evals.json`—the previously recorded baseline metrics and the `.lock.hashes` cryptographic snapshot become instantly invalid.

**You must always recapture the baseline:**
If you change the mechanics of a skill outside of an active automated loop, you must clear the old lock and recapture the baseline mapping *before* initiating the next loop session. Failing to respect the Re-Baseline Protocol will either cause the loop to fail with a tampering error (Exit 3) or optimize against corrupted metrics.
