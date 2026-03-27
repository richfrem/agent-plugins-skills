---
name: bridge-plugin
description: >-
  Installs plugin components (skills, commands/workflows, rules, hooks, MCP)
  into the .agents/ central store and symlinks them to detected agent
  environments (.agent/, .claude/, .github/, .gemini/). Use this skill when
  deploying a local plugin to agent environments, adding a new plugin to the
  ecosystem, or reconciling bridge-installed skills with the npx skills
  lock file. Trigger when a user says "bridge", "install plugin", "deploy
  plugin", or "sync plugin to agents".
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
  skills/          → .agents/skills/<skill>/        (canonical copy)
                     .agent/skills/<skill>           → symlink (Antigravity)
                     .claude/skills/<skill>          → symlink (Claude Code)
  commands/        → .agents/workflows/<plugin>_<cmd>.md  (canonical copy)
                     .agent/workflows/<plugin>_<cmd>.md   → symlink
                     .claude/commands/<plugin>_<cmd>.md   → symlink
                     .gemini/commands/<plugin>_<cmd>.toml → (TOML-wrapped)
  rules/           → .agents/rules/<plugin>_<rule>.md     (canonical copy)
                     .agent/rules/<plugin>_<rule>.md      → symlink
                     CLAUDE.md                            → appended
  hooks/hooks.json → .agents/hooks/<plugin>-hooks.json   (canonical copy)
                     .claude/hooks/<plugin>-hooks.json    → symlink (Claude only)
  .mcp.json        → ./.mcp.json                         (merged)
```

**Central store is always `.agents/` at project root.** Symlinks point from
each agent's own directory back into `.agents/`. This mirrors exactly how
`npx skills` manages its canonical store at `.agents/skills/`.

---

## Component Mapping Matrix

| Component | `.agent/` (Antigravity) | `.claude/` (Claude Code) | `.gemini/` (Gemini) | `.github/` (Copilot) |
|-----------|------------------------|--------------------------|---------------------|----------------------|
| `skills/` | `.agent/skills/<n>` → symlink | `.claude/skills/<n>` → symlink | `.gemini/skills/<n>` → symlink | `.github/skills/<n>` → symlink |
| `commands/*.md` | `.agent/workflows/<plugin>_<cmd>.md` | `.claude/commands/<plugin>_<cmd>.md` | `.gemini/commands/<plugin>_<cmd>.toml` | `.github/prompts/<plugin>_<cmd>.prompt.md` |
| `rules/` | `.agent/rules/<plugin>_<rule>.md` | Appended → `CLAUDE.md` | Appended → `GEMINI.md` | Appended → `.github/copilot-instructions.md` |
| `hooks/hooks.json` | *(ignored)* | `.claude/hooks/<plugin>-hooks.json` | *(ignored)* | *(ignored)* |
| `agents/*.md` | `.agent/skills/<plugin>-<agent>/` wrapper | `.claude/skills/<plugin>-<agent>/` wrapper | `.gemini/skills/<plugin>-<agent>/` wrapper | `.github/skills/<plugin>-<agent>/` wrapper |
| `.mcp.json` | Merged → `./.mcp.json` | Merged → `./.mcp.json` | Merged → `./.mcp.json` | Merged → `./.mcp.json` |

> **Commands naming:** Nested command folders are flattened to snake_case.
> `commands/ops/restart.md` → `<plugin>_ops_restart.md`

> **`commands/` vs `workflows/` naming:** The plugin source folder is always
> named `commands/`. The installer maps it to each platform's own directory
> name at install time — `workflows/` on Antigravity/`.agents/`, `commands/`
> on Claude Code, `commands/` (TOML) on Gemini, `prompts/` on GitHub Copilot.
> Never rename the source folder to match any single platform.

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

## Antigravity Agent — Specific Notes

**Detection:** `npx skills` detects Antigravity via
`existsSync(~/.gemini/antigravity)` (global install path). The bridge detects
it locally via `(root / ".agent").exists()`. Both are correct for their scope.

**Skills dir:** `.agent/skills/<skill-name>/` — a full skill folder containing
`SKILL.md` and supporting files, symlinked from `.agents/skills/<skill-name>/`.

**Global skills dir:** `~/.gemini/antigravity/skills/`

**Commands land in:** `.agent/workflows/` as Markdown files.

**Rules land in:** `.agent/rules/` as individual Markdown files (not appended
to a monolithic context file, unlike Claude/Gemini).

**Hooks:** Not supported by Antigravity — ignored silently.

**Symlink fallback:** On Windows without Developer Mode, symlinks fail silently.
The installer falls back to a full directory copy and logs `symlinkFailed: true`.

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
2. At least one of `.agent/`, `.claude/`, `.github/`, `.gemini/` exists
   (do NOT create these automatically — if missing, print the exact `mkdir`
   command and wait for user confirmation)
3. No `--target auto` is used anywhere in the call chain

### Phase 2: Recap-Before-Execute

State exactly what will happen:

```markdown
### Bridge Installation Plan
- **Plugin**: plugins/my-plugin (v1.2.0)
- **Components**:
  - 2 skills → .agents/skills/ + symlinks
  - 3 commands → .agent/workflows/, .claude/commands/
  - 1 rules file → .agent/rules/, appended to CLAUDE.md
  - hooks.json → .claude/hooks/
- **Detected environments**: antigravity (.agent/), claude (.claude/)
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
mkdir .agent  # for Antigravity
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

The bridge auto-detects agent environments by checking for these directories
at project root. Each entry carries the component routing for that environment:

```python
DETECTABLE_AGENTS = {
    ".agent": {
        "name": "antigravity",
        "skills": ".agent/skills",
        "commands": ".agent/workflows",   # Markdown, prefixed plugin_cmd
        "rules": ".agent/rules",          # Individual .md files
        "hooks": None,                    # Not supported
        "rules_mode": "files",            # vs "append" for Claude/Gemini
    },
    ".claude": {
        "name": "claude",
        "skills": ".claude/skills",
        "commands": ".claude/commands",   # Markdown
        "rules": None,                    # Append to CLAUDE.md instead
        "rules_append_target": "CLAUDE.md",
        "hooks": ".claude/hooks",
        "rules_mode": "append",
    },
    ".gemini": {
        "name": "gemini",
        "skills": ".gemini/skills",
        "commands": ".gemini/commands",   # TOML-wrapped
        "rules": None,
        "rules_append_target": "GEMINI.md",
        "hooks": None,
        "rules_mode": "append",
        "commands_format": "toml",
    },
    ".github": {
        "name": "github",
        "skills": ".github/skills",
        "commands": ".github/prompts",    # .prompt.md extension
        "rules": None,
        "rules_append_target": ".github/copilot-instructions.md",
        "hooks": None,
        "rules_mode": "append",
        "commands_ext": ".prompt.md",
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