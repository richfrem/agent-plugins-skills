---
description: Run Universal Bridge sync — propagate rules, workflows, and skills to all AI agents
argument-hint: "[--all]"
---

# Universal Sync (Bridge)

Synchronize the Single Source of Truth (`.kittify/memory` rules + `.windsurf/workflows`) to all agent configurations (Antigravity, Claude, Gemini, Copilot).

## Usage
```bash
# Full sync (recommended)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/speckit_system_bridge.py
```

> ⚠️ **RESTART REQUIRED**: After running sync, restart your IDE for slash commands to appear.

## What It Does
- Reads `.windsurf/workflows/*.md` → Projects to `.agent/workflows`, `.claude/commands`, `.gemini/commands`, `.github/prompts`
- Reads `.kittify/memory/*.md` → Projects to `.agent/rules`, `.claude/CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`
- Updates `.kittify/config.yaml` with all registered agents
