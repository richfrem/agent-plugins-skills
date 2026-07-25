---
name: context-bundler
plugin: dev-utils
description: >
  Interactively creates targeted code, design, and documentation bundles for external review (Markdown or ZIP).
  Includes a comprehensive library of review & delegation persona templates (Adversarial Security, Plan Critique,
  Refactoring Quality, Sub-Agent Task Handoff, Documentation Synthesis, Architecture, Compliance).
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
2. **Persona-Driven Review / Handoff Mode**: Injects specialized review or delegation persona prompts (`prompt.md`) ahead of codebase files.
3. **Monorepo Segmented Mode**: Full monorepo context packaging partitioned by domain (`/skills`, `/agents`, `/scripts`, `/docs`).

---

## 🎭 Persona Template Library (`assets/templates/`)

When bundling context for external models, sub-agents, or human reviews, select or recommend a template from `assets/templates/`:

### 1. Security & Quality Review Personas
- **`adversarial-security-auditor.md`**: OWASP Top 10, auth bypasses, injection vectors, exploit scenarios, CVSS risk ratings.
- **`refactoring-quality-specialist.md`**: DRY violations, code smells, cyclomatic complexity reduction, before/after code diffs.
- **`compliance-standards-reviewer.md`**: Project conventions, 20-line purpose headers, ADR compliance, type annotations.

### 2. Architecture & Design Planning Personas
- **`structural-architecture-reviewer.md`**: C4 model, SOLID principles, coupling, interface abstraction leaks, component boundaries.
- **`plan-critique-reviewer.md`**: Stress-tests implementation plans, unstated dependencies, execution friction, rollback mechanisms.

### 3. Agent Task Handoff & Documentation Personas
- **`agent-task-delegator.md`**: Builds turnkey task prompts for sub-agents (Copilot CLI, Claude Code, Gemini CLI) with explicit tool gates & test criteria.
- **`docs-synthesis-specialist.md`**: Generates ADRs, C4 Mermaid diagrams, README guides, and API specs from raw codebase context.

---

## Core Workflow

### Phase 1: Mode & Target Discovery
Evaluate the request and negotiate mode and format:
1. **Mode**: Standard Bundle, Persona-Driven Review/Handoff (select persona template), or Monorepo Segmented.
2. **Format**: Single Markdown payload (`.md`) or Portable ZIP archive (`.zip`).
3. **Targets**: Directories or file paths to package.

### Phase 2: Recap & Pre-Execution Confirmation
Present execution plan to user before running scripts:

```text
Context Bundle Plan:
- Mode: [Standard / Persona Review (Selected Persona) / Monorepo Segmented]
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
For Persona-Driven mode, `prompt.md` (containing the selected persona prompt) MUST be listed as the first file entry in `files`.

```json
{
  "title": "Sub-Agent Handoff Bundle",
  "description": "Task delegation bundle for Copilot CLI.",
  "excludes": ["**/*.png", "**/node_modules/**"],
  "files": [
    {
      "path": "temp/context-bundle-task/prompt.md",
      "note": "Primary Persona & Handoff Instructions"
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