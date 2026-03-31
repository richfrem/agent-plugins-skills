# Plugin Manager

**The Universal Orchestration Hub for Your Plugin Ecosystem**

The **Plugin Manager** maintains a healthy local plugin ecosystem. It adapts and bridges standard plugins for use in many compatible agent environments (allowing you to write your core plugin logic once and deploy it across a wide variety of tools), and easily distributes source plugins to other project repos.

---

## Why `npx skills` Was Replaced on Windows

`npx skills add` works correctly on **Mac and Linux** where Git creates real OS-level symlinks. This repository uses symlinks inside skill directories (e.g. `bridge-plugin/scripts/install_all_plugins.py` points back to the canonical source in `plugins/plugin-manager/scripts/`).

On **Windows**, Git checks out symlinks as plain text files containing the relative path string (e.g. `../../../scripts/install_all_plugins.py`). The `npx` installer uses Node.js `cp({ dereference: true })` which detects real symlinks and copies the target — but on Windows it sees a text file and copies the literal path string. The result is a `.agents/` folder full of one-line text files that Python cannot execute.

The **Bridge Installer** solves this by reading those text pointer files at install time, following the relative path back to the real Python source, and writing a proper hard copy into `.agents/`. No symlinks. No `npx`. No Node.js dependency. Works identically on all platforms.

---

## Installation

### Option 1: From a Marketplace (Claude Code native)
```bash
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install plugin-manager
```

### Option 2: Mac / Linux — `npx skills` (cross-agent, skills only)
```bash
# Skills only — works correctly on Mac/Linux where Git creates real symlinks
npx skills add richfrem/agent-plugins-skills --path plugins/plugin-manager
```

> [!WARNING]
> **Windows users:** do not use `npx skills add` with this repository. Git for Windows
> checks out symlinks as text files and `npx` will install broken one-line pointer files
> instead of executable Python. Use the Bridge Installer below instead.

### Option 3: Bridge Installer (Recommended for Windows — works everywhere)

After cloning or installing this plugin, run the batch installer from the project root:

```bash
# Install all plugins from the core plugins/ directory
python .agents/skills/bridge-plugin/scripts/install_all_plugins.py

# Install from an additional plugins directory (additive — does not wipe existing installs)
python .agents/skills/bridge-plugin/scripts/install_all_plugins.py --plugins-dir path/to/other/plugins

# Dry run to preview without writing
python .agents/skills/bridge-plugin/scripts/install_all_plugins.py --dry-run
```

The installer:
- Reads pointer files, resolves them to real source, and writes hard copies into `.agents/skills/`
- Creates Windows Junctions (or symlinks on Mac/Linux) from `.agents/skills/` and `.claude/skills/` into `.agents/`
- Is **additive** — running it against a second plugins directory merges without touching existing installs
- Runs correctly from its own installed location in `.agents/` — no `plugins/` source tree required in consuming projects

## 🌐 Supported Targets

The Plugin Manager acts as a **Universal Translator**. Provide the name of any target system, and the internal `bridge-plugin` will dynamically create a corresponding `.{target}` configuration folder (e.g., `--target cursor` builds `.cursor/`).

**Popular Examples:**
| Target | Command Syntax | Default Directory (Created Automatically) |
|---|---|---|
| **Claude Code** | `--target claude` | `.claude/` |
| **GitHub Copilot** | `--target github` | `.github/` |
| **Google Gemini** | `--target gemini` | `.gemini/` |
| **Antigravity** | `--target antigravity` | `.agents/` |
| **Cursor** | `--target cursor` | `.cursor/` |

> *A user or agent can extend this to any target IDE or CLI (e.g., `roo`, `openhands`, `cline`, `trae`).*

**Additional Prominent IDEs/Agents (Dynamically Supported):**
Amp, Codex, Gemini CLI, Kimi Code CLI, Opencode, Augment, Openclaw, Codebuddy, Command Code, Continue, Cortex Code, Crush, Droid, Goose, Junie, iFlow CLI, Kiko Code, Kiro CLI, Kode, Mistral Vibe, Mux, Pi, Qoder, Qwen Code, Roo Code, Trae CN, ZenCoder, Neovate, Pochi, Adal.

---

## Dependencies

The `bridge-plugin` skill requires `PyYAML`:

```bash
pip install -r requirements.txt
# or: pip install PyYAML
```

## Quick Start: Deploy Local Source

Ensure your plugin is situated inside `plugins/<name>`, then run the bridge installer to scaffold the target environment rules and commands.

**Single Plugin:**
```bash
python3 ././scripts/bridge_installer.py --plugin plugins/my-plugin
```
> The installer automatically detects existing agent directories (e.g. `.agents/`, `.claude/`). No `--target` argument is needed or accepted.

**Sync Everything / All Plugins:**
```bash
python3 ././scripts/update_agent_system.py
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
| `/plugin-manager:update` | Sync all plugins to local agent environments (`.agents/`, `.claude/` etc.) |
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
| **Antigravity** (`.agents/`) | `workflows/*.md` | `skills/` | `skills/<plugin>/agents/` | `.agents/rules/` | *(Ignored)* |
| **Universal Generic** (`.<target>/`) | `commands/*.md` | `skills/` | `skills/<plugin>/agents/` | `.<target>/rules/` | *(Ignored)* |

> **Note on Commands:** When writing command logic, you can use nested folders (`commands/ops/restart.md`). The bridge automatically flattens these into a snake_case format (`ops_restart.md`) to remain compatible with IDEs that don't support deeply nested slash-commands. Gemini targets are wrapped in TOML automatically.

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
