---
concept: ecosystem-authoritative-sources
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/ecosystem-authoritative-sources/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.031638+00:00
cluster: reference
content_hash: ec512657fe9ec315
---

# Ecosystem Authoritative Sources

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: ecosystem-authoritative-sources
description: Provides information about how to create, structure, install, and audit Agent Skills, Plugins, Antigravity Workflows, and Sub-agents. Trigger this when specifications, rules, or best practices for the ecosystem are required.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `../../requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Ecosystem Authoritative Sources

# Official Open Standard Recognition
**Important:** This reference library draws heavy inspiration and structural standards directly from the Anthropic Claude Plugins official repositories. Please refer to:
- **Foundational Specification**: `https://github.com/anthropics/claude-plugins-official/tree/main/plugins/plugin-dev`
- **L4 Interaction & Execution Patterns**: Derived from `https://github.com/anthropics/claude-knowledgework-plugins` (specifically the Legal and Bio-Research plugins).
- **Skill Creator 2.0 (Anthropic, March 2026)**: `https://github.com/anthropics/skills/tree/main/skills/skill-creator`
- **Anthropic Official Claude Code docs**: `https://docs.anthropic.com/en/docs/claude-code/`

## Agentic OS / Agent Harness Pattern
The Agentic OS is a synthesized runtime environment pattern built from Anthropic primitives:

| Component | Anthropic Primitive | Official URL |
|-----------|--------------------|--------------|
| Project kernel | `CLAUDE.md` hierarchy (5 scopes) | https://docs.anthropic.com/en/docs/claude-code/memory |
| Scheduled tasks | `/loop` command | https://docs.anthropic.com/en/docs/claude-code/loop |
| Task specialists | Sub-agents (`.claude/agents/`) | https://docs.anthropic.com/en/docs/claude-code/sub-agents |
| Automation | Hooks (`hooks.json`) | https://docs.anthropic.com/en/docs/claude-code/hooks |
| Personal shortcuts | Slash commands (`.claude/commands/`) | https://docs.anthropic.com/en/docs/claude-code/slash-commands |
| Per-project config | Plugin settings (`.claude/*.local.md`) | Anthropic plugin-dev docs |

The `context/` folder structure, `heartbeat.md`, `START_HERE.md`, and memory log patterns
are community conventions built on top of these primitives (not Anthropic-official).

For bootstrapping Agentic OS in a project, use the `agentic-os-init` skill:
```
.agents/skills/agentic-os-init/SKILL.md
```

# The Library
The following open standards are available for review:

This skill provides comprehensive information and reference guides about the conventions and constraints defining the extensibility ecosystem.

Because of the Progressive Disclosure architecture, you should selectively read the reference files below only when you need detailed information on that specific topic.

## Installation

### Claude Plugin Marketplace (Claude Code native — verified 2.1.81+)
Repos with a `.claude-plugin/marketplace.json` at the root can be registered as a marketplace:
```
/plugin marketplace add owner/repo
/plugin install <plugin-name>
```
Claude Code fetches from the default branch. The `marketplace.json` must be merged to `main` before consumers can install.

`/plugin install <name>` opens an **interactive Plugins panel** (not plain stdout) showing plugin details and a scope picker (user / project / local). The command returns no terminal output — UI renders in the panel.

**Source types in marketplace.json:**
- Relative path (same-repo monorepo): `"source": "./plugins/my-plugin"` — resolved from repo root
- Git subdirectory (sparse clone): `"source": { "type": "git-subdir", "url": "...", "subdir": "..." }`
- npm package: `"source": { "type": "npm", "package": "@scope/pkg", "version": "^1.0.0" }`
- Non-GitHub git: `"source": { "type": "url", "url": "...", "ref": "main" }`

**`strict` field:** `true` = plugin's own `plugin.json

*(content truncated)*

## See Also

- [[acceptance-criteria-ecosystem-authoritative-sources]]
- [[procedural-fallback-tree-ecosystem-authoritative-sources]]
- [[acceptance-criteria-ecosystem-authoritative-sources]]
- [[acceptance-criteria-ecosystem-authoritative-sources]]
- [[procedural-fallback-tree-ecosystem-authoritative-sources]]
- [[acceptance-criteria-ecosystem-authoritative-sources]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/ecosystem-authoritative-sources/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.031638+00:00
