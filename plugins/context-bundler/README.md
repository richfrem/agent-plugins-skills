# Context Bundler Plugin 📦

Bundle source files and documentation into single-file Markdown or compressed ZIP context packages for portable AI agent distribution.

## Installation

### Option 1: Claude Code Plugin (Recommended)
```bash
/plugin marketplace add <marketplace-url>
/plugin install context-bundler
```

### Option 2: Standalone Skill via NPX (For Agentic OS / Local Agents)
When using `npx skills add`, the system will download a self-contained hard copy of the skill folder directly into your local project's `.agents/skills/context-bundler/` directory.

```bash
# From GitHub
npx skills add richfrem/agent-plugins-skills --path plugins/context-bundler/skills/context-bundler

# From Local Development Checkout
npx skills add ./plugins/context-bundler/skills/context-bundler
```

### Prerequisites
- **Claude Code** ≥ 1.0.33 (if using as a full plugin)
- **Python** ≥ 3.8 (for local script execution)

---

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
To ensure maximum portability when installed as a standalone skill via `npx` (which creates a hard copy in the `.agents/` directory), the required execution scripts and assets are symmetrically linked or copied directly inside the skill folder itself.

```text
context-bundler/
├── .claude-plugin/
│   └── plugin.json
├── scripts/                     # Original plugin-level scripts
├── assets/                      # Original plugin-level assets
└── skills/
    └── context-bundler/         # 🎯 Target for `npx skills add`
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