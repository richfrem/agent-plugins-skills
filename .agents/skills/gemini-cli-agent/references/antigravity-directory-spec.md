# Google Agent Development Kit (ADK) & `.agents/` Specification

**Authoritative Sources:**
- **Gemini CLI Documentation:** [`https://geminicli.com/docs/cli/skills/`](https://geminicli.com/docs/cli/skills/)
- **Gemini Context Hierarchy:** [`https://geminicli.com/docs/cli/gemini-md/`](https://geminicli.com/docs/cli/gemini-md/)
- **Gemini CLI Reference:** [`https://geminicli.com/docs/cli/cli-reference/`](https://geminicli.com/docs/cli/cli-reference/)
- **Google ADK Structure:** Verified Core Component Logic for Gemini Code Assist & Antigravity
- **Plugin Isolation Principle:** Deployed plugins are strictly self-contained and assume no upstream knowledge.

## The Standard Directory Structure
The workspace root directory is governed by the universal `.agents/` directory alias (cross-compatible with `.gemini/`). It serves as the "brain" and instructional manual for your execution environment.

```text
.agents/
├── skills/              # Specialized capability directories (Workspace skills)
│   └── code-reviewer/   # A specific "Skill" 
│       ├── SKILL.md     # Instructions for this specific skill
│       ├── scripts/     # Python/Bash tools for the agent to run
│       └── templates/   # Boilerplate for the agent to use
├── prompts/             # Reusable complex prompt templates workflows
└── config.json          # Agent-specific settings (Model ID, safety, Tool overrides)
```

## 1. Master Context: `GEMINI.md` (or `AGENTS.md`)
Unlike standard plugins, background context is persistently loaded from project files like `GEMINI.md` rather than `.agents/rules/`.
- **Global Context:** `~/.gemini/GEMINI.md`
- **Workspace Context:** `{workspace}/GEMINI.md`
- **Modular Imports:** Context should be modularized using the `@file.md` import syntax (e.g. `@[./docs/api-rules.md]`) so the central file remains readable.
- **JIT Context:** Subdirectories can contain their own `GEMINI.md` files (Just-In-Time evaluation) that only inject tokens when the agent's tools explore those specific directories.

## 2. The Capability Layer: `.agents/skills/`
Skills represent **on-demand expertise** and workflows that are evaluated via *Progressive Disclosure*.
- **Discovery:** Gemini scans `.agents/skills/` and merely parses the metadata descriptions.
- **Activation:** The model natively uses the `activate_skill` tool when a user's prompt aligns with a skill description. The tool injects `SKILL.md` and provides access to local `scripts/` and `assets/`.
- **Precedence:** `.agents/skills/` outranks `.gemini/skills/` within the workspace tier to enforce cross-platform IDE compatibility. 
- **Management:** Users can execute `gemini skills list`, `gemini skills install`, and `gemini skills link`.

## 3. Reusable Workflows: `.agents/prompts/`
Contains saved complex prompt templates generated for repetitive executions without forcing the user to retype commands in the IDE or Terminal (e.g., "Generate a weekly progress report from Git logs").

## 4. The Engine Room: `.agents/config.json`
- **Model Selection**: Force parameters using available aliases (`auto`, `pro`, `flash`, `flash-lite`) or explicit names (e.g., `gemini-3.1-pro-preview`, `gemini-2.5-pro`).
- **Tool Logic:** Actively enable or disable base skills like `Google Search` or `code_execution`.
- **Context Overrides:** Override default root paths using `context.fileName`: `["AGENTS.md", "GEMINI.md"]`.
