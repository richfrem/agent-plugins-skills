---
name: ecosystem-authoritative-sources
description: Provides information about how to create, structure, install, and audit Agent Skills, Plugins, Antigravity Workflows, and Sub-agents. Trigger this when specifications, rules, or best practices for the ecosystem are required.
disable-model-invocation: false
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
plugins/agent-agentic-os/skills/agentic-os-init/SKILL.md
```

# The Library
The following open standards are available for review:

This skill provides comprehensive information and reference guides about the conventions and constraints defining the extensibility ecosystem.

Because of the Progressive Disclosure architecture, you should selectively read the reference files below only when you need detailed information on that specific topic.

## Installation (`npx skills`)
This ecosystem uses the universal `npx skills` CLI to install, update, and manage plugins across all supported agents (Claude Code, Copilot, Gemini CLI, etc).

**Quick Reference:**
*   **Install from GitHub:** `npx skills add <user>/<repo>`
*   **Install Specific Skill:** `npx skills add <user>/<repo>/plugins/<plugin-name>`
*   **Update All Skills:** `npx skills update`
*   **Local Development Install:** `rm -rf .agents/ && npx skills add ./plugins/<plugin-name> --force`

*For full installation documentation and architecture rules, strictly refer to `skills.md`.*

## Table of Contents
To read any of the reference guides, use your file system tools to `cat` or `view` the relevant file.

*   **Agent Skills**: Definition, lifecycle, progressive disclosure, and constraints of `.claude/skills/` (and equivalents like `.agent/skills/` and `.github/skills/`). Custom agents deployed as Skills are stored here as `<plugin>-<agent>/SKILL.md`.
    *   [reference/skills.md](references/skills.md)
    *   [reference/diagrams/references/diagrams/skill-execution-flow.mmd](references/diagrams/skill-execution-flow.mmd)
*   **Claude Plugins**: Specification for the `.claude-plugin` architecture, manifest setup, and distribution.
    *   [reference/plugins.md](references/plugins.md)
    *   [reference/diagrams/references/diagrams/plugin-architecture.mmd](references/diagrams/plugin-architecture.mmd)
*   **Antigravity Workflows & Rules (and Legacy Commands)**: Specifications for global/workspace Rules, deterministic trajectory Workflows, and the critical distinction between deploying **Skills** vs. Legacy **Commands**.
    *   [reference/workflows.md](references/workflows.md)
*   **Sub-Agents**: Definition, setup, and orchestration of nested contextual LLM boundaries. Sub-Agents are deployed structurally as pure Skills (mapped to `skills/<agent-name>/SKILL.md`).
    *   [reference/sub-agents.md](references/sub-agents.md)
*   **GitHub Copilot Prompts (Models)**: Documentation on the exact YAML schema, dynamic variables, and exclusion logic (`exclude-targets`) used by GitHub Copilot chat environments.
    *   [reference/github-prompts.md](references/github-prompts.md)
*   **GitHub Agentic Workflows**: Documentation on the "Continuous AI" autonomous agents responding to CI/CD events.
    *   [reference/github-agentic-./references/workflows.md](workflows.md)
*   **Hooks**: Lifecycle event integrations (e.g., `pre-commit`, `on-startup`).
    *   [reference/hooks.md](references/hooks.md)
*   **Azure AI Foundry Agents**: Documentation on how to map Open Agent-Skills to Azure Foundry Agent Service, including API payloads, constraints (e.g., 128-tool limits), and standard setups.
    *   [reference/references/azure-foundry-agents.md](references/azure-foundry-agents.md)
*   **Marketplace**: Registering registries and interacting with the `marketplace.json` distribution format.
    *   [reference/marketplace.md](references/marketplace.md)
*   **Installation & Management**: Universal CLI guidelines for `npx skills`, including remote installations, updates, and local development workarounds.
    *   [reference/npx-./references/skills.md](skills.md)

## Anthropic Plugin-Dev Key Learnings (March 2026)
The following patterns were confirmed from Anthropic's official `plugin-dev` plugin:
- **`${CLAUDE_PLUGIN_ROOT}`**: Required for all absolute path references inside plugin scripts/hooks (portability).
- **Prompt-based hooks**: LLM-driven hooks run in parallel; use for semantic decisions. Command-based hooks for deterministic validation.
- **`model: inherit`**: Default for sub-agents. Explicitly setting a model pins the agent to a version.
- **`<example>` blocks**: Use 2-4 `<example>` blocks in agent frontmatter descriptions for richer trigger context (including proactive and negative instructions).
- **`.local.md` settings**: Store per-project agent config in `.claude/<plugin-name>.local.md` (always gitignore).
- **`examples/` directory**: Add to skills alongside `references/` for working code samples.
- **SKILL.md target**: 1500-2000 words / under 500 lines. Third-person description, imperative body.
- **Description checklist**: 3-5 triggers, 100-word limit, precise action verbs, 1 negative boundary.

## Usage Instruction
Never guess the specifics of `SKILL.md` frontmatter, plugin directory limits, or workflow sizes. Read the exact specifications linked above before constructing new ecosystem extensions.
