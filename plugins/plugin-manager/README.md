# Plugin Manager

**Universal Cross-Platform Plugin Installer — Works where other managers cannot**

The **Plugin Manager** is the cross-agent, cross-platform orchestration hub for your plugin ecosystem. Where other managers install individual skills only and the Claude `/plugin` marketplace is Claude-specific, `plugin_add.py` installs **full plugins** (skills + agents + commands + hooks) directly from GitHub — on any OS, for any agent.

---

## Why This Exists: The Three-Tool Landscape

| Tool | Platform | Installs | GitHub source |
|---|---|---|---|
| Legacy skills managers | Mac/Linux only (symlink issues) | Skills only | ✓ `owner/repo` |
| `/plugin marketplace add` | Claude Code only | Full plugins | ✓ `owner/repo` |
| **`plugin_add.py`** ★ | **All platforms** (Windows, Mac, Linux) | **Full plugins** (skills + agents + commands + hooks) | ✓ `owner/repo` |

> `plugin_add.py` is the cross-platform, cross-agent equivalent of other skills managers — but for full plugins, not just individual skills.

---

## Initial Installation (Bootstrapping)

These commands are for consumers who want to add plugins seamlessly *without* cloning the repo.

### Option 1: `uvx` — Modern Python Standard (Recommended)

If you have [uv](https://docs.astral.sh/uv/) installed (the modern Python package manager), you get instantaneous, isolated installations exactly like `npx`, but natively cross-platform without Node.js.

```bash
# Interactive picker to add plugins
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills

# Install everything non-interactively
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills --all -y

# Interactive picker to remove plugins
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-remove

# Sync all installed plugins exactly to plugin-sources.json state
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-sync
```

### Option 2: Fallback Bootstrap (Zero Tooling Assumptions)

If you don't use `uv`, you can install purely using standard Python tooling without cloning the repo.

**Mac / Linux:**
```bash
curl -sL https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python -
```
**Windows (PowerShell):**
```powershell
Invoke-RestMethod https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python -
```

### Option 3: Claude Code Marketplace (Claude Code only)

```bash
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install plugin-manager
```

## Subsequent Installations

Because `uvx` and `bootstrap.py` execute ephemerally, you simply repeat the same command to add new plugins later. There is no local state to manage outside of your `.agents/` folder.

If you chose to **clone the repo locally** instead of using the remote bootstrappers, run:
```bash
python ./scripts/plugin_add.py
```

---

## Why `plugin_add.py` Works on Windows

Legacy installers often fail on Windows because Git checks out symlinks as plain text files (e.g. `scripts/install_all_plugins.py`). Node.js `cp({ dereference: true })` detects real symlinks and copies the target on Mac/Linux — but on Windows it sees a text file and copies the literal path string, leaving broken installs.

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
| **[plugin-installer](skills/plugin-installer/SKILL.md)** | Interactive TUI installer; `--all -y` for headless CI installs | `plugin_add.py`, `plugin_installer.py` |
| **[plugin-remover](skills/plugin-remover/SKILL.md)** | Interactive TUI uninstaller grouped by source; `--plugins --yes` for headless removal | `plugin_remove.py` |
| **[plugin-syncer](skills/plugin-syncer/SKILL.md)** | Reinstalls registered plugins from sources & cleans orphans | `sync_with_inventory.py` |

---

## Commands (Slash Commands)

| Command | Purpose |
| :--- | :--- |
| `/plugin-manager:install` | Install a specific plugin from GitHub or local path |
| `/plugin-manager:remove` | Safely remove a plugin and scrub its registry entry |
| `/plugin-manager:sync` | Sync all plugins to local environments based on `plugin-sources.json` |
| `/plugin-manager:cleanup` | Remove orphaned artifacts completely from `.agents/` |

---

## `plugin-sources.json` Schema

The plugin manager uses `plugin-sources.json` at your project root as the authoritative registry of installed plugins. Each source entry uses a flat `"source"` key — no separate `"local"` or `"github"` key needed.

```json
{
  "sources": [
    {
      "source": "richfrem/agent-plugins-skills",
      "plugins": ["adr-manager", "claude-cli"]
    },
    {
      "source": "/path/to/local/plugins",
      "plugins": ["agent-loops", "task-manager"]
    }
  ]
}
```

- **`source`** — Either a GitHub `owner/repo` slug or an absolute local path. The value itself signals whether it's remote or local.
- **`plugins`** — List of plugin names installed from that source. Each plugin appears under exactly one source (one source of truth).
- Adding from a different source automatically moves the plugin to the new source entry.
- Empty source entries are pruned automatically.

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
├── assets/
│   └── templates/
│       └── plugin-sources.template.json   <- Starter template for new projects
├── commands/
│   ├── update.md       <- Sync all plugins to local agent environments
│   ├── cleanup.md      <- Clean orphaned agent artifacts
│   └── install.md      <- Install a plugin from GitHub or local path
├── scripts/
│   ├── plugin_add.py          <- Interactive TUI installer (GitHub-native)
│   ├── plugin_remove.py       <- Interactive TUI uninstaller (source-grouped)
│   ├── plugin_installer.py    <- Core deploy logic (single plugin, called by plugin_add)
│   ├── sync_with_inventory.py <- Agent env sync + orphan cleanup via plugin-sources.json
│   └── test_plugin_lifecycle.py <- Full add/remove lifecycle test harness
└── skills/
    ├── plugin-installer/
    ├── plugin-remover/
    └── plugin-syncer/
```
