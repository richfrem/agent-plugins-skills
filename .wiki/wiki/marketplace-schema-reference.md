---
concept: marketplace-schema-reference
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/manage-marketplace/references/marketplace-schema.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.114821+00:00
cluster: plugins
content_hash: 85c806f385fbe838
---

# Marketplace Schema Reference

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Marketplace Schema Reference

A `.claude-plugin/marketplace.json` defines a catalog of distributable plugins.

## Schema Structure

```json
{
  "name": "marketplace-name",
  "owner": {
    "name": "Owner Name"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "source": "source-definition",
      "strict": true,
      "category": "category-name",
      "tags": ["tag1", "tag2"]
    }
  ]
}
```

### Plugin Source Types

| Source Type | Format | Example |
|-------------|--------|---------|
| Relative Path | String | `"./plugins/my-plugin"` |
| GitHub | Object | `{"source": "github", "repo": "owner/repo", "ref": "main", "sha": "commit-sha"}` |

### Field Details

- **`name`**: Marketplace identifier (**must be kebab-case**).
- **`owner`**: Object containing a `name` field describing the maintainer.
- **`strict`**: Boolean (default `true`).
    - `true`: The plugin's internal `plugin.json` is the authority.
    - `false`: The marketplace entry is the entire definition, allowing overrides.
- **`category`**: Groups plugins by category for UI filtering.
- **`tags`**: Filtering support.

---

## Installation Scopes

When installing plugins, you can specify one of these scopes with `--scope`:
- **`user`** (Default): Global access across all projects (`~/.claude/settings.json`).
- **`project`**: Checked into repository for team sharing (`.claude/settings.json`).
- **`local`**: Specific to current machine but git-ignored (`.claude/settings.local.json`).

---

## Distribution Modes

### Independent Hosting
1. Create a GitHub/Git repository.
2. Commit `marketplace.json` inside a `.claude-plugin/` directory at the root.
3. Share the Absolute HTTPS Git URL with consumers.


---

## Consumer Lifecycle (2-Step Process)

To use your marketplace, consumers run:
1. **Add Marketplace**: `/plugin marketplace add <repo-or-path>` (Registers the catalog).
2. **Install Plugin**: `/plugin install <plugin-name>` (Installs individual items cached from sources).


## See Also

- [[architecture-reference---manage-marketplace]]
- [[claude-code-settingsjson-schema-reference]]
- [[claude-code-settingsjson-schema-reference]]
- [[optimizer-engine-patterns-reference-design]]
- [[project-setup-reference-guide]]
- [[optimizer-engine-patterns-reference-design]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/manage-marketplace/references/marketplace-schema.md`
- **Indexed:** 2026-04-17T06:42:10.114821+00:00
