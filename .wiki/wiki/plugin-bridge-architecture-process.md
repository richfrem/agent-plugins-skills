---
concept: plugin-bridge-architecture-process
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/plugin-installer/references/plugin_installer_overview.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.190264+00:00
cluster: agent
content_hash: 7dd2c82570d81c17
---

# Plugin Bridge: Architecture & Process

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details


# Plugin Bridge: Architecture & Process

**Version**: 2.0

## Overview

The `plugin-installer` skill translates plugins from a common format into the specific structure expected by each agent environment. It reads from `plugins/` and writes to the agent-specific directories.

There is one bridge:

**Plugin Bridge**
- **Source**: `plugins/` (any plugin directory)
- **Tool**: `plugin_installer.py`
- **Responsibility**:
  - Installs **Skills** into agent skill/workflow directories
  - Deploys **Commands** as agent-specific slash commands
  - Converts Markdown workflows into agent-specific formats (TOML for Gemini, prompts for Copilot, etc.)
  - Patches agent-specific identifiers (e.g., `--actor` flags) into installed files

---

## Supported Agent Environments

| Environment | Config Directory | Format |
|-------------|-----------------|--------|
| Antigravity | `.agents/` | Markdown workflows + rules |
| Claude Code | `.claude/` | Markdown commands |
| Gemini CLI | `.gemini/` | TOML + Markdown |
| GitHub Copilot | `.github/` | Prompt files |

---

## Execution

### Install a single plugin
```bash
python ./plugin_installer.py \
  --plugin plugins/<plugin-name>
```

### Install all plugins
```bash
python ./install_all_plugins.py
```

---

## Architecture Diagram

![Process Diagram](agent_bridge_diagram.png)

---

## Notes
- The bridge uses automatic target detection mapping to central `.agents/` repositories. It does not accept a `--target` argument.
- The bridge is format-agnostic: any plugin following the Open Standards structure is compatible.
- Agent-specific patches (actor flags, path formats) are applied automatically per target.


## See Also

- [[agent-plugin-analyzer---architecture]]
- [[exploration-cycle-plugin-architecture-reference]]
- [[exploration-cycle-plugin-architecture-reference]]
- [[exploration-cycle-plugin-architecture-reference]]
- [[exploration-cycle-plugin-architecture-reference]]
- [[exploration-cycle-plugin-architecture-reference]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/plugin-installer/references/plugin_installer_overview.md`
- **Indexed:** 2026-04-17T06:42:10.190264+00:00
