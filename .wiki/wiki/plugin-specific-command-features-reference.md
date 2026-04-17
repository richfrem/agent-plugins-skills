---
concept: plugin-specific-command-features-reference
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-command/references/plugin-features-reference.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.826098+00:00
cluster: commands
content_hash: 6f7d33dc0251edbc
---

# Plugin-Specific Command Features Reference

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Plugin-Specific Command Features Reference

This reference covers features and patterns specific to commands bundled in Claude Code plugins.

## Table of Contents

- [Plugin Command Discovery](#plugin-command-discovery)
- [CLAUDE_PLUGIN_ROOT Environment Variable](#claude_plugin_root-environment-variable)
- [Plugin Command Patterns](#plugin-command-patterns)
- [Integration with Plugin Components](#integration-with-plugin-components)
- [Validation Patterns](#validation-patterns)

## Plugin Command Discovery

### Auto-Discovery

Claude Code automatically discovers commands in plugins using the following locations:

```
plugin-name/
├── commands/              # Auto-discovered commands
│   ├── foo.md            # /foo (plugin:plugin-name)
│   └── bar.md            # /bar (plugin:plugin-name)
└── plugin.json           # Plugin manifest
```

**Key points:**
- Commands are discovered at plugin load time
- No manual registration required
- Commands appear in `/help` with "(plugin:plugin-name)" label
- Subdirectories create namespaces

### Namespaced Plugin Commands

Organize commands in subdirectories for logical grouping:

```
plugin-name/
└── commands/
    ├── review/
    │   ├── security.md    # /security (plugin:plugin-name:review)
    │   └── style.md       # /style (plugin:plugin-name:review)
    └── deploy/
        ├── staging.md     # /staging (plugin:plugin-name:deploy)
        └── prod.md        # /prod (plugin:plugin-name:deploy)
```

**Namespace behavior:**
- Subdirectory name becomes namespace
- Shown as "(plugin:plugin-name:namespace)" in `/help`
- Helps organize related commands
- Use when plugin has 5+ commands

### Command Naming Conventions

**Plugin command names should:**
1. Be descriptive and action-oriented
2. Avoid conflicts with common command names
3. Use hyphens for multi-word names
4. Consider prefixing with plugin name for uniqueness

**Examples:**
```
Good:
- /mylyn-sync          (plugin-specific prefix)
- /analyze-performance (descriptive action)
- /docker-compose-up   (clear purpose)

Avoid:
- /test               (conflicts with common name)
- /run                (too generic)
- /do-stuff           (not descriptive)
```

## CLAUDE_PLUGIN_ROOT Environment Variable

### Purpose

`${CLAUDE_PLUGIN_ROOT}` is a special environment variable available in plugin commands that resolves to the absolute path of the plugin directory.

**Why it matters:**
- Enables portable paths within plugin
- Allows referencing plugin files and scripts
- Works across different installations
- Essential for multi-file plugin operations

### Basic Usage

Reference files within your plugin:

```markdown
---
description: Analyze using plugin script
allowed-tools: Bash(node:*), Read
---

Run analysis: !`node ${CLAUDE_PLUGIN_ROOT}/scripts/analyze.js`

Read template: @${CLAUDE_PLUGIN_ROOT}/templates/report.md
```

**Expands to:**
```
Run analysis: !`node /path/to/./scripts/analyze.js`

Read template: @/path/to/plugins/plugin-name/templates/report.md
```

### Common Patterns

#### 1. Executing Plugin Scripts

```markdown
---
description: Run custom linter from plugin
allowed-tools: Bash(node:*)
---

Lint results: !`node ${CLAUDE_PLUGIN_ROOT}/bin/lint.js $1`

Review the linting output and suggest fixes.
```

#### 2. Loading Configuration Files

```markdown
---
description: Deploy using plugin configuration
allowed-tools: Read, Bash(*)
---

Configuration: @${CLAUDE_PLUGIN_ROOT}/config/deploy-config.json

Deploy application using the configuration above for $1 environment.
```

#### 3. Accessing Plugin Resources

```markdown
---
description: Generate report from template
---

Use this template: @${CLAUDE_PLUGIN_ROOT}/templates/api-report.md

Generate a report for @$1 following the template format.
```

#### 4. Multi-Step Plugin Workflows

```markdown
---
description: Complete plugin workflow
allowed-tools: Bash(*), Read
---

Step 1 - Prepare: !`bash ${CLAUDE_PLUGIN_ROOT}/scripts/prepare.sh $1`
Step 2 - Config: @${CLAUDE_PLUGIN_ROOT}/config/

*(content truncated)*

## See Also

- [[plugin-command-examples]]
- [[command-frontmatter-reference]]
- [[exploration-cycle-plugin-architecture-reference]]
- [[exploration-cycle-plugin-architecture-reference]]
- [[exploration-cycle-plugin-architecture-reference]]
- [[exploration-cycle-plugin-architecture-reference]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-command/references/plugin-features-reference.md`
- **Indexed:** 2026-04-17T06:42:09.826098+00:00
