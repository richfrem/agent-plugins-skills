---
name: auto-update-plugins
description: >-
  Pull-based auto-sync skill. Sets up a consumer project so it automatically
  pulls fresh plugins from one or more source repos on every agent session start.
  Platform-aware: covers Mac (.zshrc aliases) and Windows (PowerShell profile +
  User env vars). Run once per machine for global env setup, once per consumer
  project to wire up the SessionStart hook and plugin-sources.json subscription.
  Trigger with "set up auto plugin sync", "auto install plugins on load",
  "subscribe this project to plugin updates", "sync plugins on startup", or
  "add a plugin source".
allowed-tools: Bash, Write, Read
---

# Auto-Update Plugins Skill

## Overview

This skill solves the multi-repo plugin sync problem using a **pull model**:

- The **source repo** (`agent-plugins-skills`) knows nothing about its consumers.
- Each **consumer project** declares what it subscribes to via `plugin-sources.json`.
- On every agent session start, a `SessionStart` hook fires `check_and_sync.py`,
  which detects changes and auto-installs updated plugins without any human prompt.

```
SOURCE REPO            CONSUMER REPOS
(agent-plugins-skills) <- oracle-project/plugin-sources.json
                       <- spec-kitty-lab/plugin-sources.json
                       <- my-new-project/plugin-sources.json
```

Adding a new consumer = drop in a `plugin-sources.json`. Nothing changes at the source.
Pivoting away = delete or clear `plugin-sources.json`. Nothing changes at the source.

---

## Phase 1: Machine Setup (One-Time Per Developer)

This step stores the path to your plugin source repos as env vars and creates
convenient named aliases. Do this once per machine, not per project.

### Mac / Linux (`~/.zshrc`)

Add the following block to `~/.zshrc`:

```bash
# ---- Agent Plugin Sources ----
# Absolute path to your agent-plugins-skills source repo on THIS machine.
export AGENT_PLUGINS_SKILLS_DIR="/Users/yourname/Projects/agent-plugins-skills"

# Add more plugin source repos as needed:
# export MY_PRIVATE_PLUGINS_DIR="/Users/yourname/Projects/my-private-plugins"

# ---- Sync Aliases ----
# On-demand manual sync for each source repo.
alias sync-agent-plugins="python3 $AGENT_PLUGINS_SKILLS_DIR/plugins/plugin-manager/scripts/install_all_plugins.py --plugins-dir $AGENT_PLUGINS_SKILLS_DIR/plugins"

# Add one alias per source repo:
# alias sync-private-plugins="python3 $AGENT_PLUGINS_SKILLS_DIR/plugins/plugin-manager/scripts/install_all_plugins.py --plugins-dir $MY_PRIVATE_PLUGINS_DIR/plugins"
```

Then reload:
```bash
source ~/.zshrc
```

### Windows (PowerShell)

**Set permanent user env vars (run once in PowerShell as your user):**
```powershell
[System.Environment]::SetEnvironmentVariable(
  "AGENT_PLUGINS_SKILLS_DIR",
  "C:\Projects\agent-plugins-skills",
  "User"
)
```

**Add aliases to your PowerShell profile (`$PROFILE`):**
```powershell
# ---- Agent Plugin Sources ----
function Sync-AgentPlugins {
  python3 "$env:AGENT_PLUGINS_SKILLS_DIR\plugins\plugin-manager\scripts\install_all_plugins.py" `
    --plugins-dir "$env:AGENT_PLUGINS_SKILLS_DIR\plugins"
}
Set-Alias sync-agent-plugins Sync-AgentPlugins
```

Reload with:
```powershell
. $PROFILE
```

---

## Phase 2: Consumer Project Setup (Once Per Project)

Run these steps inside the consumer project (e.g., `oracle-project`).

### Step 1: Create `plugin-sources.json` at the project root

Use the template at `skills/auto-update-plugins/templates/plugin-sources.json`.
Each source entry references an **env var name** (not a hardcoded path) so the
file is safe to commit and works across machines.

```json
{
  "sources": [
    {
      "name": "agent-plugins-skills",
      "env": "AGENT_PLUGINS_SKILLS_DIR",
      "plugins_subdir": "plugins",
      "installer_subpath": "plugins/plugin-manager/scripts/install_all_plugins.py"
    }
  ]
}
```

To subscribe to multiple source repos, add more entries to the `sources` array.

### Step 2: Install `check_and_sync.py` into the consumer project

Copy `skills/auto-update-plugins/scripts/check_and_sync.py` into the consumer
project at `.agents/scripts/check_and_sync.py`.

This script:
1. Reads `plugin-sources.json` at the project root.
2. Resolves each `env` variable to a real path.
3. Computes a hash of the source plugins folder.
4. Compares it against `.agents/plugin-sync-state.json` (a local hash cache).
5. If changed: runs the installer and updates the hash cache.
6. If env var is not set: logs a warning and skips that source gracefully.

### Step 3: Wire up the SessionStart Hook

Add a `SessionStart` hook to the consumer project so `check_and_sync.py` fires
automatically on every agent session start.

If the project already has a `SessionStart` hook, append this call to it.
If not, create `.agents/hooks/session_start.sh`:

```bash
#!/usr/bin/env bash
# Auto-sync plugins from registered sources on every session start.
if [ -f "plugin-sources.json" ]; then
  python3 .agents/scripts/check_and_sync.py
fi
```

For Claude Code specifically, register the hook in `.claude/settings.json`:
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

## Phase 3: Adding a Second Plugin Source to an Existing Consumer

Simply add another entry to `plugin-sources.json`:

```json
{
  "sources": [
    {
      "name": "agent-plugins-skills",
      "env": "AGENT_PLUGINS_SKILLS_DIR",
      "plugins_subdir": "plugins",
      "installer_subpath": "plugins/plugin-manager/scripts/install_all_plugins.py"
    },
    {
      "name": "my-private-plugins",
      "env": "MY_PRIVATE_PLUGINS_DIR",
      "plugins_subdir": "plugins",
      "installer_subpath": "plugins/plugin-manager/scripts/install_all_plugins.py"
    }
  ]
}
```

No other changes needed. `check_and_sync.py` will iterate all sources automatically.

---

## Opting Out / Pivoting Away

To stop a consumer project from auto-syncing:
- Delete or empty `plugin-sources.json`, OR
- Remove the `check_and_sync.py` call from the `SessionStart` hook.

Nothing at the source repo needs to change. The source repo is always unaware
of its consumers.

---

## Related Skills

- `replicate-plugin` - Manual one-off copy of a plugin to a single target.
- `bridge-plugin` - Install plugins from `.agents/` into agent environments.
- `maintain-plugins` - Health check, orphan cleanup, and ecosystem audit.
