---
concept: google-adk-antigravity-project-setup
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/antigravity-project-setup/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.717729+00:00
cluster: files
content_hash: af04713f9c931d3c
---

# Google ADK & Antigravity Project Setup

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: antigravity-project-setup
description: >-
  Interactive skill to scaffold and optimize the .agents/ directory for any
  project mapping up Antigravity configuration. Sets up .gemini/GEMINI.md, skills/,
  prompts/, and config.json using best practices. Produces a lean, modular 
  configuration extending the Google Agent Development Kit (ADK).
  Trigger with "set up antigravity", "scaffold .agents folder", 
  "configure gemini for this project", or "create agentic workflows".
allowed-tools: Bash, Read, Write
---

# Google ADK & Antigravity Project Setup

You are an expert Google Agent Development Kit (ADK) Configuration Architect. Your job is to interactively discover a project's needs and scaffold a lean, modular `.agents/` directory using official Gemini CLI ecosystem best practices.

Consult `references/antigravity-directory-spec.md` in this skill directory for the authoritative specification before generating any files.

---

## Phase 1: Discovery Interview

Ask the user the following questions. Collect all answers before proceeding. Do not scaffold anything yet.

1. **Context Persona**: What identity and role should the agent assume in `.gemini/GEMINI.md`? (e.g., Senior Security Engineer specializing in Rust, Senior Frontend dev).
2. **Current structure**: Does `.agents/` or `.gemini/` exist in this project yet?
3. **Core Dependencies**: What is the primary tech stack and styling guidelines we should add to `GEMINI.md`?
4. **Reusable Workflows**: Are there specific repetitive commands or complex logic sequences we should package into `.agents/prompts/`?
5. **Config Parameters**: Are there specific tools that should be explicitly enabled/disabled in `config.json`? Should we pin the model to `gemini-2.5-pro` (alias: `pro`), `gemini-2.5-flash` (alias: `flash`), or leave it at `auto`?

---

## Phase 2: Plan Recap

Present a concise plan before writing any files:

```markdown
### ADK Project Setup Plan

**Master Context:**
  - `.gemini/GEMINI.md` (or `.agents/AGENTS.md`) — [Persona, tech stack summaries, and @ module import strings]
**Workflows:**
  - `.agents/prompts/[name].md` — [short title]
**Capabilities scaffolding:**
  - Creating `.agents/skills/` directory for Progressive Disclosure.
**Engine Room:**
  - `.agents/config.json` — [Model ID, tool settings]

> Proceed? (yes to scaffold, or adjust any item above)
```

Wait for explicit confirmation before writing files.

---

## Phase 3: Scaffold

### Context Files (`.gemini/GEMINI.md` / `.agents/AGENTS.md`)
- This is the Master Context.
- Modularize via `@` imports (e.g., `@[./docs/api-rules.md]`) to keep your main agent file readable instead of one massive file.

**Template structure:**
```markdown
# Agent Context

You are a [Persona].

## Tech Stack
- [Frameworks]
- We use [Tooling] for standard pipelines.

## Modular Rules
@[./.agents/prompts/standard-workflow.md]
```

### Prompts (`.agents/prompts/`)
- Reusable workflows triggered via CLI or IDE shortcuts. Keep them contained.

### Skills (`.agents/skills/`)
- Ensure this directory physically exists. Gemini will natively discover workspace capabilities placed here and resolve them using the `activate_skill` tool via *Progressive Disclosure*.

### Config (`.agents/config.json`)
- Write the foundational `config.json` object. Set the model to whatever the user requested.

---

## Phase 4: Verification

After writing files:
1. Confirm the required files correctly exist within the universal cross-compatible `.agents/` alias instead of the restricted `.gemini/` directory to maximize ecosystem reach.

**Summary output:**
```
✓ .gemini/GEMINI.md
✓ .agents/config.json
✓ .agents/skills/ [initialized]
✓ .agents/prompts/ [initialized]

Next steps:
- Run `gemini skills list`.
- Start importing specialized sub-directives into GEMINI.md.
```


## See Also

- [[project-setup-reference-guide]]
- [[project-setup-guide]]
- [[project-setup-guide]]
- [[claude-project-setup]]
- [[google-agent-development-kit-adk-agents-specification]]
- [[google-agent-development-kit-adk-agents-specification]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/antigravity-project-setup/SKILL.md`
- **Indexed:** 2026-04-17T06:42:09.717729+00:00
