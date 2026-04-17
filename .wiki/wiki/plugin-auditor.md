---
concept: plugin-auditor
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/agent-scaffolders_audit-plugin.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.317124+00:00
cluster: agent
content_hash: 1b3b6b155d7112a5
---

# Plugin Auditor

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: audit-plugin
description: Validate a plugin's structure, components, and security
argument-hint: "[plugin-path]"
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Plugin Auditor

Performs comprehensive validation of a Claude Code plugin against structure standards,
naming conventions, component requirements, and security best practices. Uses the
`plugin-validator` agent for deep validation, supported by component-specific scripts.

---

## Step 1: Locate the Plugin

Establish the plugin root:
- Look for `./././././././././././././plugin.json` -- this is the definitive marker
- If user didn't specify a path, check current directory and common locations
- Confirm with user if ambiguous

---

## Step 2: Run plugin-validator Agent

> **Cross-plugin dependency**: The `plugin-validator` agent used in this step is defined in the
> `agent-scaffolders` plugin, not this plugin. It must be installed for this step to work.
> See `../CONNECTORS.md` for the dependency declaration and fallback instructions.

Trigger the `plugin-validator` agent for comprehensive validation:

```
"Validate the plugin at <path>"
```

The agent checks all 10 categories automatically:
1. Manifest (`./././././././././././././plugin.json`) -- JSON syntax, required `name` field, kebab-case
2. Directory structure -- components at root, not inside `.claude-plugin/`
3. Commands (`commands/**/*.md`) -- frontmatter, `description`, `argument-hint`, `allowed-tools`
4. Agents (`agents/**/*.md`) -- `name`, `description` with `<example>` blocks, `model`, `color`
5. Skills (`skills/*/SKILL.md`) -- frontmatter, `name`, `description`, supporting directories
6. Hooks (`hooks/hooks.json`) -- JSON syntax, valid event names, matcher + hooks array
7. MCP configuration (`.mcp.json`) -- server type, required fields, HTTPS enforcement
8. File organization -- README.md, .gitignore, no node_modules or .DS_Store
9. Security -- no hardcoded credentials, MCP uses HTTPS/WSS, no secrets in examples
10. Positive findings -- note what's done well, not just what's broken

**Output format from plugin-validator:**
```
## Plugin Validation Report
### Plugin: [name] | Location: [path]
### Summary: [PASS/FAIL with stats]
### Critical Issues ([count]) -- file path + issue + fix
### Warnings ([count]) -- file path + recommendation
### Component Summary -- counts of each type
### Positive Findings
### Overall Assessment: [PASS/FAIL + reasoning]
```

---

## Step 3: Run Component-Specific Scripts

After plugin-validator, run targeted scripts for detailed checks:

**Validate each agent file:**
```bash
bash ${CLAUDE_PLUGIN_ROOT}/../agent-scaffolders/scripts/validate-agent.sh agents/my-agent.md
```
Checks: frontmatter structure, required fields (name/description/model/color), name format
(3-50 chars, lowercase + hyphens), description has `<example>` blocks, system prompt
length (minimum 20 chars, recommended 500-3,000).

**Validate hooks.json schema:**
```bash
bash ${CLAUDE_PLUGIN_ROOT}/../agent-scaffolders/scripts/validate-hook-schema.sh hooks/hooks.json
```
Checks: JSON syntax, valid event names, each hook has `matcher` + `hooks` array,
hook type is `command` or `prompt`, command hooks reference existing scripts with
`${CLAUDE_PLUGIN_ROOT}`.

**Test a hook script directly:**
```bash
bash ${CLAUDE_PLUGIN_ROOT}/../agent-scaffolders/scripts/test-hook.sh \
  --hook hooks/scripts/validate.sh \
  --event PreToolUse \
  --input '{"tool_name": "Write", "tool_input": {"file_path": "src/app.py"}}'
```

**Lint hook scripts for common issues:**
```bash
bash ${CLAUDE_PLUGIN_ROOT}/../agent-scaffolders/scripts/hook-linter.sh hooks/
```

---

## Step 4: Manual Checks

For issues the scripts may not catch:

**Plugin structure check:**
```bash
# Manifest must be here (not in root)
ls ./././././././././././././plugin.json

# Components must be at root (not in .claude-plugin/)
ls commands/ agents/ skills/ hooks/

# Validate JSON
jq . ./././././././././././././plugin.json
```

**Security scan:**
```bash
# Check fo

*(content truncated)*

## See Also

- [[agent-plugin-analyzer-l5-red-team-auditor]]
- [[agent-plugin-analyzer-l5-red-team-auditor]]
- [[adr-manager-plugin]]
- [[test-scenario-bank-agentic-os-plugin]]
- [[security-auditor]]
- [[agent-plugin-analyzer]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/agent-scaffolders_audit-plugin.md`
- **Indexed:** 2026-04-17T06:42:10.317124+00:00
