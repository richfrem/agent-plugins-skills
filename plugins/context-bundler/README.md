# Context Bundler Plugin 📦

Bundle source files and documentation into single-file Markdown context packages
for portable AI agent distribution.

## Installation

### Option 1: Local Development
```bash
claude --plugin-dir ./plugins/context-bundler
```

### Option 2: From Marketplace (when published)
```
/plugin install context-bundler
```

### Option 3: From GitHub
```json
// In your marketplace.json
{
  "name": "context-bundler",
  "source": { "source": "github", "repo": "username/my-agent-plugins" }
}
```

### Prerequisites
- **Claude Code** ≥ 1.0.33
- **Python** ≥ 3.8 (for scripts)

### Verify Installation
After loading the plugin, ask Claude to bundle some specific files to verify the `context-bundling` skill is correctly invoked.

---

## Usage Guide

The Context Bundler operates purely through autonomous skills.

When you need to bundle technical context for export to another agent, simply tell Claude:
>"Bundle the backend services and their documentation into a single markdown file using the context-bundler specification."

Claude will:
1. Generate an internal `file-manifest.json` describing the targets.
2. Compile exactly those files into a highly compressed, annotated `.md` artifact perfectly structured for LLM ingestion.

### The JSON Manifest Schema

```json
{
  "title": "Module Name Context",
  "description": "The description of the bundle purpose.",
  "files": [
    {
      "path": "docs/architecture.md",
      "note": "Primary reasoning structure"
    },
    {
      "path": "src/module.py",
      "note": "Implementation logic"
    }
  ]
}
```

### Skills (Auto-Invoked)

- **`context-bundling`** — Claude automatically uses this skill when tasks involve
  bundling, packaging, or distributing files. It enforces standard ordering
  (identity → manifest → docs → code) and dependency checking.

---

### Plugin Directory Structure
```
context-bundler/
├── .claude-plugin/
│   └── plugin.json              # Plugin identity & metadata
├── skills/
│   └── context-bundling/
│       └── SKILL.md             # The bundling protocol definitions
├── file-manifest.json           # Example schematic
└── README.md
```

---

## License

MIT
