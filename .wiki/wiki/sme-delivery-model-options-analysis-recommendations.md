---
concept: sme-delivery-model-options-analysis-recommendations
source: plugin-code
source_file: exploration-cycle-plugin/assets/resources/design-thinking/03-Exploration-and-Design/dashboard-pattern-refactor/sme-harness-options-analysis.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.570697+00:00
cluster: fork
content_hash: c8eb28b813c730fc
---

# SME Delivery Model: Options Analysis & Recommendations

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# SME Delivery Model: Options Analysis & Recommendations

## Context & The Core Problem
We have successfully built the **Exploration Cycle Plugin** (now hosted at `agent-plugins-skills/tree/main/plugins/exploration-cycle-plugin`). It contains a highly sophisticated suite of SME-focused skills (`discovery-planning`, `visual-companion`, `subagent-driven-prototyping`).

However, the outstanding question is **delivery**: How does a non-technical Business Area Expert (BAE) or Subject Matter Expert (SME) actually *use* these skills seamlessly? Should we fork a heavy engineering harness (like `superpowers`) and rewrite it for the business, or pursue an alternative?

---

## Options Analysis

### Option 1: The Hard Fork (`business-superpowers`)
*Fork the `obra/superpowers` repository, strip out the developer terminology, and replace its engineering skills with our exploration skills.*

*   **Mechanics:** Replace `subagent-driven-development` with `subagent-driven-prototyping`. Replace `planning` logic with `discovery-planning`. Re-write all base system prompts to adopt a "Business Analyst" persona instead of a "Principal Engineer."
*   **Pros:** 
    *   You inherit the incredible mechanical rigor of `superpowers` for free (Phase A/B/C routing, persistence, state management, parallel swarm execution).
    *   It creates a dedicated, standalone repository that guarantees zero "Developer" jargon bleeds into the SME experience.
*   **Cons:** 
    *   **Massive maintenance burden.** Every time upstream `superpowers` improves its subagent routing or tool integration, merging those changes into a heavily refactored "business" fork will be a nightmare.
    *   It breaks the `plugin` model. By forking, the exploration skills become tightly coupled to the fork rather than portable plugins.

### Option 1.5: The Custom Orchestrator Skin (Best of Both Worlds)
*Maintain the plugin architecture, but rebuild the exact step-by-step mechanical rigor of `superpowers` inside our own `exploration-workflow` skill.*

*   **Mechanics:** We don't fork the code, we just copy the *pattern*. We establish a strict 4-phase sequence (Discovery -> Blueprint -> Prototype -> Handoff). The plugin autonomously maintains an `exploration-dashboard.md` in the workspace, forcing the LLM to track state, check off completed tasks, and stop for SME approval exactly like `superpowers` does.
*   **Pros:**
    *   Zero upstream merge debt. We own the logic.
    *   Maintains the clean decoupling of the plugin ecosystem.
    *   Delivers the highly reproducible, deterministic workflow behavior you liked from `superpowers`, but purely in SME taxonomy.
*   **Cons:**
    *   Requires us to build out the dashboard generation and rigid phase-gating prompts.

### Option 2: The Antigravity Plugin Ecosystem (Current Path)
*Deploy the `exploration-cycle-plugin` into Antigravity/Copilot workspaces with basic routing.*

*   **Mechanics:** The SME opens a simplified IDE environment equipped with the plugin. The `exploration-orchestrator` natively manages the workflow.
*   **Pros:** 
    *   Clean separation of Exploration vs Execution.
    *   Easy deployment.
*   **Cons:** 
    *   **Critically lacks structured workflow.** Currently, our plugin relies on the LLM "knowing what to do next." It misses the rigid dashboard-driven phase gates that ensure repeatable success.

### Option 3: The Dedicated Web App Abstraction (Productization)
*Decouple the plugin entirely from the CLI/IDE and mount it behind a custom Next.js/Vite chat interface (an Internal AI Portal).*

*   **Mechanics:** Our exploration skills become backend APIs or MCP parameters. The SME logs into an internal web portal ("The Business Builder"). They chat via browsers; the backend triggers the sub-agents and renders prototypes directly in an iFrame.
*   **Pros:** 
    *   The ultimate form of democratization. Zero tech friction. Absolute safety constraints.
*   **Cons:** 
    *   Requires a dedicated engineering cycle to build an

*(content truncated)*

## See Also

- [[meta-harness-end-to-end-optimization-of-model-harnesses]]
- [[analysis-framework-reference]]
- [[analysis-questions-by-file-type]]
- [[maturity-model-scoring]]
- [[open-recommendations-tracker]]
- [[quantification-enforcement-in-analysis]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/assets/resources/design-thinking/03-Exploration-and-Design/dashboard-pattern-refactor/sme-harness-options-analysis.md`
- **Indexed:** 2026-04-17T06:42:09.570697+00:00
