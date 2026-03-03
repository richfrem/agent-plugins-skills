---
trigger: manual
---

# Spec-Driven Development (SDD) Policy

**Effective Date**: 2026-01-29
**Related Constitution Articles**: IV (Documentation First), V (Test-First), VI (Simplicity)

**Full workflow details → `.agent/skills/spec_kitty_workflow/SKILL.md`**

## Core Mandate
**All significant work** must follow the **Spec → Plan → Tasks** lifecycle.
Artifacts live in `specs/NNN/` using templates from `.agent/templates/workflow/`.

## The Three Tracks

| Track | Name | When | Workflow |
|-------|------|------|----------|
| **A** | Factory | Deterministic, repetitive ops (`/codify-*`, `/curate-*`) | Auto-generated Spec/Plan/Tasks → Execute |
| **B** | Discovery | Ambiguous, creative work | `/spec-kitty.specify` → Draft Spec → Approve → Plan → Execute |
| **C** | Micro-Tasks | Trivial atomic fixes (typos, restarts) | Direct execution or ticket in `tasks/`. **No architectural decisions.** |

## Required Artifacts (Tracks A & B)

| Artifact | Template | Purpose |
|----------|----------|---------|
| `spec.md` | `.agent/templates/workflow/spec-template.md` | The **What** and **Why** |
| `plan.md` | `.agent/templates/workflow/plan-template.md` | The **How** |
| `tasks.md` | `.agent/templates/workflow/tasks-template.md` | Execution checklist |

## Lifecycle Summary
1. **Specify** → `/spec-kitty.specify` (or auto-generate for Track A)
2. **Plan** → `/spec-kitty.plan`
3. **Tasks** → `/spec-kitty.tasks`
4. **Implement** → `/spec-kitty.implement` (creates isolated worktree)
5. **Review** → `/spec-kitty.review`
6. **Merge** → `/spec-kitty.merge`

## Reverse-Engineering (Migration Context)
When migrating or improving an existing component:
1. **Discovery**: Run investigation tools.
2. **Reverse-Spec**: Populate `spec.md` from investigation results.
3. **Plan**: Create `plan.md` for the migration.
