---
concept: project-ecosystem-constitution-v4
source: plugin-code
source_file: spec-kitty-plugin/skills/spec-kitty-sync-plugin/rules/constitution.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.396486+00:00
cluster: approval
content_hash: 53836ec1c7420bf2
---

# Project Ecosystem Constitution V4

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
trigger: always_on
---

# Project Ecosystem Constitution V4

> **THE SUPREME LAW: HUMAN GATE**
> You MUST NOT execute ANY state-changing operation without EXPLICIT user approval.
> "Sounds good" is NOT approval. Only "Proceed", "Go", "Execute" is approval.
> **VIOLATION = SYSTEM FAILURE**

## I. The Spec-Driven Workflow (Project Purpose)
All significant work MUST follow the **Spec-Driven Development (SDD) lifecycle**.
Start with `/spec-kitty.specify` for new features.

### Workflow Hierarchy
```
/spec-kitty.specify   -> spec.md
/spec-kitty.plan      -> plan.md
/spec-kitty.tasks     -> tasks/ (work packages)
/spec-kitty.implement -> isolated worktree per WP
/spec-kitty.review    -> for_review -> done
/spec-kitty.accept    -> feature acceptance
/spec-kitty.merge     -> merge + cleanup
```

- **Track A (Factory)**: Deterministic tasks - auto-generated Spec/Plan/Tasks -> Execute.
- **Track B (Discovery)**: Ambiguous/creative work - full SDD lifecycle.
- **Track C (Micro-Task)**: Trivial fixes - direct execution, no spec needed.

## II. Zero Trust (Git & Execution)
- **NEVER** commit directly to `main`. **ALWAYS** use a feature branch.
- **NEVER** run `git push` without explicit, fresh approval.
- **NEVER** "auto-fix" via git.
- **HALT** on any user "Stop/Wait" command immediately.

### Defined: State-Changing Operation
Any operation that:
1. Writes to disk (except /tmp/)
2. Modifies version control (git add/commit/push)
3. Executes external commands with side effects
**REQUIRES EXPLICIT APPROVAL ("Proceed", "Go", "Execute").**

## III. Tool Discovery & Usage
- **NEVER** use `grep` / `find` / `ls -R` for tool discovery.
- **ALWAYS** use defined **Slash Commands** (`/spec-kitty.*`) over raw scripts.
- **ALWAYS** use `spec-kitty-cli` for SDD lifecycle operations.
- **ALWAYS** use the `task_manager.py` CLI for kanban lane transitions.

## IV. Governing Law (The Tiers)

### Tier 1: PROCESS (Deterministic)
| Policy | Purpose |
|:-------|:--------|
| `rules/spec_driven_development_policy.md` | **Lifecycle**: Spec -> Plan -> Tasks |
| `references/standard-workflow-rules.md` | **Worktree Protocol**: Branch & merge rules |

### Tier 2: TECHNICAL (Standards)
| Policy | Purpose |
|:-------|:--------|
| Coding conventions | Per language standards (snake_case, camelCase, PascalCase) |
| Dependency management | pip-compile locked-file workflow |

## V. Session Closure (Mandate)
- **ALWAYS** run `/spec-kitty.accept` then `/spec-kitty.merge` at feature completion.
- **NEVER** abandon a feature without acceptance + retrospective.

**Version**: 4.0 | **Ratified**: 2026-03-05

## See Also

- [[project-name-constitution]]
- [[project-name]]
- [[project-setup-reference-guide]]
- [[project-name]]
- [[project-setup-guide]]
- [[project-setup-guide]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/skills/spec-kitty-sync-plugin/rules/constitution.md`
- **Indexed:** 2026-04-17T06:42:10.396486+00:00
