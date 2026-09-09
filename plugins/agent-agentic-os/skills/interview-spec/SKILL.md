---
name: interview-spec
plugin: agent-agentic-os
version: 1.2.0
description: >
  CRITICAL INTAKE GATEWAY: Use at the very start of ANY non-trivial engineering task,
  feature request, architectural refactor, or multi-file bugfix before entering plan mode
  or modifying code. Enforces read-only discovery, Socratic Defaulting (1-3 structured
  questions with recommended defaults), control plane registration in control_plane.db,
  and compilation of the immutable 4-Pillar TASK_SPEC.md.
allowed-tools: Bash, Read, Write
---

# Interview Spec (`interview-spec`)

## Purpose
Acts as the universal front-door intake for non-trivial engineering tasks across all supported AI agent runtimes. Enforces Proposal Mode (strictly read-only) before code implementation:

1. **Native-First Deferral:** Detects active host runtime capabilities and defers to native environments while strictly enforcing conversational cadence.
2. **Socratic Pacing (ONE Question at a Time):** When interrogating requirements, the agent MUST ask only ONE question per turn with structured options and an explicit `[Recommended]` default. Never dump multiple questions simultaneously or answer on behalf of the user.
3. **Draft Spec & Implementation Plan Compilation:** Compiles the agreed requirements into a draft `TASK_SPEC.md` and `implementation_plan.md` in state `DRAFT_PLAN`.
4. **Multi-Agent Review Stage Gate (User-Controlled):** After draft spec compilation, explicitly asks the user whether they want to generate an external review bundle (via `context-bundler`) for multi-model critique in browser, or skip directly to approval.

## Stage-entry question contract

The authoritative stage-entry contracts are in `scripts/control_plane/transition_templates.yaml`
under `stages`. A transition template's `human_questions` are edge-approval questions; they
do not replace the questions for the state being entered.

When entering a state:

1. Load that state's `stages.<STATE>` contract before asking anything.
2. Ask every `entry_questions` item in order, exactly one per turn.
3. After each answer, evaluate matching `adaptive_follow_up_rules` and ask generated follow-ups
   one at a time. Never invent an answer or silently skip a required question.
4. Do not request the next transition until the state's `exit_requirements` are satisfied.
5. Only then load the destination transition template and ask its `human_questions`.

`TRIVIAL` selects a shorter transition path; it never skips the `INTERVIEW` entry questions or
the complete `RETROSPECTIVE` survey. Record all answers, including adaptive follow-ups. The
final `RETROSPECTIVE -> DONE` question is only a completion/skip decision after the survey has
been captured.

---

## The 4 Pillars of `TASK_SPEC.md`

Every compiled specification must satisfy:
1. **The Job:** Clear, unambiguous description of the system change and target subsystem paths.
2. **The Why:** Core problem statement, architectural rationale, and user/system impact.
3. **Semantic Guardrails & Operational Reasons:** Non-negotiable boundaries paired with concrete justifications explaining why the constraint exists.
4. **Objective Definition of Done (DoD):** Programmatic verification commands (`exit 0` tests, linters, structural audits).

---

## Usage

### Native capability and worktree boundary

Before selecting a planning or worktree path, run the repository-owned
`scripts/capability_probe.py` contract through the active runtime. It returns
explicit runtime identity, native planning/worktree/subagent facilities, tool
support, and a portable fallback. Do not infer a capability from a model name
or from a globally installed binary. Codex native worktree handling is allowed
only when the active session explicitly reports `CODEX_NATIVE_WORKTREE`; in
that case follow the returned activation guidance. Otherwise use
`worktree-manager` and keep the portable worktree below `.worktrees/`.

Native facilities change how the selected runtime executes, not the control
plane's scope, approval, verification, or transition gates. A native path must
still produce the same governed artifacts and receipts as the portable path.

### 1. Detect Intake Mode & Start Intake
```bash
python3 scripts/interview_spec_engine.py
```

Route on the returned mode — do not proceed to Socratic questions if a native mode is returned:

| Returned Mode | Required Next Action |
|---|---|
| `DEFER_CLAUDE_NATIVE` | Invoke `EnterPlanMode` (native Claude Code Plan Mode). Do not run Socratic Defaulting. |
| `DEFER_ANTIGRAVITY` | Invoke Antigravity's native planning mode. Do not run Socratic Defaulting. |
| `EXECUTE_SOCRATIC_FALLBACK` | Proceed to Socratic Defaulting (1-3 questions at a time, structured options with an explicit recommended default) and compile `TASK_SPEC.md` directly. |

### 2. Register Task, Then Interview: TRIVIAL vs STANDARD
Register the task first (`agent_control.py init`), then transition from `INTAKE` to `INTERVIEW`.
On entering `INTERVIEW`, follow the stage-entry question contract. The first question classifies
the task as `TRIVIAL` or `STANDARD`; the remaining baseline and context-driven questions still
apply to both paths.

- **If STANDARD**: complete the adaptive interview, compile the spec and plan, and continue
  through the standard review gates.
- **If TRIVIAL**: complete the baseline interview and applicable evidence follow-up, then use
  the `INTERVIEW -> RETROSPECTIVE` transition. Do not fast-track directly from `INTAKE` to
  `DONE`; the retrospective remains mandatory.
- If classification changes or the interview cannot be completed, use the `ESCALATED` escape
  hatch. Detailed commands are in `references/detailed-reference.md`.

### 3. Transition to Draft Plan & Multi-Agent Review Gate
Compile the draft spec and plan using `write_plan_document.py`, then coordinate transition to
`DRAFT_PLAN`. Next, present the User Stage Gate:
> *"Step 3 (draft plan) is done. Do you want to trigger a multi-agent review of this plan (Step 4a — an external AI reviews it before you decide), or proceed straight to Step 5 (asking for your approval)?"*

- **Path A (Review)**: coordinate transition to `MULTI_AGENT_REVIEW`, package bundle via
  `context-bundler`, ingest external feedback, and align before `AWAITING_APPROVAL`.
  See `references/multi-round-external-review-protocol.md`.
- **Path B (Skip)**: transition directly to `AWAITING_APPROVAL`.
Commands and bundle specifications in `references/detailed-reference.md`.

### Read-only transition guidance

When unsure which edge is legal or what gate remains, query the persisted task state:

```bash
python3 plugins/agent-agentic-os/scripts/agent_control.py transition-guidance \
  --task-id <task-id>
```

The result is advisory only. It is derived from the versioned registry snapshot; SQLite
triggers, deterministic policy checks, human decisions, and persisted receipts remain the
authorities. A requested illegal edge returns recovery guidance without an authorizing
command. Do not infer legality from a stale chat transcript or from the helper command alone.
