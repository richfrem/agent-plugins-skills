---
trigger: always_on
description: Graph Planning, Superpowers, and Execution Discipline Policy - native Plan Mode sandboxing, context-bundler adversarial convergence, worktree-isolated TDD, and multi-stage verification.
globs: ["**/*"]
---

# Graph Planning, Superpowers, and Execution Discipline Policy

> **THE SUPREME LAW: HUMAN GATE**
> You MUST NOT execute ANY state-changing operation (code writes, commits, external commands) without EXPLICIT user approval.
> "Sounds good" or "Looks right" is NOT approval.
> Only **"Proceed"**, **"Go"**, or **"Execute"** is approval.
> **VIOLATION = SYSTEM FAILURE**

---

## 1. Overview

All significant work MUST follow the three-phase lifecycle below. This replaces the linear
Specify/Plan/Tasks waterfall previously used here.
Before committing to an execution topology, consult [`agent-orchestration:select-loop-strategy`](../../agent-orchestration/skills/select-loop-strategy/SKILL.md)
to determine whether the task requires solo research, pair execution, an adversarial critique loop, or a deterministic state graph.

---

## 2. Phase 1: Native Plan Mode & Adversarial Review

### 2.1. Native Read-Only Plan Sandboxing
- Before generating code, you MUST enter host-native Plan Mode (Claude Code `/plan` / `Shift+Tab` or Copilot `@plan`).
- While in Plan Mode, filesystem mutations and write operations are **strictly prohibited**. Use only read-only search and AST analysis tools.
- The output must be written to an immutable spec/plan contract (e.g., `docs/plans/<feature-id>.md` or `~/.claude/plans/`).

### 2.2. Isolated Context Packaging via `context-bundler`
- Do NOT dump bloated whole-repo context or messy conversation history into reviewer prompts.
- Use `context-bundler` to package discrete codebase slices, interface contracts, and targeted role prompts for specialized adversarial reviewers.

### 2.3. Multi-Perspective Fan-Out & Convergence Cap
- Dispatch plan drafts to parallel reviewer personas coordinated via [`agent-orchestration:red-team-review`](../../agent-orchestration/skills/red-team-review/SKILL.md):
  - **Architecture Skeptic:** Interfaces, dependency cycles, missing contracts.
  - **Security / Edge-Case Auditor:** Injection, auth, failure paths, race conditions.
  - **TDD Contract Reviewer:** Deterministic test fixtures and assertion validity.
- **Convergence Rule:** Critique loops MUST cap at 2-3 rounds. If consensus is not reached, escalate the exact diff disagreement to the user for tie-breaking.

---

## 3. Phase 2: Worktree Isolation & Superpowers TDD

### 3.1. Worktree State Isolation & Graph Execution
- Execute implementation subagents strictly within dedicated `git worktree` branches (`../worktree-<feature-name>`).
- Subagents must not execute in shared or dirty working trees.
- High-assurance, multi-step tasks must execute as a deterministic Directed Acyclic Graph (DAG) state machine via [`agent-orchestration:graph-execution`](../../agent-orchestration/skills/graph-execution/SKILL.md), enforcing Proposal Mode, Verifier Sovereignty, and Asymmetric Persistence.
- Delegation between director and worker agents follows the [`agent-orchestration:dual-loop`](../../agent-orchestration/skills/dual-loop/SKILL.md) pattern (or [`agent-orchestration:co-pilot-loop`](../../agent-orchestration/skills/co-pilot-loop/SKILL.md) for fast-tier models).

### 3.2. Strict Red-Green-Refactor Enforcement
- Invoke `superpowers/test-driven-development` protocols:
  1. **Red:** Author concrete unit/integration test cases against the contract. Verify they FAIL.
  2. **Green:** Implement minimum functional code to make tests pass.
  3. **Refactor:** Clean up code while maintaining green test status.

---

## 4. Phase 3: Multi-Stage Verification

Verification is defense-in-depth and cannot rely solely on self-reported agent status:
1. **Deterministic Local Pass:** 100% green pass on test runners, static linters, and type checkers (`evaluate.py` / `npm test` / `cargo test`).
2. **Structural Workspace Verification:** Clean git worktree merge and branch teardown via host tools.
3. **Out-of-Band Context Alignment:** Use `context-bundler` to bundle modified files and git diffs for external alignment verification (e.g. Gemini UI inspection) prior to production deployment.

---

## 5. File & Character Standards
- **Paths:** Always provide unambiguous absolute or repo-relative paths (`specs/feature/plan.md`).
- **Encoding:** Strict UTF-8 only. No smart quotes (`"`, `'`), no em/en dashes (`—`, `–`), no non-ASCII glyphs. Use standard hyphens (`-`) and ASCII arrows (`->`).

---

## 6. Git & Agent Directory Discipline

- **NEVER** commit directly to `main`. **ALWAYS** use a feature branch.
- **NEVER** run `git push` without explicit, fresh approval.
- **NEVER** "auto-fix" via git operations.
- **HALT** immediately on any user "Stop/Wait" command.
- Write descriptive commit messages in the imperative mood.
- **NEVER** commit agent directories (`.agents/`, `.claude/`, `.gemini/`, `.codex/`) to version control. They contain session data and secrets.
- Any planning artifacts created inside an isolated git worktree will be deleted when the worktree is removed. Sync these to the main checkout directory before merging.

---

## 7. Context Management

- **Build context, then maintain it.** Do not redundantly re-read unchanged artifacts in a single session.
- **Never** use blind full-repo sweeps (`grep`, `find`, or `ls -R`); use targeted native `rg` / exact scoped file matches or structured directories. Zero background daemons required.

---
**Renamed**: 2026-08-27 (from `spec-driven-development-policy.md` — dropped "Spec-Kit" branding; this repo does not use the spec-kitty tool)
**Refactored**: 2026-08-27 — replaced with the three-phase Graph Planning, Superpowers, and Execution Discipline lifecycle (native Plan Mode sandboxing, context-bundler adversarial convergence capped at 2-3 rounds, worktree-isolated TDD, multi-stage verification)
**Ratified**: 2026-05-22 | **Replaces**: `constitution.md`, `AGENTS.md`, legacy `spec_driven_development_policy.md`
