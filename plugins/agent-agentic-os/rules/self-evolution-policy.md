---
trigger: always_on
description: Universal rules for agent self-healing, selector repair, and error recovery policies.
globs: ["**/*"]
---

## Self-Evolution & Self-Healing Policy

**Full context and execution protocol -> `<project_root>/.agent/skills/self-evolution/SKILL.md` (if available)**  
**Skill/directory deletion rules -> `<project_root>/.agent/rules/skill-deletion-guard.md` (if available)**

Governs responses when any tool call, subprocess, automation step, selector query, script, workflow, or sub-agent encounters failure or friction. Agents must treat failures as evolution events governed by graph state machines (via [`agent-orchestration:graph-execution`](../plugins/agent-orchestration/skills/graph-execution/SKILL.md) and [`agent-orchestration:select-loop-strategy`](../plugins/agent-orchestration/skills/select-loop-strategy/SKILL.md)) and 3-Layer Filesystem Memory.

---

### The 3 Filesystem Memory Layers

1. **Layer 1: Runtime Context (Lean Procedural Core)**
   - Lean `SKILL.md` files (target <= 100 lines). Loaded strictly on-demand.
   - Raw execution traces and multi-page dossiers are barred during active task execution.
2. **Layer 2: Compounding Wiki Layer (Permanent Knowledge)**
   - Permanent Markdown in `wiki/` and plugin `references/`: playbooks, edge cases, negative constraints, `map-debt.md`, and `evolution-log.md`.
   - **Taxonomy & Confidence Decay:** Entries tagged (`OBSERVED`, `HYPOTHESIS`, `CONFIRMED`, `REJECTED`, `OPEN`). Decays from `CONFIRMED` to `OBSERVED` if unverified for 30 days.
   - **Asymmetric Persistence Rule:** On failure, code mutations roll back, but wiki insights, edge-case findings, and failure logs are NEVER rolled back.
3. **Layer 3: Safe Audit Layer (Append-Only Manifests)**
   - Stored in `.agent/learning/traces/cycle_manifests.jsonl`.
   - Tracked audit log capturing event sequences, hashes, exit codes, and affected paths (no raw terminal text/credentials). Audited via `verify_evolution_receipt.py`.

---

### The 4-Box Automation Gate (Pre-Evolution Qualification)

Before triggering an autonomous self-evolution cycle, all 4 criteria must be satisfied:
1. *Recurring or structural failure?* (Ignore single transient flukes; repeatable errors/gaps qualify).
2. *Objective, programmatic verifier?* (Deterministic test/script returning shell exit code executed directly by controller — never self-reported).
3. *Iteration ceiling?* (Hard limit of max 3 attempts; controller strictly enforces rollback on 3rd failure).
4. *Immutable persistence sink?* (Layer 2 `wiki/` / `map-debt.md` and Layer 3 `cycle_manifests.jsonl` retain learnings regardless of code pass/fail).

---

### Proposal Mode & Verifier Sovereignty Invariants

- **Proposal Mode:** During Stage 1 (`PLAN`), workspace files and configs are strictly read-only. No repo files modified or branches/worktrees spawned until explicit human authorization (`evolution_state.py authorize`).
- **Verifier Sovereignty:** Mutation subject cannot modify the acceptance gate. Immutable base protection set (`evaluate.py`, `eval_runner.py`, tests, holdout sets, baselines, policies) and declared verifiers cannot be targeted for mutation. Pre-execution SHA256 hashes are locked; modifications abort cycle with exit code 2. Verifier command must run directly in isolated worktree.

---

### Hard Gates & Non-Negotiables (always active)

1. **Verify Edit Boundaries First**: Check permitted edit boundaries before making autonomous repairs. Escalate immediately if repairs require edits outside allowed boundaries.
2. **Three-Attempt Maximum**: Max 3 repair attempts. If the 3rd fails, hard stop and present Escalation Template with evidence bundle.
3. **Update The Map, Not Just the Diary**: Every fix must update domain playbooks, rules, or references. Log `Status: RESOLVED` in `map-debt.md` for every Tier 0-3 friction event even when patched immediately. Dual-log to `references/evolution-log.md` and `cycle_manifests.jsonl`.
4. **Autonomy & Permission Gates**:
   - **Auto-approved**: New functions/exports, fallback routines/selectors, appending diffs for modified functions.
   - **Confirmation Gated**: Renaming or moving files.
   - **Hard Gated (Requires explicit human permission)**: Deletions of any file, function, skill, rule, manifest, eval, or reference.
   - Composes with `graph-planning-superpowers-policy.md`'s Supreme Law Human Gate.
5. **The Absorption Fallacy - always wrong**: Never conclude an asset is "redundant", "consolidated", or "superseded" and delete it autonomously. Flag overlap; never delete.
6. **One Logical Fix at a Time**: Apply one clean fix per execution pass; never bundle independent repairs.
7. **Fix Forward, Never Skip**: Fix failures at source immediately and update rules/playbooks. Never skip, work around, or add blind retries.
8. **Synchronize Templates on Rule/Strategy Changes**: Update matching templates, generator configs, and prompts when core rules or strategies change.
9. **Refine Prompt Templates on Ingesting Outputs**: Evaluate external model outputs and update prompt templates to guard against observed gaps.
10. **Synchronize Manifests & Reinstall Cleanly on Deletion**: Remove deleted assets from `symlinks.json` and reinstall via `plugin_add.py <plugin-path> -y`.
11. **Pre-Deletion Git History Check**: Run `git log --follow -- <file>` before proposing any file deletion.
12. **Hub First, Spoke Second**: New skill assets must land in plugin root (`plugins/<plugin>/scripts/`, etc.) and symlink into skill folders via `symlink_manager.py` (ADR-002/003). Run `audit_plugin_structure.py`.
13. **Asymmetric Persistence via Worktree Transfer**: On 3rd attempt failure in isolated worktree, roll back code, but export Layer 2 insights, negative constraints, and debt records to main checkout before worktree teardown.
14. **Evolution Integrity Receipts**: Autonomous evolution commits require a programmatic pre-commit receipt (`EVO-INTEGRITY-<cycle_id>-<hash>`) binding staged tree, verifier exit code, and trace manifest.

---

### Friction-Driven Self-Evolution & Tiers

A self-evolution event is required when a script/eval/tool fails, an existing capability is bypassed/manually replaced, workarounds are used, or repeatable process issues arise. Task success does not waive this.

- **Tier 0 (Friction/Workaround)**: Bypassed capability or used workaround. Patch now + update map + log `Status: RESOLVED` in `map-debt.md` if small/safe; record `Status: OPEN` in `map-debt.md` if unsafe/deferred; escalate if repeated/blocking.
- **Tier 1 (Gap)**: Missing capability (build missing piece).
- **Tier 2 (Failure)**: Existing capability broken/errors (patch minimal code, save logs).
- **Tier 3 (Regression)**: External change broke working behavior (collect evidence, patch primary + fallback).

**No Silent Bypass Rule:** Agents must use intended capabilities. Workarounds are permitted only after recording the failure as a self-evolution event.

---

### Pre-Completion Self-Evolution Gate

Before claiming a task is complete, output this block verbatim:

```
PRE-COMPLETION GATE:
  Capability check: Did I verify whether an existing repo capability was intended for this task? [YES/NO]
  1. Did any existing capability fail, get bypassed, or get manually replaced?  [YES/NO - 1 line if YES]
  2. Did I guess, assume, or get corrected on a repeatable process?              [YES/NO - 1 line if YES]
  3. Did I notice something the next agent will hit again if not fixed?          [YES/NO - 1 line if YES]

If any YES: action taken -> FIX / MAP_DEBT / ESCALATE
```

The block must be emitted as literal text. The task is not complete until every YES has a declared action.

---

### Map Debt Management

If friction cannot be fixed immediately, record it as Map Debt in `<project_root>/references/map-debt.md` (mutable queue, separate from append-only evolution log).

Each entry must include: Logged date (`YYYY-MM-DD`), Cycle/Session ID, Artifact affected, Friction observed, Why not fixed now, Recommended fix, Evidence/repro, Severity (`S`/`M`/`L`), Repeat (`YES`/`NO`), Status (`OPEN`/`RESOLVED`/`ESCALATED`).

- **Aging rule:** If `OPEN` entry is older than 3 execution cycles or 14 days, auto-escalate before starting new work.
- **Repeat = YES:** Must escalate on next encounter — no further deferral permitted.
