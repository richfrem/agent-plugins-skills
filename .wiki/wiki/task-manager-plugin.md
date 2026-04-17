---
concept: task-manager-plugin
source: plugin-code
source_file: task-manager/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.417325+00:00
cluster: plugin-code
content_hash: a9735e54a5aa3304
---

# Task Manager Plugin 📋

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Task Manager Plugin 📋

Lightweight kanban task board — directory-backed with zero dependencies. Tasks are manually tracked as human-readable Markdown files natively mapped into statuses via folders.

## Quick Start
The Task Manager operates autonomously based on conversational intent, using simple file operations to manage state.

```text
"Create a new task to fix the login bug"
"Move task 0004 to in-progress"
"Show me the kanban board"
```

The agent will automatically manage `[NNNN]-[title].md` files inside the defined lanes:
`backlog` → `todo` → `in-progress` → `done`

## Structure
```
task-manager/
├── .claude-plugin/plugin.json
├── skills/task-agent/SKILL.md
├── skills/task-agent/scripts/task_manager.py
├── templates/task-template.md 
└── README.md
```


## See Also

- [[adr-manager-plugin]]
- [[plugin-manager]]
- [[acceptance-criteria-task-manager]]
- [[procedural-fallback-tree-task-manager]]
- [[acceptance-criteria-task-manager]]
- [[procedural-fallback-tree-task-manager]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `task-manager/README.md`
- **Indexed:** 2026-04-17T06:42:10.417325+00:00
