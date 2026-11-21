# Agentic OS control-plane architecture

This reference explains the executable control plane for agents and humans. The
state machine in `scripts/control_plane/state_machine.py` is authoritative for
legal transitions; `transition_templates.yaml` supplies the edge questions,
approval requirements, deterministic checks, and advisory guidance. The
`TransitionRegistry` loads that contract, and
`TransitionCoordinator` assembles a supported transition request. The SQLite
adapter is the persistence and trigger-enforcement boundary. This document is
an operational map, not a second state machine.

## Contents

- [Boundaries and authority](#boundaries-and-authority)
- [Lifecycle states](#lifecycle-states)
- [Executable transition inventory](#executable-transition-inventory)
- [Transition protocol](#transition-protocol)
- [Persistence and receipts](#persistence-and-receipts)
- [Execution-unit guidance](#execution-unit-guidance)
- [Verification and drift prevention](#verification-and-drift-prevention)


## Boundaries and authority

The public `agent_control.py` facade delegates state validation, policy, registry,
coordination, persistence, and receipt handling. Callers must use that facade or
its supported wrappers. Direct SQLite writes are not a supported transition
mechanism: the database trigger rejects state changes without the required,
bound decision rows, and the coordinator rejects non-interactive answers that
claim interactive human provenance.

Transition guidance is advisory. It explains what an agent should collect and
which command or wrapper to use, but it must not change legal transitions,
approval authority, required questions, or policy checks. The registry and
SQLite enforcement remain authoritative.

## Lifecycle states

| State | Meaning |
| --- | --- |
| INTAKE | Task is registered, scoping questions are answered, and the outline is confirmed. |
| DRAFT_PLAN | Plan, specification, and execution strategy artifacts are being authored or revised. |
| PLAN_REVIEW | Plan review and adversarial plan audit are conducted before Gate 1 signing. |
| APPROVED | Human Gate 1 SSH signature has been recorded; worktree creation may begin. |
| IN_WORKTREE | Approved implementation is being performed in the isolated worktree. |
| WORKTREE_REVIEW | Implementation diff and optional adversarial code review are presented before Gate 3 signing. |
| VERIFY_EXIT | Tests, leak/ledger checks, and retrospective are verified before closure signing. |
| DONE | Terminal completion state; only a human-authorized reset can reopen the task. |
| ROLLED_BACK | Implementation was rolled back after a failure or review finding. |
| ESCALATED | A human decision is required before the task can continue. |

*(Retired in schema v15: `INTERVIEW` absorbed into `INTAKE`, `MULTI_AGENT_REVIEW` and `AWAITING_APPROVAL` absorbed into `PLAN_REVIEW`, `MULTI_AGENT_CODE_REVIEW` absorbed into `WORKTREE_REVIEW`, `RETROSPECTIVE` absorbed into `VERIFY_EXIT`.)*

## Executable transition inventory

The following table is a documentation contract. Its rows must match both
`ALLOWED_TRANSITIONS` and the expanded transition templates (34 active edges). A row does not grant
permission by itself.

| From | To |
| --- | --- |
| INTAKE | DRAFT_PLAN |
| INTAKE | DONE |
| INTAKE | ESCALATED |
| DRAFT_PLAN | PLAN_REVIEW |
| DRAFT_PLAN | INTAKE |
| DRAFT_PLAN | DONE |
| DRAFT_PLAN | ESCALATED |
| PLAN_REVIEW | APPROVED |
| PLAN_REVIEW | DRAFT_PLAN |
| PLAN_REVIEW | INTAKE |
| PLAN_REVIEW | DONE |
| PLAN_REVIEW | ESCALATED |
| APPROVED | IN_WORKTREE |
| APPROVED | INTAKE |
| APPROVED | DONE |
| APPROVED | ESCALATED |
| IN_WORKTREE | WORKTREE_REVIEW |
| IN_WORKTREE | ROLLED_BACK |
| IN_WORKTREE | INTAKE |
| IN_WORKTREE | DONE |
| IN_WORKTREE | ESCALATED |
| WORKTREE_REVIEW | VERIFY_EXIT |
| WORKTREE_REVIEW | IN_WORKTREE |
| WORKTREE_REVIEW | ROLLED_BACK |
| WORKTREE_REVIEW | INTAKE |
| WORKTREE_REVIEW | DONE |
| WORKTREE_REVIEW | ESCALATED |
| VERIFY_EXIT | DONE |
| VERIFY_EXIT | WORKTREE_REVIEW |
| VERIFY_EXIT | IN_WORKTREE |
| VERIFY_EXIT | ROLLED_BACK |
| VERIFY_EXIT | INTAKE |
| VERIFY_EXIT | ESCALATED |
| DONE | INTAKE |
| ROLLED_BACK | PLAN_REVIEW |
| ROLLED_BACK | INTAKE |
| ROLLED_BACK | DONE |
| ROLLED_BACK | ESCALATED |
| ESCALATED | PLAN_REVIEW |
| ESCALATED | INTAKE |
| ESCALATED | DONE |

The canonical diagrams provide visual views of this same inventory:

- [`control-plane-pipeline.mermaid`](diagrams/control-plane-pipeline.mermaid)
- [`control-plane-pipeline-happy-path.mermaid`](diagrams/control-plane-pipeline-happy-path.mermaid)
- [`control-plane-architecture.mermaid`](diagrams/control-plane-architecture.mermaid)

## Transition protocol

1. Read `transition-guidance` for the current state and requested edge.
2. Confirm the edge is legal and inspect its human questions, approvals,
   deterministic checks, required artifacts, and recovery path.
3. Gather answers through the supported interactive wrapper. A programmatic
   caller must use its own actor identity; it may not label supplied answers as
   interactive human provenance.
4. Run the required policy checks and record verification or review receipts.
5. Submit the coordinated transition. The adapter binds decisions to the
   transition and lets SQLite enforce the required-question contract.
6. Report the persisted state and evidence. If a check fails, use the declared
   recovery edge or escalate; do not mutate the state directly.

Human approval is distinct from an agent or delegated review. Review skips are
explicit, justified receipts, not silent bypasses. The `APPROVED` gate remains a
human authority boundary even when plan or code reviews are skipped.

## Persistence and receipts

| SQLite surface | Responsibility |
| --- | --- |
| `tasks` | Current task state, task identity, artifacts, worktree, and metadata. |
| `task_transitions` | Append-only transition history and reasons. |
| `transition_decisions` | Answers and approvals bound to one transition attempt. |
| `required_transition_questions` | Expanded YAML requirements enforced by the SQLite trigger. |
| `verification_receipts` | Test, review, artifact, and gate evidence. |
| `delegation_contracts` | Scope, authority, budget, and delegated receipts. |
| `retrospective_followups` | Closeout follow-ups that must be resolved before `DONE`. |

Receipts are evidence, not authority. The state machine and policy decide what is
allowed; SQLite records and enforces the decisions needed for the allowed edge.

## Execution-unit guidance

The YAML registry exposes one advisory contract for each unit inside a work
package: work package, task, slice, transition, and execution step. Each unit
should make these fields explicit before it runs:

`objective`, `scope_boundary`, `prerequisites`, `authority`,
`expected_artifacts`, `validation_command`, `completion_evidence`,
`handoff_condition`, and `failure/recovery`.

The work package establishes the approved outcome and boundaries. A task owns a
bounded deliverable. A slice is a small independently verifiable increment. A
transition is a governed state change. An execution step is the next concrete
command or edit. Agents may adapt the order and implementation detail within
those boundaries, but advisory guidance must not create a parallel task graph,
expand authority, or replace a required gate.

## Verification and drift prevention

The contract tests compare registry-derived states and edges with this overview,
while the diagram contract compares the canonical state machine with the Mermaid
pipeline. Keep the registry and SQLite seeding logic authoritative; update this
reference and diagrams whenever a real lifecycle edge changes. A documentation
change alone must not imply a new legal transition.
