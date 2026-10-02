# Prototyping Build & Assembly Guide

Detailed reference guide for `subagent-driven-prototyping` covering component decomposition, dispatch strategies, build loops, and review gates.

## Contents

- [Pre-Flight & Input Checks](#pre-flight--input-checks)
- [Dispatch Strategy Execution](#dispatch-strategy-execution)
- [Build Modes: Greenfield vs Brownfield vs Plugin](#build-modes-greenfield-vs-brownfield-vs-plugin)
- [Component Decomposition & Build Loop](#component-decomposition--build-loop)
- [Two-Stage Review & TDD Validation](#two-stage-review--tdd-validation)
- [Assembly & Completion Verification](#assembly--completion-verification)
- [Gotchas & Persona Enforcement](#gotchas--persona-enforcement)

---

## Pre-Flight & Input Checks

1. **Discovery Plan**: Verify at least one approved plan exists in `exploration/discovery-plans/`.
2. **Layout Direction**: If Phase 2 was active, verify `exploration/captures/layout-direction.md`.
3. **Worktree Isolation**: Check if worktree branch is already configured.

---

## Dispatch Strategy Execution

- **`copilot-cli`**: Route simple components to fast/cheap models, complex components to dense reasoning models.
- **`claude-subagents`**: Dispatch mechanical slices to Haiku, complex architecture to Sonnet.
- **`direct`**: Implement directly in main session context.

---

## Build Modes: Greenfield vs Brownfield vs Plugin

- **Greenfield**: Build standalone prototype into `exploration/prototype/components/` and assemble in `exploration/prototype/index.html`.
- **Brownfield**: Build directly into existing codebase following prevailing architectural patterns. Record tracking summary in `exploration/prototype/components/`.
- **Agent Plugin Mode**: Scaffold into `plugins/<plugin-name>/` using `create-plugin` and `create-skill`. Ensure minimal metadata in `.claude-plugin/plugin.json` (no prohibited `skills`/`agents` arrays). Validate with `audit-plugin`.

---

## Component Decomposition & Build Loop

1. Decompose into 3–6 plain-language parts (e.g. "navigation bar", "filter drawer", "summary table").
2. Build component by component.
3. Mark status: `COMPLETE`, `BLOCKED`, or `NEEDS_CONTEXT`.
4. Only advance when current component is `COMPLETE`.

---

## Two-Stage Review & TDD Validation

1. **Stage 1 (Plan Alignment)**: Reviewer checks against Discovery Plan requirements.
2. **Stage 2 (Code Quality)**: Reviewer inspects conventions, edge cases, and cleanliness.
3. **TDD Contract**: Write test verifier for Discovery Plan requirement -> verify failure -> implement -> pass.

---

## Assembly & Completion Verification

- Link components in entry point (`exploration/prototype/index.html`).
- Write `exploration/prototype/README.md` with execution instructions.
- Ensure all tests pass before presenting to SME.

---

## Gotchas & Persona Enforcement

- Use plain language: "build" (not "scaffold"), "set up" (not "instantiate"), "check" (not "validate").
- Avoid duplicate worktree creation.
- Keep user updates to one plain sentence per component.
