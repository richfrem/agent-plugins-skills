---
concept: auto-update-plugins-skill
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/auto-update-plugins/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.740060+00:00
cluster: project
content_hash: 6c0492322bfbf2e1
---

# Auto-Update Plugins Skill

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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

Copy `./scripts/check_and_sync.py` into the consumer
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
  python .agents/scripts/check_and_sync.py
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
python ./scripts/plugin_add.py richfrem/agent-plugins-skills

# Non-interactive — reinstall everything
python ./scripts/plugin_add.py richfrem/agent-plugins-skills --all -y
```

---

## How `check_and_sync.py` Works

```
SessionStart fires
    ↓
Read plugin-sources.js

*(content truncated)*

## See Also

- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[skill-optimization-guide-karpathy-loop]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[quickstart-how-to-run-an-optimization-loop-on-any-skill]]
- [[skill-display-name-eval-skill-improvement-loop-instructions]]
- [[skill-continuous-improvement-red-green-refactor]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/auto-update-plugins/SKILL.md`
- **Indexed:** 2026-04-17T06:42:09.740060+00:00
