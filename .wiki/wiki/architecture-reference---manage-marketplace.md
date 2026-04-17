---
concept: architecture-reference---manage-marketplace
source: plugin-code
source_file: agent-scaffolders/references/marketplace-architecture.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.318862+00:00
cluster: relative
content_hash: a9fd1b6ed319d1f6
---

# Architecture Reference - manage-marketplace

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Architecture Reference - manage-marketplace

The marketplace skill governs the catalog creation setup enabling custom package hosting.

## Core Concepts

### 1. Catalog Registry (`.claude-plugin/marketplace.json`)
-   **Placement**: Positioned inside `.claude-plugin/` folder to satisfy manifest discovery layouts.
-   **Structure**: Relies on relative definitions or standard source scopes (GitHub object maps).

### 2. Caching Scopes & Caches
-   Plugins distributed are copied to an internal user/project scope cache safely.
-   **Variables**: absolute paths must use absolute variables (`${CLAUDE_PLUGIN_ROOT}`) to bridge cached isolation properly.

### 3. Relative Path Source Limitation

A marketplace entry with `"source": "./plugins/my-plugin"` resolves the path relative to the marketplace repository root. This only works when the marketplace was added via a Git clone or local filesystem path. It does NOT work when added via a direct raw URL to `marketplace.json`, because there is no filesystem root to resolve the relative path against.

### 4. `strict` Field Behavior

| `strict` value | Authority |
|---------------|-----------|
| `true` (default) | Plugin's own `.claude-plugin/plugin.json` is the source of truth. Marketplace entry supplements but does not override. |
| `false` | Marketplace entry is the complete definition. Useful for overriding plugin metadata for a specific distribution. |

### 5. Lifecycle
The 2-step consumer process (Add & Install) is natively supported by Claude Code CLI and TUI (`/plugin`).

## See Also

- [[acceptance-criteria---manage-marketplace]]
- [[acceptance-criteria---manage-marketplace]]
- [[acceptance-criteria---manage-marketplace]]
- [[triple-loop-learning-system---architecture-overview]]
- [[triple-loop-learning-system---architecture-overview]]
- [[agent-plugin-analyzer---architecture]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/references/marketplace-architecture.md`
- **Indexed:** 2026-04-17T06:42:09.318862+00:00
