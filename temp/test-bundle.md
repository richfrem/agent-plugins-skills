# Context Bundler Source Code
**Generated:** 2026-02-21 14:37:32

The source code and documentation for the context-bundler plugin.

## Index
1. `plugins/context-bundler/README.md` - Primary documentation
2. `plugins/context-bundler/file-manifest.json` - The generic JSON schema example
3. `plugins/context-bundler/skills/context-bundling/SKILL.md` - The core skill definition
4. `plugins/context-bundler/scripts/bundle.py` - The bundling engine

---

## File: `plugins/context-bundler/README.md`
> Note: Primary documentation

````markdown
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
````

---

## File: `plugins/context-bundler/file-manifest.json`
> Note: The generic JSON schema example

```json
{
  "title": "Context Bundler Source Code",
  "description": "The source code and documentation for the context-bundler plugin.",
  "files": [
    {
      "path": "plugins/context-bundler/README.md",
      "note": "Primary documentation"
    },
    {
      "path": "plugins/context-bundler/file-manifest.json",
      "note": "The generic JSON schema example"
    },
    {
      "path": "plugins/context-bundler/skills/context-bundling/SKILL.md",
      "note": "The core skill definition"
    },
    {
      "path": "plugins/context-bundler/scripts/bundle.py",
      "note": "The bundling engine"
    }
  ]
}
```

---

## File: `plugins/context-bundler/skills/context-bundling/SKILL.md`
> Note: The core skill definition

````markdown
---
name: context-bundling
description: Create technical bundles of code, design, and documentation for external review or context sharing. Use when you need to package multiple project files into a single Markdown file while preserving folder hierarchy and providing contextual notes for each file.
---

# Context Bundling Skill 📦

## Overview
This skill centralizes the knowledge and workflows for creating "Context Bundles." These bundles are essential for compiling large amounts of code and design context into a single, portable Markdown file for sharing with other AI agents or for human review.

## 🎯 Primary Directive
**Curate, Consolidate, and Convey.** You do not just "list files"; you architect context. You ensure that any bundle you create is:
1. **Complete:** Contains all required dependencies, documentation, and source code.
2. **Ordered:** Flows logically (Identity/Prompt → Manifest → Design Docs → Source Code).
3. **Annotated:** Every file must include a brief note explaining its purpose in the bundle.

## Core Workflow: Generating a Bundle

The context bundler operates through a simple JSON manifest pattern. 

### 1. Analyze the Intent
Before bundling, determine what the user is trying to accomplish:
- **Code Review**: Include implementation files and overarching logic.
- **Red Team / Security**: Include architecture diagrams and security protocols.
- **Bootstrapping**: Include `README`, `.env.example`, and structural scaffolding.

### 2. Define the Manifest Schema
You must formulate a JSON manifest containing the exact files to be bundled.
```json
{
  "title": "Bundle Title",
  "description": "Short explanation of the bundle's goal.",
  "files": [
    {
      "path": "docs/architecture.md",
      "note": "Primary design document"
    },
    {
      "path": "src/main.py",
      "note": "Core implementation logic"
    }
  ]
}
```

### 3. Generate the Markdown Bundle
Use your native tools (e.g., `cat`, `view_file`, or custom scripts depending on the host agent environment) to read the contents of each file listed in the manifest and compile them into a target `output.md` file.

The final bundle format must follow this structure:

```markdown
# [Bundle Title]
**Description:** [Description]

## Index
1. `docs/architecture.md` - Primary design document
2. `src/main.py` - Core implementation logic

---

## File: `docs/architecture.md`
> Note: Primary design document

\`\`\`markdown
... file contents ...
\`\`\`

---

## File: `src/main.py`
> Note: Core implementation logic

\`\`\`python
... file contents ...
\`\`\`
```

## Best Practices
1. **Self-Contained Functionality:** The output file must contain 100% of the context required for a secondary agent to operate without needing to run terminal commands.
2. **Specialized Prompts:** If bundling for an external review (e.g., a "Red Team" security check), suggest including a specialized prompt file as the very first file in the bundle to guide the receiving LLM.
````

---

## File: `plugins/context-bundler/scripts/bundle.py`
> Note: The bundling engine

```python
#!/usr/bin/env python3
"""
Context Bundler Engine

A simple utility that reads a JSON manifest file containing a list of
file paths and notes, and concatenates their contents into a single
Markdown artifact suitable for LLM context ingestion.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

def generate_bundle(manifest_path: Path, output_path: Path) -> None:
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"Error loading manifest '{manifest_path}': {e}")
        sys.exit(1)

    title = manifest.get('title', 'Context Bundle')
    description = manifest.get('description', '')
    files = manifest.get('files', [])

    if not files:
        print(f"Warning: Manifest '{manifest_path}' contains no files.")

    # Always write from the project root (where the script is called from ideally)
    project_root = Path.cwd()

    with open(output_path, 'w', encoding='utf-8') as out:
        # 1. Header
        out.write(f"# {title}\n")
        out.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if description:
            out.write(f"{description}\n\n")

        # 2. Table of Contents / Index
        out.write("## Index\n")
        missing_files = []

        for idx, entry in enumerate(files, 1):
            path_str = entry.get('path', '')
            note = entry.get('note', '')
            
            # Use relative paths for display if under cwd
            display_path = path_str
            
            out.write(f"{idx}. `{display_path}`")
            if note:
                out.write(f" - {note}")
            out.write("\n")
            
            # Check existence
            actual_path = project_root / path_str
            if not actual_path.exists():
                missing_files.append(path_str)

        out.write("\n---\n\n")
        
        if missing_files:
            print(f"Warning: {len(missing_files)} files listed in manifest were not found.")

        # 3. File Contents
        for entry in files:
            path_str = entry.get('path', '')
            note = entry.get('note', '')
            actual_path = project_root / path_str

            out.write(f"## File: `{path_str}`\n")
            if note:
                out.write(f"> Note: {note}\n\n")
            
            if not actual_path.exists():
                out.write("> [!WARNING] File not found or inaccessible at generation time.\n\n")
                out.write("---\n\n")
                continue

            try:
                # Basic language inference for markdown block
                ext = actual_path.suffix.lower().strip('.')
                lang = 'markdown' if ext in ['md', 'mdx'] else \
                       'python' if ext == 'py' else \
                       'json' if ext == 'json' else \
                       'typescript' if ext in ['ts', 'tsx'] else \
                       'javascript' if ext in ['js', 'jsx'] else ext

                with open(actual_path, 'r', encoding='utf-8') as source_file:
                    content = source_file.read()
                    
                    if lang == 'markdown':
                         # Don't enclose markdown within markdown if possible, just write it
                         # Or use 4 backticks to enclose 3 backticks
                         out.write("````markdown\n")
                         out.write(content)
                         if not content.endswith('\n'):
                             out.write('\n')
                         out.write("````\n\n")
                    else:
                        out.write(f"```{lang}\n")
                        out.write(content)
                        if not content.endswith('\n'):
                            out.write('\n')
                        out.write("```\n\n")
            except Exception as e:
                 out.write(f"> [!ERROR] Could not read file contents: {e}\n\n")
            
            out.write("---\n\n")

    print(f"✅ Context successfully bundled into -> {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate a markdown context bundle from a JSON manifest.")
    parser.add_argument("--manifest", required=True, type=Path, help="Path to the JSON file manifest.")
    parser.add_argument("--bundle", required=True, type=Path, help="Output path for the bundled Markdown file.")
    
    args = parser.parse_args()
    
    generate_bundle(args.manifest, args.bundle)

if __name__ == "__main__":
    main()
```

---

