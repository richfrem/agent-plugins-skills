---
trigger: always_on
description: Universal rules for agent self-healing, selector repair, and error recovery policies.
globs: ["**/*"]
---

---
description: Universal rules for agent self-healing, selector repair, and error recovery policies.
globs: ["**/*"]
---

## 🌀 Self-Evolution & Self-Healing Policy

**Full context and execution protocol (Phases 0–7) → `<project_root>/.agent/skills/self-evolution/SKILL.md` (if available)**  
**Skill/directory deletion rules → `<project_root>/.agent/rules/skill-deletion-guard.md` (if available)**

This policy governs how agents must respond when a tool call, subprocess, web automation step, selector query, script, workflow, or sub-agent execution encounters failure or friction. Rather than just retrying or patching silently, the agent must treat failures and workarounds as evolution events to ensure non-friction constant evolution.

---

### Hard Gates & Non-Negotiables (always active)

1. **Verify Edit Boundaries First**: Before making any autonomous edits to repair a failure or friction, check the permitted edit boundaries (e.g., `<project_root>/` or designated module directories). If a repair requires modifying code outside these directories, **escalate to the user immediately**—do not ask for forgiveness.
2. **Three-Attempt Maximum**: Do not loop or retry a failing repair silently. Attempt to fix a problem up to **three times**. If the third attempt fails, **hard stop** and present the formal Escalation Template to the user with the evidence bundle.
3. **Update The Map, Not Just the Diary**: Every fix must update the relevant domain playbooks, rules, or reference files (`<project_root>/docs/` or `<project_root>/references/`). A fix that is not recorded is a future regression. Log the evolution step in your history logs with the exact target, action, and outcome.
4. **Autonomy & Permission Gates**:
   - **Auto-approved**: Adding new functions/exports, fallback routines/selectors, and appending diffs for modified functions.
   - **Explicit Confirmation Gated**: Renaming or moving files.
   - **Hard Gated — always requires explicit human permission**: Deletions of any file, function, skill, rules, manifest, eval, or reference. See `skill-deletion-guard.md` if available.
5. **The Absorption Fallacy — always wrong**: Concluding that a skill, rule, file, or directory is "redundant", "absorbed", "consolidated", or "superseded" and deleting it autonomously. Overlap is never evidence that deletion is safe. Flag it; never act on it.
6. **One Logical Fix at a Time**: Apply one clean fix per execution pass. Never bundle multiple independent repairs or refactoring changes together.
7. **Fix Forward, Never Skip**: When a tool, script, sub-agent, or automation step fails or hits friction, fix it at the source immediately and update the relevant playbook or rules. Do NOT work around failures, add retries without understanding the root cause, or leave the fix for later. Every session must end with the same capabilities working as reliably as they started. The goal is smooth, issue-free runs in every future session — compound the fixes, not the workarounds.
8. **Synchronize Templates on Core Rule or Strategy Changes**: Whenever core project rules, target schemas, configurations, or strategies are modified, immediately update matching template files, generator configurations, or prompt files to verify they align with the updated standards.
9. **Refine Prompt Templates on Ingesting Model Outputs**: Every time you ingest and process responses from external models or APIs, evaluate their quality (checking for lazy placeholders, format violations, or structural errors) and immediately update the template or prompt files to guard against observed deficiencies.
10. **Synchronize Manifests on Decommissioning/Deletion**: Whenever a skill, file, or plugin is decommissioned, renamed, or deleted, immediately audit and remove its entries from the project's central manifests, registers, and configuration maps (such as `symlinks.json`). Leaving orphaned entries in manifests causes automated scripts (like the symlink manager or plugin installer) to recreate deleted directories as untracked files.
11. **Pre-Deletion Git History Check — Mandatory**: Before proposing or executing any file deletion, run `git log --follow -- <file>` to understand the file's history. Before assuming a file is dead, orphaned, or replaced — check whether a `.py` (or equivalent) replacement exists, whether symlinks reference it, and whether its purpose is documented in any prior commit message. **Never assume a file is safe to delete because of its extension, name, or apparent disuse.** Confirm with the user if the history reveals any prior active use or replacement migration.

---

### Friction-Driven Self-Evolution (always active)

Agents must not silently work around broken, unclear, missing, or awkward repository capabilities. A self-evolution event is required when **any** of the following occurs:
- A script, helper, command, skill, sub-agent, selector, eval, or documented workflow fails.
- The agent avoids an existing capability and performs the work manually instead.
- The agent uses a workaround because the intended path was broken, unclear, or ambiguous.
- The agent has to guess because instructions, profiles, schemas, or routing are unclear.
- The user corrects the agent on a repeatable process problem.
- The agent notices a missing helper, stale reference, stale agent instruction, or broken skill invocation.

**Successful task completion does not waive this requirement.** If the task succeeded only because the agent bypassed friction, self-evolution handling is still required.

---

### Failure & Friction Tiers

Group all failures and workarounds into exactly one tier to determine the required action:
- **Tier 0 (Friction/Workaround)**: Bypassed an existing capability or used a temporary workaround.
  * *Required Response (pick one)*:
    - If the fix is small + inside allowed edit boundaries: patch it now, update The Map (rules/docs).
    - If the fix is not safe or not small: record **Map Debt** in the designated register (e.g., `<project_root>/.agent/map-debt.md` or local rules equivalent) and log the event.
    - If friction is repeated/blocking: escalate to the user.
- **Tier 1 (Gap)**: Capability doesn't exist yet (build missing piece, no evidence needed).
- **Tier 2 (Failure)**: Code or script exists but is broken or returns errors (patch minimal code, save logs/stack traces).
- **Tier 3 (Regression)**: External change broke previously working behavior, e.g., stale selectors or API mutations (collect evidence/network/logs first, then patch with primary + fallback paths).

---

### No Silent Bypass Rule

If an existing repo capability is intended for the task, the agent must use it. If the capability fails, the agent may use a workaround only after recording the failure as a self-evolution event. Silent bypass is a protocol violation.

---

### Pre-Completion Self-Evolution Gate

Before claiming a task is complete, output this block verbatim:

```
PRE-COMPLETION GATE:
  Capability check: Did I verify whether an existing repo capability was intended for this task? [YES/NO]
  1. Did any existing capability fail, get bypassed, or get manually replaced?  [YES/NO — 1 line if YES]
  2. Did I guess, assume, or get corrected on a repeatable process?              [YES/NO — 1 line if YES]
  3. Did I notice something the next agent will hit again if not fixed?          [YES/NO — 1 line if YES]

If any YES: action taken → FIX / MAP_DEBT / ESCALATE
```

The block must be emitted as literal text, not silent introspection. The task is not complete until every YES has a declared action.

---

### Map Debt

If friction is real but cannot be fixed immediately, record it as Map Debt.

Map Debt lives in a project-level designated debt file (e.g., `<project_root>/.agent/map-debt.md` or local rules equivalent) — a working queue separate from the evolution log. The evolution log is append-only audit history. Map Debt is mutable: entries are resolved, aged, or escalated over time. Do not conflate the two.

Each Map Debt entry must include:
- Logged date (`YYYY-MM-DD`)
- Cycle/Session ID (if tracked in execution logs)
- Artifact affected (file path, rule, or skill slug)
- Friction observed (one sentence)
- Why it was not fixed now
- Recommended fix
- Evidence or reproduction step
- Severity: S / M / L
- Repeat: YES / NO
- Status: OPEN / RESOLVED / ESCALATED

**Aging rule:** If an `OPEN` entry is older than 3 completed execution cycles or 14 days `(today - Logged) > 14 days`, auto-escalate before starting new work.
**Repeat = YES:** must escalate on next encounter — no further deferral permitted.
