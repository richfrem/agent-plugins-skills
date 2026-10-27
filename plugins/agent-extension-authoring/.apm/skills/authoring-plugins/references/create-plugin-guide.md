# Plugin Creation & Scaffolding Guide

Comprehensive reference guide for authoring, configuring, and packaging APM-native and Claude Code-compatible plugins.

## Contents

- [Overview & Workflow](#overview--workflow)
- [APM Package Manifest (`apm.yml`)](#apm-package-manifest-apmyml)
- [Claude Code Manifest (`.claude-plugin/plugin.json`)](#claude-code-manifest-claude-pluginpluginjson)
- [APM-Native Directory Layout (`.apm/`)](#apm-native-directory-layout-apm)
- [Self-Contained Skill Architecture](#self-contained-skill-architecture)
- [Marketplace Integration](#marketplace-integration)
- [Plugin Architecture Invariants](#plugin-architecture-invariants)

---

## Overview & Workflow

1. **Phase 1: Discovery & Scoping**: Determine plugin purpose, tools needed, and component taxonomy (skills, agents, hooks, MCP servers).
2. **Phase 2: Directory Scaffolding**: Run `scripts/scaffold_plugin.py` to create `apm.yml`, `.claude-plugin/plugin.json`, `.apm/skills/`, and `README.md`.
3. **Phase 3: Component Implementation**: Scaffold individual skills under `.apm/skills/` via `authoring-skills`, sub-agents under `.apm/agents/` via `authoring-subagents`, and hooks under `.apm/hooks/` via `authoring-instructions`.
4. **Phase 4: Validation**: Verify using `scripts/audit_plugin_structure.py`, `scripts/audit.py`, and the `packaging-with-apm` skill (`apm_build_pipeline.py`).

---

## APM Package Manifest (`apm.yml`)

Every plugin root (`plugins/<plugin>/apm.yml`) declares its APM package metadata:

```yaml
name: <plugin-name>
version: 0.1.0
description: "<description>"
author: Richard Fremmerlid
license: MIT
repository: https://github.com/richfrem/agent-plugins-skills
```

To expose the plugin from the root workspace meta-package, add a path dependency entry to the repository root `apm.yml` under `dependencies.apm`:

```yaml
dependencies:
  apm:
    - ./plugins/<plugin-name>
```

---

## Claude Code Manifest (`.claude-plugin/plugin.json`)

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
- Legacy manifests (`plugin.yaml`, `__init__.py`, `symlinks.json`, `gemini-extension.json`, `.agents/ownership/`) are retired and prohibited.

---

## APM-Native Directory Layout (`.apm/`)

All deployable primitives reside inside `.apm/`:

```text
plugins/<plugin-name>/
├── .apm/
│   ├── skills/
│   │   └── <skill-name>/
│   │       ├── SKILL.md
│   │       ├── scripts/
│   │       ├── references/
│   │       ├── assets/
│   │       ├── evals/
│   │       └── tests/
│   ├── agents/
│   │   └── <agent-name>.md
│   └── hooks/
│       ├── hooks.json
│       └── <hook-script>.py
├── .claude-plugin/
│   └── plugin.json
├── apm.yml
├── README.md
└── rules/
    └── <rule-name>.md
```

- **Rules (`rules/`)**: Source governance rules are **not** deployed by APM (**SF-9**). Setup copies needed rules into `.agent/rules/`, and `AGENTS.md` lists them there.
- **No Duplicate Primitive Directories**: Never create root `skills/`, `agents/`, or `hooks/` alongside `.apm/`.

---

## Self-Contained Skill Architecture

Every skill in `.apm/skills/<skill-name>/` is 100% self-contained:
- Scripts, references, assets, evals, and tests live directly inside `.apm/skills/<skill-name>/` as real files.
- Do **not** place shared `scripts/`, `references/`, or `assets/` at the plugin root, and do **not** create symlinks or `symlinks.json` copy manifests.
- When one skill needs functionality from another skill, delegate by skill name in natural language rather than importing or calling across skill directories (**SF-8**).

---

## Marketplace Integration

- When distributed via `marketplace.json`, set `"strict": true` explicitly.
- Ensure the plugin path exists in the repository before adding to the catalog.
- Verify using the `packaging-with-apm` skill (`audit_marketplace_sources.py`).

---

## Plugin Architecture Invariants

- **No Cross-Plugin Imports**: Never import Python code from another plugin.
- **Zero Symlinks**: Raw filesystem symlinks are prohibited (**SF-2**).
- **Self-Contained Skills**: Installed skills must run independently of source checkouts across all APM target harnesses (`claude`, `copilot`, `codex`, `antigravity`).
