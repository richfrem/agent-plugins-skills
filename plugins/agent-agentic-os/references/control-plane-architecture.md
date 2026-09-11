# Agentic OS control-plane architecture

This reference explains the executable control plane for agents and humans. The
state machine in `scripts/control_plane/state_machine.py` is authoritative for
legal transitions; `transition_templates.yaml` supplies the edge questions,
approval requirements, deterministic checks, and advisory guidance. The
`TransitionRegistry` loads that contract, and
`TransitionCoordinator` assembles a supported transition request. The SQLite
adapter is the persistence and trigger-enforcement boundary. This document is
an operational map, not a second state machine.

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
| INTAKE | Task is registered and awaiting initial classification. |
| INTERVIEW | The agent is gathering boundaries, intent, classification, and adaptive answers. |
| DRAFT_PLAN | Plan and specification artifacts are being authored or revised. |
| MULTI_AGENT_REVIEW | Delegated plan review is in progress. |
| PLAN_REVIEW | Human-facing plan review and route selection. |
| AWAITING_APPROVAL | Required human implementation approval is pending. |
| APPROVED | Human approval has been recorded; worktree creation may begin. |
| IN_WORKTREE | Approved implementation is being performed in the isolated worktree. |
| WORKTREE_REVIEW | Implementation receipt and changes are presented for review. |
| MULTI_AGENT_CODE_REVIEW | Delegated code review is in progress. |
| VERIFY_EXIT | Tests, checks, artifacts, and receipts are being verified. |
| RETROSPECTIVE | Closeout survey is completed or explicitly skipped with justification. |
| DONE | Terminal completion state; only an approved reset can reopen the task. |
| ROLLED_BACK | Implementation was rolled back after a failure or review finding. |
| ESCALATED | A human decision is required before the task can continue. |

## Executable transition inventory

The following table is a documentation contract. Its rows must match both
`ALLOWED_TRANSITIONS` and the expanded transition templates. A row does not grant
permission by itself.

| From | To |
| --- | --- |
| INTAKE | INTERVIEW |
| INTAKE | DRAFT_PLAN |
| INTAKE | PLAN_REVIEW |
| INTAKE | DONE |
| INTAKE | ESCALATED |
| INTERVIEW | DRAFT_PLAN |
| INTERVIEW | PLAN_REVIEW |
| INTERVIEW | RETROSPECTIVE |
| INTERVIEW | DONE |
| INTERVIEW | ESCALATED |
| INTERVIEW | INTAKE |
| DRAFT_PLAN | PLAN_REVIEW |
| DRAFT_PLAN | INTERVIEW |
| DRAFT_PLAN | DONE |
| DRAFT_PLAN | ESCALATED |
| DRAFT_PLAN | INTAKE |
| MULTI_AGENT_REVIEW | DRAFT_PLAN |
| MULTI_AGENT_REVIEW | PLAN_REVIEW |
| MULTI_AGENT_REVIEW | DONE |
| MULTI_AGENT_REVIEW | ESCALATED |
| MULTI_AGENT_REVIEW | INTAKE |
| PLAN_REVIEW | MULTI_AGENT_REVIEW |
| PLAN_REVIEW | AWAITING_APPROVAL |
| PLAN_REVIEW | DRAFT_PLAN |
| PLAN_REVIEW | INTERVIEW |
| PLAN_REVIEW | DONE |
| PLAN_REVIEW | ESCALATED |
| PLAN_REVIEW | INTAKE |
| AWAITING_APPROVAL | APPROVED |
| AWAITING_APPROVAL | PLAN_REVIEW |
| AWAITING_APPROVAL | DRAFT_PLAN |
| AWAITING_APPROVAL | DONE |
| AWAITING_APPROVAL | ESCALATED |
| AWAITING_APPROVAL | INTAKE |
| APPROVED | IN_WORKTREE |
| APPROVED | RETROSPECTIVE |
| APPROVED | DONE |
| APPROVED | ESCALATED |
| APPROVED | INTAKE |
| IN_WORKTREE | WORKTREE_REVIEW |
| IN_WORKTREE | VERIFY_EXIT |
| IN_WORKTREE | ROLLED_BACK |
| IN_WORKTREE | DONE |
| IN_WORKTREE | ESCALATED |
| IN_WORKTREE | INTAKE |
| WORKTREE_REVIEW | MULTI_AGENT_CODE_REVIEW |
| WORKTREE_REVIEW | VERIFY_EXIT |
| WORKTREE_REVIEW | IN_WORKTREE |
| WORKTREE_REVIEW | ROLLED_BACK |
| WORKTREE_REVIEW | DONE |
| WORKTREE_REVIEW | ESCALATED |
| WORKTREE_REVIEW | INTAKE |
| MULTI_AGENT_CODE_REVIEW | WORKTREE_REVIEW |
| MULTI_AGENT_CODE_REVIEW | VERIFY_EXIT |
| MULTI_AGENT_CODE_REVIEW | IN_WORKTREE |
| MULTI_AGENT_CODE_REVIEW | ROLLED_BACK |
| MULTI_AGENT_CODE_REVIEW | DONE |
| MULTI_AGENT_CODE_REVIEW | ESCALATED |
| MULTI_AGENT_CODE_REVIEW | INTAKE |
| VERIFY_EXIT | RETROSPECTIVE |
| VERIFY_EXIT | IN_WORKTREE |
| VERIFY_EXIT | WORKTREE_REVIEW |
| VERIFY_EXIT | ROLLED_BACK |
| VERIFY_EXIT | DONE |
| VERIFY_EXIT | ESCALATED |
| VERIFY_EXIT | INTAKE |
| RETROSPECTIVE | DONE |
| RETROSPECTIVE | ESCALATED |
| RETROSPECTIVE | INTAKE |
| DONE | INTAKE |
| ROLLED_BACK | DONE |
| ROLLED_BACK | ESCALATED |
| ROLLED_BACK | PLAN_REVIEW |
| ROLLED_BACK | INTAKE |
| ESCALATED | INTAKE |
| ESCALATED | PLAN_REVIEW |
| ESCALATED | DONE |

The canonical diagrams provide visual views of this same inventory:

- [`control-plane-pipeline.mermaid`](../../../docs/diagrams/control-plane-pipeline.mermaid)
- [`control-plane-pipeline-happy-path.mermaid`](../../../docs/diagrams/control-plane-pipeline-happy-path.mermaid)
- [`control-plane-architecture.mermaid`](../../../docs/diagrams/control-plane-architecture.mermaid)

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
