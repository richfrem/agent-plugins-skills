---
name: create-command
accreditation: Patterns, examples, and terminology gratefully adapted from Anthropic public plugin-dev and skill-creator repositories.
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
disable-model-invocation: false
allowed-tools: Bash, Read, Write
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
> - `examples/simple-commands.md` -- copy-ready simple command templates
> - `examples/plugin-commands.md` -- copy-ready plugin command templates

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
   - `.claude/commands/` -- project commands (shared with team, shown as "(project)")
   - `~/.claude/commands/` -- personal commands (all projects, shown as "(user)")
   - `plugin-name/commands/` -- plugin commands (distributed with plugin, shown as "(plugin-name)")

4. **Does it need arguments?** Use `$ARGUMENTS` (all as one string) or `$1`, `$2` (positional).

5. **Does it need to read files?** Use `@file-path` or `@$1` for dynamic file args.

6. **Tool restrictions needed?** Set `allowed-tools` to restrict scope (e.g. `Bash(git:*)` not `Bash(*)`).

---

## Step 2: Choose the Right Pattern

### Pattern A: Simple static command
```markdown
---
description: Review code for security vulnerabilities
allowed-tools: Read, Grep
---

Review the current file for security vulnerabilities including:
- SQL injection risks
- XSS attack vectors
- Authentication bypass
- Insecure data handling

Provide specific line numbers and severity (critical/high/medium/low).
```

### Pattern B: Dynamic arguments with $ARGUMENTS
```markdown
---
description: Fix GitHub issue by number
argument-hint: [issue-number]
---

Fix issue #$ARGUMENTS following our coding standards and writing tests for all changes.
```

### Pattern C: Positional arguments $1, $2
```markdown
---
description: Review PR with priority and assignee
argument-hint: [pr-number] [priority] [assignee]
---

Review pull request #$1 with $2 priority.
After review, assign to $3 for follow-up action.
```

### Pattern D: File reference
```markdown
---
description: Generate documentation for a source file
argument-hint: [source-file]
---

Generate comprehensive documentation for @$1 including:
- Function/class descriptions and parameter docs
- Return value descriptions with types
- Usage examples with edge cases
```

### Pattern E: Bash context injection
```markdown
---
description: Review code changes
allowed-tools: Read, Bash(git:*)
---

Files changed: !`git diff --name-only HEAD~1`
Current branch: !`git branch --show-current`

Review each changed file for:
1. Code quality and style consistency
2. Potential bugs or regressions
3. Test coverage gaps
4. Documentation needs

Provide specific feedback per file.
```

### Pattern F: Plugin command with ${CLAUDE_PLUGIN_ROOT}
```markdown
---
description: Run plugin analyzer on target file
argument-hint: [file-path]
allowed-tools: Bash(node:*), Read
---

Run analysis: !`node ${CLAUDE_PLUGIN_ROOT}/scripts/analyze.js $1`

Load rules: @${CLAUDE_PLUGIN_ROOT}/config/rules.json

Review results and report findings by severity.
```

---

## Step 3: Scaffold and Write

### Directory and file creation
```bash
# Project command
mkdir -p .claude/commands
touch .claude/commands/<name>.md

# Personal command
mkdir -p ~/.claude/commands
touch ~/.claude/commands/<name>.md

# Plugin command (namespaced)
mkdir -p plugin-name/commands/<category>
touch plugin-name/commands/<category>/<name>.md
```

### YAML frontmatter quick reference

| Field | Purpose | Example |
|-------|---------|---------|
| `description` | Text in `/help` (keep under 60 chars) | `description: Review PR for issues` |
| `argument-hint` | Autocomplete hint | `argument-hint: [pr-number] [env]` |
| `allowed-tools` | Restrict tool access | `allowed-tools: Read, Bash(git:*)` |
| `model` | Override model | `model: haiku` |
| `disable-model-invocation` | Block programmatic calls | `disable-model-invocation: true` |

No frontmatter is needed for simple commands -- omit the `---` block entirely.

### Argument handling rules
- `$ARGUMENTS` -- all user-supplied text as one string (use for simple single-arg commands)
- `$1`, `$2`, `$3` -- positional (use when multiple distinct args needed)
- Mix: `$1` for first, `$ARGUMENTS` for "everything after"
- Always document with `argument-hint` and handle the missing-arg case in the prompt

### Bash inline execution syntax
```markdown
!`command`          -- executes, output injected before Claude processes
!`git diff HEAD~1`  -- inject git diff
!`cat package.json` -- inject file contents (alternative to @syntax)
```
Use `allowed-tools: Bash(git:*)` to scope permissions. See `references/plugin-features-reference.md`
for full bash execution details and edge cases.

### File references
```markdown
@path/to/file.md      -- static file reference, Claude reads before processing
@$1                    -- dynamic file reference using first argument
@${CLAUDE_PLUGIN_ROOT}/templates/report.md  -- plugin-relative file
```

### Argument validation pattern
```markdown
---
argument-hint: [environment]
---

Validate: !`echo "$1" | grep -E "^(dev|staging|prod)$" && echo "valid" || echo "invalid"`

If $1 is a valid environment (dev/staging/prod):
  Deploy to $1 environment
Otherwise:
  Explain valid environments and show usage: /deploy [dev|staging|prod]
```

### Multi-component workflow pattern (agent + skill + script)
```markdown
---
description: Comprehensive review workflow
argument-hint: [file]
allowed-tools: Bash(node:*), Read
---

Target: @$1

Phase 1 - Static analysis:
!`node ${CLAUDE_PLUGIN_ROOT}/scripts/lint.js $1`

Phase 2 - Deep review:
Launch the code-reviewer agent for detailed analysis.

Phase 3 - Standards check:
Use the coding-standards skill for validation.

Phase 4 - Report:
Template: @${CLAUDE_PLUGIN_ROOT}/templates/review.md
Compile findings following the template structure.
```

---

## Step 4: Organize Commands

### Naming convention
- Use verb-noun: `review-pr`, `fix-issue`, `deploy-staging`
- Avoid generics: `test`, `run`, `build` (conflict-prone)
- Hyphens for multi-word, no underscores

### Namespacing with subdirectories
```
commands/
├── ci/
│   ├── build.md        # /build (project:ci)
│   ├── test.md         # /test (project:ci)
│   └── lint.md
├── git/
│   ├── commit.md
│   └── review-pr.md
└── docs/
    └── generate.md
```
Use subdirectories when you have 15+ commands or clear logical categories.

### Inline documentation
```markdown
<!--
Usage: /deploy [staging|production] [version]
Requires: AWS credentials configured
Example: /deploy staging v1.2.3
-->

Deploy application to $1 environment using version $2...
```

---

## Step 5: Validate

**Checklist:**
- [ ] Command body written as instructions TO Claude (not messages to user)
- [ ] `description` is clear and under 60 chars
- [ ] `argument-hint` documents all arguments
- [ ] `allowed-tools` restricts to only what's needed
- [ ] `$ARGUMENTS` / `$1` / `$2` used correctly with defaults for missing args
- [ ] `@file` references use valid paths (test they exist)
- [ ] Bash commands are safe and use `Bash(cmd:*)` not `Bash(*)` where possible
- [ ] Plugin commands use `${CLAUDE_PLUGIN_ROOT}` not hardcoded paths
- [ ] Command file is in the correct location (`.claude/commands/` etc.)
- [ ] Restart Claude Code after adding new commands

**Test the command:**
```
> /command-name arg1 arg2
```
Verify arguments expand correctly and Claude follows the instructions as intended.

**Run audit:**
```
audit-plugin    -- validates full plugin structure including commands
```

---

## Next Actions
- **Refine**: Run `continuous-skill-optimizer` to benchmark trigger optimization
- **Extend**: Add interactivity with `AskUserQuestion` -- see `references/interactive-commands.md`
- **Distribute**: Add to a plugin for team sharing -- see `examples/plugin-commands.md`
- **Audit**: Run `audit-plugin` to validate structure
