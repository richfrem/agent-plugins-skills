---
name: sanctuary-spec-kitty
description: "Project Sanctuary-specific skill for Spec-Driven Development. Knows the project's constitution, safety rules, AUGMENTED.md best practices, and how the spec-kitty-plugin should be configured for this project."
---

# Sanctuary Spec-Kitty Configuration

**Status:** Active
**Domain:** Project Sanctuary
**Depends on:** `spec-kitty-plugin` (generic spec-driven development framework)

## Purpose

This skill is the **Sanctuary-specific glue layer** that knows how to configure and use the generic `spec-kitty-plugin` for Project Sanctuary's development workflow.

The spec-kitty-plugin has two layers:
1. **Auto-synced commands** (from upstream CLI) — generic, overwritten on update
2. **AUGMENTED.md files** (our custom best practices) — project-specific, never overwritten

This skill documents what's Sanctuary-specific about our spec-kitty setup.

## Sanctuary-Specific Configuration

### Constitution
The project constitution lives at `.kittify/memory/constitution.md` and is synced to `.agent/rules/constitution.md`. It defines:
- The Human Gate (no state-changing ops without explicit approval)
- The Hybrid Workflow (Universal start → Learning Loop or Custom Flow)
- Zero Trust git policy (never commit to main, never push without approval)
- Tool Discovery enforcement (use query_cache.py, no grep for tools)

### AUGMENTED.md Files
These contain project-specific best practices that survive spec-kitty CLI updates:

| File | Sanctuary-Specific Content |
|---|---|
| `commands/spec-kitty-merge/AUGMENTED.md` | Pre-merge remote backup protocol, branch protection awareness (GH006 handling), kitty-specs conflict resolution |
| `commands/spec-kitty-implement/AUGMENTED.md` | Worktree discipline, absolute paths only, commit hygiene |
| `commands/spec-kitty-review/AUGMENTED.md` | Batch review protocol, dependency verification |
| `commands/spec-kitty-specify/AUGMENTED.md` | Doc co-authoring integration for specification quality |
| `commands/spec-kitty-plan/AUGMENTED.md` | Doc co-authoring integration for plan quality |

### Workflow SKILL.md
`skills/spec-kitty-workflow/SKILL.md` is the end-to-end guide with:
- Anti-simulation rules (proof = pasted command output)
- Deterministic closure protocol (review → accept → retrospective → merge → verify)
- Pre-merge remote backup (mandatory)
- Dual-Loop mode integration (Protocol 133)

### Orchestration Diagram
The end-to-end orchestration lifecycle—including `verify_workflow_state.py` gates and the downstream `intelligence-sync`—is mapped in our master diagram:
`resources/diagrams/standard-spec-kitty-workflow.mmd`

### Sync Plugin
To update when spec-kitty CLI upgrades:
```bash
# Invoke the sync-plugin skill
/spec-kitty.sync-plugin
```
This runs `sync_configuration.py`, then the agent reviews AUGMENTED.md files for staleness.

## Protected Files

The following files MUST NOT be deleted or corrupted during any sync or merge:
- `.agent/rules/constitution.md`
- `.agent/rules/standard-workflow-rules.md`
- `.agent/rules/01_PROCESS/*`
- `.agent/rules/02_OPERATIONS/*`
- `.agent/rules/03_TECHNICAL/*`
