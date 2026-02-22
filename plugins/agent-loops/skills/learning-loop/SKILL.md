---
name: learning-loop
description: "Self-directed research and knowledge capture loop. Use when: starting a session (Orientation), performing research (Synthesis), or closing a session (Seal, Persist, Retrospective). Ensures knowledge survives across isolated agent sessions."
---

# Learning Loop

The Learning Loop is a structured cognitive continuity protocol ensuring that knowledge survives across isolated agent sessions. It is designed to be universally applicable to any agent framework.

## CRITICAL: Anti-Simulation Rules

> **YOU MUST ACTUALLY PERFORM THE STEPS LISTED BELOW.**
> Describing what you "would do", summarizing expected output, or marking
> a step complete without actually doing the work is a **PROTOCOL VIOLATION**.
>
> **Closure is NOT optional.** If the user says "end session" or you are
> wrapping up, you MUST run the full closure sequence. Skipping any step means the next agent starts blind.

---

## The Iron Chain

> **Prerequisite**: You must establish a valid session context upon Wakeup before modifying any code.

```
Orientation → Synthesis → Strategic Gate → Red Team Audit → [Execution] → Seal → Persist → Retrospective → Closure
```

---

### Phase I: Orientation (The Scout)

> **Goal**: Establish Identity & Context.
> **Trigger**: First action upon environment initialization.

1.  **Identity Check**: Read any local `cognitive_primer.md` or orientation documents provided by the user's environment.
2.  **Context Loading**: Retrieve the historical session state (the "Cognitive Hologram" or `learning_package_snapshot.md`) to understand what the previous agent accomplished.
3.  **Report Readiness**: Output: "Orientation complete. Context loaded. Ready."

**STOP**: Do NOT proceed to work until you have completed Phase I.

---

### Phase II: Intelligence Synthesis

1.  **Mode Selection**: Decide if you are doing standard documentation (recording ADRs) or exploratory research.
2.  **Synthesis**: Perform your research. Aggregate findings into clear, modular markdown files in the project's designated `learning/` or `memory/` directory.

### Phase III: Strategic Gate (HITL)

> **Human-in-the-Loop Required**
1.  **Review**: Present architectural findings or strategic shifts to the User.
2.  **Gate**: Wait for explicit "Approved" or "Proceed".
    *   *If FAIL*: Backtrack to Phase VIII (Self-Correction).

### Phase IV: Red Team Audit

1.  **Bundle Context**: Compile your proposed plans into a single, cohesive research packet.
2.  **Action**: Submit the packet to the User (or a designated Red Team adversarial sub-agent) for rigorous critique.
3.  **Gate**: Do not proceed to execution until the Audit returns a "Ready" verdict.

### Execution Branch (Post-Audit)

> **Choose your Execution Mode:**

**Option A: Standard Agent (Single Loop)**
*   **Action**: You write the code, run tests, and verify yourself.

**Option B: Dual Loop**
*   **Action**: Delegate execution to a scoped, isolated Inner Loop agent.
*   **Command**: Open the `dual-loop` SKILL. Execute according to its instructions.
*   **Return**: Once Inner Loop finishes, resume here at **Phase V (Synthesis)**.

---

## Session Close (MANDATORY — DO NOT SKIP)

> **This sequence is non-negotiable.** If the user says "done", "wrap up",
> "end session", or similar — you MUST perform these steps IN ORDER.

### Phase V: Sovereign Context Synthesis

> **Automated Summarization**.
1. Synthesize all completed work, modified files, and new protocols into a dense summary.
2. Update the system's "Cognitive Hologram" (`learning_package_snapshot.md` or equivalent state file).

### Phase VI: The Technical Seal

1.  **Action**: Snapshot the state. Verify that the project compiles/tests pass.
2.  **Gate**: The seal must mathematically or logically "PASS" (e.g., zero regression failures).

### Phase VII: Persistence

1.  **Action**: Append your session traces (what you did, why you did it, what failed) into a structured long-term memory log (e.g., `traces.jsonl`).
2.  **Sync**: If applicable, push these memory traces to a remote vector database or registry.

### Phase VIII: Self-Correction (Retrospective)

1.  **Action**: Analyze what went well/poorly during this specific session.
2.  **Document**: Write a short retrospective markdown file so the next agent learns from your mistakes.

### Phase IX: Closure

1.  **Version Control**: Sync to remote (e.g., `git add . && git commit && git push`).
2.  **End**: Declare the session complete.

---

## Phase Reference

| Phase | Name | Action Required |
|-------|------|-----------------|
| I | Orientation | Load context and assert readiness |
| II | Synthesis | Create/modify research artifacts |
| III | Strategic Gate | Obtain "Proceed" from User |
| IV | Red Team Audit | Compile packet for adversary review |
| V | Context Synthesis | Generate macro-summary of session |
| VI | Seal | Verify compilation/tests pass |
| VII | Persist | Append session logic to memory traces |
| VIII | Self-Correction | Document failures and lessons learned |
| IX | Closure | Commit and sync to remote |

---

## Task Tracking Rules

> **You are not "done" until the active task tracker says you're done.**

- Always use the user's preferred task tracking system (e.g., markdown kanbans, automated CLIs) to move tasks.
- **NEVER** mark a task `done` without running its verification sequence first.
- If using a markdown board, always display the updated board to the user to confirm the move registered.

---

## Dual-Loop Integration

When a Learning Loop runs inside a Dual-Loop session:

| Phase | Dual-Loop Role | Notes |
|-------|---------------|-------|
| I (Orientation) | Outer Loop boots, orients | Reads boot files + spec context |
| II-III (Synthesis/Gate) | Outer Loop plans, user approves | Strategy Packet generated |
| IV (Audit) | Outer Loop snapshots before delegation | Pre-execution checkpoint |
| *(Execution)* | **Inner Loop** performs tactical work | Code-only, isolated |
| *Verification* | Outer Loop inspects Inner Loop output | Validates against criteria |
| V (Context Synthesis) | Outer Loop | Cognitive Hologram generation |
| VI-IX (Seal→Closure) | Outer Loop closure | Standard seal/persist/retro/end |

**Key rule**: The Inner Loop does NOT run Learning Loop phases. All cognitive continuity is the Outer Loop's responsibility.

**Cross-reference**: [dual-loop SKILL](../dual-loop/SKILL.md)
