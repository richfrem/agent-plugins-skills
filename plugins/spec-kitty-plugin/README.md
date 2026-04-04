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

## Active Skills (2)
These skills automate the administration of the framework itself.

| Skill | Description |
|:---|:---|
| `spec-kitty-init` | Initialize the Spec-kitty environment and deploy the slash commands. |
| `spec-kitty-update`| Update an existing environment, pulling new templates and redeploying. |

## Slash Command Workflows (14)
| Command | Description |
|:---|:---|
| `/spec-kitty:specify` | Create feature specification |
| `/spec-kitty:plan` | Generate implementation plan |
| `/spec-kitty:tasks` | Generate work packages |
| `/spec-kitty:implement` | Create worktree for WP |
| `/spec-kitty:review` | Submit WP for review |
| `/spec-kitty:accept` | Validate feature readiness |
| `/spec-kitty:merge` | Automated batch merge |
| `/spec-kitty:status` | Show kanban board |

## Architecture (Workflow Provenance)

This plugin enforces strict **Workflow Provenance** to maintain a single source of truth for all Spec-Driven Development routines.

Rather than duplicating workflow files (which leads to drift and destructive overwrites), the plugin utilizes a central asset mapping architecture driven by `sync_configuration.py`. 

The upstream master `*.md` files live in `.windsurf/workflows/`. When you execute `python3 scripts/sync_configuration.py`, the script:
1. Generates master symlinks within `spec-kitty-plugin/workflows/` mapping back to the `.windsurf/workflows/` master definitions.
2. Creates isolated nested `workflows/` symlinks within each individual `skills/*` directory.
3. Injects a deterministic `[./workflows/spec-kitty.<feature>.md](./workflows/...)` provenance header into every compiled `SKILL.md`.

This ensures that any augmented best practices or custom ecosystem strategies are inherently bundled directly into the upstream source files, eliminating the need for standalone side-files while preventing blind `.kittify` template overwrites.

```text
spec-kitty-plugin/
├── .claude-plugin/plugin.json
├── agents/
├── rules/ (Synced from .kittify/memory/)
├── workflows/ (Master symlinks mapping to .windsurf/workflows/)
├── commands/
├── references/
├── scripts/
│   └── sync_configuration.py (Idempotent provenance generator)
└── skills/
    ├── spec-kitty-implement/
    │   ├── SKILL.md (Auto-generated with provenance header)
    │   └── workflows/
    │       └── spec-kitty.implement.md -> ../../workflows/...
    ├── spec-kitty-sync-plugin/ (Install/update sync)
    ├── spec-kitty-workflow/  (SDD workflow SOPs)
    └── ... (13 auto-synced skills from CLI)
```

## License
MIT
