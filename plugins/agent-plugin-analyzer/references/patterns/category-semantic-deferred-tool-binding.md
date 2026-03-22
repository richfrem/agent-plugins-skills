# Category-Semantic Deferred Tool Binding

**Status:** Draft
**Pattern Type:** Structural Constraint
**Applicable Domain:** Scaffolding, Platform Deployment, Customization, Orchestration

## Executive Summary
Artifacts are authored with placeholders that encode a human-readable **tool category**—not an abstract variable identifier—using a lightweight sigil (e.g., `~~project tracker`). The placeholder is simultaneously a machine-detectable substitution point, a semantic description of what belongs there, and the direct keyword input to a downstream tool registry search.

## The Abstract Problem
When creating templates or plugins for external distribution, you don't know what specific tools the downstream user has (Slack vs Teams, Jira vs Asana). If you hardcode standard variables (e.g., `${PROJECT_MANAGEMENT_TOOL}`), the resolving agent doesn't actually know what tools qualify for that variable without a separate, fragile mapping table.

## The Target
Any workflow that scaffolds a system, writes a template, or builds a plugin meant to be deployed across different organizations with different tech stacks.

## The Core Mechanic
A lightweight token (e.g., `~~<natural language category>`) is used directly in the text. 
Example: `Create a ticket in ~~project tracker`.
When a customizer agent processes this file later, the text `project tracker` itself is used to query the MCP tool registry (or ask the user) to resolve the correct tool. The semantic description *IS* the lookup key.

## Distinction from Similar Patterns
- **Standard Templating**: Variables like `{{tool_name}}` are opaque identifiers. CSDTB placeholders are human-readable category classifications.
- **Environment Substitution**: Env vars resolve silently from the system context. CSDTB actively triggers a tool discovery/registry search workflow.

## Implementation Standard

```markdown
1. Always use `~~<category>` for placeholder values if the target tool is unknown.
2. The category must be plain, human-readable, lowercase English (e.g., `~~chat`, `~~project tracker`).
3. Maintain a `././CONNECTORS.md` file that formally maps the categories used in the placeholders to known tool ecosystem equivalents.
4. When customizing, use the category text directly as the search query against the tool registry.
5. Never expose the `~~` syntax or the word "placeholder" to the end user.
```

## Anti-Patterns
1. **The Opaque Variable**: Using `~~TOOL_1` instead of `~~chat`.
2. **The Hardcoded Default**: Writing "Create an issue in Jira" when the target organization actually uses Linear.
3. **The User-Facing Sigil**: Asking the user "What should I replace ~~project tracker with?" instead of "Which project tracker does your team use?"
