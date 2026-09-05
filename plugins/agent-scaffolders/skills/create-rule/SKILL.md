---
name: create-rule
plugin: agent-scaffolders
description: >
  Scaffolds a lean, invariant-driven agent rule following universal best practices. Enforces
  hard constraints, zero incident post-mortems, zero dates, zero usernames, high information density,
  and strict separation between rules (constraints) and skills (procedures).
argument-hint: "[rule-name or constraint-intent]"
allowed-tools: Bash, Read, Write
---

# create-rule: Universal Agent Rule Scaffolder

Creates lean, invariant-driven markdown rules (`.agent/rules/<rule-name>.md` or `plugins/<plugin>/rules/<rule-name>.md`) adhering to strict agentic engineering standards.

---

## The 5 Invariants of Agent Rules

Rules are loaded into context continuously or matched across file interactions. Every line consumes token budget. Every rule must satisfy:

1. **Strict Invariants, Not Narrative**: State hard constraints (`MUST`, `NEVER`, `ALWAYS`), forbidden actions, and deterministic verification commands.
2. **Zero Historical Fluff or Post-Mortems**:
   - ❌ NO session dates (`2026-08-18`), incident stories ("Task 7 failed because..."), commit hashes, or session diaries.
   - ❌ NO user directory references (`/Users/...`, `C:\...`).
   - ❌ NO ADR historical changelog citations.
3. **Universally Applicable**: Rules must be fully portable and valid when installed into *any* external downstream repository. No repo-specific domain files (`ta-sweep-results.json`, `portfolio.json`).
4. **High Information Density**:
   - Target **30–70 lines**. If a rule exceeds 80 lines, strip background exposition or split concerns.
5. **Rule vs. Skill Distinction**:
   - **Rules** define *hard constraints, invariants, and guardrails* (passive policy).
   - **Skills** define *executable, multi-step procedures and interactive interviews* (active execution).

---

## Standard Rule Template

```markdown
---
trigger: always_on | on_match
description: Concise one-sentence summary of the constraint and why it exists.
globs: ["**/*"]
---

# Rule Title

## The Law

> **Core invariant stated in 1-2 sentences.** Every agent action touching [Scope]
> MUST comply with this invariant before execution.

## Invariants & Forbidden Actions

1. **[Invariant 1]**: Concrete MUST / NEVER constraint.
2. **[Invariant 2]**: Specific forbidden action and failure condition.
3. **[Invariant 3]**: Deterministic verification requirement.

## Verification & Recovery

```bash
# Deterministic verification command
<verification-command>
```

- If verification fails: <immediate rollback or corrective action>.
```

---

## Workflow

### 1. Discovery & Intent
Identify:
- **Rule Name**: lowercase-hyphen slug (e.g., `destructive-action-guard`).
- **Core Invariant**: What is forbidden? What must be verified?
- **Scope/Trigger**: Is it `always_on` or scoped to file patterns via `globs`?
- **Target Location**: Canonical source in `plugins/<plugin>/rules/` or local repo `.agent/rules/`.

### 2. Validation Gate
Before writing the rule, verify:
- [ ] Are all dates (`YYYY-MM-DD`) and incident names omitted?
- [ ] Are all personal usernames and absolute machine paths omitted?
- [ ] Is the entire text under 80 lines?
- [ ] Are constraints expressed as actionable invariants with verification commands?

### 3. Execution & Symlink Registration
- Write canonical rule to `plugins/<plugin>/rules/<rule-name>.md`.
- Symlink to `.agent/rules/<rule-name>.md` via `symlink_manager.py`.
- If modifying rule mirrors across `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, and `.github/copilot-instructions.md`, sync via `python3 plugins/cli-agents/scripts/sync_instruction_files.py`.
