# Plugin Manager

**The Orchestration Hub for Your Plugin Ecosystem**

The **Plugin Manager** maintains a healthy local plugin ecosystem. It keeps agent configurations in sync with your `plugins/` folder and distributes plugins to other project repos.

---

## Quick Start: Sync Everything

To refresh all agent environments (Antigravity, Copilot, Gemini, Claude Code) with the current plugin code:

```bash
python3 plugins/plugin-manager/scripts/update_agent_system.py
```

This 2-step master sync:
1. **Spec-Kitty Sync** — refreshes `.windsurf` workflows into the plugin
2. **Plugin Install** — deploys all plugins to `.agent/`, `.claude/`, `.gemini/`, `.github/`

---

## Initial Setup (New Project)

```bash
# Clone this repo as the central source
git clone https://github.com/richfrem/agent-plugins-skills.git .vendor/agent-plugins-skills

# Bootstrap plugins from vendor into your project
python3 plugins/plugin-manager/scripts/plugin_bootstrap.py
```

---

## Skills

| Skill | Purpose | Key Scripts |
| :--- | :--- | :--- |
| **[plugin-maintenance](skills/plugin-maintenance/SKILL.md)** | Audit structure, sync agent environments, scaffold READMEs | `sync_with_inventory.py`, `audit_structure.py` |
| **[plugin-replicator](skills/plugin-replicator/SKILL.md)** | Copy or link plugin source code to other project repos | `plugin_replicator.py`, `bulk_replicator.py` |

> For bridging plugins to specific agent runtimes, use **plugin-mapper**'s `agent-bridge` skill.

---

## Directory Structure

```
plugin-manager/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── commands/              <- Slash commands
├── scripts/               <- Core Python scripts
│   ├── update_agent_system.py   <- Master orchestrator
│   ├── sync_with_inventory.py   <- Agent env sync
│   ├── audit_structure.py       <- Structural audit
│   ├── plugin_replicator.py     <- Single plugin copy
│   ├── bulk_replicator.py       <- Bulk plugin copy
│   └── generate_readmes.py      <- README scaffolding
└── skills/
    ├── plugin-maintenance/
    └── plugin-replicator/
```
