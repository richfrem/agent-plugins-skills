---
concept: learning-loop
source: plugin-code
source_file: agent-loops/skills/learning-loop/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.727299+00:00
cluster: agent
content_hash: b37defd33f67c414
---

# Learning Loop

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: learning-loop
description: "(Industry standard: Loop Agent / Single Agent) Primary Use Case: Self-contained research, content generation, and exploration where no inner delegation is required. Self-directed research and knowledge capture loop. Use when: starting a session (Orientation), performing research (Synthesis), or closing a session (Seal, Persist, Retrospective). Ensures knowledge survives across isolated agent sessions."
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

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
Orientation → Synthesis → Strategic Gate → Red Team Audit → [Execution] → Loop Complete (Return to Orchestrator)
```

---

### Phase I: Orientation (The Scout)

> **Goal**: Establish Identity & Context.
> **Trigger**: First action upon environment initialization.

1.  **Identity Check**: Read any local orientation documents or primers provided by the user's environment.
2.  **Context Loading**: Retrieve the historical session state (the "Context Snapshot" or equivalent state file) to understand what the previous agent accomplished.
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
*   **Command**: Open the `triple-loop-learning` SKILL. Execute according to its instructions.
*   **Return**: Once Inner Loop finishes, resume here at **Phase V (Synthesis)**.

---

## Session Close (MANDATORY — DO NOT SKIP ANY STEP)

> **This loop is now complete.** You must formally exit the loop and return control to the Orchestrator.
> Skipping any close step means the next agent starts blind and the flywheel stalls.

### Phase V: Completion & Handoff

> **The specific learning cycle is finished. You must now return co

*(content truncated)*

## See Also

- [[learning-loop-retrospective-post-seal]]
- [[triple-loop-learning-meta-learning-system]]
- [[triple-loop-learning-system-outer-orchestrator-inner-execution]]
- [[agent-harness-learning-layer]]
- [[concurrent-agent-loop]]
- [[dual-loop-innerouter-agent-delegation]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-loops/skills/learning-loop/SKILL.md`
- **Indexed:** 2026-04-27T05:21:03.727299+00:00
