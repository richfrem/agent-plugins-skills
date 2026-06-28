---
description: Universal rules for agent self-healing, selector repair, and error recovery policies.
globs: ["plugins/**/SKILL.md", "plugins/**/scripts/*.py", "plugins/**/agents/*.md"]
---

## 🌀 Self-Evolution & Self-Healing Policy

**Full execution protocol (Phases 0–7) → `plugins/agent-agentic-os/skills/self-evolution/SKILL.md`**  
**Skill/directory deletion rules → `.agent/rules/skill-deletion-guard.md`**

This policy states the always-on safety gates. They apply before any skill is invoked and
regardless of whether a self-evolution run is in progress.

### Hard Gates (always active)

1. **Edit boundaries first**: Before any autonomous edit, verify the target file is inside
   the plugin's permitted edit directories (`plugins/<plugin>/skills/`, `scripts/`, `references/`).
   If no `self-evolution-profile.md` exists for the plugin, use that conservative default.
   Anything outside those dirs requires explicit user confirmation.

2. **Three-attempt maximum**: Attempt a repair up to three times. On the third failure,
   hard stop and present the Escalation Template with the full evidence bundle.

3. **Update The Map, not just the Diary**: Every fix must update the relevant domain playbook
   or reference file. A fix that is not recorded is a future regression.

4. **Autonomy gates**:
   - Auto-approved: adding new functions/exports, fallback selectors, appending to existing files
   - Explicit confirmation required: renaming or moving any file
   - **Hard gated — always requires explicit human permission**: any deletion of any file,
     function, skill, SKILL.md, eval, or reference. See `skill-deletion-guard.md`.

5. **The Absorption Fallacy — always wrong**: Concluding that a skill, file, or directory is
   "redundant", "absorbed", "consolidated", or "superseded" and deleting it autonomously.
   Overlap is never evidence that deletion is safe. Flag it; never act on it.

6. **One logical change per pass**: Never bundle multiple independent repairs in a single
   execution pass.

---

### Friction-Driven Self-Evolution (always active)

Agents must not silently work around broken, unclear, missing, or awkward repo capabilities.

A self-evolution event is required when **any** of the following occurs:

- A script, helper, command, skill, sub-agent, selector, eval, or documented workflow fails.
- The agent avoids an existing capability and performs the work manually instead.
- The agent uses a workaround because the intended path was broken, unclear, or ambiguous.
- The agent has to guess because instructions, profiles, schemas, or routing are unclear.
- The user corrects the agent on a repeatable process problem.
- The agent notices a missing helper, stale reference, stale agent instruction, or broken skill invocation.

**Successful task completion does not waive this requirement.** If the task succeeded only
because the agent bypassed friction, self-evolution handling is still required.

---

### Tier 0 — Friction / Workaround

> "The task completed, but the system did not improve."

**Signals:**
- Agent bypassed an existing script, skill, sub-agent, or helper
- Agent manually performed work that an existing repo capability should handle
- Agent encountered ambiguity and guessed instead of improving instructions
- Agent noticed an awkward or error-prone workflow but did not update The Map
- Agent used a temporary workaround

**Required response — pick exactly one:**
- Fix is small + inside allowed edit boundaries → patch it now, update The Map.
- Fix is not safe or not small → log as **Map Debt** in the evolution log.
- Friction is repeated or blocking → escalate to the user.

---

### No Silent Bypass Rule

If an existing repo capability is intended for the task, the agent must use it.
If the capability fails, the agent may use a workaround only after recording the failure
as a self-evolution event. Silent bypass is a protocol violation.

---

### Pre-Completion Self-Evolution Gate

Before claiming a task is complete, the agent must answer:

1. Did any script, skill, sub-agent, command, selector, eval, or workflow fail?
2. Did I bypass or avoid an existing capability?
3. Did I use a workaround?
4. Did I guess because repo guidance was unclear?
5. Did the user correct me on a repeatable process issue?
6. Did I notice something that should be fixed for the next run?

If any answer is YES, the agent must do one of:
- Fix the underlying artifact now and update The Map.
- Log unresolved Map Debt with evidence and next action.
- Escalate if outside allowed boundaries.

The task is not complete until this gate is satisfied.

---

### Map Debt

If friction is real but cannot be fixed immediately, record it as Map Debt in the evolution log.

Each Map Debt entry must include:
- Date
- Artifact affected (file path or skill slug)
- Friction observed (one sentence)
- Why it was not fixed now
- Recommended fix
- Evidence or reproduction step
- Severity: S / M / L
- Repeat: YES / NO (repeat = must escalate on next encounter, not defer again)
