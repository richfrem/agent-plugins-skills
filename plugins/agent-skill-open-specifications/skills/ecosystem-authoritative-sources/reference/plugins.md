# Plugins Research

This document captures our accumulated knowledge and definitive specifications for **Plugins**.

**Source:** [Create plugins](https://code.claude.com/docs/en/plugins)

## Definition
Plugins let you extend Claude Code with custom functionality (skills, agents, hooks, and MCP/LSP servers) that can be shared across projects and teams. They use explicit namespaces (e.g., `/my-plugin:hello`) to avoid conflicts, support built-in versioning, and are packaged for marketplace distribution.

## Directory Structure
Plugins must follow a strict root-level structure:
- `.claude-plugin/plugin.json`: The manifest (must only contain `plugin.json`).
- `README.md`: Included as a best practice. It is highly recommended to contain a text-based file tree structure (using `├──` and `└──`) detailing the components inside the plugin and their purpose.

*See visual representation in [plugin-architecture.mmd](./plugin-architecture.mmd)*

## Component Details
- **Skills (`skills/` prefix):** Directories containing a `SKILL.md` file. Commands are simple `.md` files in `commands/`. Always namespace (e.g., `/my-plugin:skill-name`).
- **Agents (`agents/` prefix):** Markdown files outlining capabilities and defining specialized subagent behaviors.
- **Hooks (`hooks.json`):** Event handlers (e.g., `PostToolUse`, `PreToolUse`) that automate shell scripts, prompt evaluation, or subagents.
- **MCP Servers (`.mcp.json`):** Bundles Model Context Protocol servers to provide external tools seamlessly.
- **LSP Servers (`.lsp.json`):** Language server configurations for real-time code intelligence (diagnostics, references).

## Environment Variables & Caching
- **Plugin Cache:** Installed marketplace plugins are copied to a cache (`~/.claude/plugins/cache`).
- **`${CLAUDE_PLUGIN_ROOT}`:** Always use this environment variable inside `hooks.json`, `.mcp.json`, and scripts to reference the absolute path of your plugin (e.g. `"${CLAUDE_PLUGIN_ROOT}/scripts/execute.sh"`).

## Installation Scopes
`user` (global), `project` (team, `.claude/settings.json`), `local` (git-ignored), `managed` (read-only).
- `description`: A summary displayed during installation/browsing.
- `version`: Tracks releases using semantic versioning.
- `author`: (Optional) Object containing `name` and `email`.

## Development & Usage
- During local development, you load plugins using the `--plugin-dir` flag: `claude --plugin-dir ./my-first-plugin`.
- Standalone `.claude/` configurations can be manually migrated to this plugin structure to enable sharing.
