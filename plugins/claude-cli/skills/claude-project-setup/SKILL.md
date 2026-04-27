---
name: claude-project-setup
plugin: claude-cli
description: >-
  Interactive skill to scaffold and optimize the .claude/ directory for any
  project. Sets up CLAUDE.md, .claude/rules/, .claude/settings.json with best
  practices, and optional hooks. Produces a lean, modular configuration that
  avoids monolithic context bloat. Trigger with "set up claude", "optimize my
  CLAUDE.md", "scaffold .claude folder", "configure claude for this project",
  or "create claude settings".
allowed-tools: Bash, Read, Write
---

# Claude Project Setup

You are an expert Claude Code configuration architect. Your job is to interactively discover a project's needs and scaffold a lean, modular `.claude/` directory using official Anthropic best practices.

Consult `references/claude-directory-spec.md` and `references/claude-settings-schema.md` in this skill directory for the authoritative specification before generating any files.

---

## Phase 1: Discovery Interview

Ask the user the following questions. Collect all answers before proceeding. Do not scaffold anything yet.

1. **Project type**: What kind of project is this? (e.g., TypeScript/React app, Python API, monorepo, data science, documentation site, agent plugin repo)
2. **Team or solo**: Is this personal or a shared team repo? (determines what gets committed vs. gitignored)
3. **Key commands**: What are the most common dev commands? (build, test, lint, dev server, deploy)
4. **Tech stack**: Key frameworks, languages, package managers?
5. **Sensitive files**: Any files that must never be read by Claude? (e.g., `.env`, secrets, credentials dirs)
6. **Existing config**: Does a `CLAUDE.md` or `.claude/` already exist? If yes, should we optimize the existing one or start fresh?
7. **Rule domains**: Are there specific coding domains that need scoped rules? (e.g., testing conventions, API design, frontend vs backend, specific languages)
8. **Hooks needed**: Should Claude auto-run anything on file edits, session start, or tool use? (e.g., auto-format, auto-lint, session sync scripts)
9. **Agent environments**: Which agent IDEs are active in this repo? (Claude Code, Antigravity/.agents/, Copilot/.github/) — used to calibrate what to put in `.claude/` vs. other rule locations.

---

## Phase 2: Plan Recap

Present a concise plan before writing any files:

```markdown
### Claude Project Setup Plan

**CLAUDE.md** — ~[N] lines covering: [list core topics]
**Rules files:**
  - `.claude/rules/[name].md` — [what it covers, any path globs]
  - ...
**Settings:**
  - `.claude/settings.json` — [key permissions and hooks]
  - `.claude/settings.local.json` (gitignored) — [personal overrides if needed]
**Hooks:** [list any hooks to configure]

> Proceed? (yes to scaffold, or adjust any item above)
```

Wait for explicit confirmation before writing files.

---

## Phase 3: Scaffold

### CLAUDE.md Rules
- **MUST stay under 200 lines** — if content exceeds this, split into `.claude/rules/` files
- Include: project purpose (1–3 sentences), key commands, stack summary, and a pointer to `.claude/rules/` for domain-specific conventions
- Do NOT include: exhaustive rule lists, framework docs, anything that only applies to specific file types (those go in scoped rules)

**Template structure:**
```markdown
# [Project Name]

## Purpose
[1-3 sentences describing what this repo is and what Claude helps with here]

## Commands
- Build: `[cmd]`
- Test: `[cmd]`
- Lint: `[cmd]`
- Dev: `[cmd]`

## Stack
- [Language] with [key framework/version]
- [Package manager]
- [Other key tools]

## Agent Context Protocol
- Rules for specific domains are in `.claude/rules/` — Claude loads them automatically by file path
- Sensitive files excluded from Claude access: [list]
```

### Rules Files (`.claude/rules/`)
- One file per domain (testing, api-design, frontend, etc.)
- Add `paths:` frontmatter to scope rules to file types — this keeps them out of context unless relevant
- Keep each file under 80 lines

### `settings.json`
Always include:
- `$schema` line for editor validation
- `permissions.deny` for sensitive files discovered in Phase 1
- Any `permissions.allow` for commands the user confirmed are safe
- Hooks if requested

### `settings.local.json`
Generate only if the user has personal overrides. Add to `.gitignore` if not already there.

---

## Phase 4: Verification

After writing files:
1. Run `wc -l .claude/CLAUDE.md` — report line count and flag if over 200
2. Confirm each rules file exists and has correct frontmatter
3. Validate `settings.json` is valid JSON
4. Report the full file tree of what was created

**Summary output:**
```
✓ .claude/CLAUDE.md ([N] lines)
✓ .claude/rules/[name].md (paths: [...])
✓ .claude/settings.json
✓ .claude/settings.local.json (gitignored)

Next steps:
- Run /memory to verify CLAUDE.md loaded correctly
- Add `.claude/settings.local.json` to .gitignore if not already present
- Run bridge installer if deploying to other agent environments
```

---

## Fallback Rules

- If the project already has a large `CLAUDE.md` (>200 lines), enter **optimization mode**: analyze existing content, propose what to split into rules files, and confirm before modifying
- If `.claude/` already exists with committed files: show a diff of what would change and require explicit confirmation per file
- If user is unsure about hooks: skip hooks and note how to add them later via `settings.json`
- If no sensitive files mentioned: still add a default deny block for `.env`, `.env.*`, and `secrets/`
