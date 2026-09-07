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

---

## The 4 Pillars of `TASK_SPEC.md`

Every compiled specification must satisfy:
1. **The Job:** Clear, unambiguous description of the system change and target subsystem paths.
2. **The Why:** Core problem statement, architectural rationale, and user/system impact.
3. **Semantic Guardrails & Operational Reasons:** Non-negotiable boundaries paired with concrete justifications explaining why the constraint exists.
4. **Objective Definition of Done (DoD):** Programmatic verification commands (`exit 0` tests, linters, structural audits).

---

## Usage

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

### 2. Register Task, Then Triage: TRIVIAL vs STANDARD
Register the task first (`agent_control.py init`). Before asking Socratic questions, ask the
single human triage question ("Is this a trivial fix or a standard task? [Recommended: <heuristic>]").

- **If STANDARD** (or default): coordinate transition to `INTERVIEW`, record Q&A turns with
  `record_interview_question.py`, and proceed with Socratic questions.
- **If TRIVIAL**: fast-track straight to `DONE` via `intake_to_done_trivial` (diff recorded in
  answers, no spec file written). If mis-triaged, use the `ESCALATED` escape hatch.
  Detailed commands in `references/detailed-reference.md`.

### 3. Transition to Draft Plan & Multi-Agent Review Gate
Compile the draft spec and plan using `write_plan_document.py`, then coordinate transition to
`DRAFT_PLAN`. Next, present the User Stage Gate:
> *"Step 3 (draft plan) is done. Do you want to trigger a multi-agent review of this plan (Step 4a — an external AI reviews it before you decide), or proceed straight to Step 5 (asking for your approval)?"*

- **Path A (Review)**: coordinate transition to `MULTI_AGENT_REVIEW`, package bundle via
  `context-bundler`, ingest external feedback, and align before `AWAITING_APPROVAL`.
  See `references/multi-round-external-review-protocol.md`.
- **Path B (Skip)**: transition directly to `AWAITING_APPROVAL`.
Commands and bundle specifications in `references/detailed-reference.md`.
