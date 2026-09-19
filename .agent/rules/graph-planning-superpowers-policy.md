---
trigger: always_on
description: Universal Execution Policy — Pre-Planning Intake Bookend, Native Plan Sandboxing, Worktree Isolation (.worktrees/task-<id>), Superpowers TDD, and Deterministic Exit Gates.
globs: ["**/*"]
---

# Graph Planning, Superpowers, and Execution Discipline Policy

> **THE SUPREME LAW: HUMAN GATE**
> You MUST NOT execute ANY state-changing operation (code writes, commits, external commands) without EXPLICIT user approval.
> "Sounds good" or "Looks right" is NOT approval.
> Only **"Proceed"**, **"Go"**, or **"Execute"** constitutes authorization.
> Explicit approval transitions task state to `APPROVED` in `context/control_plane.db`.
> **VIOLATION = SYSTEM FAILURE**

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
Phase 1: Native Plan Mode & Adversarial Review (critical-auditor + Human Gate)
   │
Phase 2: Worktree Isolation & Superpowers TDD (.worktrees/task-<id> + Red-Green-Refactor)
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

## 3. Phase 1: Native Plan Mode & Adversarial Review

1. **Native Plan Sandboxing:**
   - Enforce host-native Plan Mode (Claude `/plan`, Copilot `@plan`, Antigravity plan mode) where available. Defer to Superpowers graph planning *only* when native host planning is absent or when executing complex multi-agent DAGs.
   - While in Plan Mode, filesystem mutations outside plan artifacts are strictly prohibited.
2. **Pre-Execution Critic Review:**
   - Run clean-context adversarial review via `critical-auditor` (max 2–3 rounds) probing failure domains and cross-plugin boundaries before human presentation.
3. **The Supreme Law Human Gate:**
   - Present plan and require explicit user approval ("Proceed", "Go", "Execute").
   - On approval, transition task to `APPROVED` in `context/control_plane.db`.

---

## 4. Phase 2: Worktree Isolation & Superpowers TDD

1. **Standard Worktree Topology:**
   - Implementation MUST execute in dedicated isolated worktrees at `.worktrees/task-<task_id>/` (governed by `issue_worktree_manage.py`). Never use sibling directories (`../worktree-...`).
   - Update `worktree_state` in `context/control_plane.db` to `written_in_worktree`.
   - **This convention applies to `agent_control.py`-tracked tasks only.** `self-evolution`
     cycles use their own separate, documented convention — sibling directories under
     `../worktree-evolution-<cycle_id>/` — per `self-evolution/SKILL.md` and
     `self-evolution-policy.md`. This is not a violation of the rule above; it's a
     different, independently-governed system (see Section 1's scope note and
     [#537](https://github.com/richfrem/agent-plugins-skills/issues/537)).
2. **Superpowers TDD Deferral Rule:**
   - Invoke Superpowers execution loops only where native execution lacks automated TDD or DAG management.
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
