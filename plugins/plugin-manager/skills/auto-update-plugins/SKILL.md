---
name: auto-update-plugins
description: >-
  Pull-based auto-sync skill. Sets up a consumer project so it automatically
  pulls fresh plugins from GitHub on every agent session start using plugin_add.py.
  No local clone of agent-plugins-skills required — installs direct from GitHub.
  Trigger with "set up auto plugin sync", "auto install plugins on load",
  "subscribe this project to plugin updates", "sync plugins on startup", or
  "add a plugin source".
allowed-tools: Bash, Write, Read
---

# Auto-Update Plugins Skill

## Overview

This skill solves the multi-repo plugin sync problem using a **GitHub-native pull model**:

- Consumer projects declare what GitHub repos they subscribe to via `plugin-sources.json`.
- On every agent session start, a `SessionStart` hook fires `check_and_sync.py`,
  which detects upstream changes and re-runs `plugin_add.py` automatically.
- **No local clone of `agent-plugins-skills` required** — `plugin_add.py` clones
  into a temp directory, installs, and cleans up automatically.

```
GitHub (richfrem/agent-plugins-skills)
        ↓  plugin_add.py <owner/repo> --all -y
  consumer-project/.agents/   ← skills + agents + commands + hooks
```

Adding a new consumer = drop in a `plugin-sources.json`. Nothing changes at the source.
Pivoting away = delete or clear `plugin-sources.json`.

---

## Phase 1: Consumer Project Setup (Once Per Project)

### Step 1: Create `plugin-sources.json` at the project root

Each source entry declares a GitHub `owner/repo` to pull from. No env vars or
local paths required.

```json
{
  "sources": [
    {
      "name": "agent-plugins-skills",
      "github": "richfrem/agent-plugins-skills",
      "plugins": "all"
    }
  ]
}
```

To subscribe to **specific plugins only**, list them by name:

```json
{
  "sources": [
    {
      "name": "agent-plugins-skills",
      "github": "richfrem/agent-plugins-skills",
      "plugins": ["spec-kitty-plugin", "agent-agentic-os", "agent-loops"]
    }
  ]
}
```

To subscribe to **multiple source repos**, add more entries:

```json
{
  "sources": [
    {
      "name": "agent-plugins-skills",
      "github": "richfrem/agent-plugins-skills",
      "plugins": "all"
    },
    {
      "name": "my-private-plugins",
      "github": "myorg/my-private-plugins",
      "plugins": "all"
    }
  ]
}
```

### Step 2: Install `check_and_sync.py` into the consumer project

Copy `skills/auto-update-plugins/scripts/check_and_sync.py` into the consumer
project at `.agents/scripts/check_and_sync.py`.

This script:
1. Reads `plugin-sources.json` at the project root.
2. For each source, checks the latest commit SHA from the GitHub API (no auth needed for public repos).
3. Compares it against `.agents/plugin-sync-state.json` (a local SHA cache).
4. If changed: runs `plugin_add.py <owner/repo> --all -y` and updates the SHA cache.
5. If GitHub is unreachable: logs a warning and skips gracefully (no crash).

### Step 3: Wire up the SessionStart Hook

Add a `SessionStart` hook so `check_and_sync.py` fires on every agent session start.

Create `.agents/hooks/session_start.sh`:

```bash
#!/usr/bin/env bash
# Auto-sync plugins from registered GitHub sources on every session start.
if [ -f "plugin-sources.json" ]; then
  python3 .agents/scripts/check_and_sync.py
fi
```

For Claude Code, register the hook in `.claude/settings.json`:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash .agents/hooks/session_start.sh"
          }
        ]
      }
    ]
  }
}
```

---

## Phase 2: Manual On-Demand Update

To manually pull the latest plugins from GitHub at any time:

```bash
# Interactive — pick which plugins to update
python plugins/plugin-manager/scripts/plugin_add.py richfrem/agent-plugins-skills

# Non-interactive — reinstall everything
python plugins/plugin-manager/scripts/plugin_add.py richfrem/agent-plugins-skills --all -y
```

---

## How `check_and_sync.py` Works

```
SessionStart fires
    ↓
Read plugin-sources.json
    ↓
For each source:
    GET https://api.github.com/repos/<owner>/<repo>/commits?per_page=1
    sha = response[0].sha
    ↓
    Compare sha to .agents/plugin-sync-state.json["<name>"]["sha"]
    ↓
    If changed:
        python plugin_add.py <owner/repo> --all -y
        update plugin-sync-state.json sha
    If same:
        skip (no network calls beyond the SHA check)
    If GitHub unreachable:
        log warning, skip
```

The SHA check is a single lightweight API call (~1 KB). The full clone only
happens when there is an actual upstream change.

---

## Opting Out / Pivoting Away

To stop a consumer project from auto-syncing:
- Delete or empty `plugin-sources.json`, OR
- Remove the `check_and_sync.py` call from the `SessionStart` hook.

Nothing at the source repo needs to change.

---

## Migration from Old Local-Path Model

If you previously used `AGENT_PLUGINS_SKILLS_DIR` env var + `install_all_plugins.py`:

1. Replace `plugin-sources.json` with the GitHub-based format above.
2. Remove `AGENT_PLUGINS_SKILLS_DIR` from your shell profile / PowerShell profile.
3. Remove the `sync-agent-plugins` alias (no longer needed).
4. `check_and_sync.py` now calls `plugin_add.py` instead of `install_all_plugins.py`.

---

## Related Skills

- `plugin-installer` — full plugin deployment (skills + agents + commands + hooks).
- `maintain-plugins` — health check, orphan cleanup, and ecosystem audit.
