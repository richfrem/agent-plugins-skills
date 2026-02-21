---
name: ecosystem-authoritative-sources
description: Provides information about how to create, structure, install, and audit Agent Skills, Plugins, Antigravity Workflows, and Sub-agents. Trigger this when specifications, rules, or best practices for the ecosystem are required.
disable-model-invocation: false
---

# Ecosystem Authoritative Sources

# Official Open Standard Recognition
**Important:** This reference library draws heavy inspiration and structural standards directly from the Anthropic Claude Plugins official repository. For the foundational specification, always refer to:
- `https://github.com/anthropics/claude-plugins-official/tree/main/plugins/plugin-dev`

# The Library
The following open standards are available for review:

This skill provides comprehensive information and reference guides about the conventions and constraints defining the extensibility ecosystem.

Because of the Progressive Disclosure architecture, you should selectively read the reference files below only when you need detailed information on that specific topic.

## Table of Contents
To read any of the reference guides, use your file system tools to `cat` or `view` the relevant file.

*   **Agent Skills**: Definition, lifecycle, progressive disclosure, and constraints of `.claude/skills`.
    *   [reference/skills.md](plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/reference/skills.md)
    *   [reference/skill-execution-flow.mmd](plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/reference/skill-execution-flow.mmd)
*   **Claude Plugins**: Specification for the `.claude-plugin` architecture, manifest setup, and distribution.
    *   [reference/plugins.md](plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/reference/plugins.md)
    *   [reference/plugin-architecture.mmd](plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/reference/plugin-architecture.mmd)
*   **Antigravity Workflows & Rules (and Legacy Commands)**: Specifications for global/workspace Rules, deterministic trajectory Workflows, and the critical distinction between deploying **Skills** vs. Legacy **Commands**.
    *   [reference/workflows.md](plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/reference/workflows.md)
*   **Sub-Agents**: Definition, setup, and orchestration of nested contextual LLM boundaries.
    *   [reference/sub-agents.md](plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/reference/sub-agents.md)
*   **Hooks**: Lifecycle event integrations (e.g., `pre-commit`, `on-startup`).
    *   [reference/hooks.md](plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/reference/hooks.md)
*   **Marketplace**: Registering registries and interacting with the `marketplace.json` distribution format.
    *   [reference/marketplace.md](plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/reference/marketplace.md)

## Usage Instruction
Never guess the specifics of `SKILL.md` frontmatter, plugin directory limits, or workflow sizes. Read the exact specifications linked above before constructing new ecosystem extensions.
