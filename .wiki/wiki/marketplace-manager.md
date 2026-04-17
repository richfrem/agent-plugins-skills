---
concept: marketplace-manager
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/manage-marketplace/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.112685+00:00
cluster: plugin
content_hash: 9b9bd290f1f11656
---

# Marketplace Manager

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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

> **Plugin Author Note**: In hooks or server configs, use `${CLAUDE_PLUGIN_ROOT}` (read-only install path) and `${CLAUDE_PLUGIN_DATA}` (persistent state directory) instead o

*(content truncated)*

## See Also

- [[adr-manager-plugin]]
- [[acceptance-criteria-adr-manager]]
- [[identity-the-adr-manager]]
- [[session-memory-manager]]
- [[acceptance-criteria-os-memory-manager]]
- [[product-manager]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/manage-marketplace/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.112685+00:00
