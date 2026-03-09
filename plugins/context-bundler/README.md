# Context Bundler Plugin 📦

Bundle source files and documentation into single-file Markdown or compressed ZIP context packages
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
> "Package this entire module into a ZIP file using the context bundler so I can share it with another agent."

Claude will:
1. Generate an internal `file-manifest.json` describing the targets.
2. Compile exactly those files into a highly compressed, annotated `.md` or `.zip` artifact perfectly structured for LLM ingestion.

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
    },
    {
      "path": "../../scripts",
      "note": "You can provide directories to recursively bundle all text files inside."
    }
  ]
}
```

### Skills (Auto-Invoked)

- **`context-bundling`** — Claude automatically uses this skill when tasks involve
  bundling, packaging, or distributing files into a single `.md` file. It enforces standard ordering
  (identity → manifest → docs → code) and dependency checking.

- **`zip-bundling`** — Explicitly archives the targeted files into their native formats wrapped in a portable `.zip` container. It automatically injects a `_manifest_notes.md` file root index so LLM context annotations are preserved.

---

### Plugin Directory Structure
```
context-bundler/
├── .claude-plugin/
│   └── plugin.json              # Plugin identity & metadata
├── skills/
│   ├── context-bundling/
│   │   └── SKILL.md             # The markdown bundling protocol
│   └── zip-bundling/
│       └── SKILL.md             # The ZIP archiving protocol
├── scripts/
│   ├── bundle.py                # Markdown concatenator
│   └── bundle_zip.py            # ZIP archiver
├── file-manifest.json           # Example schematic
└── README.md
```

---

## License

MIT
