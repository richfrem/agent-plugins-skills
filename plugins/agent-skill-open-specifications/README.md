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
