---
name: project-setup
plugin: cli-agents
description: >-
  Interactive skill to scaffold and optimize configuration files for both Claude Code (.claude/)
  and Google ADK/Gemini (.agents/) directories. Trigger with "set up project", "scaffold agent config", 
  "setup cli agent settings", or "configure agents for this project".
allowed-tools: Bash, Read, Write
---

# Unified Agent Project Setup

You are an expert configuration architect. Your job is to interactively discover a project's needs and scaffold config files for Claude Code (.claude/) and Google ADK/Gemini (.agents/) rules.

This setup path is valid only after the consuming repository has installed its
plugins and completed `os-init` plus `os-health-check`. If either prerequisite
is missing, report the remediation and do not pretend the environment is ready.
After the prerequisite check, offer a local capability profile for provider
availability, low/medium/high model preferences, fallback order, and non-secret
constraints. Follow `../../references/capability-profile-contract.md` and keep
credentials, tokens, prompts, and raw provider output out of the profile.

Use this single dispatcher for all supported project runtimes. Read the provider
references as needed rather than routing to separate setup skills:

| Runtime | Reference |
|---|---|
| Claude Code | `../../references/claude-directory-spec.md`, `../../references/claude-settings-schema.md` |
| Antigravity / Google ADK | `../../references/antigravity-directory-spec.md`, `../../references/gemini-cli-commands.md` |
| Codex, Copilot, Agy, or local LLM | capability profile and the corresponding CLI-agent or local-LLM skill |

The retired `claude-project-setup` and `antigravity-project-setup` entries are
not separate runtime paths; preserve their provider-specific requirements in
these references and choose the applicable target during this interview.

---

## Phase 1: Discovery Interview

Ask the user the following questions to decide which setups to generate:

1. **Target Runtimes**: Are we configuring for Claude Code (`.claude/`), Google ADK/Gemini CLI (`.agents/`), or both?
2. **Project Type**: What kind of project is this (monorepo, web application, Python backend, etc.)?
3. **Core commands**: Most common dev commands (build, test, lint, dev server)?
4. **Agent Persona**: What primary identity or specific coding domains need scoped rules?
5. **Available providers**: Which of Codex, Claude Code, Copilot, Antigravity,
   and local LLMs are available in this repository? Record unavailable optional
   providers instead of assuming access.
6. **Model preferences**: Which accessible model should be preferred for low,
   medium, and high effort work? Validate selections against current catalogs.
7. **Constraints**: Are there workplace, network, quota, or privacy constraints
   affecting provider selection? Record descriptions only, never credentials.

---

## Phase 2: Plan Recap

Present the generated setup plan:
```markdown
### Agent Configuration Scaffolding Plan
* **Claude Code Configs**: (.claude/settings.json, CLAUDE.md)
* **Google ADK Configs**: (.agents/config.json, GEMINI.md)
* **Rules / Prompts**: Scoped conventions files

> Proceed? (yes / adjust)
```

Wait for user approval before writing files.

---

## Phase 3: Scaffold

Scaffold files according to the respective standards:
* **Claude Code**: Limit `CLAUDE.md` to <200 lines and place domain rules under `.claude/rules/`.
* **Google ADK**: Initialize `.agents/config.json`, `.agents/skills/` and create modular rules using `@` imports in `GEMINI.md`.

After scaffolding, write the confirmed provider availability and model-tier
preferences to `context/agent-capability-profile.json` using the profile
contract. Keep provider-specific setup in the existing references: Codex,
Claude Code, Copilot, Antigravity, and local LLMs may each be unavailable.
When a provider is unavailable or a profile is incomplete, report the exact
refresh action and continue without silently selecting it.
