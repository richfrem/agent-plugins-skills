---
concept: the-exploration-cycle-plugin-democratizing-discovery
source: plugin-code
source_file: exploration-cycle-plugin/assets/resources/design-thinking/03-Exploration-and-Design/dashboard-pattern-refactor/exploration-cycle-companion.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.570033+00:00
cluster: phase
content_hash: b9fc79f17a79d583
---

# The Exploration Cycle Plugin: Democratizing Discovery

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# The Exploration Cycle Plugin: Democratizing Discovery

While developer-centric harnesses like `superpowers` excel at driving engineering specs into code (Opportunity 4), they fall short in Opportunity 3. They are built for IT professionals—exposing Git logic, subagent dispatch logs, and test-driven development phases to the user. Furthermore, they typically stop at structural wireframes and technical specification documents.

True democratization requires abstracting that technical workflow away and elevating the output accurately for the business. To successfully implement Opportunity 3 for a non-technical Subject Matter Expert (SME), we rely on the **Exploration Cycle Plugin**.

## Filling the Gaps with the Dashboard Pattern

The Exploration Cycle Plugin is designed explicitly to fill the gaps left by developer-oriented tools, utilizing a custom "Dashboard Pattern" to ensure success:

1. **The Target Persona:** The entire workflow is fronted by friendly, conversational orchestration. The SME experiences a doc-coauthoring session guided by a "Business Analyst in a Box," never seeing a command line or subagent execution log.
2. **Deterministic, Reproducible Rigor (The Option 1.5 Pattern):** Instead of just hoping the LLM figures out what to do next, the plugin aggressively borrows the mechanical rigor of `superpowers`. It maintains a rigid `exploration-dashboard.md` state machine in the workspace. The SME is guided deterministically through a strict 4-Phase loop, with explicit `<HARD-GATE>` pauses requiring human approval before advancing.
3. **Runnable, Full Prototypes:** Wireframes are insufficient for BAEs who need to validate process flows. The `subagent-driven-prototyping` skill explicitly breaks past static wireframes to generate **runnable, interactive software prototypes** so the SME can click through and validate the exact future state.
4. **Translating the Mechanics:** We use the exact same highly effective subagent execution trees that developers use, but we translate the vernacular. Instead of formal *subagent-driven-development*, the plugin orchestrates **subagent-driven-prototyping**. The internal engine still spins up isolated worktrees, writes tests, and iterates—but it refers to this simply as "building your prototype sandbox", ensuring the SME isn't alienated by developer jargon.

---

## The Capability Tooling (The 4-Phase SME Loop)

The plugin does not allow the AI to wander chaotically. It operates on a rigidly enforced **4-Phase Dashboard Pattern**:

### Phase 1: Problem Framing
Before a single line of prototype code is written, the orchestrator invokes `discovery-planning`. This acts as the Product Owner. It establishes the context, asks clarifying questions one at a time, and secures approval on a formal Discovery Brief. The agent checks off Phase 1 in the dashboard and requests approval to proceed.

### Phase 2: Visual Blueprinting
The orchestrator invokes the `visual-companion` to quickly render structural visual layouts in a browser. This validates the SME's structural intent (the "Wireframer" step) before committing expensive agentic compute to building logic.

### Phase 3: Prototyping
Moving past static wireframes. The `subagent-driven-prototyping` skill generates a functional, interactive software prototype. The agent acts actively questions the SME's assumptions ("Who approves this? What happens if it fails?").

### Phase 4: Handoff & Specs
Finally, the `exploration-handoff` skill acts as the architectural spec writer. It translates the agreed-upon prototype flow into Agile `user-story-capture` formats, rules ledgers, and developer-ready JSON/Markdown contracts.

---

## The Key Takeaway

If `superpowers` forces the human to act like an Engineering Manager, the **Exploration Cycle Plugin** allows the human to act like a Business Stakeholder. The non-technical SME simply talks through their problem, tests the generated prototype, and approves the handoff at each dashboard gate. The massive compl

*(content truncated)*

## See Also

- [[agent-execution-prompt-exploration-cycle-plugin-upgrade]]
- [[exploration-cycle-plugin-design-recommendation]]
- [[exploration-cycle-plugin-upgrade-implementation-plan]]
- [[exploration-cycle-plugin-architecture-reference]]
- [[copilot-proposer-prompt-exploration-cycle-plugin]]
- [[optimization-program-exploration-cycle-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/assets/resources/design-thinking/03-Exploration-and-Design/dashboard-pattern-refactor/exploration-cycle-companion.md`
- **Indexed:** 2026-04-17T06:42:09.570033+00:00
