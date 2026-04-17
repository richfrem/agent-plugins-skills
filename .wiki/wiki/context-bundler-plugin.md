---
concept: context-bundler-plugin
source: plugin-code
source_file: context-bundler/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.546586+00:00
cluster: agent
content_hash: 3746e789ef876e23
---

# Context Bundler Plugin 📦

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Context Bundler Plugin 📦

Bundle source files and documentation into single-file Markdown or compressed ZIP context packages for portable AI agent distribution.

## Usage Guide

The Context Bundler operates purely through autonomous agent skills.

When you need to bundle technical context for export to another agent or human review, simply ask your agent:
> "Bundle the backend services and their documentation into a single markdown file using the context bundler."
> "Package this entire module into a ZIP file using the context bundler so I can share it with another agent."

The agent will:
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
      "path": "scripts/",
      "note": "You can provide directories (ending in /) to recursively bundle all valid files inside."
    }
  ]
}
```

### Skills (Auto-Invoked)

- **`context-bundler`** — The agent automatically uses this unified skill when tasks involve bundling, packaging, or distributing files. It dynamically determines whether to generate a single `.md` file (enforcing standard ordering and dependency checking) or archive the files into a portable `.zip` container (injecting a `_manifest_notes.md` root index so LLM context annotations are preserved) based on your request.

- **`red-team-bundler`** — Automates the preparation of targeted security and architecture review packages. It generates a strict auditor prompt, gathers the relevant code, and compiles a single Markdown artifact optimized for external LLM evaluation.

---

### Architecture & Portability
To ensure maximum portability when installed as a standalone skill (which creates a hard copy in the `.agents/` directory), the required execution scripts and assets are symmetrically linked or copied directly inside the skill folder itself.

```text
context-bundler/
├── .claude-plugin/
│   └── plugin.json
├── scripts/                     # Original plugin-level scripts
├── assets/                      # Original plugin-level assets
└── skills/
    └── context-bundler/         # 🎯 Installation target
        ├── SKILL.md             # The unified bundling protocol
        ├── evals/
        │   └── evals.json
        ├── scripts/             # Hard copy/symlink of execution engines
        └── assets/              # Hard copy/symlink of schema resources
    └── red-team-bundler/        # 🕵️‍♂️ Red Team specific protocol
        ├── SKILL.md
        ├── scripts/             # Hard copy/symlink of execution engines
        └── assets/              # Hard copy/symlink of schema resources
```

---

## License

MIT

## See Also

- [[context-bundler-skill]]
- [[acceptance-criteria-context-bundler]]
- [[procedural-fallback-tree-context-bundler-markdown]]
- [[context-bundler-skill]]
- [[acceptance-criteria-context-bundler]]
- [[procedural-fallback-tree-context-bundler-markdown]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `context-bundler/README.md`
- **Indexed:** 2026-04-17T06:42:09.546586+00:00
