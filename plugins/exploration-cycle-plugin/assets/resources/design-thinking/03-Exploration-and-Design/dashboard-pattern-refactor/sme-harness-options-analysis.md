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
    *   Requires a dedicated engineering cycle to build and maintain the web portal. High time-to-value.

---

## Strategic Recommendations

My strong recommendation is a **phased approach, starting firmly with Option 1.5 (The Custom Orchestrator Skin)**.

### **Phase 1: Validate with Option 1.5 (The Custom Orchestrator Pattern)**
Do not fork `superpowers` right now. A hard code fork creates a massive legacy debt layer. Instead, we **borrow the mechanical patterns** of `superpowers` (the rigid, deterministic workflow) and bake them directly into our existing plugin.
1. **Implement the Dashboard Pattern:** Update `exploration-workflow` or create a new orchestrator skill that strictly enforces a 4-phase loop (Discovery -> Blueprint -> Prototype -> Handoff).
2. **State Tracking:** Force the sub-agents to maintain an `exploration-dashboard.md` artifact. This ensures the LLM checks off completed phases and explicitly requests SME approval before moving to the next.
3. Give your pilot SMEs a pre-configured VS Code environment. Teach them to invoke Copilot in "Chat" mode with a simple `Start exploration-workflow` trigger. The workflow will hold their hand the rest of the way.

### **Phase 2: Evaluate Option 1 (The Fork) only if friction is too high**
If the SMEs aggressively reject the Copilot/IDE interface due to the latent developer features (terminals, repo trees), *then* evaluate the business-focused fork. However, if Antigravity / Claude Code prove robust enough to hide the complexity when paired with our structured dashboard, the fork is unnecessary overhead.

---

## Next Steps for Execution

If you agree with this recommendation, here are the immediate next steps to execute:

1. **Rewrite `exploration-workflow` (The Dashboard Pattern):** Refactor the outdated orchestrator skills in `agent-plugins-skills/plugins/exploration-cycle-plugin` to establish the new strict SME-facing pipeline. Introduce the `exploration-dashboard.md` state-tracking loop so the agent behaves deterministically.
2. **Complete the Documentation Sync:** Finish the pending edits to `exploration-cycle-companion.md` and the Medium article to explicitly define how this Custom Orchestrator Pattern acts as the universal bridge without requiring a heavy harness fork.
3. **Repository Linking:** Embed direct links and README instructions pointing SMEs to the GitHub repository so they know exactly what framework is powering the conversation.
