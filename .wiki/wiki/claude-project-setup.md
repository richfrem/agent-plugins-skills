---
concept: claude-project-setup
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/claude-project-setup/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.744310+00:00
cluster: files
content_hash: 5f90ab558b4e1703
---

# Claude Project Setup

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: claude-project-setup
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
- `$schema` l

*(content truncated)*

## See Also

- [[project-setup-reference-guide]]
- [[project-setup-guide]]
- [[project-setup-guide]]
- [[google-adk-antigravity-project-setup]]
- [[google-adk-antigravity-project-setup]]
- [[project-setup-reference-guide]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/claude-project-setup/SKILL.md`
- **Indexed:** 2026-04-17T06:42:09.744310+00:00
