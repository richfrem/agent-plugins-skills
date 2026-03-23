---
name: manage-marketplace
description: >
  This skill should be used when the user wants to "create a marketplace", 
  "setup a marketplace catalog", "scaffold marketplace.json", or "initialize 
  a plugin registry". Use this even if they just mention "setting up a marketplace".
allowed-tools: Bash, Read, Write
---

# Marketplace Manager

Guidelines for authoring, appending, and distributing plugin marketplace catalogs.

## Step 1: Initialize the Marketplace

To create a new marketplace:
1.  **Create directory**: Create a dedicated git repository or local path for the catalog.
2.  **Create config directory**: Create a `.claude-plugin/` directory at the root.
3.  **Create catalog file**: Create a `marketplace.json` file inside `.claude-plugin/`.
4.  Add basic setup metadata (**name must be kebab-case**):
    ```json
    {
      "name": "my-marketplace",
      "owner": {
        "name": "My Name",
        "email": "optional@example.com"
      },
      "plugins": []
    }
    ```

> **Reserved names** (blocked by Claude Code): `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences`. Names that impersonate official marketplaces (e.g. `official-claude-plugins`) are also blocked.

## Step 2: Add Plugin Entries

To add entries to your marketplace `plugins` list:
1.  Define the **`name`** (kebab-case).
2.  Specify the **`source`** — choose the type that matches your hosting:

### Source Types

**Same-repo subdirectory (monorepo — verified working)**
```json
{ "source": "./plugins/my-plugin-folder" }
```
Path is resolved relative to the marketplace root (the directory containing `.claude-plugin/`), not from `.claude-plugin/` itself. Must start with `./`.

> **Note**: Relative paths only work when the marketplace is added via Git (GitHub, GitLab, git URL). If added via a direct URL to `marketplace.json`, relative paths fail — use `github`, `npm`, or `url` sources instead.

**GitHub repository**
```json
{ "source": { "source": "github", "repo": "owner/repo", "ref": "v2.0.0", "sha": "a1b2c3d..." } }
```
`ref` and `sha` are optional. Omit to use the default branch.

**Monorepo subdirectory via sparse clone (avoids fetching whole repo)**
```json
{ "source": { "source": "git-subdir", "url": "https://github.com/owner/repo", "path": "plugins/my-plugin" } }
```
Note: field is `path` (not `subdir`), and the key is `source` (not `type`). Also accepts GitHub shorthand or SSH URLs.

**npm package**
```json
{ "source": { "source": "npm", "package": "@scope/my-plugin", "version": "^1.0.0", "registry": "https://registry.npmjs.org" } }
```
`version` defaults to `latest`; `registry` defaults to the public npm registry.

**Non-GitHub git host**
```json
{ "source": { "source": "url", "url": "https://gitlab.com/owner/repo.git", "ref": "main" } }
```
The `.git` suffix is optional — Azure DevOps and AWS CodeCommit URLs without it work fine.

3.  Set **`strict`** mode:
    - `strict: true` (default) — plugin's own `plugin.json` is authoritative; marketplace entry can supplement with additional components.
    - `strict: false` — marketplace entry IS the entire definition; plugin must NOT also have a `plugin.json` declaring components (conflict = plugin fails to load).

4.  Optional: use `metadata.pluginRoot` to shorten relative source paths. Setting `"pluginRoot": "./plugins"` lets you write `"source": "formatter"` instead of `"source": "./plugins/formatter"`.

5.  Optional: pin a version. **Warning**: do not set `version` in both the marketplace entry and the plugin's `plugin.json` — `plugin.json` wins silently and the marketplace version is ignored. For relative-path plugins, set version in the marketplace entry. For all other sources, set it in `plugin.json`.

> **Plugin Author Note**: In hooks or server configs, use `${CLAUDE_PLUGIN_ROOT}` (read-only install path) and `${CLAUDE_PLUGIN_DATA}` (persistent state directory) instead of absolute host paths.

---

## Step 3: Validate Before Publishing

Run validation to catch schema errors before consumers see them:
```bash
/plugin validate .
# or via CLI:
claude plugin validate .
```

Validator checks: `plugin.json`, skill/agent/command frontmatter, `hooks/hooks.json` syntax and schema.

Common errors:
| Error | Solution |
|---|---|
| `File not found: .claude-plugin/marketplace.json` | Create the file with required fields |
| `Duplicate plugin name "x"` | Give each plugin a unique `name` |
| `plugins[0].source: Path contains ".."` | Use paths without `..` |
| `YAML frontmatter failed to parse` | Fix YAML syntax in the skill/agent file |

---

## Step 4: Distribution

### Publishing to GitHub (verified — Claude Code 2.1.81+)
1. Create `.claude-plugin/marketplace.json` at the **repo root** (not inside a subdirectory).
2. Commit and push to the default branch (`main`).
3. Claude Code fetches from the default branch — the PR must be merged before consumers can install.

Consumers register the marketplace with:
```
/plugin marketplace add owner/repo
```
Example: `/plugin marketplace add richfrem/agent-plugins-skills`

On success, Claude Code responds: `Successfully added marketplace: <name>`

**Known non-working subcommands (Claude Code 2.1.81):**
- `/plugin marketplace browse` — returns no content, not a supported subcommand
- Use `/plugin list` or `/plugin help` to discover what subcommands are available in your version

---

## Step 5: Install Plugins (Consumer)

After adding the marketplace, install any listed plugin by name:
```
/plugin install <name>
```

This opens an **interactive Plugins panel** (not plain text output) showing:
- Plugin name and source marketplace
- Description pulled from `marketplace.json`
- Scope picker: **user scope** (all repos) / **project scope** (collaborators on this repo) / **local scope** (this repo only)

Scope flags (if using CLI directly):
- `/plugin install <name>` — user scope (default)
- `/plugin install <name> --scope project` — team shared
- `/plugin install <name> --scope local` — machine local

Note: The command returns no stdout — the install UI renders in the Plugins panel, not the terminal.

After install, run `/reload-plugins` to activate immediately without restarting. Output format:
```
Reloaded: N plugins · N skill · N agents · N hooks · N plugin MCP servers · N plugin LSP server
```

---

## Plugin Manager TUI (`/plugin`)

Running `/plugin` with no arguments opens the full plugin manager with tabs:
- **Plugins** — browse all available
- **Discover** — explore by category
- **Installed** — manage active plugins
- **Marketplaces** — view/manage registered marketplaces
- **Errors** — installation or load errors

### Marketplaces Tab
Shows each registered marketplace with:
```
• claude-plugins-official *        ← * = built-in/pinned
  anthropics/claude-plugins-official
  117 available • 2 installed • Updated 3/22/2026

• my-marketplace-id
  owner/repo
  27 available • 1 installed • Updated 3/22/2026
```
Keybindings: `Enter` select · `u` update · `r` remove

### Installed Plugin Detail View
Selecting an installed plugin shows:
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
Options: Disable plugin · Mark for update · Update now · Uninstall · View repository · Back to plugin list

---

## Team & Enterprise Distribution

### Auto-install for a team (`.claude/settings.json`)
```json
{
  "extraKnownMarketplaces": {
    "my-marketplace-id": {
      "source": {
        "source": "github",
        "repo": "owner/repo"
      }
    }
  },
  "enabledPlugins": {
    "my-plugin@my-marketplace-id": true
  }
}
```
`extraKnownMarketplaces` is a **keyed object** (not an array) where the key is the marketplace ID (kebab-case). `enabledPlugins` is also a keyed object using the format `"plugin-name@marketplace-id": true`. Both make the marketplace and plugin available by default for every team member.

### Lock to approved marketplaces only (enterprise)

`strictKnownMarketplaces` in managed settings restricts which sources users can add:
```json
{ "strictKnownMarketplaces": [] }                    // complete lockdown
{ "strictKnownMarketplaces": [{ "source": "github", "repo": "acme/approved" }] }  // allowlist
{ "strictKnownMarketplaces": [{ "source": "hostPattern", "hostPattern": "^github\\.example\\.com$" }] }  // regex on host
{ "strictKnownMarketplaces": [{ "source": "pathPattern", "pathPattern": "^/opt/approved/" }] }  // regex on path
```
Note: this is a policy gate only — it does NOT register marketplaces. Pair with `extraKnownMarketplaces` to pre-register allowed ones.

### Pre-populate plugins in containers / CI
```bash
export CLAUDE_CODE_PLUGIN_SEED_DIR=/path/to/pre-installed-plugins
# Seed directory mirrors ~/.claude/plugins structure (known_marketplaces.json, marketplaces/, cache/)
# Seed entries are read-only — auto-updates disabled for seeded marketplaces
# To layer multiple seed dirs, separate with : (Unix) or ; (Windows)
```

### Release channels
Point two marketplace entries at different `ref` values of the same repo:
```json
{ "name": "stable-tools", "plugins": [{ "name": "my-plugin", "source": { "source": "github", "repo": "acme/plugin", "ref": "stable" } }] }
{ "name": "latest-tools", "plugins": [{ "name": "my-plugin", "source": { "source": "github", "repo": "acme/plugin", "ref": "latest" } }] }
```
Each ref's `plugin.json` must declare a **different `version`** — same version = Claude Code treats them as identical and skips the update.

---

## Marketplace Management Commands (Consumer)

```bash
/plugin marketplace list                    # list all registered marketplaces
/plugin marketplace update <name>           # refresh catalog from remote
/plugin marketplace remove <name>           # remove (also uninstalls its plugins)

/plugin install <plugin>@<marketplace>      # install (user scope default)
/plugin disable <plugin>@<marketplace>      # disable without uninstalling
/plugin enable <plugin>@<marketplace>       # re-enable
/plugin uninstall <plugin>@<marketplace>    # remove completely
claude plugin install <plugin> --scope project   # install at specific scope
```

Shortcuts: `/plugin market` = `/plugin marketplace`, `rm` = `remove`.

---

## Environment Variables

| Variable | Purpose |
|---|---|
| `CLAUDE_CODE_PLUGIN_SEED_DIR` | Pre-populate plugins for containers/CI |
| `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS` | Git clone/pull timeout in ms (default: 120000) |
| `GITHUB_TOKEN` / `GH_TOKEN` | Auth for private GitHub marketplace repos (auto-updates) |
| `GITLAB_TOKEN` / `GL_TOKEN` | Auth for private GitLab repos |
| `BITBUCKET_TOKEN` | Auth for private Bitbucket repos |
| `FORCE_AUTOUPDATE_PLUGINS=true` | Keep plugin auto-updates on when `DISABLE_AUTOUPDATER` is set |

---

## SkillsMP.com (Open SKILL.md Ecosystem Marketplace)

[skillsmp.com](https://skillsmp.com) auto-indexes open-source SKILL.md skills from GitHub daily.

### Requirements to Get Indexed
1. Public GitHub repo with `SKILL.md` files containing `name` + `description` frontmatter
2. Add GitHub topic tags: `claude-skills` and/or `claude-code-skill`
3. Wait up to 24 hours for the daily sync

> **TODO: CHECK INDEXING** - Topics added to `richfrem/agent-plugins-skills` on 2026-03-22. Verify at skillsmp.com after 2026-03-23.

### Watch Out
Skills at `plugins/<plugin>/skills/<skill>/SKILL.md` (4 levels deep) may not be crawled. If not indexed after first sync, add a top-level `skills/` directory mirroring the skill folders.

---

## References & Examples

- [references/marketplace-schema.md](../../references/marketplace-schema.md) - Struct, vars, and strict overrides.
- [examples/marketplace.json](./examples/marketplace.json) - Working sample with GitHub lookup.