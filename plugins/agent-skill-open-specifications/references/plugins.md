# Plugins Research

This document captures our accumulated knowledge and definitive specifications for **Plugins**.

**Source:** [Create plugins](https://code.claude.com/docs/en/plugins)

## Definition
Plugins let you extend Claude Code with custom functionality (skills, agents, hooks, and MCP/LSP servers) that can be shared across projects and teams. They use explicit namespaces (e.g., `/my-plugin:hello`) to avoid conflicts, support built-in versioning, and are packaged for marketplace distribution.

## Directory Structure
Plugins must follow a strict root-level structure:
- `.claude-plugin/plugin.json`: The manifest (must only contain `plugin.json`).
- `README.md`: Included as a best practice. It is highly recommended to contain a text-based file tree structure (using `├──` and `└──`) detailing the components inside the plugin and their purpose.

*See visual representation in [plugin-architecture.mmd](../assets/diagrams/plugin-architecture.mmd)*

## Component Details
- **Skills (`skills/` prefix):** Directories containing a `././SKILL.md` file. Commands are simple `.md` files in `commands/`. Always namespace (e.g., `/my-plugin:skill-name`).
- **Agents (`agents/` prefix):** Markdown files outlining capabilities and defining specialized subagent behaviors.
- **Hooks (`hooks.json`):** Event handlers (e.g., `PostToolUse`, `PreToolUse`) that automate shell scripts, prompt evaluation, or subagents.
- **MCP Servers (`.mcp.json`):** Bundles Model Context Protocol servers to provide external tools seamlessly.
- **LSP Servers (`.lsp.json`):** Language server configurations for real-time code intelligence (diagnostics, references).

## Environment Variables & Caching
- **Plugin Cache:** Installed marketplace plugins are copied to a cache (`~/.claude/plugins/cache`).
- **`plugins`:** Always use this environment variable inside `hooks.json`, `.mcp.json`, and scripts to reference the absolute path of your plugin (e.g. `"plugins/scripts/execute.py"`).

## Installation Scopes
`user` (global), `project` (team, `.claude/settings.json`), `local` (git-ignored), `managed` (read-only).

## plugin.json Manifest Schema

The manifest lives at `.claude-plugin/plugin.json` (hyphen, not underscore).

**Required (only `name` is truly required):**
```json
{
  "name": "plugin-name"
}
```

**Full recommended manifest:**
```json
{
  "name": "plugin-name",
  "version": "0.1.0",
  "description": "Brief explanation of plugin purpose",
  "author": {
    "name": "Author Name"
  }
}
```

**Optional metadata fields:** `homepage`, `repository`, `license`, `keywords`

**Custom path overrides (supplements auto-discovery, does not replace it):**
```json
{
  "commands": "./custom-commands",
  "agents": ["./agents", "./specialized-agents"],
  "hooks": "./config/hooks.json",
  "mcpServers": "./.mcp.json"
}
```

**Documentation arrays (ignored by runtime, kept for human readability):**

The agent runtime auto-discovers skills from `skills/*/././SKILL.md`, agents from `agents/`,
etc. These arrays are NOT read by Claude/Cowork, but are useful for humans browsing
the manifest:
```json
{
  "skills": ["skill-a", "skill-b"],
  "agents": [],
  "hooks": [],
  "commands": [],
  "scripts": ["scripts/my_tool.py"]
}

**No cross-plugin dependencies.** There is no `dependencies` field in the official spec.
Plugins must be self-contained -- any script a plugin needs must be copied into its own
`scripts/` directory. See ADR-004.
```

**Schema rules:**
- `name` must be kebab-case (lowercase, hyphens, no spaces)
- `version` is semver - start at `0.1.0`
- `author` is an object with a `name` field, NOT a string
- No `author.url` field (not in spec)
- No `commands_dir` or `skills_dir` fields (auto-discovered)

## Portability and Discovery

| Component | Universal Bridge (.agents) | Claude Code Native |
|-----------|-------------------------------|-------------------|
| `skills/` | Portable - installed everywhere | Discovered natively |
| `agents/` | Included in bridge (.agents)  | Discovered natively |
| `commands/`| Included in bridge (.agents)  | Discovered natively |

**Key rule:** If you want something universally installable across all agents
(Claude, Gemini, Copilot, Antigravity, Cursor, etc.), it MUST be a skill.
Agents and commands are Claude Code-only constructs.

## Development & Usage
- During local development, you load plugins using the `--plugin-dir` flag: `claude --plugin-dir ./my-first-plugin`.
- Standalone `.claude/` configurations can be manually migrated to this plugin structure to enable sharing.

