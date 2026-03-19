# Marketplace Research

This document captures our accumulated knowledge and definitive specifications for the **Marketplace**.

**Source:** [Claude Plugin Marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)

## Definition
A **plugin marketplace** is a catalog used to distribute plugins. It provides centralized discovery, version tracking, automatic updates, and supports multiple source types like git repositories and local paths. When a user installs a plugin, the plugin directory is copied to a cache, so relative paths outside the plugin directory (`../`) do not work unless they are symlinks.

## The `marketplace.json` Registry
The `marketplace.json` file is a manifest placed inside a `.claude-plugin/` directory at the root of a repository. It lists plugins and where to find them.

### Required Catalog Fields
- `name`: Marketplace identifier (kebab-case).
- `owner`: Object with at least a `name` field for the maintainer.
- `plugins`: Array of plugin entries available in the marketplace.

### Plugin Entry Fields
Each entry in the `plugins` array defines how a specific plugin is fetched. You can override or supplement the plugin's internal `plugin.json` fields via the marketplace entry.
- `name` (required): Plugin identifier (kebab-case).
- `source` (required): Where to fetch the plugin. Can be:
    - Relative Path: `"./plugins/my-plugin"` (Note: only works if the marketplace itself was installed via a Git repository clone or local path, not a direct URL).
    - GitHub Source: `{"source": "github", "repo": "owner/repo", "ref": "branch", "sha": "commit-hash"}`.
- `strict`: Boolean controlling whether the plugin's internal `plugin.json` is the authority (`true`, default), or if the marketplace entry is the entire definition (`false`), overriding the plugin's native manifest.
- Custom component paths: The marketplace entry can also specify paths to `commands`, `agents`, `hooks`, etc., relative to the plugin's root. For paths referencing files after the plugin is cached, the `plugins` variable can be used.

## Discovery and Installation

Marketplaces are primarily accessed in Claude Code via `/plugin` (TUI) or CLI commands (`claude plugin install`).

### Adding Marketplaces
Marketplaces must be explicitly added so their catalog can be discovered:
- **GitHub**: `/plugin marketplace add owner/repo` (e.g., `anthropics/claude-code`)
- **Git URLs**: `/plugin marketplace add https://gitlab.com/company/plugins.git`
- **Local Paths**: `/plugin marketplace add ./my-marketplace` (directory must contain `.claude-plugin/marketplace.json`)
- **Remote URLs**: Directly to `marketplace.json` (Note: internal relative plugin references may fail if the market isn't a git clone or real folder).

### Installing Plugins
Once a marketplace catalog is added, individual plugins can be installed into specific scopes:
- **User scope (`user`)**: Globally available across all projects (`~/.claude/settings.json`). This is the default.
- **Project scope (`project`)**: Checked into source logic for team sharing (`.claude/settings.json`).
- **Local scope (`local`)**: Specific to the project but git-ignored (`.claude/settings.local.json`).

### Prebuilt & Official Tooling
- **Anthropic Official Marketplace (`claude-plugins-official`)**: Pre-installed. Discoverable under the Discover tab. Notably hosts Code Intelligence plugins (e.g., `typescript-lsp`, `python-lsp`) and External Integrations (e.g., `github`, `slack`, `figma`).
- **Code Intelligence Plugins**: LSP plugins only configure the connection to the Language Server; the underlying binary (like `pyright` or `typescript-language-server`) MUST be installed manually by the user in their OS `$PATH`.
