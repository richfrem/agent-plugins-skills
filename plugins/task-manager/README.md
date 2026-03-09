# Task Manager Plugin 📋

Lightweight kanban task board — directory-backed with zero dependencies. Tasks are manually tracked as human-readable Markdown files natively mapped into statuses via folders.

## Installation
```bash
claude --plugin-dir ./plugins/task-manager
```

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
