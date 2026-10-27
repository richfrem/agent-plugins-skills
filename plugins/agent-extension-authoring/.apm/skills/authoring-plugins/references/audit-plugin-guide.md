# Plugin Audit Reference Guide

Comprehensive guide for auditing and validating APM-native and Claude Code plugins against structure standards, naming conventions, component requirements, and security best practices.

## Contents

- [Overview & Workflow](#overview--workflow)
- [Step 1: Locate the Plugin](#step-1-locate-the-plugin)
- [Step 2: Structural & Compliance Audits](#step-2-structural--compliance-audits)
- [Step 2b: Manifest & Hook Format Checks](#step-2b-manifest--hook-format-checks)
- [Step 3: Component-Specific Audits](#step-3-component-specific-audits)
- [Step 4: Manual Checks & Security](#step-4-manual-checks--security)
- [Step 4b: Marketplace Source Path Audit](#step-4b-marketplace-source-path-audit)
- [Step 5: Report and Remediate](#step-5-report-and-remediate)
- [Standards Reference](#standards-reference)

---

## Overview & Workflow

Plugin validation checks:
1. Manifest validity (`apm.yml` and `.claude-plugin/plugin.json`).
2. Unified `.apm/` primitive directory structure (no duplicate root `skills/`, `agents/`, `hooks/`).
3. Self-contained skills (zero symlinks, zero plugin-root duplicate scripts/references, zero climbing `../` paths in code blocks).
4. Hook definitions, matchers, and harness-neutral script execution paths (`.apm/hooks/hooks.json`, **SF-11**).
5. Agent frontmatter, prompt quality, `<example>` blocks, and absence of skill-mirror symlinks (**SF-12**).
6. `lsp.json` flat map conformance (**SF-10**).
7. Security hygiene (no hardcoded secrets or machine-specific paths).

---

## Step 1: Locate the Plugin

Establish the plugin root:
- Look for `apm.yml` and `.claude-plugin/plugin.json` — these are the definitive markers.
- Confirm with user if ambiguous.

---

## Step 2: Structural & Compliance Audits

Run the two scripts in this skill:

```bash
# 1. Validate manifests, .apm/ unification, lsp.json, and absence of symlinks/duplicates
python3 scripts/audit_plugin_structure.py plugins/<plugin-name>

# 2. Validate plugin compliance and run per-skill audits (via sibling authoring-skills)
python3 scripts/audit.py --path plugins/<plugin-name>
```

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

## Step 2b: Manifest & Hook Format Checks

**Common load issues and root causes:**

| Issue | Symptom | Root cause |
|---|---|---|
| `plugin.json` has `skills`/`agents`/`hooks`/`commands` field | `Invalid input` | Validator rejects these — auto-discovery handles them |
| Duplicate root `skills/` alongside `.apm/skills/` | `duplicate_primitive_root` | Primitives must live exclusively under `.apm/` |
| `lsp.json` is `{}` or wraps `"languageServers"` | `invalid_lsp_json` (**SF-10**) | Must be a flat map `{serverName: {command, ...}}` |
| `hooks.json` is `{}` (empty object) or `[]` (array) | `expected record, received undefined` | Must be `{"hooks": {}}` |
| `SKILL.md` has comment lines before `---` | skill fails to load | Frontmatter parser requires `---` on line 1 |

**Correct `.apm/hooks/hooks.json` format:**
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/.apm/hooks/script.py || python ${CLAUDE_PLUGIN_ROOT}/.apm/hooks/script.py"
          }
        ]
      }
    ]
  }
}
```

---

## Step 3: Component-Specific Audits

Delegate component validation to the sibling skills in `agent-extension-authoring`:

```bash
# Audit all skills in the plugin (authoring-skills)
python3 ../authoring-skills/scripts/audit_skill.py plugins/<plugin-name> --all --mode source

# Audit all sub-agents in the plugin (authoring-subagents)
python3 ../authoring-subagents/scripts/audit_sub_agent.py plugins/<plugin-name> --all

# Audit rules in the plugin (authoring-instructions)
python3 ../authoring-instructions/scripts/audit_rule.py plugins/<plugin-name> --all

# Validate hooks schema and lint hook scripts (authoring-instructions)
python3 ../authoring-instructions/scripts/validate_hook_schema.py plugins/<plugin-name>/.apm/hooks/hooks.json
python3 ../authoring-instructions/scripts/hook_linter.py plugins/<plugin-name>/.apm/hooks/

# Run full APM 7-stage packaging & alignment pipeline (packaging-with-apm)
python3 ../packaging-with-apm/scripts/apm_build_pipeline.py --plugin plugins/<plugin-name>
```

---

## Step 4: Manual Checks & Security

1. **Manifests**: Both `apm.yml` and `.claude-plugin/plugin.json` exist at the plugin root.
2. **Author Format**: `author` in `plugin.json` must be an object `{"name": "...", "email": "..."}`, never a string.
3. **No Hardcoded Secrets**: Scan for tokens, passwords, keys.
4. **Portability**: No `/Users/` or `/home/` absolute paths. Use skill-relative paths or `${CLAUDE_PLUGIN_ROOT}`.
5. **Harness-Neutral Hooks (**SF-11**)**: Hook scripts use `Path(__file__).resolve()` for sibling files and `context/` for runtime state, never `.claude/` or `.agents/`.
6. **Naming**: kebab-case for plugins, skills, agents, commands, and scripts.

---

## Step 4b: Marketplace Source Path Audit

If `marketplace.json` is used, ensure entries point to existing folders via the `packaging-with-apm` skill (`audit_marketplace_sources.py`).

---

## Step 5: Report and Remediate

- **Critical**: Invalid JSON, string author, duplicate primitive roots, raw symlinks, hardcoded credentials, missing required fields.
- **Warning**: Missing `apm.yml`, oversized skills, missing `<example>` blocks in agents.
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
