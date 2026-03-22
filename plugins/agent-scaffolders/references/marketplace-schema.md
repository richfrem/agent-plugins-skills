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
