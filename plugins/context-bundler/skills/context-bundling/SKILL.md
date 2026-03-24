---
name: context-bundling
description: Create technical bundles of code, design, and documentation for external review or context sharing. Use when you need to package multiple project files into a single Markdown file while preserving folder hierarchy and providing contextual notes for each file.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty -- standard library only).

---
# Context Bundling Skill

## Overview
This skill centralizes the knowledge and workflows for creating "Context Bundles." These bundles are essential for compiling large amounts of code and design context into a single, portable Markdown file for sharing with other AI agents or for human review.

## Primary Directive
**Curate, Consolidate, and Convey.** You do not just "list files"; you architect context. You ensure that any bundle you create is:
1. **Complete:** Contains all required dependencies, documentation, and source code.
2. **Ordered:** Flows logically (Identity/Prompt -> Manifest -> Design Docs -> Source Code).
3. **Annotated:** Every file must include a brief note explaining its purpose in the bundle.

## Core Workflow: Generating a Bundle

The context bundler operates through a simple JSON manifest pattern.

### 1. Analyze the Intent
Before bundling, determine what the user is trying to accomplish:
- **Code Review**: Include implementation files and overarching logic.
- **Red Team / Security**: Include architecture diagrams and security protocols.
- **Bootstrapping**: Include `README`, `.env.example`, and structural scaffolding.

### 2. Define the Manifest Schema

You must formulate a JSON manifest containing the files or directories to be bundled.

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
    },
    {
      "path": "plugins/my-plugin/",
      "note": "Full plugin source -- recursive directory inclusion"
    }
  ]
}
```

#### IMPORTANT: Directory Paths Are Recursive

**A path ending in `/` is treated as a recursive directory include.** When you encounter a directory path in the manifest, walk the directory recursively and include all text files found. Skip binary files (`.png`, `.jpg`, `.pyc`, `.pdf`, `.zip`, `.exe`, etc.).

This is the preferred approach for bundling entire plugins or modules -- use a single directory entry rather than listing each file individually:

```json
{
  "path": "plugins/agent-agentic-os/",
  "note": "Full plugin source -- all text files included recursively"
}
```

Instead of:
```json
{ "path": "plugins/agent-agentic-os/README.md", "note": "..." },
{ "path": "plugins/agent-agentic-os/SUMMARY.md", "note": "..." },
{ "path": "plugins/agent-agentic-os/skills/agentic-os-guide/SKILL.md", "note": "..." },
...
```

**Agent failure pattern to avoid**: Agents frequently expand directory references into exhaustive file lists in the manifest, then fail mid-bundle because the file list is too long. Use the directory path shorthand instead.

### 3. Generate the Markdown Bundle
**CRITICAL:** DO NOT write your own Python scripts or bash loops to create the bundle. You MUST use the provided tooling. The scripts handle recursive directories, missing files, and markdown formatting automatically.

Use the provided scripts to compile the JSON manifest into a target `output.md` file:

- **Option A (Simple/Recursive Bundling):** Use `plugins/context-bundler/scripts/bundle.py`. This script handles reading the manifest, walking directories recursively, and applying the standard markdown bundle formatting.
  ```bash
  python plugins/context-bundler/scripts/bundle.py --manifest path/to/manifest.json --bundle path/to/output.md
  ```

- **Option B (Advanced Manifest Management):** Use `plugins/context-bundler/scripts/manifest_manager.py` if you need to perform intelligent context bundling and manifest manipulation.

## Best Practices & Anti-Patterns
1. **Self-Contained Functionality:** The output file must contain 100% of the context required for a secondary agent to operate without needing to run terminal commands.
2. **Specialized Prompts:** If bundling for an external review (e.g., a "Red Team" security check), suggest including a specialized prompt file as the very first file in the bundle to guide the receiving LLM.
3. **Use directory paths for plugins:** A single `plugins/my-plugin/` entry beats a 50-item file list every time.

### Common Bundling Mistakes
- **Bloat**: Including `node_modules/` or massive `.json` dumps instead of targeted files.
- **Silent Exclusion**: Filtering out an unreadable file without explicitly declaring it missing (violates transparency).
- **Exploding directories into file lists**: Listing every file in a directory individually in the manifest instead of using the directory shorthand. This creates brittle manifests and causes agents to time out.
