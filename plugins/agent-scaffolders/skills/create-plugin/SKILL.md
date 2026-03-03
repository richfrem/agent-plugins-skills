---
name: create-plugin
description: Interactive initialization script that generates a compliant '.claude-plugin' directory structure and `plugin.json` manifest. Use when building a new plugin wrapper to distribute skills or agent logic.
disable-model-invocation: false
---

# Plugin Scaffold Generator

You are tasked with generating a new Agent Plugin boundary. Because we demand absolute determinism and compliance with Open Standards, you MUST use the internal CLI tool to scaffold the files.

## Execution Steps:

### 1. Gather Requirements
Use progressive questioning (broad → specific) to understand the plugin design:

- **Plugin Name**: Must be descriptive, kebab-case, lowercase.
- **Architecture Style**: Ask using a numbered option menu:
  ```
  Which architecture pattern should this plugin follow?
  1. Standalone — works entirely without external tools
  2. Supercharged — works standalone but enhanced with MCP integrations
  3. Integration-Dependent — requires MCP tools to function
  ```
- **External Tool Integrations**: If supercharged or integration-dependent, ask which tool categories are needed (e.g., `~~CRM`, `~~project tracker`, `~~source control`). These will seed the `CONNECTORS.md`.
- **Interaction Style**: Will skills in this plugin need guided discovery interviews with users, or are they primarily autonomous?

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
Print a success message and recap the scaffolded structure. If supercharged, remind the user to populate `CONNECTORS.md` with their specific tool mappings.
