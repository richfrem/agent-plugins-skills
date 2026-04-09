# Option 1.5: SME Orchestrator Implementation - Copilot Prompt

**Goal:** Execute the architectural refactor of the `exploration-cycle-plugin` using the `superpowers` framework.

Please copy the text below the separator into your new GitHub Copilot Claude Sonnet 4.6 session to kick off the execution safely and mechanically.

---

Hey Claude, we are going to use the `superpowers` plugin installed in this workspace to execute an architectural refactor of a different plugin. 

**Context:** We need to update our `exploration-cycle-plugin` (located at `/Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/exploration-cycle-plugin`) to implement a new custom orchestrator dashboard pattern (which we refer to as "Option 1.5").

**Input Material:** I have prepared a detailed implementation plan that describes exactly what we are building. The path is:
`/Users/richardfremmerlid/Projects/AI-Research/07-Opportunities/03-Exploration-and-Design/dashboard-pattern-refactor/sme-orchestrator-implementation-plan.md`

### Your Instructions:
1. Please start by invoking the `brainstorming` skill (refer to its rules in `superpowers/skills/brainstorming/SKILL.md`). 
2. Use the provided Implementation Plan file as your primary context for the brainstorming phase. Let's rigorously follow the `brainstorming` checklist.
3. Read the codebase in `plugins/exploration-cycle-plugin` to understand the current state of `exploration-workflow`, `discovery-planning`, and the other skills mentioned in the plan.
4. Ask me any clarifying questions ONE at a time.
5. Propose the design spec and present it to me in sections for approval.
6. Once we have a final approved design doc, transition seamlessly to the `writing-plans` skill to generate the implementation steps.
7. Finally, we will use `subagent-driven-development` to execute the changes.

Please begin with Step 1 of the `brainstorming` checklist: Explore the project context and read the implementation plan.
