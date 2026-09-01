---
trigger: always_on
description: Universal rules for agent self-healing, selector repair, and error recovery policies.
globs: ["**/*"]
---

## Self-Evolution & Self-Healing Policy

**Full context and execution protocol -> `<project_root>/.agent/skills/self-evolution/SKILL.md` (if available)**  
**Skill/directory deletion rules -> `<project_root>/.agent/rules/skill-deletion-guard.md` (if available)**

This policy governs how agents must respond when a tool call, subprocess, web automation step, selector query, script, workflow, or sub-agent execution encounters failure or friction. Rather than just retrying or patching silently, the agent must treat failures and workarounds as evolution events governed by deterministic graph state machines (orchestrated via [`agent-orchestration:graph-execution`](../../agent-orchestration/skills/graph-execution/SKILL.md) and classified via [`agent-orchestration:select-loop-strategy`](../../agent-orchestration/skills/select-loop-strategy/SKILL.md)) and a zero-dependency 3-Layer Filesystem Memory.

---

### The 3 Filesystem Memory Layers

1. **Layer 1: Runtime Context (Lean Procedural Core)**
   - Lean `SKILL.md` files (target <= 100 lines). Loaded strictly on-demand.
   - **Inference Restriction:** Historical raw execution traces and multi-page wiki dossiers are barred during active task execution to eliminate context window bloat.
2. **Layer 2: Compounding Wiki Layer (Permanent Knowledge)**
   - Permanent Markdown documents stored in `wiki/` and plugin `references/`.
   - Contains: domain playbooks, known edge cases, negative constraints, `map-debt.md`, and `evolution-log.md`.
   - **Knowledge Status Taxonomy:** Entries are tagged with explicit confidence (`OBSERVED`, `HYPOTHESIS`, `CONFIRMED`, `REJECTED`, `OPEN`).
   - **Confidence Decay:** Knowledge not re-verified within 30 days decays from `CONFIRMED` to `OBSERVED`.
   - **Asymmetric Persistence Rule:** When an evolution attempt fails, code mutations roll back, but wiki insights, edge-case discoveries, and failure logs are NEVER rolled back.
3. **Layer 3: Safe Audit Layer (Append-Only Manifests)**
   - Stored in `.agent/learning/traces/cycle_manifests.jsonl`.
   - Tracked audit log capturing event sequences, hashes, exit codes, and affected paths (zero raw terminal text or credentials).
   - Audited exclusively via `verify_evolution_receipt.py`.

---

### The 4-Box Automation Gate (Pre-Evolution Qualification)

Before an agent triggers an autonomous self-evolution cycle, all 4 qualification criteria must be satisfied:
1. *Is the failure recurring or structural?* (Single transient flukes are ignored; repeatable errors or capability gaps qualify).
2. *Is there an objective, programmatic verifier?* (A deterministic test command, script, or evaluator returning a shell exit code, executed directly by the controller — never self-reported).
3. *Is there an iteration ceiling?* (Hard machine-enforced limit of maximum 3 attempts; controller strictly rejects retries beyond attempt 3 and forces rollback).
4. *Is there an immutable persistence sink?* (Layer 2 `wiki/` / `map-debt.md` and Layer 3 `cycle_manifests.jsonl` to guarantee learnings are retained regardless of code pass/fail).

---

### Proposal Mode Invariant

During Stage 1 (`PLAN`), repository workspace files and configuration are strictly read-only. The controller may record internal planning state (`.agent/learning/evolution_state.json`), but no repository files may be created or modified, and no git branches or worktrees may be spawned until explicit human authorization is granted (`evolution_state.py authorize`).

---

### Verifier Sovereignty Invariant

The mutation subject cannot control or modify the gate that determines whether the mutation is accepted.
The controller enforces that an immutable base protection set (`evaluate.py`, `eval_runner.py`, test definitions, holdout sets, baseline results, and policy files) plus any manifest-declared verifier files cannot be targeted for mutation. Pre-execution SHA256 hashes of verifier machinery are locked; any modification aborts the cycle immediately with integrity exit code 2. The verifier command must be directly executed by the controller inside the isolated worktree, never accepted via caller self-report.

---

### Hard Gates & Non-Negotiables (always active)

1. **Verify Edit Boundaries First**: Before making any autonomous edits to repair a failure or friction, check the permitted edit boundaries (e.g., `<project_root>/` or designated module directories). If a repair requires modifying code outside these directories, **escalate to the user immediately** - do not ask for forgiveness.
2. **Three-Attempt Maximum**: Do not loop or retry a failing repair silently. Attempt to fix a problem up to **three times**. If the third attempt fails, **hard stop** and present the formal Escalation Template to the user with the evidence bundle.
3. **Update The Map, Not Just the Diary**: Every fix must update the relevant domain playbooks, rules, or reference files (`<project_root>/docs/` or `<project_root>/references/`). A fix that is not recorded is a future regression. Log the evolution step in your history logs with the exact target, action, and outcome. **This includes fixes applied immediately, not just deferred ones** - add a `Status: RESOLVED` entry to `map-debt.md` for every Tier 0-3 friction event, even when patched in the same turn. Dual-log to `references/evolution-log.md` alongside `.agent/learning/traces/cycle_manifests.jsonl`.
4. **Autonomy & Permission Gates**:
   - **Auto-approved**: Adding new functions/exports, fallback routines/selectors, and appending diffs for modified functions.
   - **Explicit Confirmation Gated**: Renaming or moving files.
   - **Hard Gated - always requires explicit human permission**: Deletions of any file, function, skill, rules, manifest, eval, or reference. See `skill-deletion-guard.md` if available.
   - These gates compose with, not substitute for, `graph-planning-superpowers-policy.md`'s "SUPREME LAW: HUMAN GATE" - that policy governs state-changing execution generally (code writes, commits, external commands); this section governs the specific autonomy tiers for *self-repair* actions within that broader gate.
5. **The Absorption Fallacy - always wrong**: Concluding that a skill, rule, file, or directory is "redundant", "absorbed", "consolidated", or "superseded" and deleting it autonomously. Overlap is never evidence that deletion is safe. Flag it; never act on it.
6. **One Logical Fix at a Time**: Apply one clean fix per execution pass. Never bundle multiple independent repairs or refactoring changes together.
7. **Fix Forward, Never Skip**: When a tool, script, sub-agent, or automation step fails or hits friction, fix it at the source immediately and update the relevant playbook or rules. Do NOT work around failures, add retries without understanding the root cause, or leave the fix for later.
8. **Synchronize Templates on Core Rule or Strategy Changes**: Whenever core project rules, target schemas, configurations, or strategies are modified, immediately update matching template files, generator configurations, or prompt files to verify they align with the updated standards.
9. **Refine Prompt Templates on Ingesting Model Outputs**: Every time you ingest and process responses from external models or APIs, evaluate their quality and immediately update template or prompt files to guard against observed deficiencies.
10. **Synchronize Manifests & Reinstall Cleanly on Decommissioning/Deletion**: Whenever a skill, file, reference, or plugin is decommissioned, renamed, or deleted, immediately audit and remove entries from `symlinks.json`, then execute `plugin_add.py <plugin-path> -y`.
11. **Pre-Deletion Git History Check - Mandatory**: Before proposing or executing any file deletion, run `git log --follow -- <file>`. Never assume a file is safe to delete because of its extension, name, or apparent disuse.
12. **New Skill Files Must Land in the Hub, Not the Spoke - Mandatory**: When creating a new script, template, or asset file for a skill, write it to the plugin root first (`plugins/<plugin>/scripts/`, `plugins/<plugin>/assets/`) and symlink it into `skills/<skill>/...` via `symlink_manager.py` (ADR-002/ADR-003). Run `audit_plugin_structure.py <plugin>` before considering complete.
13. **Asymmetric Persistence via Worktree Transfer**: During worktree-isolated repairs, if verification fails on the 3rd attempt, code branches are rolled back and temporary worktrees deleted, but Layer 2 failure insights, negative constraints, and debt records MUST be exported to the main repository checkout before worktree teardown.
14. **Evolution Integrity Receipts**: All code commits resulting from autonomous self-evolution require a programmatic pre-commit receipt (`EVO-INTEGRITY-<cycle_id>-<hash>`) binding the staged git tree, verifier exit code, and trace manifest.
15. **Single Source of Truth Verification First — Mandatory**: Before making any assertional recommendation, analytical classification, or lifecycle status assignment on an entity (such as portfolio holding vs. watchlist, active position vs. unheld), the agent MUST verify live state against the canonical domain database/ledger first. Guessing state, assuming defaults without verification, or fabricating entity status is a strict protocol violation.
16. **In-Situ Evolution (The Stairclimber Flywheel) — Mandatory**: Self-evolution is not an isolated offline exercise or a separate chore. It occurs *in-situ* during normal product tasks. When performing routine work, any friction, missing CLI flag, or broken selector must be resolved at the shared tool/script/skill layer immediately as part of fulfilling the user request. Every user task must leave the underlying repository capabilities strictly better equipped than when the turn began.

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
    - If the fix is small + inside allowed edit boundaries: patch it now, update The Map (rules/docs), **and log a `Status: RESOLVED` entry in `map-debt.md`** - resolved fixes still count.
    - If the fix is not safe or not small: record **Map Debt** in the designated register (`map-debt.md`) as `Status: OPEN` and log the event.
    - If friction is repeated/blocking: escalate to the user.
- **Tier 1 (Gap)**: Capability does not exist yet (build missing piece, no evidence needed).
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
  1. Did any existing capability fail, get bypassed, or get manually replaced?  [YES/NO - 1 line if YES]
  2. Did I guess, assume, or get corrected on a repeatable process?              [YES/NO - 1 line if YES]
  3. Did I notice something the next agent will hit again if not fixed?          [YES/NO - 1 line if YES]

If any YES: action taken -> FIX / MAP_DEBT / ESCALATE
```

The block must be emitted as literal text, not silent introspection. The task is not complete until every YES has a declared action.

---

### Map Debt

If friction is real but cannot be fixed immediately, record it as Map Debt.

Map Debt lives in a project-level designated debt file (e.g., `<project_root>/references/map-debt.md` or `.agent/map-debt.md`) - a working queue separate from the evolution log. The evolution log is append-only audit history. Map Debt is mutable: entries are resolved, aged, or escalated over time. Do not conflate the two.

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
**Repeat = YES:** must escalate on next encounter - no further deferral permitted.
