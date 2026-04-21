# Plugin Bridge: Architecture & Process

**Version**: 3.0

## Overview

The `plugin_installer.py` engine orchestrates the translation of agnostic plugin architectures into the rigid constraints expected by consumer agent environments. Rather than hard-linking symlinks (which breaks on Windows), it deterministically builds flat `plugin-sources.json` ledger files and copies absolute configurations to ensure pure compatibility.

## Supported Agent Environments

| Environment | Config Directory | Integration Logic |
|-------------|-----------------|-------------------|
| Universal | `.agents/` | Primary source of truth. |
| Claude Code | `.claude/` | Direct symlinks mirroring `.agents/` |
| Azure AI | `.azure/` | Direct symlinks mirroring `.agents/` |

---

## Execution Constraints

All installations are explicitly channeled through a canonical single entrypoint to prevent partial states.

### Option 1: Headless UVX (Modern)
```bash
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills
```

### Option 2: Fallback Bootstrapper
```bash
curl -sL https://raw.githubusercontent.com/richfrem/agent-plugins-skills/main/bootstrap.py | python -
```

---

## Technical Notes

- The installer automatically flattens `commands/` paths into snake_case structures (e.g. `commands/ops/restart.md` -> `plugin_ops_restart.md`) to bypass IDE routing constraints.
- `plugin-sources.json` uses a single `source` key array; it deprecated the earlier `github` and `local` dict mappings to allow seamless local-to-remote transitions.
