# SME Orchestrator (Option 1.5): Detailed Implementation Plan

## Objective
Refactor the **Exploration Cycle Plugin** (`agent-plugins-skills/plugins/exploration-cycle-plugin`) to implement the "Dashboard Pattern." This pattern borrows the mechanical rigor and reproducible state-tracking of the `superpowers` framework but rewrites the taxonomy exclusively for Business Area Experts (SMEs).

The goal is to force the LLM orchestrator to follow a deterministic 4-phase loop, maintaining state via a markdown dashboard, and explicitly pausing for SME approval at every gate.

---

## 1. The Core Mechanism: The Exploration Dashboard
We will introduce a new artifact into the SME's workspace: `exploration-dashboard.md`. 
Just as `superpowers` uses a `todo.md` or `tasks.md` to keep the agent grounded, the `exploration-workflow` skill will be responsible for creating and updating this dashboard.

### Example Dashboard Structure:
```markdown
# Business Exploration Dashboard

**Current Phase:** [Phase 1 / Phase 2 / Phase 3 / Phase 4]
**Status:** [Pending / In Progress / Waiting for Approval / Completed]

## The 4-Phase SME Loop

- [ ] **Phase 1: Problem Framing** (Skill: `discovery-planning`)
  - Status: Establish context, ask clarifying questions, secure BRD/Brief approval.
- [ ] **Phase 2: Visual Blueprinting** (Skill: `visual-companion`)
  - Status: Map the structural layout of the solution before building.
- [ ] **Phase 3: Prototyping** (Skill: `subagent-driven-prototyping`)
  - Status: Construct the tangible UI/artifact based on the blueprint.
- [ ] **Phase 4: Handoff & Specs** (Skill: `exploration-handoff`)
  - Status: Bundle requirements, user stories, and prototypes for Opportunity 4 Engineering.
```

---

## 2. Refactoring `exploration-workflow` (The Orchestrator Skill)
The primary entry point for the SME will be the `exploration-workflow` skill. We will rewrite its `SKILL.md` to act as the rigid state machine.

### Key Prompt/Logic Updates for `exploration-workflow`:
1. **Bootstrapping:** When invoked, the first action must be to check for `exploration-dashboard.md`. If it doesn't exist, scaffold it.
2. **State Reading:** Read the dashboard to determine the active phase.
3. **Skill Routing:** Depending on the incomplete phase, immediately instruct the agent to utilize the corresponding specialized skill:
   - If Phase 1 is empty, invoke `discovery-planning`.
   - If Phase 1 is complete, invoke `visual-companion` for Phase 2.
4. **The Hard-Gate (Approval):** Introduce `<HARD-GATE>` XML tags in the prompt: *Do not advance to the next Phase or check the box until the SME explicitly types "Approve" for the current phase's output.*
5. **Dashboard Updating:** After SME approval, the agent must use the native `Write` tool to check the `[x]` box in the dashboard and update the "Current Phase" before proceeding.

---

## 3. Synchronizing the Child Skills
The specialized skills already exist and are excellent, but they need minor prompt updates to respect the orchestrator.

*   **`discovery-planning`:** Update the terminal state of this skill to tell the agent: *"Once the discovery brief is approved, return to the orchestrator to update the `exploration-dashboard.md`."*
*   **`subagent-driven-prototyping`:** Update the entry point so it expects a handoff from the Visual Blueprinting phase, rather than raw context.
*   **`exploration-handoff`:** Ensure it flags its completion in the dashboard, marking the formal end of Opportunity 3 and prompting the user to transition to Opportunity 4.

---

## 4. Execution Steps for the Claude Sonnet 4.6 Session
When executing this plan via the `superpowers` framework, the agent should follow this sequence:
1. **Explore Context:** Read the existing `exploration-cycle-plugin` directory.
2. **Draft the Dashboard Template:** Create the markdown structure for `exploration-dashboard.md` within the plugin's `assets/` or `templates/` folder.
3. **Rewrite `SKILL.md`:** Overhaul `skills/exploration-workflow/SKILL.md` to implement the state-machine rules and routing logic described above.
4. **Update Child Skills:** Apply the minor terminal-state updates to `discovery-planning`, `visual-companion`, and `subagent-driven-prototyping`.
5. **Clean Up:** Remove any outdated Python dispatcher scripts (`execute.py`) in `exploration-orchestrator` that conflict with this new conversational dashboard pattern.
