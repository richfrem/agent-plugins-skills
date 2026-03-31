---
name: plugin-installer
description: >-
  Installs plugin components (skills, commands/workflows, rules, hooks, MCP)
  into the .agents/ central store and symlinks them to agent environments that
  require it (.claude/). Use this skill when deploying a local plugin to agent
  environments, adding a new plugin to the ecosystem, or reconciling
  bridge-installed skills with the npx skills lock file. Trigger when a user
  says "install plugin", "deploy plugin", or "sync plugin to agents".
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

| Installer | Skills | Commands | Rules | Hooks | MCP |
|-----------|--------|----------|-------|-------|-----|
| `npx skills add` | ✓ | ✗ | ✗ | ✗ | ✗ |
| `bridge_installer.py` | ✓ | ✓ | ✓ | ✓ | ✓ |

> **Use `npx skills add`** for pure skill distribution to end users.
> **Use `bridge_installer.py`** when you need commands, rules, hooks, or MCP
> configs deployed alongside skills — or when developing locally.

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

## npx skills Compatibility

`bridge_installer.py` writes to the `npx skills` lock file after installation
so that `npx skills list`, `check`, and `update` remain aware of
bridge-installed skills.

**Lock file locations:**

| File | Path | Purpose |
|------|------|---------|
| Global lock | `~/.agents/.skill-lock.json` | Tracks global installs; enables `npx skills check/update` |
| Project lock | `<project>/skills-lock.json` | Tracks project installs; enables `npx skills experimental_install` |

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

After running `bridge_installer.py`, each installed skill must be written to
the appropriate lock file. Skills only — commands, rules, hooks, and MCP are
not tracked by `npx skills`.

---

---

## Usage

### Standard: `npx skills` (skills only)
```bash
# Install all skills from remote repo
npx skills add richfrem/agent-plugins-skills

# Install a single plugin's skills
npx skills add richfrem/agent-plugins-skills/plugins/my-plugin

# Update all tracked skills
npx skills update

# Remove a skill
npx skills remove skill-name
```

> This installs **skills only**. Commands, rules, hooks, and MCP are not
> deployed. For full plugin deployment, use `bridge_installer.py` below.

### Full Deployment: `bridge_installer.py` (skills + commands + rules + hooks)

**Before reinstalling local changes**, flush stale artifacts:
```bash
rm -rf .agents/ && npx skills remove --all -y
```

**Install a single plugin:**
```bash
python ./bridge_installer.py \
  --plugin plugins/my-plugin
```

**Install all plugins:**
```bash
python ./install_all_plugins.py
```

**Dry run (preview only, no writes):**
```bash
python ./bridge_installer.py \
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
Log `symlinkFailed: true`. Fall back to directory copy for that agent.
Warn: "On Windows, enable Developer Mode for symlink support."

### 6. Lock file write failed
Log the error but do not abort the install. Warn the user that
`npx skills list/check/update` may not reflect this installation.

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

- **End-user consumption from remote repo** — use `npx skills add` instead;
  it's simpler, has no Python dependency, and handles 30+ agents natively
- **Replicating plugin source to another project** — use `replicate-plugin`
- **Auditing plugin structure** — use `maintain-plugins`

## Related Skills

- `maintain-plugins` — structural audits, sync, orphan cleanup, README generation
- `replicate-plugin` — copy plugin source between local project repositories
- `package-plugin` — package a plugin into a distributable ZIP archive