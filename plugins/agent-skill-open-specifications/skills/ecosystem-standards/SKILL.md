---
name: ecosystem-standards
description: Provides active execution protocols to rigorously audit how code, directory structures, and agent actions comply with the authoritative ecosystem specs. Trigger when validating new skills, plugins, or workflows.
disable-model-invocation: false
allowed-tools: Bash, Read, Write
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
    *   **Content**: Does the YAML frontmatter adhere precisely to rules (e.g. `description` length limits, lower-case hyphenated names). If generating commands intended for explicit exclusion from GitHub/Gemini, use the `exclude-targets` array flag as defined in the standards.
    *   **Progressive Disclosure**: For Skills, is the `SKILL.md` file appropriately constrained (< 500 lines) with extraneous detail pushed to one-level deep reference files?
    *   **Multi-CLI Support**: When integrating agent CLI plugins, support exists for `claude-cli`, `gemini-cli`, and `copilot-cli`. Plugins must reflect the native CLI syntax in their system files.
    *   **Anti-Patterns**: Check for hardcoded credentials, Windows style paths (`\`), silent error punting, and missing namespaces on MCP tool calls.
    *   **Connector Abstraction**: If the plugin uses MCP tools, does it include a `CONNECTORS.md` using the `~~category` abstraction pattern instead of hardcoding specific tool names? This is required for portability.
    *   **Interaction Design Quality**: For skills with user interaction, verify they use appropriate patterns:
        - Discovery phases use progressive questioning (broad → specific), not question walls
        - Decision points offer numbered option menus (3-7 items max)
        - Expensive operations have confirmation gates
        - Multi-step workflows include inline progress indicators
        - Skills end with next-action menus, not dead ends
        - Workflows taking long documents gracefully degrade using Document Format Agnosticism.
    *   **Dual-Mode Architecture**: If the skill both creates new artifacts AND improves existing ones, verify it implements the Bootstrap + Iteration dual-mode pattern with separate sections and trigger phrases.
    *   **Output Templates**: If the skill generates reports or artifacts, verify it either defines an output template or negotiates the format with the user.
    *   **Escalation and Safety**: Workflows with external risk must explicitly implement Graduated Autonomy Routing and Escalation Trigger Taxonomies rather than blanket-stopping on all issues.
    *   **Source Transparency**: Data synthesis output MUST conclude with explicit `Sources Checked` and `Sources Unavailable` blocks.
4.  **Produce Feedback**: Provide explicit, granular feedback outlining exactly which ecosystem constraints were violated and concrete suggestions for fixing them. Ensure your feedback is actionable.
