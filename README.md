# Agent Plugins & Skills Ecosystem

Welcome to the central repository for Open Standard Agent extensions. 

This repository is designed fundamentally differently than standard codebases. It is built **for AI agents, by AI agents**. 

## Purpose
The extensions stored here are designed to be universally loaded into any compliant Agentic IDE or CLI tool (such as Claude Code, GitHub Copilot, Gemini Antigravity, or Roo Code). They adhere to the `agentskills.io` open standard and the `.claude-plugin` distribution architecture.

Instead of keeping documentation trapped in web browsers or PDF files, this repository utilizes **Meta-Plugins**. These plugins are loaded into an agent's context window, actively training the agent on how to build, audit, and distribute *new* capabilities natively.

## The Meta-Plugins Suite

This repository comes pre-packaged with two critical meta-plugins designed to establish an autonomous creation loop:

### 1. `agent-skill-open-specifications` (The Reference Library)
This plugin acts as a passive, progressive-disclosure knowledge base. It contains the official specifications for:
- Agent Skills (`SKILL.md` constraints)
- Plugins (`.claude-plugin` and directory architectures)
- Sub-Agents
- Hooks (`hooks.json`)
- Workflows & Legacy Commands
- MCP / LSP server integrations

*AI Agents: Do not guess how to build extensions. Load the reference skills from this plugin to read the exact character limits and folder structures before writing any code.*

### 2. `agent-scaffolders` (The Active Creator Suite)
This plugin houses highly deterministic, interactive generation tools. It contains conversational skills like `create-plugin` or `create-skill`.
When invoked, these prompt-based skills automatically execute a deterministic Python backend (`scaffold.py`) that generates perfect standard-compliant architectures (including READMEs, Mermaid diagrams, and strict directory trees).

## How to Use This Repository

If you are a Developer:
1. Load this directory into your preferred AI Agent IDE.
2. Ask your agent: `"I need to build a new capability. Can you run the create-plugin skill to scaffold a new workspace for me?"`

If you are an AI Agent:
1. Familiarize yourself with the `ecosystem-standards` skill.
2. When asked to build a new feature, ALWAYS utilize the `agent-scaffolders` to generate the foundational files.
3. Review your generated output against the specifications located in the `agent-skill-open-specifications` reference library.
## Features
- **Progressive Disclosure**: Skills map complex logic into isolated folders loaded on-demand.
- **Cross-Platform Output**: Generates pure Python scripts, never Bash, solving execution bugs.
- **Deterministic**: The framework uses programmatic validation instead of relying entirely on LLM logic guessing. 

## Acknowledgments
We would like to give special recognition to the open ecosystem driving this architecture:

- [Agent Skills Open Standard (agentskills.io)](https://agentskills.io/) and its [Official GitHub](https://github.com/agentskills/agentskills) for defining the strict `SKILL.md` specification format.
- [Anthropic Claude Plugins Official Repository](https://github.com/anthropics/claude-plugins-official) for establishing the `.claude-plugin/plugin.json` and `hooks.json` infrastructure.
- [Microsoft Skills Repository](https://github.com/microsoft/skills) for their best-practice patterns in Progressive Disclosure and skill testing strategies.
