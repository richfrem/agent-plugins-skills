---
concept: marketplace-research
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/ecosystem-authoritative-sources/references/reference/marketplace.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.051639+00:00
cluster: plugin
content_hash: 14c662aeee651185
---

# Marketplace Research

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Marketplace Research

This document captures our accumulated knowledge and definitive specifications for the **Marketplace**.

**Source:** [Claude Plugin Marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)

## Definition
A **plugin marketplace** is a catalog used to distribute plugins. It provides centralized discovery, version tracking, automatic updates, and supports multiple source types like git repositories and local paths. When a user installs a plugin, the plugin directory is copied to a cache, so relative paths outside the plugin directory (`../`) do not work unless they are symlinks.

## The `marketplace.json` Registry
The `marketplace.json` file is a manifest placed inside a `.claude-plugin/` directory at the root of a repository. It lists plugins and where to find them.

### Required Catalog Fields
- `name`: Marketplace identifier (kebab-case). Public-facing — users see it as the `@marketplace` suffix when installing.
- `owner`: Object with at least a `name` field; `email` is optional.
- `plugins`: Array of plugin entries available in the marketplace.

**Reserved names** (blocked): `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences`. Impersonating names (e.g. `official-claude-plugins`) are also blocked.

**Optional metadata:**
- `metadata.description`: Brief marketplace description.
- `metadata.version`: Marketplace version.
- `metadata.pluginRoot`: Base directory prepended to relative plugin source paths. Setting `"./plugins"` lets entries use `"source": "formatter"` instead of `"source": "./plugins/formatter"`.

### Plugin Entry Fields
Each entry in the `plugins` array defines how a specific plugin is fetched. You can include any `plugin.json` field plus these marketplace-specific fields:
- `name` (required): Plugin identifier (kebab-case).
- `source` (required): Where to fetch the plugin:
    - Relative Path: `"./plugins/my-plugin"` — must start with `./`. Only works when marketplace added via Git clone, not direct URL.
    - GitHub: `{"source": "github", "repo": "owner/repo", "ref": "branch", "sha": "40-char-hash"}`.
    - Git URL: `{"source": "url", "url": "https://gitlab.com/owner/repo.git", "ref": "main", "sha": "..."}`.
    - Git subdirectory (sparse clone): `{"source": "git-subdir", "url": "https://github.com/owner/repo", "path": "plugins/my-plugin", "ref": "main"}`. Field is `path` not `subdir`.
    - npm: `{"source": "npm", "package": "@scope/plugin", "version": "^1.0.0", "registry": "https://registry.npmjs.org"}`.
- `strict` (default `true`): When `true`, `plugin.json` is authoritative and marketplace entry supplements it. When `false`, marketplace entry is the entire definition — plugin must NOT also declare components in `plugin.json` (conflict = load failure).
- `version`: **Warning** — do not set in both the marketplace entry and `plugin.json`. The `plugin.json` wins silently; marketplace version is ignored. For relative-path plugins, set version in marketplace entry. For all other sources, set in `plugin.json`.
- `category`, `tags`: For organization and searchability.
- `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`: Custom path overrides.
- Custom component paths: The marketplace entry can also specify paths to `commands`, `agents`, `hooks`, etc., relative to the plugin's root. For paths referencing files after the plugin is cached, the `plugins` variable can be used.

## Discovery and Installation

Marketplaces are primarily accessed in Claude Code via `/plugin` (TUI) or CLI commands (`claude plugin install`).

### Adding Marketplaces
Marketplaces must be explicitly added so their catalog can be discovered:
- **GitHub**: `/plugin marketplace add owner/repo` (e.g., `anthropics/claude-code`)
- **Git URLs**: `/plugin marketplace add https://gitlab.com/company/plugins.git`
- **Local Paths**: `/plugin marketplace add ./my-marketplace` (directory mu

*(content truncated)*

## See Also

- [[research-summary-agent-operating-systems-agent-os]]
- [[research-summary-agent-operating-systems-aos]]
- [[sources-template---research-topic-name]]
- [[architecture-reference---manage-marketplace]]
- [[marketplace-schema-reference]]
- [[marketplace-manager]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/ecosystem-authoritative-sources/references/reference/marketplace.md`
- **Indexed:** 2026-04-17T06:42:10.051639+00:00
