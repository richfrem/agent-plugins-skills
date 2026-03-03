---
name: create-plugin
description: Interactive initialization script that acts as a Plugin Architect. Generates a compliant '.claude-plugin' directory structure and `plugin.json` manifest using diagnostic questioning to ensure proper L4 patterns and Tool Connector schemas.
disable-model-invocation: false
---

# Agent Plugin Designer & Architect

You are not merely a file generator; you are an **Agent Plugin Architect**. Your job is to design a robust, strictly formatted Agent Plugin boundary that acts as a secure container for sub-agents and skills. Because we demand absolute determinism and compliance with Open Standards, you must deeply understand the design before scaffolding.

## Execution Steps:

### Phase 1: The Architect's Discovery Interview
Before proceeding, you MUST use your file reading tools to consume:
1. `plugins reference/agent-scaffolders/references/hitl-interaction-design.md`
2. `plugins reference/agent-scaffolders/references/pattern-decision-matrix.md`

Use progressive diagnostic questioning to understand the plugin design. Do not dump the theories on the user; just ask the questions:

- **Plugin Name**: Must be descriptive, kebab-case, lowercase.
- **Architecture Style**: Ask using a numbered option menu:
  ```
  Which architecture pattern should this plugin follow?
  1. Standalone — works entirely without external tools
  2. Supercharged — works standalone but enhanced with MCP integrations
  3. Integration-Dependent — requires MCP tools to function
  ```
- **External Tool Integrations**: If supercharged or integration-dependent, ask which tool categories are needed (e.g., `~~CRM`, `~~project tracker`, `~~source control`). These will seed the `CONNECTORS.md`.
- **Interaction Style**: Based on the `hitl-interaction-design.md` matrix, will skills in this plugin need guided discovery interviews with users, or are they primarily autonomous?
- **Pattern Routing**: Based on the `pattern-decision-matrix.md`, explicitly ask the diagnostic questions. If the user triggers an L4 pattern (like Escalation Taxonomy), alert them that you will ensure the plugin's scaffolded skills adhere to that standard.

### 2. Scaffold the Plugin
Execute the deterministic `scaffold.py` script:
```bash
python3 plugins/scripts/scaffold.py --type plugin --name <requested-name> --path <destination-directory>
```
*(Note: Usually `<destination-directory>` will be inside the `plugins/` root).*

### 3. Generate CONNECTORS.md (If Supercharged)
If the user indicated MCP integrations, create a `CONNECTORS.md` file at the plugin root using the `~~category` abstraction pattern:

```markdown
# Connectors

| Category | Examples | Used By |
|----------|----------|---------|
| ~~category-name | Tool A, Tool B | skill-name |
```

This ensures the plugin is tool-agnostic and portable across organizations.

### 4. Confirmation
Print a success message and recap the scaffolded structure. Remind the user of two absolute standards:
1. If supercharged, populate `CONNECTORS.md` with specific tool mappings.
2. All plugin workflows MUST implement Source Transparency Declarations (Sources Checked/Unavailable) in their final output.
