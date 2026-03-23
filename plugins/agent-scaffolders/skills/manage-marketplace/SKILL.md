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
        "name": "My Name"
      },
      "plugins": []
    }
    ```

## Step 2: Add Plugin Entries

To add entries to your marketplace `plugins` list:
1.  Define the **`name`** (kebab-case).
2.  Specify the **`source`** — choose the type that matches your hosting:

### Source Types

**Same-repo subdirectory (monorepo — verified working)**
```json
{ "source": "./plugins/my-plugin-folder" }
```
Path is resolved relative to the repo root (the directory containing `.claude-plugin/`), not from `.claude-plugin/` itself.

**Monorepo subdirectory via sparse clone (avoids fetching whole repo)**
```json
{ "source": { "type": "git-subdir", "url": "https://github.com/owner/repo", "subdir": "plugins/my-plugin" } }
```

**npm package**
```json
{ "source": { "type": "npm", "package": "@scope/my-plugin", "version": "^1.0.0", "registry": "https://registry.npmjs.org" } }
```
`version` defaults to `latest`; `registry` defaults to the public npm registry.

**Non-GitHub git host**
```json
{ "source": { "type": "url", "url": "https://gitlab.com/owner/repo", "ref": "main" } }
```

3.  Set **`strict`** mode:
    - `strict: true` — plugin's own `plugin.json` is authoritative (recommended when plugin has its own manifest).
    - `strict: false` — marketplace entry IS the entire definition; no `plugin.json` needed (good for lightweight entries).

4.  Optional: use `metadata.pluginRoot` to set the base directory for relative path resolution within the plugin:
```json
{ "name": "my-plugin", "source": "./plugins/my-plugin", "metadata": { "pluginRoot": "src" } }
```

> **Plugin Author Note**: In hooks or server configs, use `${CLAUDE_PLUGIN_ROOT}` (read-only install path) and `${CLAUDE_PLUGIN_DATA}` (persistent state directory) instead of absolute host paths.

---

## Step 3: Validate Before Publishing

Run validation to catch schema errors before consumers see them:
```bash
/plugin validate .
# or via CLI:
claude plugin validate .
```

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

---

## Team & Enterprise Distribution

### Auto-install for a team (`.claude/settings.json`)
```json
{
  "extraKnownMarketplaces": [
    { "name": "my-marketplace", "sourceUrl": "https://github.com/owner/repo" }
  ],
  "enabledPlugins": ["my-plugin"]
}
```
`enabledPlugins` makes listed plugins active by default for every team member.

### Lock to approved marketplaces only (enterprise)
```json
{ "strictKnownMarketplaces": true }
```
Prevents users from adding unapproved marketplaces.

### Pre-populate plugins in containers / CI
```bash
export CLAUDE_CODE_PLUGIN_SEED_DIR=/path/to/pre-installed-plugins
```

### Release channels
Point multiple marketplace entries at different git refs (e.g. `main` vs `release/stable`) to give consumers a choice of stability tier.

---

## References & Examples

- [references/marketplace-schema.md](../../references/marketplace-schema.md) - Struct, vars, and strict overrides.
- [examples/marketplace.json](./examples/marketplace.json) - Working sample with GitHub lookup.