---
name: create-plugin
description: Scaffold a complete Claude Code plugin from scratch
argument-hint: "[plugin-name]"
allowed-tools: Bash, Read, Write
---

Follow the `create-plugin` skill workflow to scaffold a new Claude Code plugin.

## Inputs

- `$ARGUMENTS` — optional plugin name in kebab-case. Omit to start with discovery.

## Steps

1. If `$ARGUMENTS` provides a plugin name, use it to seed Phase 1
2. Follow the create-plugin phased workflow: discover purpose and plugin type,
   plan component table (skills / commands / agents / hooks / MCP), ask clarifying
   questions per component, scaffold directory structure and `plugin.json`, implement
   each component using the appropriate sub-skill, validate, test, and document
3. Report the created plugin directory and verification checklist results

## Output

Plugin directory with `.claude-plugin/plugin.json`, component directories, `README.md`,
and a `.claude/settings.json` stub for reliable local discovery.

## Edge Cases

- If `$ARGUMENTS` is empty: begin with Phase 1 discovery — do not pre-fill plugin name
- If similar plugin already exists: reference it as a starting point
- If MCP integrations are needed: invoke `create-mcp-integration` for each one
- After scaffolding: run `/agent-scaffolders:audit-plugin` to validate structure

## Symlink Standards for Shared Scripts

When a skill needs to call a Python helper script that is shared across skills in the same
plugin, always create a **file-level symlink** in the skill's `scripts/` folder pointing to the
canonical copy at the plugin root — never duplicate the file.

**Standard pattern:**
```
plugins/<plugin>/scripts/<canonical_name>.py      ← canonical source (real file)
plugins/<plugin>/skills/<skill>/scripts/<name>.py  ← symlink → ../../../scripts/<canonical_name>.py
```

The symlink name and target name may differ (e.g. `execute.py` → `exploration_optimizer_execute.py`).
The bridge installer resolves all symlinks to physical copies when deploying via the marketplace.

**Creating symlinks correctly:**
```bash
# From the skill's scripts/ directory:
ln -s ../../../scripts/<canonical_name>.py <symlink_name>.py

# Or via symlink_manager.py:
python3 plugins/link-checker/scripts/symlink_manager.py create \
  --src plugins/<plugin>/scripts/<canonical_name>.py \
  --dst plugins/<plugin>/skills/<skill>/scripts/<symlink_name>.py
```

**⚠️ Windows / core.symlinks warning:** If `git config core.symlinks` is `false`, git checks
out symlinks as plain-text "stand-in" files. These are silently broken — the bridge installer
copies the path string, not the script. After checkout on Windows or any machine where
symlinks may have degraded, run:
```bash
python3 plugins/link-checker/scripts/bulk_symlink_fixer.py plugins/<plugin-name>
```
Then manually verify: `find plugins/<plugin-name>/skills -path "*/scripts/*" -type f ! -type l`
should return nothing (all script references should be real symlinks, not plain files).
