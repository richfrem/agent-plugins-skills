# Agent Skill Open Specifications Meta-Plugin

## Purpose
This plugin acts as the central **Meta-Protocol** for the repository. It houses the authoritative research and the execution instructions necessary for agents to build, audit, and understand the extensible agent ecosystem.

## Cross-IDE Reusability
The capabilities built within this project—and formalized by the blueprints in this meta-plugin—are explicitly designed to adhere to the open **Agent Skills Spec** (`agentskills.io`). 

Therefore, the instructions, reference materials, and active skills documented here are inherently reusable and universally deployable across any compliant AI Developer tool, including:
- **Google Deepmind Antigravity / Gemini CLI**
- **Claude Code**
- **GitHub Copilot**
- **Cursor**
- **Roo Code / Cline**
- **And more...**

Our architectural mandate is that skills function as pure, portable filesystem resources that agents dynamically pull into context, completely agnostic of the execution system running the LLM.

## Included Skills
1. `ecosystem-authoritative-sources`: A progressive-disclosure library containing detailed documentation on plugins, sub-agents, workflows, and skills.
2. `ecosystem-standards`: An execution skill detailing how to audit structures, files, and code against those ecosystem standards.

## 📚 Core Inspirations & Specifications

This repository aligns with and draws massive inspiration from a neutral open ecosystem of standards:

1.  **Agent Skills Open Standard (`agentskills.io`)**: For standardizing the `SKILL.md` format, Progressive Disclosure directory structures (`scripts/`, `references/`), and multi-agent compatibility.
2.  **Anthropic Model Context Protocol (MCP)**: For standardizing tool and server integrations.
3.  **Anthropic Claude Code Plugins**: Specifically the `.claude-plugin` repository structure, `hooks/hooks.json` lifecycle methods, and `.mcp.json` dynamic context integrations.

Our specifications enforce a unified "Scaffolder V2" paradigm that perfectly harmonizes these open standards into a single, aggressively compatible meta-structure spanning Antigravity, GitHub Copilot, Gemini, Roo Code, and Claude Code.
