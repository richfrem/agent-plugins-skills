# Agent Execution Disciplines

> **Acknowledgement and Attribution**
> The skills in this plugin are directly inspired by and ported from the
> **[Superpowers](https://github.com/obra/superpowers)** project by
> **[Jesse Vincent (obra)](https://github.com/obra)**.
> The original work established the core execution discipline philosophy
> (Iron Laws, Red-Green-Refactor enforcement, evidence-before-claims) that
> makes these skills effective. All credit for the foundational concepts belongs
> to Jesse. This plugin adapts and integrates those ideas into the
> `agent-plugins-skills` ecosystem. Please star and study the original repo.

Execution discipline skills ported from [obra/superpowers](https://github.com/obra/superpowers),
adapted to work alongside `agent-agentic-os` and `exploration-cycle-plugin`.

This plugin houses universal workflow enforcement skills: verification, testing, debugging,
code review, and safe git branch management. It is a companion to `agent-agentic-os` and
should be installed alongside it.

## Why a Separate Plugin

These skills are useful across multiple plugins (`agent-agentic-os`,
`exploration-cycle-plugin`, and any project that installs either). Per ADR-001, cross-plugin
skill sharing uses Agent Skill Delegation - once this plugin is installed, any other skill
can reference these by name without cross-plugin script dependencies.

## Skills

| Skill | Purpose | Source |
|---|---|---|
| `verification-before-completion` | Evidence before claims - run verification commands before any success claim | superpowers |
| `systematic-debugging` | 4-phase root-cause-first debugging protocol | superpowers |
| `test-driven-development` | Red-Green-Refactor cycle with Iron Law enforcement | superpowers |
| `using-git-worktrees` | Safe worktree creation, isolation, and .gitignore verification | superpowers |
| `finishing-a-development-branch` | 4 completion options with typed confirmation for destructive ops | superpowers |
| `requesting-code-review` | Dispatch independent code review with spec and quality reviewers | superpowers |

## Agents

| Agent | Purpose |
|---|---|
| `code-reviewer` | Independent code review agent (dispatched by requesting-code-review) |

## Installation

```bash
# Full deployment (skills + any commands/rules/hooks)
python ./bridge_installer.py --plugin plugins/agent-execution-disciplines

# Skills only via npx
npx skills add richfrem/agent-plugins-skills/plugins/agent-execution-disciplines
```

## ADR Compliance

- ADR-001: No cross-plugin script paths. Skills reference each other by name via Agent Skill Delegation.
- ADR-002: No scripts in this plugin (all ported skills are prose-only). N/A.
- ADR-003: If scripts are added in future, real files at plugin root, file-level symlinks from skill dir.
- ADR-004: Self-contained at deploy time. No runtime dependencies on sibling plugins.
