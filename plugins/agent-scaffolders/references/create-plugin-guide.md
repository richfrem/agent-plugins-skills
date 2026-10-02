# Plugin Creation & Scaffolding Guide

Comprehensive reference guide for authoring, configuring, and packaging new Claude Code and Hermes-compatible plugins.

## Contents

- [Overview & Workflow](#overview--workflow)
- [Plugin Manifest Specification](#plugin-manifest-specification)
- [Hermes Compatibility (`plugin.yaml`)](#hermes-compatibility-pluginyaml)
- [Hermes Wiring (`__init__.py`)](#hermes-wiring-__init__py)
- [Hub-and-Spoke Shared Script Pattern](#hub-and-spoke-shared-script-pattern)
- [Marketplace Integration](#marketplace-integration)
- [Plugin Architecture Invariants](#plugin-architecture-invariants)

---

## Overview & Workflow

1. **Phase 1: Discovery & Scoping**: Determine plugin purpose, tools needed, and component taxonomy (skills, commands, agents, hooks, MCP servers).
2. **Phase 2: Directory Scaffolding**: Create root directory, `.claude-plugin/plugin.json`, `README.md`, and component folders.
3. **Phase 3: Multi-Platform Manifests**: Generate `.claude-plugin/plugin.json`, `plugin.yaml`, and `__init__.py`.
4. **Phase 4: Component Implementation**: Scaffold individual skills via `create-skill` and hooks via `create-hook`.
5. **Phase 5: Validation**: Verify using `audit-plugin` and `claude plugin validate .`.

---

## Plugin Manifest Specification

Every plugin's `.claude-plugin/plugin.json` must adhere to the minimal metadata schema:

```json
{
  "name": "<plugin-name>",
  "version": "0.1.0",
  "description": "<description>",
  "author": {
    "name": "richfrem",
    "email": "connect.richfrem@gmail.com"
  },
  "repository": "https://github.com/richfrem/agent-plugins-skills",
  "license": "MIT",
  "keywords": [
    "<keyword>"
  ]
}
```

### Invariants:
- Never include `skills`, `agents`, `hooks`, or `commands` arrays (these are auto-discovered).
- `author` must always be an object with `name` and optional `email`, never a string.
- No duplicate top-level keys.

---

## Hermes Compatibility (`plugin.yaml`)

Scaffold `plugin.yaml` at the plugin root for hermes-agent compatibility:

```yaml
name: <plugin-name>
version: <version>
description: "<description>"
author: <author>
kind: backend  # or standalone (no Python scripts)
platforms:
  - linux
  - macos
  - windows
provides_tools:          # list script basenames (no .py) that expose callable tools
  - script_name
skills:                  # list skill directory names under skills/
  - skill-name
```

- `kind: standalone`: Plugin contains prompts/skills but no callable Python tools.
- `kind: backend`: Plugin has Python scripts in `scripts/` invoked by agents.

---

## Hermes Wiring (`__init__.py`)

If the plugin provides callable Python scripts in `scripts/`, scaffold `__init__.py` at the plugin root:

```python
from __future__ import annotations
from pathlib import Path

_HERE = Path(__file__).resolve().parent

def register(ctx) -> None:
    # Register skills
    for skill_dir in (_HERE / "skills").iterdir():
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            ctx.register_skill(name=skill_dir.name, path=skill_dir)
```

---

## Hub-and-Spoke Shared Script Pattern

When a script or reference is shared across multiple skills in the same plugin:
- Canonical file lives at the plugin root (`plugins/<plugin>/scripts/` or `plugins/<plugin>/references/`).
- Consuming skills contain only file-level symlinks pointing to the hub.
- Symlinks are created and registered via `symlink_manager.py create`.

```bash
python plugins/dev-utils/scripts/symlink_manager.py create \
  --src plugins/<plugin>/scripts/<canonical>.py \
  --dst plugins/<plugin>/skills/<skill>/scripts/<name>.py
```

---

## Marketplace Integration

- When distributed via `marketplace.json`, set `"strict": true` explicitly.
- Ensure the plugin path exists in the repository before adding to the catalog.
- Verify using `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit_marketplace_sources.py .`.

---

## Plugin Architecture Invariants

- **No Cross-Plugin Imports**: Never import Python code from another plugin.
- **File-Level Symlinks Only**: No directory symlinks or duplicated code copies.
- **Self-Contained Skills**: Installed skills must run independently of source checkouts.
