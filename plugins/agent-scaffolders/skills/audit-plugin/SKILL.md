---
name: audit-plugin
plugin: agent-scaffolders
description: >
  This skill should be used when the user asks to "audit a plugin", "validate my plugin",
  "check plugin structure", "verify plugin is correct", "validate .claude-plugin/plugin.json", "check if
  my plugin is compliant", "review plugin components", or mentions plugin validation or
  structure compliance. Also trigger proactively after the user creates or modifies any
  plugin component (commands, agents, skills, hooks, .claude-plugin/plugin.json). Use this skill even
  when the user says "check my work" or "make sure this is right" in a plugin context.
  Do NOT use this for auditing individual skills only (use skill-reviewer for that).
allowed-tools: Bash, Read, Write, Glob, Grep
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `../../requirements.txt` for the dependency lockfile (currently empty — standard library only).

---

# Plugin Auditor

Performs comprehensive validation of a Claude Code plugin against structure standards,
naming conventions, component requirements, and security best practices. Uses the
`plugin-validator` agent for deep validation, supported by component-specific scripts.

---

## Step 1: Locate the Plugin

Establish the plugin root:
- Look for `../../../../.claude-plugin/plugin.json` -- this is the definitive marker
- If user didn't specify a path, check current directory and common locations
- Confirm with user if ambiguous

---

## Step 2: Run plugin-validator Agent

> **Note**: The `plugin-validator` agent is defined in `agent-scaffolders`. If not installed,
> skip this step and rely on the component scripts in Step 3 and manual checks in Step 4.

Trigger the `plugin-validator` agent for comprehensive validation:

```
"Validate the plugin at <path>"
```

The agent checks all 10 categories automatically:
1. Manifest (`../../../../.claude-plugin/plugin.json`) -- JSON syntax, required `name` field, kebab-case
2. Directory structure -- components at root, not inside `.claude-plugin/`
3. Commands (`commands/**/*.md`) -- frontmatter, `description`, `argument-hint`, `allowed-tools`
4. Agents (`agents/**/*.md`) -- `name`, `description` with `<example>` blocks, `model`, `color`
5. Skills (`skills/*/SKILL.md`) -- frontmatter, `name`, `description` (<= 1024 chars), supporting directories
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

## Step 2b: Auto-Fix Claude Code Load Errors

Before deep validation, run the load-error fixer to catch issues that prevent
Claude Code from loading the plugin at all. These are silent failures — the plugin
simply doesn't load with no useful error until you run `/doctor`.

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/fix_plugin_load_errors.py <plugin_root>
```

**What it fixes automatically:**

| Issue | Symptom in /doctor | Root cause |
|---|---|---|
| `plugin.json` has `skills`/`agents`/`hooks`/`commands` arrays | `Invalid input` | Validator rejects these — auto-discovery handles them |
| `hooks.json` is `{}` (empty object) | `expected record, received undefined` | Must be `{"hooks": {}}` |
| `hooks.json` is `[]` (array) | `expected object received array` | Must be an object |
| `hooks.json` flat format `{"EventName":{...}}` | `expected record, received undefined` | Must be nested under `"hooks"` key |
| `hooks.json`/`lsp.json`/`.mcp.json` has literal `\n` chars | `Unrecognized token '\'` | Python `json.dump` wrote escaped newlines; file must have real newlines |
| `SKILL.md` has comment lines before `---` | skill fails to load | Frontmatter parser requires `---` as the very first line |

**Correct `hooks.json` format:**
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [{ "type": "command", "command": "python ${CLAUDE_PLUGIN_ROOT}/hooks/script.py" }]
      }
    ]
  }
}
```

**Empty hooks (no hooks needed):**
```json
{ "hooks": {} }
```

**IMPORTANT — Cache coverage**: Claude Code scans ALL cached versions under
`~/.claude/plugins/cache/`, not just the active `installPath`. Fixing source files
and reinstalling is the only reliable fix. Use `uvx plugin-add` to reinstall.

---

## Step 2c: Detect and Fix Symlink Stand-Ins

Git checks out symlinks as plain-text "stand-in" files when `core.symlinks=false` (common on
Windows without Developer Mode, or when cloned without the setting). Stand-ins look like real files
but contain only a relative path (e.g. `../../../scripts/execute.py`). They are functionally broken
— the bridge installer will copy the path string, not the actual script.

**Run the bulk scanner** from the link-checker plugin:

```bash
python plugins/link-checker/scripts/bulk_symlink_fixer.py plugins/<plugin-name>
```

The scanner detects both:
- **text-file stand-ins**: small plain-text files (`< 512 bytes`) whose content looks like a relative path
- **broken symlinks**: real symlinks whose target no longer exists

**Important — the fixer has a silent failure mode.** `symlink_manager.py` always exits 0, so
`bulk_symlink_fixer.py` prints "✓ Fixed" even when the source doesn't exist. Always verify manually:

```bash
# Confirm symlinks resolved (count should match expectations)
find plugins/<plugin-name> -type l | wc -l

# Confirm no text-file stand-ins remain for scripts paths (critical)
find plugins/<plugin-name>/skills -path "*/scripts/*" -type f ! -type l
```

**Two categories of stand-ins:**

1. **Valid stand-ins** (target exists) — the fixer converts these automatically. If it fails
   silently, convert manually:
   ```python
   # Read the path out of the stand-in, unlink the file, recreate as symlink
   content = Path(standin).read_text().strip()
   Path(standin).unlink()
   Path(standin).symlink_to(content)
   ```

2. **Wrong-path stand-ins** (target missing) — common cause: an extra subdirectory in the path
   (e.g. `references/architecture/architecture.md` when the file is at `references/architecture.md`).
   Correct the relative path before creating the symlink. Check what actually exists at the plugin
   `references/` root and recalculate the depth.

**Correct symlink pattern (must match ADR manager / all standard skills):**
```
skills/<skill>/scripts/execute.py  →  ../../../scripts/<canonical_name>.py
skills/<skill>/references/architecture.md  →  ../../../references/architecture.md
```
The symlink filename and the target filename may differ (e.g. `execute.py` → `exploration_optimizer_execute.py`)
— that is intentional and valid.

**6 known missing-source stand-ins in exploration-cycle-plugin** (leave as-is until source files
are created at `plugins/exploration-cycle-plugin/references/`):
`agent-loop-patterns.md`, `exploration-output-standards.md`

---

## Step 3: Run Component-Specific Scripts

After plugin-validator, run targeted scripts for detailed checks:

**Validate each agent file:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate_agent.py agents/my-agent.md
```
Checks: frontmatter structure, required fields (name/description/model/color), name format
(3-50 chars, lowercase + hyphens), description has `<example>` blocks, system prompt
length (minimum 20 chars, recommended 500-3,000).

**Validate hooks.json schema:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate_hook_schema.py hooks/hooks.json
```
Checks: JSON syntax, valid event names, each hook has `matcher` + `hooks` array,
hook type is `command` or `prompt`, command hooks reference existing scripts with
`${CLAUDE_PLUGIN_ROOT}`.

**Test a hook script directly:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/test_hook.py \
  --hook hooks/scripts/validate.py \
  --event PreToolUse \
  --input '{"tool_name": "Write", "tool_input": {"file_path": "src/app.py"}}'
```

**Lint hook scripts for common issues:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/hook_linter.py hooks/
```

---

## Step 4: Manual Checks

For issues the scripts may not catch:

**Plugin structure check:**
```bash
# Manifest must be here (not in root)
ls .claude-plugin/plugin.json

# Components must be at root (not in .claude-plugin/)
ls commands/ agents/ skills/ hooks/

# Validate JSON
jq . .claude-plugin/plugin.json
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

---

## Standards & References

- **Architectural Decision Records (ADRs)** located at `references/*.md`. Always consult them (especially ADR 001-006) to verify if the plugin follows our standards for shared scripts, cross-plugin dependencies, symlinking patterns, and loose coupling. A plugin that violates these ADRs (e.g. duplicates shared scripts instead of symlinking) is considered structurally non-compliant.

## Standards Reference

**.claude-plugin/plugin.json minimal valid:**
```json
{ "name": "plugin-name" }
```

**.claude-plugin/plugin.json recommended:**
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
- **Distribute**: Push to GitHub — users install via `plugin_add.py richfrem/agent-plugins-skills`
