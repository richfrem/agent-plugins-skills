---
name: using-exploration-cycle
description: Use when starting any conversation - establishes how to find and follow the business exploration workflow.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent (via dispatch.py) to execute a specific task, skip this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
You are operating with the exploration-cycle-plugin active. 

Before responding to ANY user message (including answering general questions or scoping requests), you MUST verify the state of the active exploration session. If a session is in progress, you DO NOT have a choice: you MUST route execution through the active phase of the exploration-workflow.
</EXTREMELY-IMPORTANT>

## How to Check Session State

Before generating any response:
1. Check if `exploration/exploration-dashboard.md` exists.
2. If it DOES exist:
   - Read the dashboard using the Read tool.
   - Check the `**Status:**` field.
   - If status is `Complete`, the prior session has ended. You may answer normally or offer to start a new exploration.
   - If status is `In Progress` or `TBD`, identify the `**Current Phase:**`.
   - **Immediately yield control to the active phase of the exploration workflow.** Always invoke the `exploration-workflow` skill. Never directly invoke child skills unless authorized by the orchestrator. Do NOT answer the user's question directly in freeform prose.
3. If it DOES NOT exist:
   - If the user's message matches any exploration triggers (e.g. "I want to build...", "Let's explore...", "I have an idea...", "start discovery"), you must bootstrap the session.
   - Invoke the `exploration-workflow` skill to initiate Phase 0 intake.

## State Authority

The SQLite state database and programmatic phase artifacts are the absolute state authority. The markdown dashboard is a read-only projection of the database. Do not rely on conversational chat history to assume a phase is complete or that a gate has been passed.

## Active Verification & Review during Waits

When executing the workflow or waiting for sub-agent execution / task completions:
- Proactively read and review the artifacts produced in earlier phases (such as the discovery plans, visual layouts, and prototype READMEs) to ensure consistency.
- Validate that the current phase's work aligns with the requirements and constraints established in earlier phases.
- Do not remain idle; use any wait time to verify file existences, scan for unresolved placeholders, and check that status mappings are accurate.

