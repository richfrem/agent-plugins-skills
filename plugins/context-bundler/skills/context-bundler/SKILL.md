---
name: context-bundler
description: Create technical bundles of code, design, and documentation for external review or context sharing. Use when you need to package multiple project files into a single Markdown file or a portable `.zip` archive while preserving folder hierarchy and providing contextual notes for each file.
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
# Context Bundler Skill 📦

## Overview
This skill centralizes the knowledge and workflows for creating "Context Bundles." These bundles are essential for compiling large amounts of code and design context into either a single, portable Markdown file for sharing with other AI agents, or a compressed `.zip` file for native format sharing and human review.

## Primary Directive
**Curate, Consolidate, and Package.** You do not just "list files" or run the zip command; you architect context. You ensure that any bundle you create is:
1. **Targeted:** You select the right output format (`.md` vs `.zip`) based on the user's request.
2. **Complete:** Contains all required dependencies, documentation, and source code.
3. **Annotated:** Every file must include a brief `"note"` explaining its purpose in the bundle.

## Core Workflow: Generating a Bundle

The context bundler operates through a simple JSON manifest pattern for both Markdown and ZIP formats.

### 1. Analyze the Intent & Format
Before bundling, determine what the user is trying to accomplish:
- **Markdown (.md)**: Best for Code Review, Red Team / Security analysis, and direct LLM context injection.
- **ZIP Archive (.zip)**: Best for Handoffs, preserving native file formats, and bootstrapping structural scaffolding.

### 2. Define the Manifest Schema
You must formulate a JSON manifest containing the files or directories to be bundled.

```json
{
  "title": "Bundle Title",
  "description": "Short explanation of the bundle's goal.",
  "files": [
    {
      "path": "docs/architecture.md",
      "note": "Primary design document. Look closely at the Auth flow chart."
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
**A path ending in `/` is treated as a recursive directory include.** When you encounter a directory path in the manifest, the scripts will walk the directory recursively and include all valid files found. 

This is the preferred approach for bundling entire plugins or modules -- use a single directory entry rather than listing each file individually. 

**Agent failure pattern to avoid**: Agents frequently expand directory references into exhaustive file lists in the manifest, then fail mid-bundle because the file list is too long. Use the directory path shorthand instead.

### 3. Generate the Bundle
**CRITICAL:** DO NOT write your own Python scripts, bash loops, or use native `zip` shell commands to create the bundle. You MUST use the provided tooling. The scripts handle recursive directories, missing files, formatting, and manifest note injection automatically.

Once the `file-manifest.json` is safely written to disk, invoke the appropriate script:

- **Option A: Markdown Bundling**
  Compiles the manifest into a single `output.md` file.
  ```bash
  python3 ./scripts/bundle.py --manifest path/to/file-manifest.json --bundle path/to/output.md
  ```

- **Option B: ZIP Bundling**
  Archives the files and automatically injects a `_manifest_notes.md` root index so LLM context annotations are preserved inside the ZIP.
  ```bash
  python3 ./scripts/bundle_zip.py --manifest path/to/file-manifest.json --bundle path/to/output.zip
  ```

*(Note: If advanced manifest manipulation is needed before bundling, you can use `./scripts/manifest_manager.py`)*

## Best Practices, Fallbacks & Error Handling
1. **Self-Contained Functionality:** The output file must contain 100% of the context required for a secondary agent to operate without needing to run terminal commands.
2. **Missing Files:** If a file requested in the manifest does not exist or raises a permissions error, do **not** abort the entire bundle generation. The Python scripts will automatically accommodate this by injecting a failure warning (e.g., `🔴 **NOT INCLUDED**`) into the Markdown or ZIP index. Proceed with the remaining valid files.
3. **Binary Bloat (ZIP only):** If passing a directory causes the script to zip massive unintended binaries (e.g., raw video assets), warn the user about the size when presenting the ZIP, and ask if they want to regenerate excluding specific extensions.
4. **Bundle Exceeds Target Size (Markdown only):** If compiling results in a massive Markdown file that takes too long to generate, STOP. Report to the user that the size is unmanageable as a single file and suggest switching to ZIP bundling or explicitly removing broad directories.
5. **Vague Requests:** If the user says "bundle the logic" without specifying files, perform a quick codebase search to identify 3-5 high-value files. Present the proposed manifest to the user for confirmation BEFORE generating the bundle.