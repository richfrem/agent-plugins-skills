# ADR Manager Plugin 📐

Manage Architecture Decision Records natively — auto-number, scaffold, and maintain design logs using standard prompts.

## Installation
```bash
claude --plugin-dir ./plugins/adr-manager
```



### Dependencies
This plugin uses only standard library capabilities by default. If external dependencies are added later, compile and install them using:
```bash
cd plugins/adr-manager
pip-compile requirements.in
pip install -r requirements.txt
```

## Quick Start
The ADR Manager operates autonomously based on conversational intent.

```text
"Create an ADR documenting our decision to use ChromaDB for vector storage instead of pgvector. It should be accepted."
```

The agent will automatically:
1. Check `docs/architecture/decisions/` for the next available ADR number.
2. Scaffold `NNNN-use-chromadb.md` using the standard 5-part template.
3. Fill in the logical Context, Consequences, and Alternatives based on the prompt.

## Structure
```
adr-manager/
├── .claude-plugin/plugin.json
├── skills/adr-management/SKILL.md
├── templates/adr-template.md  # ADR scaffold reference
└── README.md
```
