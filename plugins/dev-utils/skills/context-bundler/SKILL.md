---
name: context-bundler
plugin: dev-utils
description: >
  Interactively creates targeted code, design, and documentation bundles for external review (Markdown or ZIP).
  Supports Red Team review personas (Adversarial Security, Structural Architecture, Compliance Standards),
  full monorepo segmentation, and custom file manifest packaging.
allowed-tools: Bash, Read, Write, Glob, Grep
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

---

# Context Bundler Skill 📦

## Overview
This skill centralizes workflows for compiling codebase files, documentation, and instructions into portable payloads (`.md` for AI chat UIs or `.zip` for offline/agent handoffs).

`context-bundler` supports **3 Execution Modes**:
1. **Standard Bundle Mode**: Custom interactive selection of files/directories for general review or context sharing.
2. **Red Team Review Mode**: Injects specialized review persona prompts (Adversarial Security, Structural Architecture, Compliance Standards) as `prompt.md` ahead of codebase files.
3. **Monorepo Segmented Mode**: Full monorepo context packaging partitioned by domain (`/skills`, `/agents`, `/scripts`, `/docs`).

---

## 🎭 Persona Templates (Red Team & Specialized Review Modes)

When running in **Red Team Review Mode**, select or recommend a review persona template from `assets/templates/`:

- **`adversarial-security-auditor.md`**: Focuses on OWASP Top 10, auth bypasses, injection vectors, and severity scoring (Critical/High/Medium/Low).
- **`structural-architecture-reviewer.md`**: Focuses on C4 models, SOLID principles, coupling, modularity, and refactoring blueprints.
- **`compliance-standards-reviewer.md`**: Focuses on project conventions, 20-line purpose headers, ADR compliance, and type annotation audits.

---

## Core Workflow

### Phase 1: Mode & Target Discovery
Evaluate the request and negotiate mode and format:
1. **Mode**: Standard Bundle, Red Team Review (select persona template), or Monorepo Segmented.
2. **Format**: Single Markdown payload (`.md`) or Portable ZIP archive (`.zip`).
3. **Targets**: Directories or file paths to package.

### Phase 2: Recap & Pre-Execution Confirmation
Present execution plan to user before running scripts:

```text
Context Bundle Plan:
- Mode: [Standard / Red Team (Persona) / Monorepo Segmented]
- Format: [.md or .zip]
- Persona Prompt: assets/templates/[selected-persona].md
- Included Paths:
  1. plugins/dev-utils/
  2. docs/architecture.md
- Output Target: temp/context-bundle-[name]/payload.[md|zip]

Proceed? (yes / adjust)
```

### Phase 3: Manifest Construction
Generate `file-manifest.json` in temporary directory (`temp/context-bundle-[name]/`).
For Red Team mode, `prompt.md` (containing the persona prompt) MUST be listed as the first file entry in `files`.

```json
{
  "title": "Red Team Review: Auth Subsystem",
  "description": "Adversarial security review bundle.",
  "excludes": ["**/*.png", "**/node_modules/**"],
  "files": [
    {
      "path": "temp/context-bundle-auth/prompt.md",
      "note": "Primary Persona Instructions"
    },
    {
      "path": "plugins/dev-utils/skills/github-issue-agent/",
      "note": "Target codebase"
    }
  ]
}
```

### Phase 4: Bundler Script Execution

- **Markdown (.md)**:
  ```bash
  python3 ./scripts/bundle.py --manifest temp/context-bundle-[name]/file-manifest.json --bundle temp/context-bundle-[name]/payload.md
  ```

- **ZIP Archive (.zip)**:
  ```bash
  python3 ./scripts/bundle_zip.py --manifest temp/context-bundle-[name]/file-manifest.json --bundle temp/context-bundle-[name]/payload.zip
  ```

Inform user when payload is ready for handoff or clipboard copying.