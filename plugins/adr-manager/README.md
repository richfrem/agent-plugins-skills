# ADR Manager Plugin 📐

Manage Architecture Decision Records natively — auto-number, scaffold, and maintain design logs using standard prompts.

## Installation

### Option 1: From a Marketplace (Recommended)
```bash
/plugin marketplace add <marketplace-url>
/plugin install adr-manager
```
For skills-only portability across all agents (Claude, Gemini, Copilot, etc.):
```bash
npx skills add <marketplace-url>/plugins/adr-manager
```

### Option 2: From GitHub Directly
```bash
# Skills only
npx skills add richfrem/agent-plugins-skills --path plugins/adr-manager

# Full plugin (Claude Code native)
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install adr-manager
```

### Option 3: Local Development Checkout
```bash
npx skills add ./plugins/adr-manager
```



### Dependencies

**For Skill Users:** See the Dependencies section in [`skills/adr-management/SKILL.md`](./skills/adr-management/SKILL.md) for what you need to install the skill.

**For Plugin Developers:** This plugin manages dependencies using the standard lockfile workflow:
```bash
cd plugins/adr-manager
pip-compile requirements.in
pip install -r requirements.txt
```

Currently this plugin requires **standard library only** (no external dependencies). See `requirements.txt` for the lockfile.

## Quick Start
The ADR Manager operates autonomously based on conversational intent.

```text
"Create an ADR documenting our decision to use ChromaDB for vector storage instead of pgvector. It should be accepted."
```

The agent will automatically:
1. Execute `adr_manager.py create` which checks the target directory (default: `ADRs/` at the project root) for the next available ADR number.
2. The script scaffolds the new file (e.g., `0001-use-chromadb.md`) using the standard 5-part template.
3. The agent reads the generated file and fills in the logical Context, Consequences, and Alternatives based on the prompt.

*Note: You can override the default location by specifying it in your prompt (e.g., "Save to `docs/decisions/`").*

## Structure
```
adr-manager/
├── .claude-plugin/plugin.json
├── skills/adr-management/SKILL.md
├── skills/adr-management/scripts/adr_manager.py
├── templates/adr-template.md  # ADR scaffold reference
└── README.md
```

## Plugin Components

### Skills
- `adr-management`

