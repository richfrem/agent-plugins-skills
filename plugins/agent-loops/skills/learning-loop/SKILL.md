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
*   **Command**: Open the `dual-loop` SKILL. Execute according to its instructions.
*   **Return**: Once Inner Loop finishes, resume here at **Phase V (Synthesis)**.

---

## Session Close (MANDATORY — DO NOT SKIP ANY STEP)

> **This loop is now complete.** You must formally exit the loop and return control to the Orchestrator.
> Skipping any close step means the next agent starts blind and the flywheel stalls.

### Phase V: Self-Assessment Survey (MANDATORY)

Before handoff, you MUST complete the Post-Run Self-Assessment Survey
(`references/post_run_survey.md`). Answer every question — do not summarize or skip sections.

Survey sections (all mandatory):

**Run Metadata**: date, task type, task complexity, skill/capability under test

**Completion Outcome**:
- Did you complete the full intended workflow end to end? (Yes/No)
- Did the run require major human rescue? (Yes/No)

**Count-Based Signals (Karpathy Parity)**:
- How many times did you not know what to do next?
- How many times did you miss or skip a required step?
- How many times did you use the wrong CLI syntax?
- How many times were you redirected by a human?
- Total Friction Events

**Qualitative Friction**:
1. At what point were you most uncertain about what to do next?
2. Which instruction, rule, or workflow step felt ambiguous or underspecified?
3. Which command, tool, or template was most confusing in practice?
4. What was the single biggest source of friction in this run?
5. Which failure felt avoidable with a better prompt, skill, or rule?
6. What is the smallest workflow change that would have improved this run the most?

**Improvement Recommendation**:
- What one change should be tested before the next run?
- What evidence from this run supports that change?
- Target (Skill/Prompt/Script/Rule)?

Save completed survey to:
`${CLAUDE_PROJECT_DIR}/context/memory/retrospectives/survey_[YYYYMMDD]_[HHMM]_[AGENT].md`

Emit survey completion event:
```bash
python3 context/kernel.py emit_event --agent os-learning-loop \
  --type learning --action survey_completed \
  --summary "retrospectives/survey_[DATE]_[TIME]_[AGENT].md"
```

### Phase VI: Post-Run Metrics

Run the automated metric collector:
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/post_run_metrics.py"
```

This emits a `type: metric` event capturing: human_interventions, workflow_uncertainty,
missed_steps, cli_errors, friction_events_total, hook_errors. These feed the os-learning-loop
auto-trigger: 3+ friction events of same type = Full Loop improvement before next cycle.

### Phase VII: Memory Persistence

Run `session-memory-manager` to write the dated session log and promote key findings to L3:
- Write `context/memory/YYYY-MM-DD.md` including survey outcomes and metric counts
- Promote architectural decisions and new conventions to `context/memory.md` with dedup IDs
- Reference the survey file in the session log for future cycles to read at orientation

### Phase VIII: Handoff

1.  **Verify Exit Condition**: Confirm research/synthesis acceptance criteria met, survey saved, metrics emitted, memory written.
2.  **Return Data**: Pass synthesized documents and context back up to the Orchestrator.
3.  **Terminate Loop**: Explicitly state "Learning Loop Complete. Survey saved. Metrics emitted. Passing control to Orchestrator."

---

## Phase Reference

| Phase | Name | Action Required |
|-------|------|-----------------|
| I | Orientation | Load context, last survey, last session log |
| II | Synthesis | Create/modify research artifacts |
| III | Strategic Gate | Obtain "Proceed" from User |
| IV | Red Team Audit | Compile packet for adversary review |
| V | Self-Assessment Survey | Answer all sections, save to retrospectives/, emit event |
| VI | Post-Run Metrics | Run post_run_metrics.py, emit metric event |
| VII | Memory Persistence | Session log + L3 promotion via session-memory-manager |
| VIII | Handoff | Return control to Orchestrator |

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
| V (Handoff) | Outer Loop receives results | Triggers global retrospective |

**Key rule**: The Inner Loop does NOT run Learning Loop phases. All cognitive continuity is the Outer Loop's responsibility.

**Cross-reference**: [dual-loop SKILL](../dual-loop/SKILL.md)
