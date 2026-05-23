---
description: Universal rules for agent self-healing, selector repair, and error recovery policies.
globs: ["plugins/**/SKILL.md", "plugins/**/scripts/*.py", "plugins/**/agents/*.md"]
---

## 🌀 Self-Evolution & Self-Healing Policy

**Full context and execution loop → `plugins/agent-agentic-os/skills/self-evolution/SKILL.md`**

This policy governs how agents must respond when a tool call, subprocess, web automation step, or selector query encounters a failure. Rather than just retrying or patching silently, the agent must treat failures as evolution events.

### Non-Negotiables

1. **Verify Edit Boundaries First**: Before making any autonomous edits to repair a failure, check the permitted edit boundaries in `<plugin>/references/self-evolution-profile.md`. If a repair requires modifying code outside these directories, **escalate to the user immediately**—do not ask for forgiveness.
2. **Classify Failures by Tier**: Group all failures into exactly one tier to determine the required action:
   * **Tier 1 (Gap)**: Capability doesn't exist yet (build missing piece, no evidence needed).
   * **Tier 2 (Failure)**: Code exists but is broken or returns errors (patch minimal code, save stack traces).
   * **Tier 3 (Regression)**: External change broke previously working behavior, e.g., stale DOM selectors or API mutations (collect DOM/network/screenshot evidence first, then patch with primary + fallback selector paths).
3. **Three-Attempt Maximum**: Do not loop or retry a failing repair silently. Attempt to fix a problem up to **three times**. If the third attempt fails, **hard stop** and present the formal Escalation Template to the user with the evidence bundle.
4. **Update The Map, Not Just the Diary**: A fix that is not recorded is a future regression waiting to happen. You must:
   * Update the relevant domain playbooks and references (`references/<topic>-playbook.md`) with updated selectors or timing rules.
   * Log the evolution step in `evolution-log.md` with the exact tier, target, and outcome.
5. **Autonomy & Permission Gates**:
   * **Auto-approved**: Adding new functions/exports, fallback selectors, and appending diffs for modified functions.
   * **Explicit Confirmation Gated**: Renaming or moving files.
   * **Hard Gated**: **Deletions of any file or function are strictly forbidden** without explicit human permission.
6. **One Logical Fix at a Time**: Apply one clean fix per execution pass. Never bundle multiple refactoring changes or unrelated patches together.
