# Plugin Manager

**Universal Cross-Platform Plugin Installer — Works Everywhere `npx skills` Cannot**

The **Plugin Manager** is the cross-agent, cross-platform orchestration hub for your plugin ecosystem. Where `npx skills add` installs skills only and the Claude `/plugin` marketplace is Claude-specific, `plugin_add.py` installs **full plugins** (skills + agents + commands + hooks) directly from GitHub — on any OS, for any agent.

---

## Why This Exists: The Three-Tool Landscape

| Tool | Platform | Installs | GitHub source |
|---|---|---|---|
| `npx skills add` | Mac/Linux only (symlink issue on Windows) | Skills only | ✓ `owner/repo` |
| `/plugin marketplace add` | Claude Code only | Full plugins | ✓ `owner/repo` |
| **`plugin_add.py`** ★ | **All platforms** (Windows, Mac, Linux) | **Full plugins** (skills + agents + commands + hooks) | ✓ `owner/repo` |

> `plugin_add.py` is the cross-platform, cross-agent equivalent of `npx skills add` — but for full plugins, not just skills.

---

## Installation

### Option 1: Interactive TUI — from GitHub (Recommended)

No clone required. Auto-downloads, shows a plugin picker, installs selected plugins.

```bash
# Interactive picker — browse and select which plugins to install
python plugins/plugin-manager/scripts/plugin_add.py richfrem/agent-plugins-skills

# Install everything non-interactively
python plugins/plugin-manager/scripts/plugin_add.py richfrem/agent-plugins-skills --all -y

# Preview without writing any files
python plugins/plugin-manager/scripts/plugin_add.py richfrem/agent-plugins-skills --dry-run
```

> Inspired by the [`npx skills add`](https://skills.sh) UX from [Vercel Labs](https://github.com/vercel-labs/skills). Re-implemented in pure Python stdlib for cross-platform compatibility and full-plugin deployment.

### Option 2: From a Marketplace (Claude Code only)

```bash
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install plugin-manager
```

### Option 3: `npx skills` (Mac/Linux, skills only)

```bash
# Skills only — works correctly on Mac/Linux where Git creates real symlinks
npx skills add richfrem/agent-plugins-skills --path plugins/plugin-manager
```

> [!WARNING]
> **Windows users:** do not use `npx skills add` with this repository. Git for Windows
> checks out symlinks as text files and `npx` will install broken one-line pointer files
> instead of executable Python. Use `plugin_add.py` instead.

---

## Why `plugin_add.py` Works on Windows

`npx skills add` fails on Windows because Git checks out symlinks as plain text files (e.g. `../../../scripts/install_all_plugins.py`). Node.js `cp({ dereference: true })` detects real symlinks and copies the target on Mac/Linux — but on Windows it sees a text file and copies the literal path string, leaving broken installs.

`plugin_add.py` solves this by reading those pointer files at install time, following the relative path back to the real Python source, and writing a proper hard copy into `.agents/`. **No symlinks. No npm. No Node.js dependency.** Works identically on all platforms.

---

## 🌐 Supported Targets

The Plugin Manager deploys to `.agents/` as the universal canonical store, then symlinks to:

| Agent Environment | Directory |
|---|---|
| **Universal / All agents** | `.agents/` |
| **Claude Code** | `.claude/` |
| **Azure AI** | `.azure/` |

> Antigravity, GitHub Copilot, and Gemini CLI all read directly from `.agents/` — no per-agent symlinks needed.

---

## Skills

| Skill | Purpose | Key Scripts |
| :--- | :--- | :--- |
| **[plugin-installer](skills/plugin-installer/SKILL.md)** | Default: `plugin_add.py` interactive TUI; also `plugin_installer.py` for single-plugin CI installs | `plugin_add.py`, `bridge_installer.py` |
| **[maintain-plugins](skills/maintain-plugins/SKILL.md)** | Audit structure, sync agent environments, scaffold READMEs, clean orphans | `sync_with_inventory.py`, `audit_structure.py` |
| **[auto-update-plugins](skills/auto-update-plugins/SKILL.md)** | SessionStart hook that auto-syncs from GitHub sources on every session | `check_and_sync.py` |

---

## Commands (Slash Commands)

| Command | Purpose |
| :--- | :--- |
| `/plugin-manager:update` | Sync all plugins to local agent environments (`.agents/`, `.claude/` etc.) |
| `/plugin-manager:cleanup` | Remove orphaned artifacts from deleted plugins in agent environments |
| `/plugin-manager:install` | Install a specific plugin from GitHub or local path |

---

## Component Mapping Matrix

The installer intelligently deploys plugin components to the correct directories for each agent:

| Component | `.agents/` (canonical) | Claude Code `.claude/` |
|-----------|------------------------|------------------------|
| `skills/*/` | `skills/<name>/` | `skills/<name>/` (symlinked) |
| `agents/*.md` | `agents/<plugin>-<name>.md` | `agents/<plugin>-<name>.md` (symlinked) |
| `commands/*.md` | `workflows/<plugin>_<cmd>.md` | `commands/<plugin>_<cmd>.md` (symlinked) |
| `hooks/hooks.json` | `hooks/<plugin>-hooks.json` | `hooks/<plugin>-hooks.json` (symlinked) |

> **Note on Commands:** Nested command folders (`commands/ops/restart.md`) are flattened to snake_case (`plugin_ops_restart.md`) for IDE compatibility.

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
│   └── install.md      <- Install a plugin from GitHub or local path
├── scripts/
│   ├── plugin_add.py          <- Interactive TUI installer (default, GitHub-native)
│   ├── bridge_installer.py    <- Core deploy logic (single plugin)
│   ├── install_all_plugins.py <- Batch install loop
│   ├── sync_with_inventory.py <- Agent env sync + orphan cleanup
│   ├── audit_structure.py     <- Structural audit
│   └── generate_readmes.py    <- README scaffolding
└── skills/
    ├── plugin-installer/
    ├── maintain-plugins/
    └── auto-update-plugins/
```
