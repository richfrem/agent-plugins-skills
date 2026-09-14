---
trigger: always_on
description: Policy for Spec-Driven Development (SDD) lifecycle and human-gate approval enforcement.
globs: ["**/*"]
---

# Spec-Driven Development (SDD) Policy

> **THE SUPREME LAW: HUMAN GATE**
> You MUST NOT execute ANY state-changing operation (code writes, commits, external commands) without EXPLICIT user approval.
> "Sounds good" or "Looks right" is NOT approval. 
> Only **"Proceed"**, **"Go"**, or **"Execute"** is approval.
> **VIOLATION = SYSTEM FAILURE**

---

## 1. The Spec-Kit Lifecycle

All significant work MUST follow the **Spec-Driven Development (SDD)** lifecycle. This is a tool-agnostic pattern that requires documentation and human approval *before* any implementation begins.

### The Lifecycle Map

1. **Specify**: Generate or write `spec.md` (The What and Why) -> **[STOP FOR GATE 0: USER APPROVES]**
2. **Plan**: Generate or write `plan.md` (The How) -> **[STOP FOR GATE 1: USER APPROVES]**
3. **Tasks**: Break down execution into `tasks.md` -> **[STOP FOR GATE 2: USER APPROVES]**
4. **Implement**: Execute tasks sequentially in an isolated feature branch.
5. **Review & Merge**: Review the implementation, seek acceptance, and merge.

*Note: For standard planning mode, an `implementation_plan.md` (combining Spec & Plan) and `task.md` satisfies these requirements as long as explicit approval is obtained before execution.*

---

## 2. The Three Execution Tracks

| Track | Name | When to Use | Workflow Required |
|-------|------|-------------|-------------------|
| **A** | **Factory** | Deterministic, repetitive operations | Auto-generated Spec/Plan/Tasks ➜ Execute |
| **B** | **Discovery** | Ambiguous, creative, or complex work | Full lifecycle with strict, sequential Human Gates |
| **C** | **Micro-Fix** | Trivial atomic fixes (typos, quick restarts) | Direct execution (No Spec/Plan required, no architectural decisions) |

---

## 3. Core Development Safeguards

### 3.1. Zero Trust Execution & Git Discipline
- **NEVER** commit directly to `main`. **ALWAYS** use a feature branch.
- **NEVER** run `git push` without explicit, fresh approval.
- **NEVER** "auto-fix" via git operations. 
- **HALT** immediately on any user "Stop/Wait" command.
- Write descriptive commit messages in the imperative mood.

### 3.2. Worktree & Agent Directory Safety
- **NEVER** commit agent directories (`.agents/`, `.claude/`, `.gemini/`, `.codex/`) to version control. They contain session data and secrets.
- Any planning artifacts (like `spec.md`, `plan.md`) created inside an isolated git worktree will be deleted when the worktree is removed. You MUST sync these research artifacts to the main checkout directory before merging.

### 3.3. Path Reference Rule
**Always provide unambiguous paths.**
When you mention directories or files, provide either the absolute path or a path relative to the project root.
- ✅ `kitty-specs/001-feature/tasks/WP01.md`
- ❌ "the tasks folder" or "WP01.md"

### 3.4. Strict UTF-8 Encoding Rule
**When writing ANY file (Markdown, JSON, YAML, code), use ONLY clean UTF-8 compatible characters.**
Failure to follow this rule breaks UI dashboards and parsers.
- ✅ Standard ASCII quotes: `"`, `'`
- ❌ Windows-1252 smart quotes: " " ' '
- ✅ Hyphen-minus: `-`
- ❌ Em/en dashes: — –
- ✅ ASCII arrow: `->`
- ❌ Special arrows: →

---

## 4. Context Management

- **Build context, then maintain it.** Do not redundantly re-read unchanged artifacts in a single session.
- **Never** use `grep`, `find`, or `ls -R` blindly for tool discovery; use specialized search tools (like RLM/Vector DB queries) or structured directories. 

---
**Ratified**: 2026-05-22 | **Replaces**: `constitution.md`, `AGENTS.md`, legacy `spec_driven_development_policy.md`
