---
concept: ecosystem-bake-off-spec-kitty-vs-organic-stack
source: research-docs
source_file: experiments/ecosystem-bake-off/experiment-plan.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.452136+00:00
cluster: agent
content_hash: 845303776137b4ac
---

# Ecosystem Bake-Off: Spec-Kitty vs. Organic Stack

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Ecosystem Bake-Off: Spec-Kitty vs. Organic Stack

**Goal:** Stop architecting in the abstract. Test both workflows side-by-side using a dead-simple, real-world task. Let empirical data (metrics) dictate which stack we keep or deprecate.

---

## The Core Thesis: Transitional Architectures
As we evaluate these ecosystems, we must explicitly acknowledge the reality of the current AI landscape:
1. **We cannot change the underlying Frontier Models.**
2. **We cannot change what the SDKs natively support.**
3. **The landscape changes weekly.** Workflows that were revolutionary six months ago are obsolete today.

Because of these immutable facts, frameworks like `spec-kit`, `spec-kitty`, `superpowers`, and `germes-agent` are fundamentally **Transitional Architectures**. We operate under the working hypothesis that large portions of their core mechanics (like prompt-driven worktree management or manual memory files) will be temporary and eventually replaced by native features.

Therefore, the purpose of this repository is to **strictly decouple business logic (Skills) from the underlying agent usage.** We must not lock our workflows into the proprietary quirks of any single transitional framework. The absolute most critical feature we are testing across any stack is the **Continuous Improvement Loop**—ensuring that decoupling allows our skills, workflows, and agents to organically improve themselves after every run, regardless of what SDK executes them. 

---

## The Challenge: A Trivial Task
**Build a simple Python utility (`parser.py`) that parses a CSV file and calculates the average value of a specific column, handling common errors (missing files, malformed rows).**

*Why so trivial?* We are trying to measure the friction of the **frameworks**, not the intelligence of the model. By keeping the coding task dead simple, any errors, amnesia, or token bloat can be 100% attributed to the overhead of Spec-Kitty or the Organic Stack failing to manage the flow.

## Hypotheses & Predictions
Before running the experiment, here is the architectural prognosis of how these two stacks will behave under stress:

* **Prediction 1 (Overhead):** Spec-Kitty will consume 3x to 5x more tokens and take significantly longer just to start writing code, because its SDD lifecycle forces the generation of `spec.md`, `plan.md`, and `tasks.md` before it touches Python.
* **Prediction 2 (State Breakage):** Spec-Kitty will struggle with Git branching and kanban lane transitions, repeatedly requiring human intervention ("Please merge this"). The Organic Stack will proceed fluidly because it relies on standard TDD loops rather than proprietary CLI commands and file moves.
* **Prediction 3 (Amnesia):** The Organic Stack may lose sight of the "big picture" requirements because it lacks a formal `spec.md`, but it will produce working, tested code faster due to the Superpowers TDD execution rules. Spec-Kitty will produce a beautiful checklist, but the agent will forget to follow it when it actually starts writing `parser.py`.

---

## The Testing Grounds

### Run A: The Rigid Framework (`run-A-spec-kitty/`)
1. CD into `run-A-spec-kitty/`.
2. Initialize `spec-kitty init .`
3. Tell the agent: "Use spec-kitty to build a CSV parsing utility that calculates the average of a column."
4. **Constraint:** The agent *must* follow the rigid Spec-Driven Development lifecycle (specify -> plan -> tasks -> implement -> review -> merge).

### Run B: The Organic Stack (`run-B-organic-stack/`)
1. CD into `run-B-organic-stack/`.
2. Initialize the agentic OS (`python3 kernel.py init` or similar). Ensure the `superpowers` execution skills are loaded.
3. Tell the agent: "Build a CSV parsing utility that calculates the average of a column using strict TDD."
4. **Constraint:** Let the agent govern itself organically with the event bus and execution rules (TDD, verification-before-completion) without a formal Spec-Kitty Kanban board.

---

## Evaluation Rubric (To Record After Runs)

### 

*(content truncated)*

## See Also

- [[post-integration-analysis-prompt-the-ecosystem-bake-off-ab-test]]
- [[identity-the-spec-kitty-agent]]
- [[spec-kitty-setup-sync-orchestrator]]
- [[spec-kitty-workflow-meta-tasks]]
- [[spec-kitty-sync-plugin]]
- [[spec-kitty-workflow]]

## Raw Source

- **Source:** `research-docs`
- **File:** `experiments/ecosystem-bake-off/experiment-plan.md`
- **Indexed:** 2026-04-17T06:42:10.452136+00:00
