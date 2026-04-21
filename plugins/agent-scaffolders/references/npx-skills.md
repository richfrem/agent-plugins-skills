# Installation & Management (npx skills)

This document captures the high-level specifications for the `npx skills` CLI. For the authoritative, project-specific installation commands and logic, strictly refer to the root-level installation hub:

> ### 👉 [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md)

## Overview
The `npx skills` CLI is a universal package manager for AI agent skills. It is designed to auto-detect installed agents (Claude Code, GitHub Copilot, Gemini CLI, etc.) and seamlessly wire up requested skills into their respective configuration environments.

## Specification Principles
1. **Universal Discovery**: The CLI must detect agent-specific config paths (e.g., `.claude/skills/`, `.agents/skills/`).
2. **Atomic Deployment**: Skills should be deployed as self-contained entities with their own `SKILL.md` and `references/`.
3. **Environment Isolation**: The tool handles dereferencing symlinks and packaging resources to ensure skills remain functional in isolated agent sessions.
4. **Environment Hygene**: Developers should manually clear destination folders (e.g., `rm -rf .agents/`) before forced reinstalls to prevent symlink caching issues.

*For implementation details and the current command set, see the central [INSTALL.md](https://github.com/richfrem/agent-plugins-skills/blob/main/INSTALL.md).*
