---
name: compile-apm-package
description: >-
  Activate when the user wants to compile an APM package into top-level context
  documents such as AGENTS.md, CLAUDE.md, or GEMINI.md, especially for Codex,
  Gemini, OpenCode, or agents-protocol style hosts. Do not use when the user
  only needs per-skill installation; use install-apm-package instead.
allowed-tools: Bash, Read, Glob
---

# compile-apm-package Skill 📄

## Overview
This skill generates merged context documents from APM primitives. This is primarily required for harnesses that consume a single authoritative file (like Gemini's `GEMINI.md`) rather than distributed skill directories.

## 🚫 Non-Negotiables
1. **Artifact Status** — Compiled files (`AGENTS.md`, etc.) are generated artifacts. NEVER edit them directly if a `.apm/` source tree exists.
2. **Conditional Use** — Do not run compile if the user's harness (e.g., Claude Code, Copilot Chat) supports native directory-based skills.
3. **Validation First** — Ensure the package is valid before merging primitives.

## Decision Tree
1. **Target supports directory-based skills?** -> Use `install-apm-package`.
2. **Target needs top-level context?** (e.g., Gemini, Codex) -> Run `apm compile`.
3. **Authoring shared context?** -> Use `apm compile` to verify how fragments merge into the final doc.

## Workflow
1. Verify `apm.yml` existence.
2. Execute `python scripts/validate_apm_package.py`.
3. Identify target requirements.
4. Run `apm compile [--target <slug>]`.
5. Report the location of generated context files.

## Anti-Patterns
- **Unnecessary Compilation**: Running `apm compile` for a Claude Code project (redundant work).
- **Direct Artifact Editing**: Fixing a typo in `GEMINI.md` instead of the source `.prompt.md`.
