---
name: context-bundler
description: Interactively creates technical bundles of code, design, and documentation for external review or context sharing. It conducts a brief discovery phase to confirm the targets and format, presents a plan, and then packages multiple project files into a single Markdown file or a portable `.zip` archive.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

---
# Context Bundler Skill 📦

## Overview
This skill centralizes the knowledge and workflows for creating "Context Bundles." These bundles compile large amounts of code and design context into either a single, portable Markdown file for sharing with other AI agents, or a compressed `.zip` file for native format sharing and human review.

Because context limits are strict and re-bundling is inefficient, this is a **Level 2.0 Interactive Skill**. You must follow the phased workflow below to confirm the target files and output format before generating the payload.

## 🎯 Primary Directive
**Discover, Confirm, and Package.** You do not just "list files" or immediately run the bundling scripts. You ensure the bundle is targeted, complete, and annotated, getting user sign-off before execution.

---

## Core Workflow

When asked to bundle files, you MUST follow these phases in order. **Do not skip to execution.**

### Phase 1: Discovery Interview (Targeted Diagnostics)
Evaluate the user's initial request. If it is vague (e.g., "Bundle the auth logic" or "Bundle these files"), ask targeted questions to shape the payload:
1. **Target Confirmation:** What specific directories or files should be included? (Perform a quick `ls` or codebase search to suggest 3-5 high-value files if they don't know).
2. **Format Negotiation:** Do you need this as a single Markdown file (`.md`) to paste into an LLM, or a portable Archive (`.zip`)?

*Wait for the user's response before proceeding.*

### Phase 2: Recap & Confirm (Pre-Execution Gate)
Draft the JSON manifest schema conceptually, but **DO NOT execute the Python scripts or write to disk yet.** Present the proposed plan to the user for approval:

```text
Context Bundle Plan:
- Title: [Proposed Title]
- Format: [.md or .zip]
- Proposed Files/Directories:
  1. src/main.py (Core logic)
  2. docs/architecture.md (Design reference)
  
Does this look right? (yes / adjust / exclude certain extensions)
```

*Wait for the user to confirm.*

### Phase 3: Build the Manifest
Once confirmed, formulate the actual `file-manifest.json` on disk.
**IMPORTANT:** Use directory paths (ending in `/`) to recursively include entire folders rather than listing 50 files individually. 

```json
{
  "title": "Bundle Title",
  "description": "Short explanation of the bundle's goal.",
  "files": [
    {
      "path": "docs/architecture.md",
      "note": "Primary design document."
    },
    {
      "path": "src/module/",
      "note": "Implementation logic (recursive)"
    }
  ]
}
```

### Phase 4: Execute & Handoff
Invoke the appropriate script based on the format negotiated in Phase 1. 
*(Adjust the script path below depending on if you are running this from the plugin root or via an npx installed `.agents/` path).*

- **For Markdown (.md):**
  ```bash
  python ./scripts/bundle.py --manifest path/to/file-manifest.json --bundle path/to/output.md
  ```

- **For ZIP Archive (.zip):**
  ```bash
  python ./scripts/bundle_zip.py --manifest path/to/file-manifest.json --bundle path/to/output.zip
  ```

Inform the user the payload is ready.