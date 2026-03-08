# Plugin Manager

> [!NOTE]
> **Partially superseded by `npx skills`.**
> `npx skills` auto-detects your agent environment and installs all plugins natively.
> This plugin is now primarily a **local development tool** for contributors who need to:
> - Deploy modifications directly from local source
> - Sync local plugins to multiple IDEs simultaneously
> - Copy or replicate source code to entirely separate project repositories

**The Universal Orchestration Hub for Your Plugin Ecosystem**

The **Plugin Manager** maintains a healthy local plugin ecosystem. It adapts and bridges standard plugins for use in many compatible agent environments (allowing you to write your core plugin logic once and deploy it across a wide variety of tools), and easily distributes source plugins to other project repos.

---

## 🌐 Supported Targets

The Plugin Manager acts as a **Universal Translator**. Provide the name of any target system, and the internal `agent-bridge` will dynamically create a corresponding `.{target}` configuration folder (e.g., `--target cursor` builds `.cursor/`).

**Popular Examples:**
| Target | Command Syntax | Default Directory (Created Automatically) |
|---|---|---|
| **Claude Code** | `--target claude` | `.claude/` |
| **GitHub Copilot** | `--target github` | `.github/` |
| **Google Gemini** | `--target gemini` | `.gemini/` |
| **Antigravity** | `--target antigravity` | `.agent/` |
| **Cursor** | `--target cursor` | `.cursor/` |

> *A user or agent can extend this to any target IDE or CLI (e.g., `roo`, `openhands`, `cline`, `trae`).*

**Additional Prominent IDEs/Agents (Dynamically Supported):**
Amp, Codex, Gemini CLI, Kimi Code CLI, Opencode, Augment, Openclaw, Codebuddy, Command Code, Continue, Cortex Code, Crush, Droid, Goose, Junie, iFlow CLI, Kiko Code, Kiro CLI, Kode, Mistral Vibe, Mux, Pi, Qoder, Qwen Code, Roo Code, Trae CN, ZenCoder, Neovate, Pochi, Adal.

---

## Quick Start: Deploy Local Source

Ensure your plugin is situated inside `plugins/<name>`, then run the bridge installer to scaffold the target environment rules and commands.

**Single Plugin:**
```bash
python3 ./plugins/plugin-manager/scripts/bridge_installer.py --plugin plugins/my-plugin --target auto
```

**Sync Everything / All Plugins:**
```bash
python3 ./plugins/plugin-manager/scripts/update_agent_system.py
```

> For step-by-step control, invoke the `maintain-plugins` skill.

---

## Skills

| Skill | Purpose | Key Scripts |
| :--- | :--- | :--- |
| **[bridge-plugin](skills/bridge-plugin/SKILL.md)** | Map, install, and translate components to target envs | `bridge_installer.py`, `install_all_plugins.py` |
| **[maintain-plugins](skills/maintain-plugins/SKILL.md)** | Audit structure, sync agent environments, scaffold READMEs | `sync_with_inventory.py`, `audit_structure.py` |
| **[replicate-plugin](skills/replicate-plugin/SKILL.md)** | Copy or link plugin source code to other project repos | `plugin_replicator.py`, `bulk_replicator.py` |

---

## Commands (Slash Commands)

| Command | Purpose |
| :--- | :--- |
| `/plugin-manager:update` | Sync all plugins to local agent environments (`.agent/`, `.claude/` etc.) |
| `/plugin-manager:cleanup` | Remove orphaned artifacts from deleted plugins in agent environments |
| `/plugin-manager:install` | Replicate a specific plugin from this repo to a target project's `plugins/` |

---

## Component Mapping Matrix

The installer intelligently translates plugin components into the specific directories and formats expected by the target IDE.

| Target Environment | `commands/*.md` | `skills/` | `agents/*.md` | `rules/` | `hooks/hooks.json` |
|-------------------|----------------|-----------|---------------|----------|-------------------|
| **Claude Code** (`.claude/`) | `commands/*.md` | `skills/` | `skills/<plugin>/agents/` | Appended to `./CLAUDE.md` | `hooks/<plugin>-hooks.json` |
| **GitHub Copilot** (`.github/`) | `prompts/*.prompt.md` | `skills/` | `skills/<plugin>/agents/` | Appended to `.github/copilot-instructions.md` | *(Ignored)* |
| **Google Gemini** (`.gemini/`) | `commands/*.toml` | `skills/` | `skills/<plugin>/agents/` | Appended to `./GEMINI.md` | *(Ignored)* |
| **Antigravity** (`.agent/`) | `workflows/*.md` | `skills/` | `skills/<plugin>/agents/` | `.agent/rules/` | *(Ignored)* |
| **Universal Generic** (`.<target>/`) | `commands/*.md` | `skills/` | `skills/<plugin>/agents/` | `.<target>/rules/` | *(Ignored)* |

> **Note on Commands:** When writing command logic, you can use nested folders (`commands/ops/restart.md`). The bridge automatically flattens these into a snake_case format (`ops_restart.md`) to remain compatible with IDEs that don't support deeply nested slash-commands. Gemini targets are wrapped in TOML automatically.

---

## Directory Structure

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
│   ├── bridge_installer.py      <- Core translation/routing logic
│   ├── install_all_plugins.py   <- Batch bridge loop processor
│   ├── audit_structure.py       <- Structural audit
│   ├── plugin_replicator.py     <- Single plugin copy (--source/--dest/--clean)
│   ├── bulk_replicator.py       <- Bulk plugin copy
│   └── generate_readmes.py      <- README scaffolding
└── skills/
    ├── bridge-plugin/
    ├── maintain-plugins/
    └── replicate-plugin/
```
