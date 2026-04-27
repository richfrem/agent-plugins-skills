# agent-loops Simplification Plan

**Context:** This document outlines the architectural pruning and realignment of the `agent-loops` plugin. It acts as the counterpart to the `agent-agentic-os` Simplification Plan. While the OS provides evaluation, memory, and state, `agent-loops` provides strict **framework-agnostic execution patterns**.

**Version:** v1.2 — Updated with Red Team Review identifying deep OS-level leakage.

---

## The Core Thesis

The `agent-loops` plugin is severely bloated (114k+ tokens, 121 files). The complexity does not stem from its execution loops; it stems from absorbing an entire library of 33+ third-party personas and highly opinionated domain templates that violate its "framework-agnostic" design goals.

The fix is: **Extract the personas, standardize the 5 execution primitives, and strip out OS-level assumptions.**

---

## What the System Actually Is

At its core, `agent-loops` is a library of **execution primitives** (analogous to the Google Agent Design Kit patterns) mapped to Python engines. 

```text
User / OS Trigger
    ↓
orchestrator              ← The Router: Picks the right primitive for the job
    ├── learning-loop     ← Primitive 1: Single Agent (Linear research/synthesis)
    ├── red-team-review   ← Primitive 2: Review & Critique (Adversarial loops)
    ├── dual-loop         ← Primitive 3: Sequential Agent (Manager/Worker delegation)
    ├── agent-swarm       ← Primitive 4: Parallel Agent (Concurrent execution)
    └── triple-loop       ← Primitive 5: Hierarchical Meta-Loop (Outer/Mid/Inner execution)
```

Everything else—specifically the 33 domain personas and the heavily opinionated markdown templates—is scope creep.

---

## Cuts & Extractions (The Persona & Template Problem)

### 1. Extract the `personas/` Directory Completely
**The Problem:** The `personas/` folder contains 33+ highly specific system prompts (`frontend-developer`, `graphql-architect`, `postgres-pro`, etc.) separated across `business/`, `data-ai/`, `development/`, `infrastructure/`, `quality-testing/`, and `security/`.
* **Token Bloat:** They account for over 50% of the plugin's total token footprint.
* **Scope Violation:** A plugin designed to manage *how* agents loop should not dictate *what* personality the agents have. The OS or the user should supply the persona.
* **The Fix:** Remove the `personas/` directory entirely. Extract them into a standalone, optional plugin (e.g., `agent-personas`) or migrate them to a global `.claude/prompts/` directory.

### 2. Prune Opinionated Templates
**The Problem:** Files like `learning_audit_template.md` (which hardcodes references to "QEC-AI hypothesis", "DrHall", and "Containment Trauma") or `sources_template.md` are highly opinionated. They lock the "framework-agnostic" loop into a specific user's legacy workflow.
* **The Fix:** Delete these domain-specific templates. Keep only the pure structural templates required for the loops to function.

### 3. Deep Scrub of Remaining Templates
**The Problem:** Even the "kept" structural templates carry OS-level bias. `loop_retrospective_template.md` explicitly mentions "ADR 088" and "Red Team Meta-Audit".
* **The Fix:** Scrub all remaining templates (`strategy-packet-template.md`, `loop_retrospective_template.md`) to remove hardcoded project references, making them true boilerplate templates for any codebase. (Note: The four-question "Red Team Meta-Audit" section structure itself is domain-neutral and generically valuable, so it is kept—only the "ADR 088" reference is replaced with a generic placeholder).

### 4. `cli-agent-executor.md` Persona Hardcoding
**The Problem:** `references/cli-agent-executor.md` acts as the routing manual for the CLI execution patterns, but it hardcodes the exact directory structures of the 33 personas being deleted (`.agents/skills/claude-cli-agent/personas/`).
* **The Fix:** Rewrite this reference document. Change the examples from `cat <PERSONA_PROMPT>` to generic examples (e.g., `cat system_prompt.md | claude -p "Analyze" < input.md`).

---

## Boundary Enforcement: Decoupling from the OS

As established in the `agent-agentic-os` simplification plan, the two plugins duplicate concerns. The agreement was:
> *`agent-loops` provides the execution patterns; `agent-agentic-os` adds the eval gate, experiment log, and improvement infrastructure on top.*

**The Current Violations in `agent-loops`:**

1. **`triple-loop-learning` Leakage:** The `triple-loop-learning/SKILL.md` currently references "Friction Aggregation," "Headless Scoring," and "Keep/Discard & L3 Memory". These are OS-level concepts. 
   * **The Fix:** Strip `triple-loop-learning` down to pure execution mechanics (Outer Loop spawns planners, Mid Loop partitions work, Inner Loop executes packets). Remove all references to evals, metrics, and memory persistence. Scrub `eval_runner.py` from dependencies.
2. **`learning-loop` and `dual-loop` Leakage:** Both are heavily contaminated with OS-specific infrastructure. `learning-loop/SKILL.md` explicitly mandates running `python "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/post_run_metrics.py"`, defines "L3 promotion via session-memory-manager", and mandates saving to `context/memory/retrospectives/`. `dual-loop/SKILL.md` mentions `context/kernel.py emit_event`.
   * **The Fix:** Scrub both skills of all `context/`, `session-memory-manager`, and `kernel.py` references. Output should go to the terminal or a generic local file. Memory promotion is left to the calling system.
3. **`orchestrator` Slash-Command Contamination:** The orchestrator explicitly instructs the user to run `/sanctuary-seal` and `/sanctuary-persist`. These are highly opinionated slash commands native only to a specific OS environment.
   * **The Fix:** Rewrite the Orchestrator's handoff protocol to output: *"Execution complete. Please run your environment's standard closure/persistence commands."*

---

## What We Keep (The Core Engines)

The true value of this plugin lies in its Python execution scripts, which are robust and well-designed.

| Component | Role | Verdict |
|-----------|------|---------|
| `swarm_run.py` | The parallel execution engine | **KEEP (High Value)**. Token-efficient batching, rate-limit backoff, and checkpoint resume logic are production-grade. |
| `agent_orchestrator.py` | The dual-loop/sequential engine | **KEEP**. Provides reliable packet generation and verification steps without fragile LLM terminal parsing. |
| `closure_guard.py` | Safety hook | **KEEP AS-IS**. It checks for `closure_done: true` flag and contains zero references to sanctuary/seal. It is already generic. |

---

## System Dependency Map (Execution Boundaries)

To prevent future scope creep, enforce these system boundaries:

| Primitive | Triggered By | Generates | Dependency Constraints |
|-----------|-------------|-----------|------------------------|
| **learning-loop** | User / Orchestrator | Synthesis Docs | Zero external dependencies |
| **dual-loop** | User / Orchestrator | Handoff & Results | Requires `agent_orchestrator.py` |
| **agent-swarm** | User / Orchestrator | Parallel execution | Requires `swarm_run.py` |
| **triple-loop** | `agent-agentic-os` | 3-tier execution | **MUST NOT** perform evaluations |

---

## The Actual Before/After

### Before (Current State)
* 121 files, massive 114k+ token footprint.
* Acts as an orchestration engine AND a marketplace for 33 specialized developer personas.
* Opinionated templates enforce specific documentation styles and external domain concepts.
* Heavy OS-leakage across skills (`triple-loop-learning`, `learning-loop`, `dual-loop`, `orchestrator`, `closure_guard.py`) dictating memory and evaluation.

### After (Proposed)
* ~30 files, extremely lightweight and fast to load into context.
* Purely an execution library (Single, Sequential, Parallel, Review, Hierarchical).
* Personas are decoupled, allowing users to plug in their own system prompts.
* Clean boundary: `agent-loops` runs the loop; `agent-agentic-os` evaluates the result.

---

## Execution Priority

**Phase 1: Extraction & Pruning (Immediate)**
1. Delete the entire `plugins/agent-loops/personas/` directory. 
2. Delete highly opinionated domain templates (`learning_audit_template.md`, `sources_template.md`).
3. Scrub remaining templates (`loop_retrospective_template.md`): keep the Meta-Audit section structure, but replace "ADR 088" with a generic placeholder.
4. Verify `plugin.json` (already clean in v2.0.0, no persona keywords present). Bump version to 2.1.0 to signal architectural cleanup boundary.
5. In `red-team-review/SKILL.md`, update dependencies to state adversarial persona prompt is "user-supplied or from installed CLI agent plugin".

**Phase 2: Architecture Realignment (Decoupling from the OS)**
6. In `learning-loop/SKILL.md`: Fix two broken cross-references (`triple-loop` -> `triple-loop-learning` and `../triple-loop/SKILL.md` -> `../triple-loop-learning/SKILL.md`).
7. In `learning-loop/SKILL.md` and `dual-loop/SKILL.md`: remove all references to `session-memory-manager`, `kernel.py`, and `post_run_metrics.py`. Replace Phases V-VIII in learning-loop with the framework-agnostic close protocol found in `references/phases.md`.
8. In `triple-loop-learning/SKILL.md`: Remove OS terminology (L3 memory, Keep/Discard gates). Scrub `eval_runner.py` from dependencies with a note that the eval gate belongs to the calling system.
9. In `orchestrator/SKILL.md`: remove specific slash commands (`/sanctuary-seal`, `/sanctuary-persist`). Replace with generic handoff: "Please trigger your environment's standard session closure sequence."
10. Rewrite `references/cli-agent-executor.md` to remove the persona tables and hardcoded persona file paths.
11. Keep `closure_guard.py` as-is (it is already generic).

**Phase 3: Script Hardening & Evals**
12. In `swarm_run.py` and `agent_orchestrator.py`, ensure the logic fully supports the decoupled architecture. Ensure documentation in `README.md` reflects these scripts as standalone "LEGO bricks."
13. Audit `evals/evals.json` for each of the 5 primitives. Verify all entries use `should_trigger: boolean` schema. Replace any `expected_behavior` entries. Target: ≥ 6 real routing scenarios per primitive (3 true, 3 false).
