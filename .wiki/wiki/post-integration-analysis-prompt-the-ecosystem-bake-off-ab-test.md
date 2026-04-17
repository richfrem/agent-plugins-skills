---
concept: post-integration-analysis-prompt-the-ecosystem-bake-off-ab-test
source: research-docs
source_file: superpowers/deprecation-analysis-prompt.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.463224+00:00
cluster: stack
content_hash: 3e470e317435e607
---

# Post-Integration Analysis Prompt: The Ecosystem Bake-Off (A/B Test)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Post-Integration Analysis Prompt: The Ecosystem Bake-Off (A/B Test)

**Target Agent:** Claude Sonnet (claude-cli)
**Context:** To be executed *after* `feat/superpowers-hybrid-integration` is merged.

---

## Assignment: Design an Empirical A/B Test for Ecosystems

You have successfully completed the 6-phase hybrid integration, importing the core execution disciplines from the `superpowers` repository (TDD, Systematic Debugging, Verification-before-completion, Git Worktrees, Code Review) into our universal `agent-execution-disciplines` plugin. 

This repository now possesses two distinct approaches to managing Agentic workflows:

**Stack A: The Rigid Framework (Spec-Kitty SDD)**
Relying on the `spec-kitty-plugin` and its CLI, this enforces a strict top-down macro-lifecycle: `/spec-kitty.specify` -> `plan` -> `tasks` -> `implement` -> `review` -> `merge`. State is managed via Markdown checklists in Kanban lane directories (`tasks/doing/`, `tasks/review/`).

**Stack B: The Organic Agentic Stack (OS + Exploration + Execution)**
Relying on `agent-agentic-os`, `exploration-cycle-plugin`, and the newly imported `agent-execution-disciplines`. This approach relies on cheap CLI sub-agents for discovery (BRDs, Stories), the robust Python event bus (`kernel.py` / `.locks`) for state persistence, and hard runtime constraints (TDD, verify-before-complete) during execution.

---

### The Objective: Evaluate "What is Actually Better"

The user has explicitly noted that upstream `spec-kitty` / `spec-kit` repositories have historically failed to function consistently or reliably during the execution phase, leading to the creation of the OS layer. However, before we consider deprecating or sidelining Spec-Kitty, we must evaluate both paradigms empirically, side-by-side.

**Your Task:**
Develop a comprehensive test plan (`ecosystem-bake-off-plan.md`) to conduct an empirical A/B test of Stack A versus Stack B. 

Your plan must include:

#### 1. Test Methodology
Define exactly how the side-by-side testing will be conducted. 
- How do we control for agent variability? 
- Will we use identical fresh repositories for each challenge?

#### 2. Evaluation Criteria
Define metrics for success and friction. Examples must include:
- **State Fragility:** Did the agent accidentally break a `.md` Kanban board or a `kernel.py` lock?
- **Execution Quality:** Did the agent hallucinate completion? (Measure activation of `false_completion_claim` events).
- **Overhead:** How many tokens/prompts were burned on administrative paperwork vs. writing actual code?

#### 3. Challenge Scenarios (Simple to Complex)
Design 3 highly specific, scoped coding challenges to run through both stacks. They must be simple enough to iterate on quickly, but complex enough to expose fragility. 
* *Challenge 1 (Simple Fix):* e.g., "Add a new validation rule to an existing Python script with full test coverage."
* *Challenge 2 (New Feature):* e.g., "Build a new standalone utility script that parses CSVs and handles known edge cases."
* *Challenge 3 (State Breakage Test):* e.g., Intentionally interrupt the agent mid-task and ask it to "resume work" to see which state machine recovers better.

#### 4. The Output
Structure the document so that the user can immediately pick "Challenge 1", follow your steps to run it in Stack A and Stack B, and record the results objectively.


## See Also

- [[ecosystem-bake-off-spec-kitty-vs-organic-stack]]
- [[triple-loop-architect-sample-test-prompt]]
- [[strategic-analysis-agent-skills-ecosystem-in-azure]]
- [[recursive-logic-discovery-the-infinite-context-ecosystem]]
- [[strategic-analysis-agent-skills-ecosystem-in-azure]]
- [[strategic-analysis-agent-skills-ecosystem-in-azure]]

## Raw Source

- **Source:** `research-docs`
- **File:** `superpowers/deprecation-analysis-prompt.md`
- **Indexed:** 2026-04-17T06:42:10.463224+00:00
