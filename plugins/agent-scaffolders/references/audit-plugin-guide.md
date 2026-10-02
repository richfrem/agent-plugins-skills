# Plugin Audit Reference Guide

Comprehensive guide for auditing and validating Claude Code plugins against structure standards, naming conventions, component requirements, and security best practices.

## Contents

- [Overview & Workflow](#overview--workflow)
- [Step 1: Locate the Plugin](#step-1-locate-the-plugin)
- [Step 2: Component Validation Scripts](#step-2-component-validation-scripts)
- [Step 2b: Auto-Fix Load Errors](#step-2b-auto-fix-load-errors)
- [Step 2c: Detect and Fix Symlink Stand-Ins](#step-2c-detect-and-fix-symlink-stand-ins)
- [Step 3: Component-Specific Scripts](#step-3-component-specific-scripts)
- [Step 3b: Self-Evolution Policy Compliance](#step-3b-self-evolution-policy-compliance)
- [Step 4: Manual Checks & Security](#step-4-manual-checks--security)
- [Step 4b: Marketplace Source Path Audit](#step-4b-marketplace-source-path-audit)
- [Step 5: Report and Remediate](#step-5-report-and-remediate)
- [Standards Reference](#standards-reference)

---

## Overview & Workflow

Plugin validation checks:
1. Manifest validity (`.claude-plugin/plugin.json`).
2. Component directory structure and naming conventions.
3. Hook definitions, matchers, and script execution paths.
4. Agent frontmatter, prompt quality, and `<example>` blocks.
5. Symlink integrity and stand-in resolution.
6. Self-evolution policy artifacts (`self-evolution-profile.md`, `map-debt.md`, `evolution-log.md`).
7. Security hygiene (no hardcoded secrets or machine-specific paths).

---

## Step 1: Locate the Plugin

Establish the plugin root:
- Look for `.claude-plugin/plugin.json` — this is the definitive marker.
- If user did not specify a path, check current directory and common locations.
- Confirm with user if ambiguous.

---

## Step 2: Component Validation Scripts

Run scripts bundled in `plugins/agent-scaffolders/scripts/`:

```bash
# Validate agent files
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate_agent.py agents/my-agent.md

# Validate hooks.json schema
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate_hook_schema.py hooks/hooks.json

# Lint hook scripts
python ${CLAUDE_PLUGIN_ROOT}/scripts/hook_linter.py hooks/
```

Checks performed: frontmatter structure, required fields (name/description/model/color),
`<example>` blocks in agent descriptions, hook event names, matcher + hooks array structure.

**Validation report format:**
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

## Step 2b: Auto-Fix Load Errors

Before deep validation, run the load-error fixer to catch issues that prevent Claude Code from loading the plugin:

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/fix_plugin_load_errors.py <plugin_root>
```

**Common load issues and root causes:**

| Issue | Symptom in /doctor | Root cause |
|---|---|---|
| `plugin.json` has `skills`/`agents`/`hooks`/`commands` field | `Invalid input` | Validator rejects these entirely — auto-discovery handles them |
| `hooks.json` is `{}` (empty object) | `expected record, received undefined` | Must be `{"hooks": {}}` |
| `hooks.json` is `[]` (array) | `expected object received array` | Must be an object |
| `hooks.json` flat format `{"EventName":{...}}` | `expected record, received undefined` | Must be nested under `"hooks"` key |
| `hooks.json`/`lsp.json`/`.mcp.json` has literal `\n` | `Unrecognized token '\'` | Escaped newlines in JSON; must have real newlines |
| `SKILL.md` has comment lines before `---` | skill fails to load | Frontmatter parser requires `---` on line 1 |

**Correct `hooks.json` format:**
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/script.py || python ${CLAUDE_PLUGIN_ROOT}/hooks/script.py" }]
      }
    ]
  }
}
```

---

## Step 2c: Detect and Fix Symlink Stand-Ins

Git checks out symlinks as plain-text stand-in files when `core.symlinks=false`. Stand-ins look like real files but contain only relative path text (< 512 bytes).

**Bulk scanner:**
```bash
python plugins/dev-utils/scripts/bulk_symlink_fixer.py plugins/<plugin-name>
```

**Verify resolution:**
```bash
find plugins/<plugin-name> -type l | wc -l
find plugins/<plugin-name>/skills -path "*/scripts/*" -type f ! -type l
```

**Correct symlink pattern:**
```
skills/<skill>/scripts/execute.py  →  ../../../scripts/<canonical_name>.py
skills/<skill>/references/architecture.md  →  ../../../references/architecture.md
```

---

## Step 3: Component-Specific Scripts

**Validate each agent file:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate_agent.py agents/my-agent.md
```

**Validate hooks schema:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate_hook_schema.py hooks/hooks.json
```

**Lint hook scripts:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/hook_linter.py hooks/
```

---

## Step 3b: Self-Evolution Policy Compliance

Check required policy files:
```bash
ls plugins/<plugin>/references/self-evolution-profile.md
ls plugins/<plugin>/references/map-debt.md
ls plugins/<plugin>/references/evolution-log.md
```

Check eval contracts:
```bash
grep -r "expected_behavior\|expected_output\|\"expected\":" plugins/<plugin>/skills/*/evals/evals.json
```
All evals must use `should_trigger` boolean schema.

Check file-level-symlinks rule:
```bash
find plugins/<plugin> -type l -exec test -d {} \; -print
```

---

## Step 4: Manual Checks & Security

1. **Manifest Location**: Must be `.claude-plugin/plugin.json`.
2. **Author Format**: Must be an object `{"name": "...", "email": "..."}`, never a string.
3. **No Hardcoded Secrets**: Scan for tokens, passwords, keys.
4. **Portability**: No `/Users/` or `/home/` absolute paths. Use relative paths or `${CLAUDE_PLUGIN_ROOT}`.
5. **Cross-Platform Commands**: Use `python3 ... || python ...` in hook declarations.
6. **Naming**: kebab-case for plugins, skills, agents, commands, and scripts.

---

## Step 4b: Marketplace Source Path Audit

Ensure marketplace entries point to existing folders:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audit_marketplace_sources.py .
```

---

## Step 5: Report and Remediate

- **Critical**: Invalid JSON, string author, hardcoded credentials, missing required fields.
- **Warning**: Missing self-evolution files, oversized skills, missing `<example>` blocks.
- **Minor**: Style or documentation improvements.

---

## Standards Reference

**Minimal valid `.claude-plugin/plugin.json`:**
```json
{
  "name": "plugin-name",
  "author": { "name": "Author Name", "email": "email@example.com" }
}
```

**Recommended `.claude-plugin/plugin.json`:**
```json
{
  "name": "plugin-name",
  "version": "0.1.0",
  "description": "What the plugin does",
  "author": { "name": "Author Name", "email": "email@example.com" }
}
```
