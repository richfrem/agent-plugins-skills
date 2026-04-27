---
name: plugin-installer
plugin: plugin-manager
description: >-
  Installs plugin components (skills, commands/workflows, rules, hooks, MCP)
  into the .agents/ central store and symlinks them to agent environments that
  require it (.claude/). DEFAULT method: run plugin_add.py for an interactive
  require it (.claude/). DEFAULT method: run plugin_add.py (the primary TUI and headless orchestrator) 
  which internally delegates to plugin_installer.py (the execution engine) for the actual OS-level installation.
  Trigger when a user says "install plugin", "deploy plugin", "add plugin", 
  "install from GitHub", or "sync plugin to agents".
allowed-tools: Bash, Write, Read
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---

# Agent Bridge

## Overview

This skill deploys plugin components to agent environments using the
`.agents/` central store + symlink pattern. It is the **full-stack** installer:

| Installer | Features | Requires Local Clone? | Recommended For |
|-----------|----------|-----------------------|-----------------|
| `uvx` ★ **default** | Runs `plugin_add.py` natively | No (runs from GitHub) | Everyone using `uv` |
| `bootstrap.py` | Downloads & runs `plugin_add.py` | No (downloads in-memory) | End users without `uv` |
| `plugin_add.py` | Full interactive TUI or Headless CI | Yes | Local developers debugging or updating locally |
| `plugin_installer.py` | Execution Engine (No UX) | Yes | Internal framework usage only |

> **Use `uvx`** (★ recommended default) for an interactive TUI that installs full plugins without requiring Node.js.
> **Use the `bootstrap.py` curl pipeline** if you do not have `uv` installed.
> **Use `plugin_add.py`** directly for scripted/CI installs from a local clone (e.g. `plugin_add.py --all -y`).

## Initial vs Subsequent Installs

There is no difference between an initial install and a subsequent install from the consumer's perspective. Because `uvx` and `bootstrap.py` execute ephemerally, they are inherently stateless tooling. 

You do not need to "install the installer". Just run the `uvx` or `curl` command whenever you need to add or update a plugin. The state is strictly kept inside your `.agents/` repository.

---

## Attribution

The `plugin_add.py` interactive TUI (multiselect, arrow-key navigation, fuzzy search, `owner/repo` GitHub shorthand, temp-clone-then-install flow) is inspired by universal one-liner installation patterns:

- GitHub Repository Patterns: <https://github.com/vercel-labs/skills>
- Marketplace: <https://skills.sh>

This implementation re-creates those UX patterns in **pure Python stdlib** (no npm, no external packages) so they work on Windows without symlink issues and operate at the **plugin** level rather than individual SKILL.md files.

---

## Architecture: How Installation Works

```
plugins/<plugin>/
  skills/          → .agents/skills/<skill>/        (canonical copy, all agents read from here)
                     .claude/skills/<skill>          → symlink (Claude Code)
  commands/        → .agents/workflows/<plugin>_<cmd>.md  (canonical copy)
                     .claude/commands/<plugin>_<cmd>.md   → symlink (Claude Code)
  rules/           → .agents/rules/<plugin>_<rule>.md     (canonical copy)
                     CLAUDE.md                            → appended (Claude Code)
  hooks/hooks.json → .agents/hooks/<plugin>-hooks.json   (canonical copy)
                     .claude/hooks/<plugin>-hooks.json    → symlink (Claude only)
  .mcp.json        → ./.mcp.json                         (merged)
```

**Central store is always `.agents/` at project root.** Symlinks point from
each agent's own directory back into `.agents/`. This mirrors exactly how
`npx skills` manages its canonical store at `.agents/skills/`.

---

## Component Mapping Matrix

| Component | `.agents/` (canonical) | `.claude/` (Claude Code) |
|-----------|------------------------|--------------------------|
| `skills/` | `.agents/skills/<n>/` full copy | `.claude/skills/<n>` → symlink |
| `commands/*.md` | `.agents/workflows/<plugin>_<cmd>.md` | `.claude/commands/<plugin>_<cmd>.md` → symlink |
| `rules/` | `.agents/rules/<plugin>_<rule>.md` | Appended → `CLAUDE.md` |
| `hooks/hooks.json` | `.agents/hooks/<plugin>-hooks.json` | `.claude/hooks/<plugin>-hooks.json` → symlink |
| `agents/*.md` | `.agents/agents/<plugin>-<agent>.md` | `.claude/agents/<plugin>-<agent>.md` → symlink |
| `.mcp.json` | Merged → `./.mcp.json` | Merged → `./.mcp.json` |

> **Antigravity, Gemini, and GitHub Copilot** all natively read from `.agents/`
> — no separate symlinks needed. The canonical `.agents/` copy is sufficient.

> **Commands naming:** Nested command folders are flattened to snake_case.
> `commands/ops/restart.md` → `<plugin>_ops_restart.md`

> **`commands/` vs `workflows/` naming:** The plugin source folder is always
> named `commands/`. The installer writes to `.agents/workflows/` (canonical)
> and `.claude/commands/` (symlink). Never rename the source folder.

> **`skills/` as slash commands (Claude Code):** In Claude Code, any `skills/<name>/SKILL.md`
> entry in a plugin is deployed to `.claude/skills/<name>/` and automatically functions as
> both a proactive skill AND a namespaced slash command (`/plugin-name:name`). This is the
> **preferred** pattern for new commands — use `commands/` as thin wrappers that delegate
> to skills. The installer handles both paths independently; no special flag needed.

---

## External Skills Compatibility

`plugin_installer.py` writes to the external skills lock file after installation
so that legacy tools remain aware of bridge-installed skills.

**Lock file locations:**

| File | Path | Purpose |
|------|------|---------|
| Global lock | `~/.agents/.skill-lock.json` | Tracks global installs; enables legacy check/update |
| Project lock | `<project>/skills-lock.json` | Tracks project installs; enables legacy experimental installs |

**Lock file schema (version 3):**
```json
{
  "version": 3,
  "skills": {
    "my-skill": {
      "source": "richfrem/agent-plugins-skills",
      "sourceType": "github",
      "sourceUrl": "https://github.com/richfrem/agent-plugins-skills.git",
      "skillPath": "plugins/my-plugin/skills/my-skill",
      "skillFolderHash": "<git-tree-sha>",
      "installedAt": "<iso-timestamp>",
      "updatedAt": "<iso-timestamp>"
    }
  },
  "dismissed": {}
}
```

After running `plugin_installer.py`, each installed skill must be written to
the appropriate lock file. Skills only — commands, rules, hooks, and MCP are
not tracked by `npx skills`.

---

---

## Usage

### Bootstrapped (no clone required): `uvx` ★ Recommended
```bash
# Interactive TUI from any GitHub repo
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills

# Install from Anthropic official plugins (has plugins/ subdir)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add anthropics/claude-plugins-official

# Install from flat-layout repo (no plugins/ dir — auto-discovered)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add anthropics/knowledge-work-plugins

# Install all non-interactively
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills --all -y

# Local installation testing via uvx (uses remote script but local plugin files)
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add plugins/
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add plugins/agent-scaffolders
```

### Full Deployment: `plugin_add.py` (interactive TUI)

The recommended local invocation. Supports the same GitHub source syntax as `uvx`.

#### Source Format

`plugin_add.py` accepts a flexible `owner/repo[/subpath]` source:

| Source Format | What Happens |
|---|---|
| `richfrem/agent-plugins-skills` | Clone repo, auto-detect `plugins/` dir |
| `anthropics/claude-plugins-official/plugins` | Clone repo, use `plugins/` subpath directly |
| `anthropics/knowledge-work-plugins` | Clone repo, no `plugins/` dir — scans root for plugin-shaped dirs |
| `anthropics/knowledge-work-plugins/engineering` | Clone repo, drill into `engineering/` as a single plugin |
| `https://github.com/org/repo/tree/main/plugins` | Full GitHub URL — `tree/main/` is stripped automatically |
| `/local/path/to/repo` | Local clone — same discovery waterfall |

#### Plugin Discovery Waterfall

When a repo root is resolved, plugins are found via three-tier fallback:

1. **Classic monorepo** — `plugins/` subdir exists → scan its children
2. **Flat layout** — No `plugins/` dir → scan root-level dirs that have `.claude-plugin/plugin.json` or `skills/`
3. **Single plugin** — The pointed-to directory itself has `.claude-plugin/plugin.json` → treat as one plugin

```bash
# Interactive plugin picker — current repo
python ./scripts/plugin_add.py

# Install from remote GitHub repo (any layout)
python ./scripts/plugin_add.py richfrem/agent-plugins-skills

# Install specific subpath
python ./scripts/plugin_add.py anthropics/knowledge-work-plugins/engineering

# Full GitHub URL (tree/main/ stripped automatically)
python ./scripts/plugin_add.py https://github.com/anthropics/claude-plugins-official/tree/main/plugins

# Install all non-interactively
python ./scripts/plugin_add.py richfrem/agent-plugins-skills --all -y

# Dry-run preview
python ./scripts/plugin_add.py --dry-run
```

#### Fresh Project: `.claude/` Auto-Init

If no `.claude/` directory exists in the target project, `plugin_add.py` will prompt:

```
  No .claude/ directory found in this project.
  Initialize .claude/ for Claude Code integration? [Y/n]
```

Answering `Y` (default) creates `.claude/` so Claude Code symlinks are activated during installation. Answering `n` skips it — only `.agents/` (the canonical store) will be populated.

### The Execution Engine: `plugin_installer.py`

This script is the literal OS execution engine. You should generally run `plugin_add.py`, but you can explicitly trigger the bridge engine if you need to bypass plugin discovery entirely.

**Install a single plugin directly via bridge:**
```bash
python scripts/plugin_installer.py \
  --plugin plugins/my-plugin
```

**Dry run (preview only, no writes):**
```bash
python scripts/plugin_installer.py \
  --plugin plugins/my-plugin --dry-run
```

---

## Execution Protocol

> **CRITICAL**: Do not run the installer without a Recap-Before-Execute summary.
> Always propose `--dry-run` first for any destructive or first-time operation.

### Phase 1: Pre-flight Check

Before running the bridge, verify:

1. Plugin path exists and has `./plugin.json`
2. At least one of `.agents/`, `.claude/` exists
   (do NOT create these automatically — if missing, print the exact `mkdir`
   command and wait for user confirmation)
3. No `--target auto` is used anywhere in the call chain

### Phase 2: Recap-Before-Execute

State exactly what will happen:

```markdown
### Plugin Installation Plan
- **Plugin**: plugins/my-plugin (v1.2.0)
- **Components**:
  - 2 skills → .agents/skills/ (canonical) + .claude/skills/ symlinks
  - 3 commands → .agents/workflows/, .claude/commands/
  - 1 rules file → .agents/rules/, appended to CLAUDE.md
  - hooks.json → .agents/hooks/ + .claude/hooks/
- **Detected environments**: claude (.claude/)
- **Lock file**: will update skills-lock.json

> Proceed? (yes to run live, no to dry-run first)
```

### Phase 3: Execute

Wait for explicit confirmation before running live. Default to dry-run.

---

## Fallback Tree

### 1. Target directory not found
Do NOT create automatically. Print:
```bash
mkdir .claude # for Claude Code
```
Wait for user confirmation. A missing directory may mean an uninitialised project.

### 2. Plugin not found
Do NOT scan for similar names. Report the error and list `plugins/` contents.
Ask the user to confirm the correct plugin name.

### 3. Partial bridge (some components failed)
Report each failed component individually with its error. Do NOT claim success.
Offer to retry individual components once the user resolves the issue.

### 4. `--target auto` attempted
STOP immediately. Ask the user to specify the exact environment name
(`antigravity`, `claude`, `gemini`, `github`). Never run with `--target auto`.

### 5. Symlink failed (Windows)
Log `symlinkFailed: true`. Fallback chain:
1. `os.symlink()` — true symlink (needs Developer Mode)
2. `mklink /J` for dirs / `mklink /H` for files — no Developer Mode needed
3. `shutil.copy2()` — plain copy (last resort, no live sync)

Warn: "On Windows, enable Developer Mode for true symlink support."

### 6. Lock file write failed
Log the error but do not abort the install. Warn the user that
installed skills may not be tracked in `skills-lock.json`.

---

## DETECTABLE_AGENTS Reference

The installer auto-detects agent environments by checking for these directories
at project root. Antigravity, Gemini, and GitHub Copilot now natively read from
`.agents/` so no per-agent symlinks are needed for them. Only environments that
require their own directory layout (Claude Code, Azure) are listed here:

```python
DETECTABLE_AGENTS = {
    ".claude": {
        "name": "claude",
        "skills": ".claude/skills",
        "agents": ".claude/agents",
        "commands": ".claude/commands",   # Markdown
        "rules": None,                    # Append to CLAUDE.md instead
        "rules_append_target": "CLAUDE.md",
        "hooks": ".claude/hooks",
        "rules_mode": "append",
    },
    ".azure": {
        "name": "azure",
        "skills": ".azure/skills",
        "commands": None,
        "rules": None,
        "hooks": None,
    },
}
```

---

## When to Use This Skill

- **Deploying a new plugin locally** — full component installation including
  commands, rules, and hooks that `npx skills` won't handle
- **After modifying a plugin** — re-run bridge to push changes to all envs
- **Adding a new target environment** — existing plugins need re-bridging
- **Reconciling with npx skills ecosystem** — write lock file entries so
  `npx skills list/check/update` sees bridge-installed skills
- **Debugging missing commands or rules** — `npx skills` installs will be
  missing these; bridge install completes the picture

## When NOT to Use This Skill

- **End-user consumption from remote repo** — use `plugin_add.py owner/repo` (auto-clones + interactive TUI) or the authoritative installation hub for individual skills.
- **Auditing plugin structure** — use `maintain-plugins`

## Related Skills

- `maintain-plugins` — structural audits, sync, orphan cleanup, README generation