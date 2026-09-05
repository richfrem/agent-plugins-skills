---
name: create-command
plugin: agent-scaffolders
description: >
  Guidance on slash commands vs. skills. Explains modern best practices where skills
  (skills/<name>/SKILL.md) supersede legacy commands/workflows (commands/<name>.md),
  and guides users to use create-skill instead for portable, evaluated, multi-agent workflows.
  Retains reference for creating personal flat prompt shortcuts if explicitly requested.
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

# Slash Commands & Modern Skill Architecture

> [!IMPORTANT]
> **Modern Agent Guidance (2026+): Skills Supersede Commands & Workflows**
> In modern agent platforms (Claude Code, Antigravity, Cursor, Codex, Gemini CLI, MAF):
> 1. **Skills ARE Slash Commands**: Any skill placed in `skills/<skill-name>/SKILL.md` is automatically invokable via `/skill-name` (or `@skill-name`).
> 2. **Skills are Superior**: Skills support accompanying scripts, evaluation suites (`evals/evals.json`), references, and multi-file context. Flat command files (`commands/*.md`) do not.
> 3. **Avoid Duplication**: Never create identical copies in `commands/` and `skills/`.
> 
> **Recommendation:**
> - If building plugin capabilities or multi-step agent workflows: **USE `create-skill` INSTEAD**.
> - Only use flat slash commands (`.claude/commands/<name>.md` or `~/.claude/commands/<name>.md`) for personal, lightweight, single-file prompt templates that require no scripts or evaluations.

---

## Slash Command Designer (Legacy & Personal Shortcuts)

Slash commands are Markdown prompt templates executed when invoked with `/command-name`.
In early Claude Code setups, they lived in `.claude/commands/<name>.md`. Today, authoring as a
Skill (`skills/<name>/SKILL.md`) is standard across all agent tooling.

> Reference files for deep dives:
> - `references/frontmatter-reference.md` -- full list of all frontmatter fields
> - `references/interactive-commands.md` -- AskUserQuestion, conditional logic
> - `references/advanced-workflows.md` -- multi-step, multi-component patterns
> - `references/plugin-features-reference.md` -- ${CLAUDE_PLUGIN_ROOT}, bash execution syntax
> - `references/examples/simple-commands.md` -- copy-ready simple command templates
> - `references/examples/plugin-commands.md` -- copy-ready plugin command templates

---

## The Most Important Rule

**Commands are instructions FOR the AI agent, not messages TO the user.**

When `/command-name` is invoked, the command body becomes instructions. Write
what the AI agent should DO, not what the user will see.

```markdown
# CORRECT -- tells agent what to do:
Review this code for security vulnerabilities:
- SQL injection
- XSS attacks
- Authentication bypass
Provide specific line numbers and severity ratings.

# WRONG -- addresses the user, not agent:
This command will review your code for security issues.
You will receive a report with vulnerability details.
```

---

## Step 1: Decision Matrix — Skill vs. Command

Before writing a flat command file, evaluate:

| Requirement | Recommended Path | Reason |
|:---|:---|:---|
| Plugin feature, reusable agent capability | **`create-skill`** | First-class across all agents, has `evals.json`, scripts, references |
| Multi-step workflow with helper scripts | **`create-skill`** | Commands cannot cleanly bundle dedicated scripts |
| Cross-tool portability (Claude, Codex, Gemini, MAF) | **`create-skill`** | `commands/` is Claude-only legacy; `skills/` is universal |
| Personal quick prompt shortcut (no scripts, single user) | Flat command (`~/.claude/commands/`) | Simple, zero overhead for personal ad-hoc use |

If the user wants a reusable capability, **redirect to `create-skill`**:
```bash
# Scaffold as a standard portable skill instead
/create-skill <name>
```

---

## Step 2: Where Should It Live? (If Flat Command is Explicitly Chosen)

1. **Personal ad-hoc shortcuts**: `~/.claude/commands/<name>.md`
2. **Project-local prompt shortcut**: `.claude/commands/<name>.md`
3. **Plugin capability**: Put in `plugins/<plugin>/skills/<name>/SKILL.md` (**NOT** `commands/`). Modern plugin installers discover `skills/` directly as slash commands.

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

### Default scaffold: `skills/` directory (recommended)
```bash
# Project command (as skill directory)
mkdir -p .claude/skills/<name>
touch .claude/skills/<name>/SKILL.md
# optionally: mkdir -p .claude/skills/<name>/evals
# optionally: touch .claude/skills/<name>/acceptance-criteria.md

# Personal command
mkdir -p ~/.claude/skills/<name>
touch ~/.claude/skills/<name>/SKILL.md

# Plugin command (namespaced as /plugin-name:<name>)
mkdir -p plugin-name/skills/<name>
touch plugin-name/skills/<name>/SKILL.md
```

### Simple mode: flat `.md` file (still supported)
```bash
mkdir -p .claude/commands
touch .claude/commands/<name>.md
```
Use for one-liner prompts with no supporting files. For anything more complex, prefer
the `skills/` directory so you can add `references/`, `evals/`, and inline hooks later.

### YAML frontmatter complete reference

| Field | Purpose | Default | Example |
|-------|---------|---------|---------|
| `name` | **Required.** Slash command name. Kebab-case. | — | `name: deploy` |
| `description` | Text in `/help`. Hard limit 1024 chars. Keep under 150 words. | — | `description: Deploy to target env.` |
| `argument-hint` | Autocomplete hint for arguments | — | `argument-hint: "[env: dev\|staging\|prod]"` |
| `allowed-tools` | Restrict tool access (least privilege) | All | `allowed-tools: Read(*), Bash(git *)` |
| `disable-model-invocation` | `true` = user-only, blocks auto-invoke | `false` | `disable-model-invocation: true` |
| `user-invocable` | `false` = background knowledge, not user-typed | `true` | `user-invocable: false` |
| `model` | Override model for this command | session default | `model: claude-haiku-4-5-20251001` |
| `effort` | Override effort level | `medium` | `effort: low` |
| `maxTokens` | Cap token budget for this command | model default | `maxTokens: 4096` |
| `hooks` | Inline hooks scoped to this skill's lifetime | — | see create-hook |
| `isolation` | Run in isolated git worktree | `none` | `isolation: worktree` |

No frontmatter is needed for the simplest commands -- omit the `---` block entirely.

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
- [ ] `name` field present (required — without it the command silently fails to register)
- [ ] `description` clear, under 150 words, hard limit 1024 chars
- [ ] `argument-hint` documents all arguments
- [ ] `allowed-tools` restricts to only what's needed
- [ ] `$ARGUMENTS` used for single-arg commands; `$1`/`$2` for multiple distinct args
- [ ] `@file` references use valid paths
- [ ] Bash commands scoped: `Bash(git *)` not `Bash(*)` where possible
- [ ] Plugin commands use `${CLAUDE_PLUGIN_ROOT}` not hardcoded paths
- [ ] Plugin commands referenced from agents/skills use **full namespaced form**: `/plugin-name:command`
- [ ] Command is in `skills/` directory (preferred) or `commands/` (flat, simple only)

**Test the command:**
```
/command-name arg1 arg2
```

**If the command isn't showing up, work through this in order:**
```
[ ] 1. YAML syntax: open SKILL.md, check frontmatter manually.
        `---` markers must be on their own lines, no leading spaces.
[ ] 2. name field: must be present.
[ ] 3. Plugin namespace: if installed as plugin, use /plugin-name:command not /command.
[ ] 4. Scope: is it in ~/.claude/skills/ (always) or .claude/skills/ (this project only)?
[ ] 5. Budget: run /context -- are skills excluded? Fix: SLASH_COMMAND_TOOL_CHAR_BUDGET=200000
[ ] 6. Platform: macOS + .claude/commands/ has a known bug (#13906). Migrate to skills/.
[ ] 7. Reload: run /reload-plugins after editing.
[ ] 8. Health: run /doctor for failures.
[ ] 9. Verify: run /help -- does the command appear with correct namespace?
```

**Run audit:**
```
audit-plugin    -- validates full plugin structure including commands
```

---

## Next Actions
- **Refine**: Run `continuous-skill-optimizer` to benchmark trigger optimization
- **Extend**: Add interactivity with `AskUserQuestion` -- see `references/interactive-commands.md`
- **Distribute**: Add to a plugin for team sharing -- see `references/examples/plugin-commands.md`
- **Audit**: Run `audit-plugin` to validate structure
