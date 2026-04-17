---
concept: claude-code-claude-directory-specification
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/claude-project-setup/references/claude-directory-spec.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.744644+00:00
cluster: project
content_hash: f8b08332957181cb
---

# Claude Code `.claude/` Directory Specification

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Claude Code `.claude/` Directory Specification

Source: https://code.claude.com/docs/en/claude-directory

## Project-Level Files

### `CLAUDE.md` (or `.claude/CLAUDE.md`)
- Project instructions Claude reads every session
- Loaded into context at start of every session
- **Target under 200 lines.** Longer files still load in full but may reduce adherence
- If something only matters for specific tasks, move it to a skill or a path-scoped rule in `.claude/rules/`
- Also works at `.claude/CLAUDE.md` if you prefer to keep the project root clean

### `.claude/rules/*.md`
- Topic-scoped instructions, optionally gated by file paths
- Rules **without** `paths:` frontmatter load at session start (like CLAUDE.md)
- Rules **with** `paths:` frontmatter load only when Claude reads a matching file
- Subdirectories work: `.claude/rules/frontend/react.md` is discovered automatically
- When CLAUDE.md approaches 200 lines, start splitting into rules

**Rule file format:**
```markdown
---
paths:
  - "**/*.test.ts"
  - "**/*.test.tsx"
---

# Testing Rules

- Use descriptive test names
- Mock external dependencies, not internal modules
```

### `.claude/settings.json`
- Permissions, hooks, env vars, model defaults
- Committed to git — shared with team
- Overridden by `settings.local.json` for personal use

**Key fields:**
- `permissions.allow` — allow tool use without prompting (e.g. `Bash(npm test *)`)
- `permissions.deny` — block tool use (e.g. `Bash(rm -rf *)`)
- `permissions.ask` — require confirmation
- `hooks` — run your scripts at lifecycle events (PreToolUse, PostToolUse, SessionStart, etc.)
- `model` — default model override
- `env` — environment variables set in every session
- `outputStyle` — custom system-prompt style

### `.claude/settings.local.json`
- Personal overrides, **auto-gitignored**
- Same schema as `settings.json`
- Highest of user-editable settings; use for machine-specific or experimental config

### `.claude/skills/`
- Reusable prompts invoked with `/skill-name` or auto-invoked by Claude
- Each skill is a folder with a `SKILL.md` plus supporting files
- `disable-model-invocation: true` — user-only, Claude cannot auto-invoke
- `user-invocable: false` — hidden from `/` menu, Claude can still invoke

### `.claude/commands/`
- Single-file prompts invoked with `/name`; same mechanism as skills
- **Prefer skills for new workflows** — use `commands/` as thin wrappers that delegate to skills

### `.claude/agents/`
- Subagents with their own context window, system prompt, and tool restrictions
- Frontmatter: `name`, `description`, `tools` (restrict tool access), `memory`

### `.claude/hooks/`  
- Hook configuration files. Registered in `settings.json` under `hooks:`

### `.mcp.json` (project root)
- Project-scoped MCP servers, committed and shared with team
- Personal/user servers go in `~/.claude.json` instead

## Settings Precedence (highest → lowest)
1. Managed settings (IT/admin deployed) — cannot be overridden
2. Command line arguments
3. Local project settings (`.claude/settings.local.json`)
4. Shared project settings (`.claude/settings.json`)
5. User settings (`~/.claude/settings.json`)

**Array settings merge across scopes** — `permissions.allow` arrays are concatenated, not replaced.


## See Also

- [[claude-code-subagents-collection]]
- [[claude-code-settingsjson-schema-reference]]
- [[claude-code-settingsjson-schema-reference]]
- [[improvement-ledger-specification]]
- [[context-status-specification-contextstatusmd]]
- [[claude-md-hierarchy]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/claude-project-setup/references/claude-directory-spec.md`
- **Indexed:** 2026-04-17T06:42:09.744644+00:00
