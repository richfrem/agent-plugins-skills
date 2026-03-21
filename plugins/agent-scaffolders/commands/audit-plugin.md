---
name: audit-plugin
description: >
  This skill should be used when the user asks to "audit a plugin", "validate my plugin",
  "check plugin structure", "verify plugin is correct", "validate ././././././././././././plugin.json", "check if
  my plugin is compliant", "review plugin components", or mentions plugin validation or
  structure compliance. Also trigger proactively after the user creates or modifies any
  plugin component (commands, agents, skills, hooks, ././././././././././././plugin.json). Use this skill even
  when the user says "check my work" or "make sure this is right" in a plugin context.
  Do NOT use this for auditing individual skills only (use skill-reviewer for that).
disable-model-invocation: false
allowed-tools: Bash, Read, Write, Glob, Grep
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `../requirements.txt` for the dependency lockfile (currently empty — standard library only).

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
# Check for hardcoded credentials
grep -rn "password\|api_key\|secret\|token" --include="*.md" --include="*.json" --include="*.sh" .
```

**${CLAUDE_PLUGIN_ROOT} portability:**
```bash
# Ensure no hardcoded paths in hook commands or MCP config
grep -rn "/Users/\|/home/" --include="*.json" --include="*.sh" .
```

**Naming conventions:**
- Plugin name: kebab-case (`my-plugin`, not `MyPlugin` or `my_plugin`)
- Command files: kebab-case `.md`
- Agent files: kebab-case `.md` describing role
- Skill directories: kebab-case
- Script files: kebab-case with extension (`.sh`, `.py`, `.js`)

**Skill quality (run skill-reviewer for each skill):**
```
"Review my skill at skills/skill-name/SKILL.md"
```

---

## Step 5: Report and Remediate

**Severity levels:**
- **Critical** -- plugin won't work or is insecure. Fix immediately. (e.g., invalid JSON, hardcoded credentials, missing required fields)
- **Warning** -- degrades quality or usability. Fix before distribution. (e.g., missing README, vague skill descriptions, no `<example>` blocks in agents)
- **Minor** -- best practice improvement. Fix when convenient.

**Fix critical issues first, then re-validate:**
```bash
# Re-run validation after fixes
"Validate my plugin at <path>"
```

**Keep running until: 0 critical issues, warnings addressed or documented.**

---

## Standards Reference

**././././././././././././plugin.json minimal valid:**
```json
{ "name": "plugin-name" }
```

**././././././././././././plugin.json recommended:**
```json
{
  "name": "plugin-name",
  "version": "0.1.0",
  "description": "What the plugin does",
  "author": { "name": "Author Name", "email": "email" }
}
```

**Agent description pattern (must have `<example>` blocks):**
```markdown
description: |
  Use this agent when user asks to "do X", "run Y", or mentions Z.
  
  <example>
  Context: user just finished creating a plugin
  user: "I've set up my plugin"
  assistant: "Let me validate the structure."
  </example>
```

**Skill description pattern (third-person, anti-undertrigger):**
```yaml
description: >
  This skill should be used when the user asks to "X", "Y", or "Z".
  Use this skill even when the user doesn't explicitly say "Z" -- 
  mentions of [related concept] should also trigger this.
```

---

## Next Actions
- **Fix gaps**: Run `create-skill`, `create-command`, or `create-hook` to add missing components
- **Improve skills**: Run `skill-reviewer` on each skill for trigger optimization
- **Upgrade to L5**: Run `audit-plugin-l5` for advanced red-team structural audit
- **Package**: Run `package-plugin` to create a distributable ZIP
