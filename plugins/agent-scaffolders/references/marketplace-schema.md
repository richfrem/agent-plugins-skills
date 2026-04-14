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
- **`strict`**: Boolean (default `true`, **always set explicitly** — do not rely on the default).

    | Value | Requires | Behavior |
    |-------|----------|----------|
    | `true` *(default)* | Plugin **must** have its own `plugin.json` | `plugin.json` is authoritative; marketplace entry supplements |
    | `false` | Plugin **must NOT** have a `plugin.json` declaring components | Marketplace entry IS the entire definition |

    **Both mismatches silently prevent the entire plugin from loading:**
    - `strict: true` (or omitted) + **no** `plugin.json` → load failure (authority source missing)
    - `strict: false` + plugin **has** a `plugin.json` with components → conflict = load failure

    **Rule of thumb:** Monorepo plugins with their own `plugin.json` must always use `"strict": true`.
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
