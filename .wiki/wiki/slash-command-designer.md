---
concept: slash-command-designer
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-command/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.797693+00:00
cluster: bash
content_hash: e5fed588b387ccba
---

# Slash Command Designer

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: create-command
description: >
  This skill should be used when the user asks to "create a slash command", "add a command",
  "write a custom command", "define a command with arguments", "create a command that runs
  bash", "add a /command to my plugin", "use $ARGUMENTS in a command", "set up
  argument-hint", "create a workflow command", "interactive command", or needs guidance on
  slash command structure, YAML frontmatter fields, file references, bash execution,
  command organization, or command best practices. Use this skill whenever Claude Code
  slash commands are mentioned even without the word "command" -- e.g. "I want a shortcut
  that reviews PRs" or "automate my deploy workflow" should trigger this.
  Do NOT use this for hooks (use create-hook), skills (use create-skill), or agents
  (use create-sub-agent).
allowed-tools: Bash, Read, Write
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

# Slash Command Designer

Slash commands are reusable Markdown prompts that Claude executes when invoked with
`/command-name`. They provide consistency, efficiency, and shareability for common
workflows. Commands can be simple prompts or powerful multi-step workflows using dynamic
arguments, file references, bash execution, and integration with agents and skills.

> Reference files for deep dives:
> - `references/frontmatter-reference.md` -- full list of all frontmatter fields
> - `references/interactive-commands.md` -- AskUserQuestion, conditional logic
> - `references/advanced-workflows.md` -- multi-step, multi-component patterns
> - `references/plugin-features-reference.md` -- ${CLAUDE_PLUGIN_ROOT}, bash execution syntax
> - `references/examples/simple-commands.md` -- copy-ready simple command templates
> - `references/examples/plugin-commands.md` -- copy-ready plugin command templates

---

## The Most Important Rule

**Commands are instructions FOR Claude, not messages TO the user.**

When `/command-name` is invoked, the command body becomes Claude's instructions. Write
what Claude should DO, not what the user will see.

```markdown
# CORRECT -- tells Claude what to do:
Review this code for security vulnerabilities:
- SQL injection
- XSS attacks
- Authentication bypass
Provide specific line numbers and severity ratings.

# WRONG -- addresses the user, not Claude:
This command will review your code for security issues.
You will receive a report with vulnerability details.
```

---

## Step 1: Understand the Use Case

Extract from context first. Ask only what is unclear.

**Core questions:**

1. **What workflow should this automate?** One command, one purpose.

2. **Which command type fits?**
   - **Simple**: Static prompt, no arguments, no bash -- just a great reusable instruction
   - **Dynamic**: Uses `$ARGUMENTS`, `$1`/`$2` positional args, or file references (`@$1`)
   - **Bash-powered**: Inline `!`` `` ` `` bash commands to gather dynamic context before Claude runs
   - **Multi-component**: Coordinates skills, agents, and scripts in a workflow

3. **Where should it live?**
   - `.claude/skills/<name>/SKILL.md` -- **recommended** for new work (supports supporting files,
     cross-agent portability, inline hooks). The directory name becomes the slash command.
   - `.claude/commands/<name>.md` -- flat file, still works, simpler but no supporting files.
     **Note**: confirmed macOS discovery bug (GitHub #13906) with `.claude/commands/` in
     some Claude Code versions. Prefer `skills/` or a local plugin for reliability.
   - `~/.claude/skills/<name>/SKILL.md` -- personal commands available in all projects
   - `plugin-name/skills/<name>/SKILL.md` -- distributed with plugin, namespaced as
     `/plugin-name:<name>` -- **always us

*(content truncated)*

## See Also

- [[os-init-command]]
- [[os-loop-command]]
- [[os-memory-command]]
- [[ui-designer]]
- [[ux-designer]]
- [[chained-command-invocation-via-offer-next-steps-blocks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-command/SKILL.md`
- **Indexed:** 2026-04-17T06:42:09.797693+00:00
