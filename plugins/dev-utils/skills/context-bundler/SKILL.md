---
name: context-bundler
plugin: dev-utils
description: >
  Interactively creates targeted code, design, and documentation bundles for external review (Markdown or ZIP).
  Includes a comprehensive library of review & delegation persona templates (Adversarial Security, Plan Critique,
  Refactoring Quality, Sub-Agent Task Handoff, Documentation Synthesis, Architecture, Compliance, TDD Contract
  Review), plus a Multi-Persona Fan-Out mode for parallel adversarial plan review (see
  graph-planning-superpowers-policy.md Phase 1).
allowed-tools: Bash, Read, Write, Glob, Grep
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

---

# Context Bundler Skill 📦

## Overview
This skill centralizes workflows for compiling codebase files, documentation, and instructions into portable payloads (`.md` for AI chat UIs or `.zip` for offline/agent handoffs).

> **Storage & Git Discipline:** All bundle manifests, markdown payloads, and archives MUST be generated inside a gitignored `temp/` subfolder (e.g., `temp/bundles/` or `temp/context-bundle-[name]/`). Never write bundle outputs to project root or non-ignored directories, which would pollute `git status` with massive generated review packages.

`context-bundler` supports **4 Execution Modes**:
1. **Standard Bundle Mode**: Custom interactive selection of files/directories for general review or context sharing.
2. **Persona-Driven Review / Handoff Mode**: Injects specialized review or delegation persona prompts (`prompt.md`) ahead of codebase files.
3. **Monorepo Segmented Mode**: Full monorepo context packaging partitioned by domain (`/skills`, `/agents`, `/scripts`, `/docs`).
4. **Multi-Persona Fan-Out Mode**: Packages the *same* target content against **multiple** persona templates in one pass, producing one bundle per persona for parallel adversarial dispatch. This is the mechanism `graph-planning-superpowers-policy.md` §2.2-2.3 refers to for Phase 1 plan review.

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

### 4. Graph Planning Phase 1 Fan-Out Trio
The canonical three-persona set for `graph-planning-superpowers-policy.md` §2.3's adversarial
plan review — use all three together via Multi-Persona Fan-Out Mode, not individually:
- **`structural-architecture-reviewer.md`** — **Architecture Skeptic** role: interfaces, dependency cycles, missing contracts.
- **`adversarial-security-auditor.md`** — **Security / Edge-Case Auditor** role: injection, auth, failure paths, race conditions.
- **`tdd-contract-reviewer.md`** — **TDD Contract Reviewer** role: deterministic test fixtures and assertion validity.

(For CLI-dispatched review instead of a bundle-to-external-chat handoff, the equivalent
`cli-agents` sub-agents are `architect-review`, `security-auditor`, and `tdd-contract-reviewer`.)

---

## Core Workflow

### Phase 1: Mode & Target Discovery
Evaluate the request and negotiate mode and format:
1. **Mode**: Standard Bundle, Persona-Driven Review/Handoff (select persona template), Monorepo Segmented, or Multi-Persona Fan-Out (select persona set — see below).
2. **Format**: Single Markdown payload (`.md`) or Portable ZIP archive (`.zip`).
3. **Targets**: Directories or file paths to package.

### Phase 2: Recap & Pre-Execution Confirmation
Present execution plan to user before running scripts:

```text
Context Bundle Plan:
- Mode: [Standard / Persona Review (Selected Persona) / Monorepo Segmented / Multi-Persona Fan-Out (Persona Set)]
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

---

## Multi-Persona Fan-Out Mode (Mode 4)

Used when the same target content (typically a Phase 1 plan draft, per `graph-planning-superpowers-policy.md` §2.2-2.3) needs parallel review by more than one persona in a single pass, with a bounded convergence loop.

1. **Select the persona set** — default to the Graph Planning Phase 1 Fan-Out Trio (`structural-architecture-reviewer.md`, `adversarial-security-auditor.md`, `tdd-contract-reviewer.md`) unless the caller specifies a different set.
2. **Build one manifest per persona**, each following the standard Phase 3 manifest format above, with that persona's `prompt.md` as the first file entry and the *same* target content following it:
   ```
   temp/context-bundle-[name]/architecture-skeptic/file-manifest.json
   temp/context-bundle-[name]/security-edge-case-auditor/file-manifest.json
   temp/context-bundle-[name]/tdd-contract-reviewer/file-manifest.json
   ```
3. **Run Phase 4 (bundler script execution) once per manifest** — this produces one payload per persona, ready for parallel dispatch (CLI sub-agents, or paste-to-chat/browser for each).
4. **Convergence cap**: the caller (typically `red-team-review`) tracks round count across all three personas combined and caps at 2-3 rounds total, per `graph-planning-superpowers-policy.md` §2.3 — `context-bundler` only packages each round's bundles, it does not track rounds itself.