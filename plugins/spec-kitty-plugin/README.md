# Spec-Kitty Plugin 🐱

The flagship workflow plugin — **Spec-Driven Development lifecycle** + **Universal Bridge sync engine**.

> **⚠️ CRITICAL REQUIREMENT**: This plugin is entirely dependent on the host machine having `spec-kitty-cli` installed and initialized locally via `spec-kitty init . --ai windsurf`. Do not install this plugin if those prerequisites are not met.

Source repo [https://github.com/Priivacy-ai/spec-kitty](https://github.com/Priivacy-ai/spec-kitty)

## Prerequisites
```bash
# Install CLI
pip install spec-kitty-cli  # or: uv tool install spec-kitty-cli

# update CLI
pip install spec-kitty-cli --upgrade

# Initialize in project
spec-kitty init . --ai windsurf
```

### 1. Initializing Spec Kitty (First Time)
Once the plugin is installed, you can ask your agent to trigger the `spec-kitty-init` skill:
> "Hey Assistant, run spec-kitty-init to set up this repository."

The agent will autonomously:
1. Run the `spec-kitty init` CLI command.
2. Synchronize the generated `.windsurf/workflows` into the plugin's `commands/` directory.
3. Synchronize the generated `.kittify/memory` rules into the plugin's `rules/` directory.
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

Rather than duplicating workflow files (which leads to drift and destructive overwrites), the plugin utilizes a central asset mapping architecture driven by `sync_configuration.py`. 

The upstream master `*.md` files live in `.windsurf/workflows/`. When you execute `python scripts/sync_configuration.py`, the script:
1. Generates master symlinks within `spec-kitty-plugin/workflows/` mapping back to the `.windsurf/workflows/` master definitions.
2. Creates isolated nested `workflows/` symlinks within each individual `skills/*` directory.
3. Injects a deterministic `[./workflows/spec-kitty.<feature>.md](./workflows/...)` provenance header into every compiled `SKILL.md`.

This ensures that any augmented best practices or custom ecosystem strategies are inherently bundled directly into the upstream source files, eliminating the need for standalone side-files while preventing blind `.kittify` template overwrites.

```text
spec-kitty-plugin/
├── agents/
│   ├── spec-kitty-agent.md   (SDD lifecycle orchestrator)
│   └── spec-kitty-setup.md   (install/sync orchestrator)
├── rules/ (Synced from .kittify/memory/)
├── workflows/ (Master symlinks → .windsurf/workflows/)
├── references/
├── scripts/
│   └── sync_configuration.py (Idempotent provenance generator)
└── skills/                   (19 total)
    ├── spec-kitty-sync-plugin/ (custom — install/update)
    ├── spec-kitty-workflow/    (custom — SDD SOPs)
    └── ... (17 auto-synced skills from CLI via sync_configuration.py)
```

## License
MIT
