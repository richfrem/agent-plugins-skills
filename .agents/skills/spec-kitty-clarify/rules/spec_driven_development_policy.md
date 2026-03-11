---
trigger: manual
---

# Spec-Driven Development (SDD) Policy

**Effective Date**: 2026-01-29
**Revised**: 2026-03-12
**Related Constitution Articles**: IV (Documentation First), V (Test-First), VI (Simplicity)

**Full workflow details -> `.agent/skills/spec_kitty_workflow/SKILL.md`**

---

## THE SUPREME LAW: HUMAN GATE

> **YOU MUST NOT advance between phases without EXPLICIT user approval.**
> Approval words: "Proceed", "Go", "Execute".
> "Sounds good", "Looks right", "That makes sense" are NOT approval.
> **VIOLATION = SYSTEM FAILURE**

### Required Approval Gates

| Gate | Stop After | Get Approval Before |
|------|-----------|---------------------|
| **Gate 0** | Writing `spec.md` | Running `spec-kitty plan` |
| **Gate 1** | Writing `plan.md` | Running task generation |
| **Gate 2** | Generating `tasks.md` + WP files | Running `spec-kitty implement` |
| **Gate 3** | WP implementation complete | Moving to `for_review` |

**After generating each phase artifact**: STOP, show the artifact to the user, and end your turn. Do not proceed until the user explicitly approves.

---

## Core Mandate

**All significant work** must follow the **Spec -> Plan -> Tasks** lifecycle.
Artifacts live in `kitty-specs/NNN/` using the spec-kitty CLI.
**Manual creation of `spec.md`, `plan.md`, or `tasks/` is STRICTLY FORBIDDEN.**

---

## The Three Tracks

| Track | Name | When | Workflow |
|-------|------|------|----------|
| **A** | Factory | Deterministic, repetitive ops | Auto-generated Spec/Plan/Tasks -> Execute |
| **B** | Discovery | Ambiguous, creative work | `/spec-kitty.specify` -> [Gate 0] -> Plan -> [Gate 1] -> Tasks -> [Gate 2] -> Implement |
| **C** | Micro-Tasks | Trivial atomic fixes (typos, restarts) | Direct execution. **No architectural decisions.** |

---

## Required Artifacts (Tracks A and B)

| Artifact | CLI Command | Purpose |
|----------|-------------|---------|
| `spec.md` | `spec-kitty agent feature create-feature <slug>` | The **What** and **Why** |
| `plan.md` | `spec-kitty agent feature setup-plan --feature <slug>` | The **How** |
| `tasks.md` + WPs | `/spec-kitty.tasks` then `finalize-tasks` | Execution checklist |

---

## Lifecycle (Pre-Execution Workflow Commitment)

Before starting work, display this visual map:

```text
+-----------------------------------------------------------+
|               SPEC-KITTY LIFECYCLE MAP                    |
+-----------------------------------------------------------+
| [ ] Phase 0a: Specify  -> [GATE 0: USER APPROVES spec]   |
| [ ] Phase 0b: Plan     -> [GATE 1: USER APPROVES plan]   |
| [ ] Phase 0c: Tasks    -> [GATE 2: USER APPROVES tasks]  |
| [ ] Phase 1:  Implement WP -> code -> commit -> push     |
| [ ] Phase 2:  Accept -> Retro -> Merge -> Sync           |
+-----------------------------------------------------------+
```

1. **Specify** -> `/spec-kitty.specify` -> **[STOP FOR GATE 0]**
2. **Plan** -> `/spec-kitty.plan` -> **[STOP FOR GATE 1]**
3. **Tasks** -> `/spec-kitty.tasks` -> **[STOP FOR GATE 2]**
4. **Implement** -> `/spec-kitty.implement` (creates isolated worktree)
5. **Review** -> `/spec-kitty.review`
6. **Accept** -> `spec-kitty agent feature accept --feature <slug> --mode local --lenient --json`
7. **Merge** -> `/spec-kitty.merge`

---

## Known Agent Violations (DO NOT DO THESE)

| Violation | Why Dangerous | Correct Behavior |
|-----------|--------------|-----------------|
| Spec -> Plan -> Tasks -> Implement in one turn | Skips all Human Gates, user cannot course-correct | STOP after EACH artifact and wait for explicit approval |
| Creating tasks.md or WP files before plan is approved | Wasted work; architecture may be wrong | Gate 1 must pass before tasks |
| Committing `kitty-specs/` from a WP branch | Pre-commit hook blocks it; research files will be orphaned in worktree | Copy research files to main checkout before merge |
| Not pushing WP branch to origin before merge | Worktree deletion destroys untracked files permanently | `git push origin <WP-branch>` before any merge step |
| Marking WPs done without frontmatter | Bare WP files without `---` YAML frontmatter are invisible to spec-kitty lane tracking | Every WP file must have `lane:` in YAML frontmatter |
| Running `spec-kitty merge` with dirty working tree | Preflight counts `??` untracked files as dirty | `git stash -u` before merge, `git stash pop` after |

---

## Reverse-Engineering (Migration Context)

When migrating or improving an existing component:
1. **Discovery**: Run investigation tools.
2. **Reverse-Spec**: Populate `spec.md` from investigation results.
3. **Plan**: Create `plan.md` for the migration.
4. **Gate**: Show both to user before generating tasks.
