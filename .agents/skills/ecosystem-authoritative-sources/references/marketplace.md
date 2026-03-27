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
- **Local Paths**: `/plugin marketplace add ./my-marketplace` (directory must contain `.claude-plugin/marketplace.json`)
- **Remote URLs**: Directly to `marketplace.json` (Note: internal relative plugin references may fail if the market isn't a git clone or real folder).

On success: `Successfully added marketplace: <marketplace-id>`

### Installing Plugins
Once a marketplace catalog is added, individual plugins can be installed into specific scopes:
- **User scope (`user`)**: Globally available across all projects (`~/.claude/settings.json`). This is the default.
- **Project scope (`project`)**: Checked into source logic for team sharing (`.claude/settings.json`).
- **Local scope (`local`)**: Specific to the project but git-ignored (`.claude/settings.local.json`).

After install, run `/reload-plugins` to activate without restarting. Output:
```
Reloaded: N plugins · N skill · N agents · N hooks · N plugin MCP servers · N plugin LSP server
```

### Settings JSON Format (Verified — Claude Code 2.1.81)

`extraKnownMarketplaces` is a **keyed object**, not an array. `enabledPlugins` uses `"plugin-name@marketplace-id": true` format:

```json
{
  "extraKnownMarketplaces": {
    "richfrem-agent-plugins-skills": {
      "source": {
        "source": "github",
        "repo": "richfrem/agent-plugins-skills"
      }
    }
  },
  "enabledPlugins": {
    "context-bundler@richfrem-agent-plugins-skills": true,
    "pyright-lsp@claude-plugins-official": true
  }
}
```

### Plugin Manager TUI (`/plugin`)

Running `/plugin` opens the full TUI with tabs: **Plugins · Discover · Installed · Marketplaces · Errors**

**Marketplaces tab** shows each registered marketplace:
```
• claude-plugins-official *         ← * = built-in/pinned
  anthropics/claude-plugins-official
  117 available • 2 installed • Updated 3/22/2026

• richfrem-agent-plugins-skills
  richfrem/agent-plugins-skills
  27 available • 1 installed • Updated 3/22/2026
```

**Installed plugin detail view:**
```
plugin-name @ marketplace-id
Scope: project
Version: 2.0.0
<description>

Author: Author Name
Status: Enabled

Installed components:
• Skills: skill-a, skill-b
```
Options: Disable · Mark for update · Update now · Uninstall · View repository

### Prebuilt & Official Tooling
- **Anthropic Official Marketplace (`claude-plugins-official`)**: Pre-installed, marked with `*` in the Marketplaces tab. Categories: Code Intelligence (LSP plugins), External Integrations (`github`, `gitlab`, `slack`, `figma`, `linear`, `notion`, `vercel`, `sentry`, etc.), Development Workflows (`commit-commands`, `pr-review-toolkit`, `plugin-dev`), Output Styles.
- **Code Intelligence Plugins**: LSP plugins only configure the connection. The underlying binary (e.g. `pyright-langserver`, `typescript-language-server`) MUST be installed in `$PATH`. Check the **Errors** tab in `/plugin` for `Executable not found in $PATH`.
- **Demo marketplace** (`anthropics/claude-code`): Add with `/plugin marketplace add anthropics/claude-code` — example plugins showing what's possible.
- **Submit to official marketplace**: Claude.ai: `claude.ai/settings/plugins/submit` · Console: `platform.claude.com/plugins/submit`.

---

## Management Commands

```bash
# Marketplace management
/plugin marketplace list                      # list all registered
/plugin marketplace update <name>             # refresh catalog
/plugin marketplace remove <name>             # remove (uninstalls its plugins)

# Plugin management
/plugin install <plugin>@<marketplace>        # install (user scope default)
/plugin disable <plugin>@<marketplace>        # disable without uninstalling
/plugin enable <plugin>@<marketplace>         # re-enable
/plugin uninstall <plugin>@<marketplace>      # remove completely
claude plugin install <plugin> --scope project  # target specific scope

# Reload without restarting
/reload-plugins
```

Shortcuts: `/plugin market` = `/plugin marketplace`, `rm` = `remove`. Requires Claude Code v1.0.33+.

Plugin commands are namespaced: a plugin named `commit-commands` exposes `/commit-commands:commit`.

---

## Environment Variables

| Variable | Purpose |
|---|---|
| `CLAUDE_CODE_PLUGIN_SEED_DIR` | Pre-populate plugins for containers/CI (mirrors `~/.claude/plugins` structure; read-only, separate with `:` for multiple) |
| `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS` | Git timeout in ms (default: 120000). Increase for large repos or slow networks |
| `GITHUB_TOKEN` / `GH_TOKEN` | Auth for private GitHub repos (required for background auto-updates) |
| `GITLAB_TOKEN` / `GL_TOKEN` | Auth for private GitLab repos |
| `BITBUCKET_TOKEN` | Auth for private Bitbucket repos |
| `DISABLE_AUTOUPDATER` | Disable Claude Code auto-updates (set `FORCE_AUTOUPDATE_PLUGINS=true` to keep plugin updates) |

---

## Release Channels Pattern

Point two marketplace entries at different `ref` values of the same repo:
```json
{ "name": "stable-tools", "plugins": [{ "source": { "source": "github", "repo": "acme/plugin", "ref": "stable" } }] }
{ "name": "latest-tools", "plugins": [{ "source": { "source": "github", "repo": "acme/plugin", "ref": "latest" } }] }
```
Each ref's `plugin.json` must declare a **different `version`** — same version = Claude Code treats them as identical and skips the update. Assign to user groups via managed `extraKnownMarketplaces`.
