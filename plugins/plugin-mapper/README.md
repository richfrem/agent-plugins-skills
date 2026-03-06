# Plugin Mapper

> [!NOTE]
> **For consumers: use `npx skills` instead.**
> `npx skills add richfrem/agent-plugins-skills` auto-detects your agent environment and installs all plugins natively -- no Python required.
> This plugin is now primarily a **local development tool** for contributors who need to: deploy from local source, generate Gemini TOML, wire lifecycle hooks, or bridge to custom/unlisted targets.

**The Universal Bridge for Agent Plugins**


The **Plugin Mapper** adapts and bridges standard Claude Code plugins for use in many compatible agent environments — allowing you to write your core plugin logic once and deploy it across a wide variety of tools.

## 🌐 Supported Targets

The Plugin Mapper is designed as a **Universal Translator**. Provide the name of any target system, and the script will dynamically create a corresponding `.{target}` configuration folder (e.g., `--target cursor` builds `.cursor/`).

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

**How to Extend for a New Target:**
If your environment is not explicitly documented but relies on standard markdown prompts, slash commands, or tools, simply run the bridge installer with the name of your environment:
```bash
# Example for 'cursor' or 'roo'
python plugins/plugin-mapper/skills/agent-bridge/scripts/bridge_installer.py --plugin <plugin-path> --target cursor
```
This automatically scaffolds a `.{target}/` hidden directory populated with `commands/` and `skills/` using the generic markdown fallback installer. Agents equipped with the `agent-bridge` skill can do this dynamically on-demand for any target!

---

## 🚀 Quick Start

### 1. Identify Your Environment
Determine which AI agent or IDE you are using. The bridge will handle directory creation automatically based on the `--target` flag.

> ⚠️ If you use `--target auto`, the bridge will scan your current directory for existing configuration folders (like `.claude` or `.agent`) and install to all detected systems.

### 2. Drop Your Plugin In
Place any standard Claude Code plugin in `plugins/`:
```
my-repo/
├── .github/          ← GitHub Copilot target
├── .gemini/          ← Gemini target
├── .agent/           ← Antigravity target
├── .claude/          ← Claude Code target
└── plugins/
    ├── plugin-mapper/   ← This tool
    └── my-plugin/       ← Your plugin (standard .claude-plugin format)
```

### 3. Run the Bridge

**Single plugin:**
```bash
python plugins/plugin-mapper/skills/agent-bridge/scripts/bridge_installer.py --plugin plugins/my-plugin --target auto
```

**All plugins at once:**
```bash
python plugins/plugin-mapper/skills/agent-bridge/scripts/install_all_plugins.py
```

---

## 🛠️ Advanced Usage

### Force a Specific Target
Install to a specific environment only (creates directory if needed):
```bash
python plugins/plugin-mapper/skills/agent-bridge/scripts/bridge_installer.py --plugin plugins/my-plugin --target github
```

### Component Mapping Matrix

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

## 🧩 Plugin Format

The bridge supports any plugin following the standard `.claude-plugin` manifest structure:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json      ← Plugin metadata (name, version, etc.)
├── commands/            ← Slash commands (supports subdirectories)
├── skills/              ← Persistent knowledge/behavior files
├── agents/              ← Sub-agent persona definitions
├── rules/               ← Behavioral rules
├── hooks/
│   └── hooks.json       ← Claude Code lifecycle hooks
```

All components are optional — the bridge gracefully skips missing directories.
