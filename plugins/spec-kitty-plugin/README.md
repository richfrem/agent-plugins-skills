# Spec-Kitty Plugin 🐱

The flagship workflow plugin — **Spec-Driven Development lifecycle** + **Universal Bridge sync engine**.

> **⚠️ CRITICAL REQUIREMENT**: This plugin is entirely dependent on the host machine having `spec-kitty-cli` installed and initialized locally via `spec-kitty init . --ai antigravity`. Do not install this plugin if those prerequisites are not met.

Source repo [https://github.com/Priivacy-ai/spec-kitty](https://github.com/Priivacy-ai/spec-kitty)

## Prerequisites
```bash
# Install CLI
pip install spec-kitty-cli  # or: uv tool install spec-kitty-cli

# update CLI
pip install spec-kitty-cli --upgrade

# Initialize in project
spec-kitty init . --ai antigravity
```

### 1. Initializing Spec Kitty (First Time)
Once the plugin is installed, you can ask your agent to trigger the `spec-kitty-sync-plugin` skill:
> "Hey Assistant, run spec-kitty-sync-plugin to set up this repository."

The agent will autonomously:
1. Run the `spec-kitty init . --ai antigravity` CLI command.
2. Verify the configuration under `.kittify/` is ready.
3. Automatically load the global commands/skills for Google Antigravity.
4. Redeploy the updated bundle into your IDE so the slash commands become active.

## Active Skills (19)
Two categories: **2 custom/admin skills** (hand-maintained) and **17 auto-synced workflow skills** (generated from `.kittify/` templates by `sync_configuration.py`).

### Admin Skills (custom — never overwritten by sync)
| Skill | Description |
|:---|:---|
| `spec-kitty-sync-plugin` | Full-cycle install **or** update — upgrades CLI, refreshes templates, syncs plugin, reconciles custom knowledge, and bridges to agent environments. |
| `spec-kitty-workflow` | End-to-end SDD workflow SOPs, safety steps, and best practices. |

### Workflow Skills (auto-synced from `.kittify/` via `sync_configuration.py`)
| Skill | Description |
|:---|:---|
| `spec-kitty-specify` | Phase 0 — draft feature specification |
| `spec-kitty-plan` | Phase 0 — generate implementation plan |
| `spec-kitty-tasks` | Phase 0 — generate work packages |
| `spec-kitty-tasks-outline` | Work package outline generation |
| `spec-kitty-tasks-packages` | Work package packaging |
| `spec-kitty-tasks-finalize` | Finalize and lock work packages |
| `spec-kitty-implement` | Phase 1 — create worktree for WP |
| `spec-kitty-review` | Phase 1 — submit WP for review |
| `spec-kitty-accept` | Validate feature readiness |
| `spec-kitty-merge` | Automated batch merge |
| `spec-kitty-status` | Show kanban board |
| `spec-kitty-analyze` | Analyze specification or codebase |
| `spec-kitty-checklist` | Generate pre-merge checklist |
| `spec-kitty-clarify` | Identify spec ambiguities |
| `spec-kitty-constitution` | Enforce workflow constitution rules |
| `spec-kitty-dashboard` | Project health dashboard |
| `spec-kitty-research` | Research and discovery phase |

## Slash Commands (17)
All workflow skills are invocable as slash commands once deployed to your agent environment.
| Command | Description |
|:---|:---|
| `/spec-kitty:specify` | Create feature specification |
| `/spec-kitty:plan` | Generate implementation plan |
| `/spec-kitty:tasks` | Generate work packages |
| `/spec-kitty:tasks-outline` | Work package outline |
| `/spec-kitty:tasks-packages` | Work package packaging |
| `/spec-kitty:tasks-finalize` | Finalize work packages |
| `/spec-kitty:implement` | Create worktree for WP |
| `/spec-kitty:review` | Submit WP for review |
| `/spec-kitty:accept` | Validate feature readiness |
| `/spec-kitty:merge` | Automated batch merge |
| `/spec-kitty:status` | Show kanban board |
| `/spec-kitty:analyze` | Analyze specification or codebase |
| `/spec-kitty:checklist` | Generate pre-merge checklist |
| `/spec-kitty:clarify` | Identify spec ambiguities |
| `/spec-kitty:constitution` | Enforce workflow constitution |
| `/spec-kitty:dashboard` | Project health dashboard |
| `/spec-kitty:research` | Research and discovery phase |

## Architecture (Workflow Provenance)

This plugin enforces strict **Workflow Provenance** to maintain a single source of truth for all Spec-Driven Development routines.

With native Google Antigravity support in Spec Kitty v3.2.2+, command and skill templates are served globally by the CLI or integrated directly. The configuration layout is simplified:

```text
spec-kitty-plugin/
├── agents/
│   ├── spec-kitty-agent.md     (SDD lifecycle orchestrator)
│   └── spec-kitty-setup.md     (install/sync orchestrator)
├── rules/                      (Synced from .agent/ rules)
├── references/
└── skills/                     (19 total)
    ├── spec-kitty-sync-plugin/ (custom — install/update)
    ├── spec-kitty-workflow/    (custom — SDD SOPs)
    └── ...                     (17 auto-synced skills)
```

## License
MIT
