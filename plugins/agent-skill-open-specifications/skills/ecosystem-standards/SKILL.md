---
name: ecosystem-standards
description: Provides active execution protocols to rigorously audit how code, directory structures, and agent actions comply with the authoritative ecosystem specs. Trigger when validating new skills, plugins, or workflows.
disable-model-invocation: false
---

# Ecosystem Standards Review Protocol

This skill details how to perform an audit on new or existing capabilities (Skills, Plugins, Workflows, Sub-Agents, and Hooks) against authoritative ecosystem specifications to ensure they are created, installed, and structured correctly.

## Instructions
When invoked to review a codebase component or a planned extension:

1.  **Identify the Component Type**: Determine if the subject is a Plugin boundary, an Agent Skill, an Antigravity Workflow/Rule, a Sub-Agent, or a Hook.
2.  **Recall the Specs**: Before reviewing, read the relevant specification file found in the `ecosystem-authoritative-sources` skill library.
    *   *Path:* `plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/reference/*.md`
3.  **Perform Rigorous Audit**:
    *   **Structure**: Does the directory schema match the standard? (e.g., `.claude-plugin/plugin.json`, `my-skill/SKILL.md`).
    *   **Content**: Does the YAML frontmatter adhere precisely to rules (e.g. `description` length limits, lower-case hyphenated names).
    *   **Progressive Disclosure**: For Skills, is the `SKILL.md` file appropriately constrained (< 500 lines) with extraneous detail pushed to one-level deep reference files?
    *   **Anti-Patterns**: Check for hardcoded credentials, Windows style paths (`\`), silent error punting, and missing namespaces on MCP tool calls.
4.  **Produce Feedback**: Provide explicit, granular feedback outlining exactly which ecosystem constraints were violated and concrete suggestions for fixing them. Ensure your feedback is actionable.
