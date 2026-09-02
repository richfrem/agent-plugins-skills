---
trigger: always_on
description: Universal rules for agent self-healing, selector repair, and error recovery policies.
globs: ["**/*"]
---

## Self-Evolution & Self-Healing Policy

**Protocol details -> `<project_root>/.agent/skills/self-evolution/SKILL.md` | Deletions -> `skill-deletion-guard.md`**

When any tool, script, workflow, or sub-agent fails or hits friction, agents must treat it as an evolution event governed by 3-Layer Filesystem Memory rather than silently patching or retrying.

---

### The 3 Filesystem Memory Layers

1. **Layer 1: Runtime Context (Lean Core)**: Lean `SKILL.md` (<=100 lines) loaded on-demand. Raw execution traces barred during task runs.
2. **Layer 2: Compounding Wiki (Permanent Knowledge)**: Documents in `wiki/` and `references/` (`map-debt.md`, `evolution-log.md`).
   - *Status Taxonomy*: `OBSERVED`, `HYPOTHESIS`, `CONFIRMED`, `REJECTED`, `OPEN`. 30-day decay from CONFIRMED -> OBSERVED.
   - *Asymmetric Persistence*: Failed evolution attempts roll back code, but wiki insights, edge cases, and logs are NEVER rolled back.
3. **Layer 3: Safe Audit (Append-Only Manifests)**: `.agent/learning/traces/cycle_manifests.jsonl` verified via `verify_evolution_receipt.py`.

---

### Pre-Evolution Qualification & Invariants

- **4-Box Gate**: (1) Structural/recurring failure, (2) Programmatic exit-code verifier, (3) Max 3 iteration ceiling, (4) Layer 2/3 persistence sink.
- **Proposal Mode**: During `PLAN` stage, workspace files are read-only until explicit human authorization (`evolution_state.py authorize`).
- **Verifier Sovereignty**: Mutation subjects cannot control evaluation gates. Verifier machinery and base policies are SHA256 locked.

---

### Hard Gates & Non-Negotiables

1. **Verify Boundaries First**: Escalate immediately if repairs require modifying files outside permitted boundaries.
2. **Three-Attempt Maximum**: Max 3 attempts per failure. If 3rd fails, stop and present formal Escalation Template.
3. **Update The Map, Not Just the Diary**: Every fix must update domain playbooks/rules (`wiki/` or `references/`). Log a `Status: RESOLVED` entry in `map-debt.md` for every Tier 0-3 friction event even when patched immediately. Dual-log to `references/evolution-log.md`.
4. **Autonomy Gates**: Auto-approve: new functions/selectors. Gated: file renames/moves. **Hard Gated (Human Permission Required)**: deletions of any file, function, rule, or skill.
5. **Absorption Fallacy**: Never delete a file/skill assuming it is 'redundant' or 'consolidated'.
6. **One Fix at a Time**: Apply one clean logical fix per execution pass.
7. **Fix Forward**: Never skip failures, add blind retries, or leave workarounds unaddressed.
8. **Sync Templates & Generators**: Update templates/generators immediately when core rules, schemas, or strategies change.
9. **Refine Prompt Templates**: Evaluate external model outputs and update prompt templates to guard against observed gaps.
10. **Sync Manifests on Decommission**: Remove entries from `symlinks.json` and reinstall via `plugin_add.py`.
11. **Pre-Deletion Git Check**: Always run `git log --follow -- <file>` before proposing deletions.
12. **Hub First, Spoke Second**: New skill assets must land in plugin root and symlink into skill folders via `symlink_manager.py`.
13. **Asymmetric Worktree Transfer**: Export Layer 2 failure insights to main checkout before tearing down failed worktrees.
14. **Integrity Receipts**: Autonomous evolution commits require `EVO-INTEGRITY-<cycle_id>-<hash>`.
15. **Single Source of Truth**: Verify live state against canonical DB/ledger before classifying entity status (e.g. holding vs watchlist).
16. **In-Situ Evolution (Flywheel)**: Resolve friction at shared tool/skill layer immediately during normal user tasks.

---

### Failure Tiers & Silent Bypass

- **No Silent Bypass**: Using manual workarounds without recording a self-evolution event is a protocol violation.
- **Tier 0 (Friction/Workaround)**: Patch small in-boundary fixes immediately and log `Status: RESOLVED` in `map-debt.md`; if unsafe/large, log `Status: OPEN`.
- **Tier 1 (Gap)**: Build missing capability.
- **Tier 2 (Failure)**: Patch broken code, capture stack trace.
- **Tier 3 (Regression)**: External change broke behavior; collect evidence and patch primary + fallback paths.

---

### Pre-Completion Self-Evolution Gate

> [!IMPORTANT]
> **Turn-by-Turn Mandatory Protocol**: On EVERY turn modifying code, running tests, or presenting findings, the agent MUST proactively output this block verbatim before yielding control:

```
PRE-COMPLETION GATE:
  Capability check: Did I verify whether an existing repo capability was intended for this task? [YES/NO]
  1. Did any existing capability fail, get bypassed, or get manually replaced?  [YES/NO - 1 line if YES]
  2. Did I guess, assume, or get corrected on a repeatable process?              [YES/NO - 1 line if YES]
  3. Did I notice something the next agent will hit again if not fixed?          [YES/NO - 1 line if YES]

If any YES: action taken -> FIX / MAP_DEBT / ESCALATE
  [Physical Disk Write Verified: wiki/<playbook>.md (if resolved) or references/map-debt.md]
```

The turn is not complete until every YES is backed by a verified physical disk write to `wiki/` or `references/map-debt.md`.

---

### Map Debt Management

- Lives in `references/map-debt.md` (columns: Logged, Cycle ID, Artifact, Friction, Why not fixed, Recommended fix, Evidence, Severity, Repeat, Status).
- **Aging**: Auto-escalate `OPEN` entries older than 3 cycles or 14 days. If `Repeat = YES`, escalate immediately on next encounter.
