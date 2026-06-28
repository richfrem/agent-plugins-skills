---
name: audit-plugin
description: Validate a plugin's structure, components, and security
argument-hint: "[plugin-path]"
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Plugin Auditor

Performs comprehensive validation of a Claude Code plugin against structure standards,
naming conventions, component requirements, and security best practices.

---

## Step 1: Locate the Plugin

Establish the plugin root:
- Look for `./././././././././././././plugin.json` -- this is the definitive marker
- If user didn't specify a path, check current directory and common locations
- Confirm with user if ambiguous

---

## Step 2: Run Component Validation Scripts

Run the scripts bundled in this plugin to validate the target plugin's components.
All scripts are in the `agent-scaffolders` plugin's own `scripts/` directory.

**Validate agent files:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate_agent.py agents/my-agent.md
```

**Validate hooks.json schema:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate_hook_schema.py hooks/hooks.json
```

**Test a hook script directly:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/test_hook.py \
  --hook hooks/scripts/validate.py \
  --event PreToolUse \
  --input '{"tool_name": "Write", "tool_input": {"file_path": "src/app.py"}}'
```

**Lint hook scripts:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/hook_linter.py hooks/
```

Checks performed by validate_agent.py: frontmatter structure, required fields (name/description/model/color),
name format (3-50 chars, lowercase + hyphens), `<example>` blocks in description, system prompt length.

**Output format:**
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

## Step 3: Additional Manual Checks

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

**Portability check:**
```bash
# No hardcoded paths in hook commands or MCP config
grep -rn "/Users/\|/home/" --include="*.json" --include="*.sh" .
# No cross-plugin sibling paths
grep -rn "\.\./\.\." --include="*.md" --include="*.json" .
```

**Naming conventions:**
- Plugin name: kebab-case (`my-plugin`, not `MyPlugin` or `my_plugin`)
- Command files: kebab-case `.md`
- Agent files: kebab-case `.md` describing role
- Skill directories: kebab-case
- Script files: kebab-case with extension (`.py`, `.js`)

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

---

## Post-Audit Verification

After making any changes, verify commands are correctly discovered:

1. Run `/reload-plugins` to pick up changes without restarting Claude Code
2. Run `/context` to verify no skills are excluded by the character budget
   - If skills are excluded: set `SLASH_COMMAND_TOOL_CHAR_BUDGET=200000` in your environment
3. Run `/help` and confirm commands appear with the correct namespace (`/plugin-name:command`)
4. Test one command end-to-end: `/plugin-name:command-name test-argument`
5. Run `/doctor` if commands still don't appear — it reports discovery failures

**If a command is missing after reload:**
```
[ ] YAML frontmatter valid? `name` field present? No tabs, no missing closing ---?
[ ] Plugin namespace correct? Use /plugin-name:command, not /command.
[ ] macOS + .claude/commands/ bug? Migrate to .claude/skills/ or a local plugin.
[ ] Character budget? Run /context to check.
```

---

## Next Actions
- **Fix gaps**: Run `create-skill`, `create-command`, or `create-hook` to add missing components
- **Improve skills**: Run `skill-reviewer` on each skill for trigger optimisation
- **Upgrade to L5**: Run `audit-plugin-l5` for advanced red-team structural audit
- **Distribute**: Push to GitHub — users install via `plugin_add.py richfrem/agent-plugins-skills`
