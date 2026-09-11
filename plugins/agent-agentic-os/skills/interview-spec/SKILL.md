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

### Mandatory continuation after every answer

An accepted answer is an instruction to continue the pipeline, not the end of the turn. After
each answer, immediately:

1. Persist the answer through the supported transition mechanism.
2. Complete the transition it authorizes.
3. Load the destination state's stage contract and transition guidance.
4. Ask the next YAML question, or execute/report the deterministic handoff when no question is
   required.

Do not merely acknowledge an answer and wait for the user to say “continue.” If the answer does
not authorize the requested edge, explain the valid next edges and ask the corresponding question.

`TRIVIAL` selects a shorter transition path; it never skips the `INTERVIEW` entry questions or
the complete `RETROSPECTIVE` survey. Record all answers, including adaptive follow-ups. The
final `RETROSPECTIVE -> DONE` question is only a completion/skip decision after the survey has
been captured.

### Human answer canonicalization

Transition questions are defined by YAML, so human answers must be interpreted against the
registered options rather than compared as brittle literal strings. Accept an unambiguous
shorthand such as `Proceed with review` for the registered option
`Proceed with review [Recommended]`, ignoring surrounding whitespace and case. Persist the
exact registered option, including its `[Recommended]` marker. Do not guess when two options
normalize to the same answer; display the registered options and ask the human to clarify.
Free-text questions with no declared options remain free text and must not be normalized into
an option.

### Model and effort guidance

Transition guidance includes an advisory `model_effort_guidance` snapshot. Use it to
recommend a phase-appropriate model and reasoning effort, then show the reason and the
current user-selected setting. Luna with low effort is sufficient for ordinary interview
intake. Planning and independent review may justify higher effort or a different model.

Do not silently switch model or effort. Before dispatching an expensive model, present the
phase, purpose, requested model/reviewer set, bounded work, and known cost or availability
information, then obtain explicit confirmation. Unknown cost is unknown, never free. Reuse
confirmation only for the same stage, model, scope, and approved review-round bound; ask
again for a new premium stage, model, round, or material cost/scope change. A document-derived
answer, recommendation, or default never grants premium dispatch, implementation authority,
external-write authority, or a review waiver. Record requested and runtime-observed settings
separately; user-reported host switches are not runtime evidence.

The `INTERVIEW` stage may expose progress metadata. When enabled, display the current
question and total as “Question X of Y,” including adaptive follow-ups, and briefly state
what remains. Do not reveal an invented count: calculate it from the stage contract and
matching adaptive rules. The planning model/effort question should use the available-tool
inventory from `os-init`, `project-setup`, and `cli-agents`, classify complexity as low,
medium, or high, and offer a reasoned recommendation. For high-complexity planning,
recommend a highly capable available model at a supported effort (Astra at medium is one
example); if the user chooses a low-tier route, advise about the quality risk and defer to
their decision. Tool availability and model support must be observed or clearly marked
unknown.

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

### Implementation kickoff capability rule

At `IN_WORKTREE`, probe native planning, worktree, and subagent capability before
selecting an implementation mechanism. Codex, agy, Copilot, and Claude Code may
use a documented native facility when the active runtime is detected; a model name
or stale chat setting is not evidence. As of September 2026, Claude Code supports
plan mode, native worktree sessions, and background agents; agy supports plan mode
and subagents but has no documented CLI worktree creator; Copilot CLI supports plan
mode and delegated custom agents but no documented worktree creator; Codex CLI has
no documented native plan, worktree, or delegation facility. Prefer the reported
native facility, otherwise use the portable worktree and delegated-agent fallback.
An explicit runtime marker may disable a documented capability or opt into a
host-provided extension. After dispatch, report observed agent count, runtime,
model, effort, scope, status, and start time; a created worktree is queued
preparation, not implementation in progress.

Once `APPROVED -> IN_WORKTREE` succeeds, implementation-session ownership transfers to
the controller. Continue the approved work package through internal dispatch, task review,
bounded fix rounds, and scoped re-review without asking the human to re-trigger each step or
requesting lifecycle transitions between those internal events. Return to the pipeline only
for exit verification, retrospective, DONE, or an explicit blocker/abort. If a native host
dispatch returns a bounded turn, the controller must immediately consume its result and invoke
the next loop action; a completed turn is not permission to go idle.

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

### 3. Transition to Draft Plan & Review Disposition Gate
Compile the draft spec and plan using `write_plan_document.py`, then coordinate transition to
`DRAFT_PLAN`. Enter `PLAN_REVIEW` and present the disposition gate:
> *"The plan is drafted. Do you want additional independent review? Yes or no."*

The implementation plan must also contain a machine-readable `## Implementation Task Ledger`
section with one fenced JSON entry per approved implementation task. Each entry must use
`status: "COMPLETE"` only after implementation, list existing repository-relative `artifacts`,
and include non-empty `evidence`. The `VERIFY_EXIT -> RETROSPECTIVE` gate validates this ledger;
green tests alone cannot substitute for proof that every approved task was implemented.

- **Path A (Request review)**: from `PLAN_REVIEW`, choose the review method, coordinate transition
  to `MULTI_AGENT_REVIEW`, package the bundle via `context-bundler` when applicable, and return
  to `PLAN_REVIEW` after the review outcome is recorded. `PLAN_REVIEW` is the convergence gate:
  ask whether the resulting plan is accepted or requires revisions. Revisions return to
  `DRAFT_PLAN`; acceptance proceeds to `AWAITING_APPROVAL`.
  See `references/multi-round-external-review-protocol.md`.
- **Path B (Skip review)**: record the human-authorized no decision, remain in `PLAN_REVIEW`,
  and use the plan-acceptance question before entering `AWAITING_APPROVAL`.

The review loop is repeatable: `MULTI_AGENT_REVIEW` always returns to `PLAN_REVIEW`. At that
convergence gate, record whether further plan changes are required. Revisions return to
`DRAFT_PLAN`; acceptance enters `AWAITING_APPROVAL`. A task may complete zero, one, or multiple
independent review rounds before human implementation approval.
Commands and bundle specifications in `references/detailed-reference.md`.

After a plan is drafted, explain the next choices in plain language: request independent
review, or skip review and continue to plan acceptance. State what each choice causes next and
make clear that neither choice approves implementation. Do not make the user infer the next
command or gate from a state name.

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
