---
concept: adr-manager-plugin
source: plugin-code
source_file: adr-manager/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.117409+00:00
cluster: standard
content_hash: 7e3b6818f9d677d8
---

# ADR Manager Plugin 📐

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# ADR Manager Plugin 📐

Manage Architecture Decision Records natively — auto-number, scaffold, and maintain design logs using standard prompts.

### Dependencies

**For Skill Users:** See the Dependencies section in [`skills/adr-management/SKILL.md`](./skills/adr-management/SKILL.md) for what you need to install the skill.

**For Plugin Developers:** This plugin manages dependencies using the standard lockfile workflow:
```bash
cd <PLUGINPATH>/adr-manager
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



## See Also

- [[acceptance-criteria-adr-manager]]
- [[identity-the-adr-manager]]
- [[adr-001-cross-plugin-script-dependencies]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]
- [[adr-005-plugin-separation-of-concerns-and-loose-coupling]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `adr-manager/README.md`
- **Indexed:** 2026-04-17T06:42:09.117409+00:00
