# Plugin Manager

> [!NOTE]
> **Partially superseded by `npx skills`.**
> - `/plugin-manager:update` and `/plugin-manager:cleanup` -- use `npx skills update` instead (auto-detects agents, no Python required).
> - **`plugin-replicator`** remains the only tool for copying plugin source between local repos -- no npx equivalent exists for this workflow.
> - `/plugin-manager:install` -- superseded by `npx skills add richfrem/agent-plugins-skills/plugins/<name>`.

**The Orchestration Hub for Your Plugin Ecosystem**


The **Plugin Manager** maintains a healthy local plugin ecosystem. It keeps agent configurations in sync with your `plugins/` folder and distributes plugins to other project repos.

---

## Quick Start: Sync Everything

To refresh all agent environments with the latest plugin code:

```bash
python3 plugins/plugin-manager/skills/*/scripts/update_agent_system.py
```

> For step-by-step control, invoke the `plugin-maintenance` skill.

---

## Skills

| Skill | Purpose | Key Scripts |
| :--- | :--- | :--- |
| **[plugin-maintenance](skills/plugin-maintenance/SKILL.md)** | Audit structure, sync agent environments, scaffold READMEs | `sync_with_inventory.py`, `audit_structure.py` |
| **[plugin-replicator](skills/plugin-replicator/SKILL.md)** | Copy or link plugin source code to other project repos | `plugin_replicator.py`, `bulk_replicator.py` |

> For bridging plugins to specific agent runtimes, use **plugin-mapper**'s `agent-bridge` skill.

---

## Commands (Slash Commands)

| Command | Purpose |
| :--- | :--- |
| `/plugin-manager:update` | Sync all plugins to local agent environments (`.agent/`, `.claude/` etc.) |
| `/plugin-manager:cleanup` | Remove orphaned artifacts from deleted plugins in agent environments |
| `/plugin-manager:install` | Replicate a specific plugin from this repo to a target project's `plugins/` |

---

## Directory Structure

```
plugin-manager/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── commands/
│   ├── update.md       <- Sync all plugins to local agent environments
│   ├── cleanup.md      <- Clean orphaned agent artifacts
│   └── install.md      <- Replicate a plugin to another project
├── scripts/
│   ├── update_agent_system.py   <- Master orchestrator
│   ├── sync_with_inventory.py   <- Agent env sync + cleanup
│   ├── audit_structure.py       <- Structural audit
│   ├── plugin_replicator.py     <- Single plugin copy (--source/--dest/--clean)
│   ├── bulk_replicator.py       <- Bulk plugin copy
│   └── generate_readmes.py      <- README scaffolding
└── skills/
    ├── plugin-maintenance/
    └── plugin-replicator/
```
