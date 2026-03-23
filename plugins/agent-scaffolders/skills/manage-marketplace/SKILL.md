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
2.  Specify the **`source`** as a relative path from the repo root:
    - **Relative path (verified working)**: `"./plugins/my-plugin-folder"`
    - This works when Claude Code fetches the marketplace from GitHub — the path is resolved relative to the repo root, not the `.claude-plugin/` directory.
3.  Set **`strict`** to `true` to let the plugin's own manifest control definition lookup.

> **💡 Plugin Author Note**: When writing hooks or server configs, use `${CLAUDE_PLUGIN_ROOT}` (read-only install path) and `${CLAUDE_PLUGIN_DATA}` (persistent state directory) instead of absolute host paths.

---

## Step 3: Distribution

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

---

## Step 4: Install Plugins (Consumer)

After adding the marketplace, install any listed plugin by name:
- `/plugin install <name>` (Global **`user`** scope)
- `/plugin install <name> --scope project` (Team shared)
- `/plugin install <name> --scope local` (Machine local)

---

## References & Examples

- [references/marketplace-schema.md](../../references/marketplace-schema.md) - Struct, vars, and strict overrides.
- [examples/marketplace.json](./examples/marketplace.json) - Working sample with GitHub lookup.