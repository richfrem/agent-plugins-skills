---
name: interview-spec
plugin: agent-agentic-os
version: 1.1.0
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

### 2. Register Task in SQLite Control Plane
```bash
python3 scripts/agent_control.py init --task-id "<task-id>" --title "<title>" --runtime "<runtime>" --spec-path "docs/plans/<task-id>-spec.md"
python3 scripts/agent_control.py transition --task-id "<task-id>" --to "INTERVIEW" --reason "Beginning Socratic intake"
```

### 3. Transition to Draft Plan & Multi-Agent Review Gate
Once the 1-question-at-a-time interview concludes, compile the draft spec and plan, then transition:
```bash
python3 scripts/agent_control.py transition --task-id "<task-id>" --to "DRAFT_PLAN" --reason "Draft spec and plan compiled from interview"
```

Next, present the **User Stage Gate**:
> *"Would you like to run the Multi-Agent Review Phase (generate an external review bundle for browser models), or skip review and proceed directly to implementation approval?"*

#### Path A: User Chooses Multi-Agent Review
Transition to `MULTI_AGENT_REVIEW`:
```bash
python3 scripts/agent_control.py transition --task-id "<task-id>" --to "MULTI_AGENT_REVIEW" --reason "User requested multi-agent review bundle"
```
Invoke `context-bundler` to package:
- Target files: `docs/plans/<task-id>-spec.md`, `implementation_plan.md`, plus relevant architectural references.
- Persona template: `assets/templates/plan-critique-reviewer.md` or Multi-Persona Fan-Out.
- Output location: Saved strictly to a gitignored subfolder: `temp/review_<task-id>/`.
- Present the prompt and `.md` bundle path to the user to copy-paste into external browser models (ChatGPT, Claude Web, Grok).
- Ingest external model feedback, iterate on spec/plan, and once aligned, transition to `AWAITING_APPROVAL`.

#### Path B: User Skips Multi-Agent Review
Transition directly to `AWAITING_APPROVAL`:
```bash
python3 scripts/agent_control.py transition --task-id "<task-id>" --to "AWAITING_APPROVAL" --reason "User opted to skip multi-agent review gate"
```
