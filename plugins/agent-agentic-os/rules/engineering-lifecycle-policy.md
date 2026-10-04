---
trigger: always_on
description: Universal Execution Policy — Pre-Planning Intake Bookend, Native Plan Sandboxing, Worktree Isolation (.worktrees/task-<id>), Test-Driven Development, and Deterministic Exit Gates.
globs: ["**/*"]
---

# Engineering Lifecycle & Execution Discipline Policy

> **THE SUPREME LAW: CRYPTOGRAPHIC HUMAN GATE**
> You MUST NOT execute ANY state-changing operation (code writes, commits, external commands) without EXPLICIT signed human authorization.
> Chat confirmations like "Sounds good", "Looks right", "Proceed", "Go", or "Execute" are NOT parsed by the agent to self-approve Gate 1.
> Gate 1 is a signed transition (`AWAITING_APPROVAL` -> `APPROVED`). The human signs the content-bound challenge with their enrolled OpenSSH key via `agent_control.py approve-transition --request-id <id>` (or simulation key in simulation mode).
> Explicit signed approval advances task state to `APPROVED` in `context/control_plane.db`.
> **VIOLATION = SYSTEM FAILURE**

---

## Contents
- [1. Overview & 4-Phase Lifecycle](#1-overview--4-phase-lifecycle)
- [2. Phase 0: Pre-Planning Intake Bookend & Socratic Gate](#2-phase-0-pre-planning-intake-bookend--socratic-gate)
- [3. Phase 1: Native Plan Mode, Topology Strategy & Adversarial Review](#3-phase-1-native-plan-mode-topology-strategy--adversarial-review)
- [4. Phase 2: Worktree Isolation & TDD Execution](#4-phase-2-worktree-isolation--tdd-execution)
- [5. Phase 3: Deterministic Exit Gates & Asymmetric Persistence](#5-phase-3-deterministic-exit-gates--asymmetric-persistence)
- [6. Git & Environment Invariants](#6-git--environment-invariants)

---

## 1. Overview & 4-Phase Lifecycle

All STANDARD-classified engineering tasks MUST progress through the 4-phase lifecycle below. This replaces legacy waterfall approaches and couples upstream discovery to deterministic execution.

```
Phase 0: Intake & Socratic Gate (exploration-cycle-plugin + work-intake)
   │
   ├─ TRIVIAL classification (single-file/few-line, no architectural impact):
   │    CORRECTED 2026-09-19 (verified against the real state machine — see
   │    references/map-debt.md): there is NO dedicated stage-skipping edge for
   │    TRIVIAL work. The only edges reaching DONE directly from INTAKE or
   │    INTERVIEW are human_force_done__from_INTAKE/INTERVIEW — the force-close
   │    family, requiring live interactive human authorization, not a distinct
   │    trivial shortcut. TRIVIAL still walks every stage of the same pipeline
   │    (INTERVIEW -> DRAFT_PLAN -> PLAN_REVIEW -> AWAITING_APPROVAL -> APPROVED
   │    -> IN_WORKTREE -> WORKTREE_REVIEW -> VERIFY_EXIT -> RETROSPECTIVE ->
   │    DONE); it only LIGHTENS the evidence required at each stage (focused
   │    verification instead of full-suite, skip external reviewers, concise
   │    plan instead of the full contract) — it does not skip stages. If a
   │    change is small enough that even that full-but-lightened sequence is
   │    disproportionate, the correct choice is NOT a fabricated shortcut
   │    through this pipeline — it is to skip this control plane entirely
   │    (direct commit/push, `--no-verify` if the push hook blocks it) with the
   │    user's explicit authorization. See work-intake/SKILL.md and GitHub
   │    Issue #534 for the original (aspirational, never implemented) design
   │    this correction supersedes.
   │
   └─ STANDARD classification: continue below.
   │
Phase 1: Native Plan Mode, Strategy & Adversarial Review (critical-auditor + select-loop-strategy + Human Gate)
   │
Phase 2: Worktree Isolation & TDD Execution (.worktrees/task-<id> + worktree-manager + pattern runner)
   │
Phase 3: Deterministic Exit Gates & Asymmetric Persistence (6-State Vocabulary + Wiki)
```

**Scope note:** this policy governs tasks tracked in `agent_control.py`'s SQLite control
plane. The `self-evolution` skill runs a separate, independent lifecycle
(`evolution_state.py`, TRIAGE→...→COMPLETED/ROLLBACK/ESCALATED) with its own worktree
convention and approval flow — see `self-evolution-policy.md` and Section 4's note below.
Whether these two systems should eventually be reconciled into one is an open architectural
question tracked in [GitHub Issue #537](https://github.com/richfrem/agent-plugins-skills/issues/537); until that's decided, treat them as two separately-governed systems, not one universal mechanism.

---

## 2. Phase 0: Pre-Planning Intake Bookend & Socratic Gate

Before Plan Mode can ever be entered, the task must be bounded. Immediately after task
registration and before any Socratic question, `work-intake` asks one direct triage
question — TRIVIAL or STANDARD — with a heuristic-derived recommended default (see the
TRIVIAL fast-track branch in Section 1). Only STANDARD-classified tasks proceed through the
rest of this phase and into Phase 1:

1. **Read-Only Exploration Cycle:**
   - Execute read-only codebase discovery via `exploration-cycle-plugin` (`technical_diagnostic_engine.py`).
   - Inspect coupling surfaces (touched files, SQLite schemas, cross-plugin symlinks), surface hidden assumptions, and evaluate candidate architectural forks.
   - Emit `exploration/DIAGNOSTIC_BRIEF.md`.
2. **Interview Gate (`work-intake`):**
   - **Native-First Deferral:** Inspect session environment markers first (`CLAUDE_CODE_ENTRY`, `ANTIGRAVITY_IDE`). Defer to native interactive intake if present. Fall back to Socratic Defaulting loop for headless/Copilot sessions.
   - Socratic Defaulting: 1–3 questions max, structured options with explicit recommended default (`Option A [Recommended]` vs. `Option B`).
   - Compiles the immutable **4-Pillar Spec** (`TASK_SPEC.md`):
     - **1. The Job:** System objective and target subsystem paths.
     - **2. The Why:** Architectural rationale and user/system impact.
     - **3. Semantic Guardrails & Operational Reasons:** Non-negotiables paired with operational justifications.
     - **4. Definition of Done (DoD):** Programmatic verification commands.
   - Atomically records task and transitions state in `context/control_plane.db` (`INTAKE` -> `INTERVIEW`).

---

## 3. Phase 1: Native Plan Mode, Topology Strategy & Adversarial Review

1. **Two-Step Native Plan Sandboxing:**
   - Enforce host-native Plan Mode (Claude `/plan`, Copilot `@plan`, Antigravity plan mode) where available.
   - Host Plan Mode is strictly read-only and blocks filesystem mutations.
   - Two-step planning sequence: (1) author the plan natively in read-only plan mode; (2) exit plan mode to persist the plan artifacts (`TASK_PLAN.md` or implementation plan and pattern-owned artifacts).
2. **Execution Strategy Selection & Pattern Peerage (`select-loop-strategy`):**
   - Evaluate execution topology among the 6 peer patterns (`direct`, `dual-loop`, `graph`, `agent-swarm`, `red-team-review`, `learning-loop` / `triple-loop-learning`).
   - `graph-execution` is an equal peer pattern, chosen only when genuine structural dependency exists (parallel read fan-out, barrier synchronization, sequential ordered mutations). It is never chosen merely because a task needs human approval or rollback.
   - The control-plane plan records `strategy=<pattern>, rationale=<why>`.
   - **Pattern-Owned Plan Artifacts:** Each pattern owns its plan artifact (`graph-manifest.json` for graph, task packets for dual-loop, job files for agent-swarm). Never embed large execution manifests inside `TASK_PLAN.md`.
   - When `strategy=graph`, invoke `graph-planner` to author and compile `graph-manifest.json`, and run `validate_manifest.py` before submitting to `PLAN_REVIEW`.
3. **Pre-Execution Critic Review:**
   - Run clean-context adversarial review via `critical-auditor` (max 2–3 rounds) probing failure domains and cross-plugin boundaries before human presentation.
4. **The Supreme Law Cryptographic Human Gate:**
   - Request transition to `APPROVED` (`coordinate-transition --to APPROVED`), binding the reviewed spec, plan, and pattern artifact hashes into the challenge snapshot.
   - Human verifies the challenge snapshot and executes `agent_control.py approve-transition --request-id <id>` with their enrolled OpenSSH key.
   - The verified signature commits the transition to `APPROVED` in `context/control_plane.db`.

---

## 4. Phase 2: Worktree Isolation & TDD Execution

1. **Standard Worktree Topology (`worktree-manager`):**
   - Implementation MUST execute in dedicated isolated worktrees at `.worktrees/task-<task_id>/` (governed by `worktree-manager` and `issue_worktree_manage.py`). Never use sibling directories (`../worktree-...`).
   - Update `worktree_state` in `context/control_plane.db` to `written_in_worktree`.
   - **This convention applies to `agent_control.py`-tracked tasks only.** `self-evolution`
     cycles use their own separate, documented convention — sibling directories under
     `../worktree-evolution-<cycle_id>/` — per `self-evolution/SKILL.md` and
     `self-evolution-policy.md`. This is not a violation of the rule above; it's a
     different, independently-governed system (see Section 1's scope note and
     [#537](https://github.com/richfrem/agent-plugins-skills/issues/537)).
2. **Deterministic Orchestration & TDD Execution:**
   - The execution pattern selected during Phase 1 (`direct`, `dual-loop`, `graph`, `agent-swarm`, `red-team-review`, `learning-loop`) executes inside the isolated worktree sandbox.
   - For graph-planned tasks, `graph-execution` consumes `graph-manifest.json` inside the isolated worktree sandbox, dispatching parallel reads and sequential mutations with strict receipt verification.
   - Enforce strict Red-Green-Refactor:
     - **Red:** Author concrete unit/integration tests matching the contract. Verify they FAIL.
     - **Green:** Implement minimum functional code to make tests pass.
     - **Refactor:** Clean up while maintaining 100% green test status.
3. **Mandatory Post-Task Leak Detection:**
   - Immediately after any subagent reports back, the controller MUST run `git status --short` in the main checkout (not the worktree) before packaging reviews. Discard stray uncommitted diffs matching superseded work.

---

## 5. Phase 3: Deterministic Exit Gates & Asymmetric Persistence

1. **Deterministic Local Exit:**
   - 100% green pass (`exit 0`) on tests (`pytest`), linters, and structural audits (`audit_plugin_structure.py`).
2. **Clean-Context Holistic Diff Review:**
   - Perform full-diff review to verify zero unintended mutations.
3. **Exact 6-State Worktree Status Vocabulary:**
   - Status reports must use the exact vocabulary from `worktree-lifecycle-management.md`:
     `written_in_worktree` | `committed_in_worktree` | `pushed_to_origin` | `merged_into_origin_main` | `local_branch_ref_updated` | `checked_out_on_disk`.
4. **Asymmetric Knowledge Persistence:**
   - Code mutations roll back on failure, but architectural insights, negative constraints, and discovered edge cases are permanently preserved in `wiki/decisions/` and `references/map-debt.md`.

---

## 6. Git & Environment Invariants

- **NEVER** commit directly to `main`. Always use isolated branches.
- **NEVER** run `git push` without explicit approval.
- **NEVER** commit transient agent directories (`.agents/`, `.claude/`, `.gemini/`, `.codex/`).
- UTF-8 encoding only. No smart quotes or non-ASCII characters in manifests and rules.
