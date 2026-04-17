---
concept: skills-research
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/ecosystem-authoritative-sources/references/skills-research.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.058423+00:00
cluster: skill
content_hash: 943e82d7cb014313
---

# Skills Research

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Skills Research

This document captures our accumulated knowledge and definitive specifications for **Skills**.

**Source:** [Extend Claude with skills](https://code.claude.com/docs/en/skills)

## Definition
Skills are modular capabilities that package procedural knowledge, context, and workflows into reusable, filesystem-based resources. While built primarily for Claude and Claude Code, they adhere to the open [Agent Skills](https://agentskills.io/) standard originally developed by Anthropic. Because it is an open standard, skills are highly portable and supported by a wide ecosystem of AI developer tools (e.g., Cursor, Gemini CLI, Goose, VS Code, Letta, Roo Code, etc.). They replace and expand upon older legacy feature sets like `/commands`.

## Creation & Structure
- Skills are individual directories named `<skill-name>`, housing at least one `././././././././././././././././././././././././SKILL.md` file.
- The `././././././././././././././././././././././././SKILL.md` file contains YAML frontmatter configuring the skill and Markdown content acting as the prompt instructions.
- Supporting files must be strictly organized into the official standard directories (`scripts/`, `references/`, or `assets/`) and referenced inside `././././././././././././././././././././././././SKILL.md`. Claude will read them only if needed.

## Optional Directories
Agent skills support three standard optional directories to keep the root clean:
- **`scripts/`**: Contains executable code (Python, Bash, JS). Must be self-contained, handle edge cases gracefully, and include helpful error messages instead of failing silently.
- **`references/`**: Contains additional documentation loaded on-demand (e.g., `REFERENCE.md`, `FORMS.md`, `domain.md`). Keep these small and focused to save context window space.
- **`assets/`**: Contains static resources like templates, images (diagrams), and data files (lookup tables, schemas).

## Resolution Precedence
Skills are resolved automatically. Any nested `.claude/skills/` directory relative to the current working file is also discovered (useful in monorepos).
1. **Enterprise** (`managed settings`)
2. **Personal** (`~/.claude/skills/<skill-name>/././././././././././././././././././././././././SKILL.md`)
3. **Project** (`.claude/skills/<skill-name>/././././././././././././././././././././././././SKILL.md`)
4. **Plugin** (`<plugin_root>/skills/<skill-name>/././././././././././././././././././././././././SKILL.md` - namespaces prevent conflicts here)

## Configuration (YAML Frontmatter)
The frontmatter configures invocation rules, argument hints, tool allowances, and execution environments.

### Open Standard Properties (`agentskills.io`)
- `name` **(Required)**: Display name. 1-64 characters. Must contain only lowercase alphanumeric characters and hyphens (`a-z` and `-`). Cannot start/end with a hyphen, nor contain consecutive hyphens (`--`). **Must perfectly match the parent directory name.**
- `description` **(Required)**: Helps the agent decide autonomously when it should trigger the skill. 1-1024 characters.
- `license` *(Optional)*: License name or reference to a bundled license file (e.g., `Apache-2.0`). Recommendation: Keep it short.
- `compatibility` *(Optional)*: Indicates specific environment requirements like system packages or network access. Max 500 characters.
- `metadata` *(Optional)*: A map from string keys to string values for tool-specific meta. Make key names unique to avoid conflicts (e.g., `author: org`, `version: "1.0"`).
- `allowed-tools` *(Optional/Experimental)*: Space-delimited list of pre-approved tools the skill may use (e.g., `Bash(git:*) Read`). Support varies by implementation.

### Claude Code Specific Properties
- `argument-hint`: Visual hint for the autocomplete UI (e.g., `[issue-number]`).
- `disable-model-invocation`: Boolean. If `true`, Claude *cannot* automatically decide to run this skill; it must be manually invoked by the user `/name`.
- `user-invocable`: Boolean. If `false`

*(content truncated)*

## See Also

- [[research-summary-agent-operating-systems-agent-os]]
- [[research-summary-agent-operating-systems-aos]]
- [[sources-template---research-topic-name]]
- [[synthesis-of-learnings-anthropic-skills-repository]]
- [[from-the-skills-scripts-directory]]
- [[azure-ai-foundry-agents-open-agent-skills]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/ecosystem-authoritative-sources/references/skills-research.md`
- **Indexed:** 2026-04-17T06:42:10.058423+00:00
