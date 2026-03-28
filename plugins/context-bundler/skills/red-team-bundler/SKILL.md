---
name: red-team-bundler
description: Prepares a targeted Red Team Review package. It generates a strict security auditor prompt, compiles a manifest of relevant project files, and bundles them into a single Markdown artifact ready to be pasted into an external LLM (like Grok, ChatGPT, or Gemini).
allowed-tools: Bash, Read, Write
---

# Red Team Bundler Skill 🕵️‍♂️

## Overview
This skill automates the preparation of "Red Team" security and architecture reviews. Instead of manually explaining the context to an external LLM, this skill generates a highly specific instruction prompt, gathers the relevant codebase files, and uses the core Context Bundler scripts to compile them into a single, seamless payload.

## 🎯 Primary Directive
**Isolate, Instruct, and Package.** You are creating a standalone artifact designed to be read by an external AI. The most critical part of this bundle is the **Prompt**—it must explicitly tell the receiving AI how to attack, review, or analyze the accompanying code.

## Core Workflow

When asked to prepare a red team review for a specific topic, module, or feature, follow these exact steps:

### 1. Initialize the Workspace
Create a dedicated temporary directory at the root of the project to house the artifacts.
```bash
mkdir -p temp/red-team-review-[topic-name]
```

### 2. Draft the Red Team Prompt
Draft a robust set of instructions targeting the external LLM. Save this as `prompt.md` inside the temp directory.

**The prompt must include:**
- **Role:** "Act as a ruthless, expert Red Team security auditor and senior architect."
- **Objective:** Clearly state what is being reviewed (e.g., "Find vulnerabilities in this auth flow," "Identify logical flaws in this routing state").
- **Rules of Engagement:** Tell the LLM how to respond (e.g., "Do not flatter the code. Be direct. Output findings organized by severity (Critical, High, Medium, Low). Provide exploit scenarios for critical findings.").

### 3. Build the Manifest
Create a `file-manifest.json` inside the temp directory. 

**CRITICAL ORDERING:** The newly created `prompt.md` MUST be the very first item in the `files` array. This ensures the external LLM reads the instructions before reading the source code.

```json
{
  "title": "Red Team Review: [Topic Name]",
  "description": "Security and architecture review bundle.",
  "files": [
    {
      "path": "temp/red-team-review-[topic-name]/prompt.md",
      "note": "Primary Instructions & Rules of Engagement"
    },
    {
      "path": "src/auth/logic.py",
      "note": "Target: Core authentication logic"
    },
    {
      "path": "docs/security-model.md",
      "note": "Context: Intended security architecture"
    }
  ]
}
```
*Note: Use directory paths (e.g., `src/auth/`) to recursively include entire folders if necessary, rather than listing 50 files manually.*

### 4. Execute the Bundle
Invoke the core Markdown bundler script (housed in the `context-bundler` plugin) to compile the manifest into the final payload.

```bash
python3 ./scripts/bundle.py --manifest temp/red-team-review-[topic-name]/file-manifest.json --bundle temp/red-team-review-[topic-name]/final_red_team_bundle.md
```
*(Adjust the script path depending on if you are running this from the plugin root or via an npx installed `.agents/` path).*

### 5. Handoff
Once the `final_red_team_bundle.md` is generated, inform the user that it is ready. Tell them they can now copy the contents of that file and paste it directly into their external chat interface (Claude Web, ChatGPT, Grok, etc.) to initiate the review.