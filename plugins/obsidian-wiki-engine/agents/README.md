# obsidian-wiki-engine — Agents Directory

This plugin's wiki capabilities are implemented as **skills**, not sub-agents.
They run inline in the calling session rather than as isolated sub-agents.

| Capability | Skill location |
|------------|----------------|
| Build wiki nodes from raw sources | `../skills/obsidian-wiki-builder/SKILL.md` |
| Distill wiki content via RLM | `../skills/obsidian-rlm-distiller/SKILL.md` |
| Lint wiki for drift/orphans | `../skills/obsidian-wiki-linter/SKILL.md` |
| Query the wiki | `../skills/obsidian-query-agent/SKILL.md` |

The only true sub-agents in this plugin live alongside this README:
- `super-rag-setup-agent.md` — interactive RAG stack setup
- `wiki-init-agent.md` — interactive vault initialization
