---
name: red-team-bundler
description: Interactively prepares a targeted Red Team Review package. It conducts a brief discovery interview to determine the threat model, generates a strict security auditor prompt, compiles a manifest of relevant project files, and bundles them into a single Markdown artifact or ZIP archive ready for an external LLM (like Grok, ChatGPT, or Gemini) or a human reviewer.
allowed-tools: Bash, Read, Write
---

# Red Team Bundler Skill 🕵️‍♂️

## Overview
This skill automates the preparation of "Red Team" security and architecture reviews. Instead of manually explaining the context to an external LLM, this skill generates a highly specific instruction prompt, gathers the relevant codebase files, and uses the core Context Bundler scripts to compile them into a single, seamless payload.

Because context windows are valuable and red team reviews require precision, this is a **Level 2.0 Interactive Skill**. You must not blindly guess the user's intent or immediately execute scripts. You must follow the phased workflow below to confirm the target, threat model, and format before generating the payload.

## 🎯 Primary Directive
**Discover, Confirm, Isolate, Instruct, and Package.** You are creating a standalone artifact designed to be read by an external AI or human. The most critical part of this bundle is the **Prompt**—it must explicitly tell the receiving AI how to attack, review, or analyze the accompanying code based on the user's specific threat model.

---

## Core Workflow

When asked to prepare a red team review, you MUST follow these phases in order. **Do not skip to execution.**

### Phase 1: Discovery Interview (Targeted Diagnostics)
Before creating any directories or writing any files, evaluate the user's initial request. If it is vague, you must ask 1-2 targeted questions to shape the payload:
1. **Threat Model / Focus:** What specific vulnerabilities are we hunting for? (e.g., OWASP top 10, Authentication bypass, Business logic flaws, Data exfiltration).
2. **Format Negotiation:** Where is this bundle going? (e.g., "Are you pasting this into a web UI like ChatGPT/Grok (needs `.md`), or do you need a `.zip` to send to a human reviewer/offline agent?")

*Wait for the user's response before proceeding.*

### Phase 2: Recap & Confirm (Pre-Execution Gate)
Draft the execution plan based on the discovery phase, but **DO NOT execute the Python scripts or write to disk yet.** Present the proposed plan to the user for approval:

```text
Red Team Bundle Plan:
- Target Topic: [Topic Name]
- Format: [.md or .zip]
- Proposed Persona/Prompt: "Act as a ruthless security auditor focusing on [Threat Model]..."
- Proposed Files to Bundle:
  1. src/auth/...
  2. docs/security...
  
Does this look right? (yes / adjust)
```

*Wait for the user to confirm.*

### Phase 3: Initialize & Draft
Once the user confirms the plan, create the workspace and draft the prompt:

1. **Create the Temp Directory:**
   ```bash
   mkdir -p temp/red-team-review-[topic-name]
   ```
2. **Write the Prompt:** Write the agreed-upon text into `temp/red-team-review-[topic-name]/prompt.md`. The prompt must explicitly establish the Red Team rules of engagement, the specific threat model, and the desired severity scoring (Critical, High, Medium, Low).

### Phase 4: Build the Manifest
Create `file-manifest.json` inside the temp directory. 

**CRITICAL ORDERING:** The newly created `prompt.md` MUST be the very first item in the `files` array. This ensures the receiving LLM reads the instructions before reading the source code.

```json
{
  "title": "Red Team Review: [Topic Name]",
  "description": "Security and architecture review bundle focusing on [Threat Model].",
  "files": [
    {
      "path": "temp/red-team-review-[topic-name]/prompt.md",
      "note": "Primary Instructions & Rules of Engagement"
    },
    {
      "path": "src/target/logic.py",
      "note": "Target: Core implementation logic"
    },
    {
      "path": "docs/security-model.md",
      "note": "Context: Intended security architecture"
    }
  ]
}
```
*(Note: Use directory paths like `src/auth/` to recursively include entire folders if necessary, rather than listing 50 files manually).*

### Phase 5: Execute & Handoff
Invoke the appropriate core Context Bundler script based on the format negotiated in Phase 1. 

*(Adjust the script path below depending on if you are running this from the plugin root or via an npx installed `.agents/` path).*

- **For Markdown (.md):**
  ```bash
  python3 ./scripts/bundle.py --manifest temp/red-team-review-[topic-name]/file-manifest.json --bundle temp/red-team-review-[topic-name]/payload.md
  ```

- **For ZIP Archive (.zip):**
  ```bash
  python3 ./scripts/bundle_zip.py --manifest temp/red-team-review-[topic-name]/file-manifest.json --bundle temp/red-team-review-[topic-name]/payload.zip
  ```

Once the payload is generated, inform the user that it is ready for handoff. If it is a Markdown file, explicitly remind them they can copy the contents of that file and paste it directly into their external chat interface.