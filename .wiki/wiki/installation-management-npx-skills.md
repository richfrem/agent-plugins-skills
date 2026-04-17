---
concept: installation-management-npx-skills
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/ecosystem-authoritative-sources/references/npx-skills.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.036443+00:00
cluster: plugin-code
content_hash: 7bb18c7af2efb476
---

# Installation & Management (npx skills)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[procedural-fallback-tree-adr-management]]
- [[006-python-native-plugin-bootstrap-installer-replacing-npx]]
- [[lifecycle-aware-knowledge-management]]
- [[synthesis-of-learnings-anthropic-skills-repository]]
- [[006-python-native-plugin-bootstrap-installer-replacing-npx]]
- [[006-python-native-plugin-bootstrap-installer-replacing-npx]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/ecosystem-authoritative-sources/references/npx-skills.md`
- **Indexed:** 2026-04-17T06:42:10.036443+00:00
