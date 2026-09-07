# TASK SPEC: Universal Transition-Authority Gate for Registered Phase Actions
**Task ID:** `issue-529`
**Status:** APPROVED (multi-agent review converged: TDD contract approved, security approved, architecture approved)
**Round 1 receipts:** interview `EVO-INTEGRITY-issue-529-f46adbe930b5`; critic reviews `review_id` 6, 7, 8 (`architect-review`, `security-auditor`, `tdd-contract-reviewer`, all verdict `REVISE`).
**Round 2 receipts:** critic reviews `review_id` 9, 10, 11 (`external-reviewer`, `security-auditor`, `tdd-contract-reviewer`, all verdict `REVISE`).
**Round 3 receipts:** critic reviews `review_id` 12, 13, 14 (`architecture-skeptic` [REVISE], `security-auditor` [REVISE], `tdd-contract-reviewer` [PASS/APPROVE]).
**Round 4 receipts:** critic reviews `review_id` 15 (`architecture-skeptic` [REVISE]).
**Round 5 receipts:** critic reviews `review_id` 16 (`architecture-skeptic` [REVISE]).
**Round 6 receipts:** critic reviews `review_id` 17 (`security-edge-case-auditor` [PASS]), `review_id` 18 (`architecture-skeptic` [REVISE]).
**Round 7 receipts:** critic reviews `review_id` 19 (`architecture-skeptic` [PASS/APPROVE]).
**Prerequisite issue filed:** [#531](https://github.com/richfrem/agent-plugins-skills/issues/531) (soft plugin-composition convention for dev-utils surfaces).

## 1. The Job & User-Experience Intent
- **Objective:** Close the control-plane audit-trail-trust gap in both directions:
  - **Original scenario (#524):** task remains in `INTAKE`; an interview action is attempted; the interview wrapper must deny before any phase-specific output or database state mutation.
  - **Opposite-direction scenario (live-reproduced in this session, #529):** task is persisted in `INTERVIEW`; a `plan_write` action is attempted; the plan wrapper must deny before creating or modifying plan files.
- **The Core User Experience (Non-Negotiable):**
  At *every* transition boundary, the user visibly sees:
  1. Current phase & Requested next phase
  2. Why the transition is being proposed (Purpose)
  3. What checks have passed or failed (Checklist & Deterministic Checks)
  4. What artifacts are required
  5. What decision is being requested from the human
  6. Whether skipping is allowed and what it requires
  7. What capabilities the next phase releases
  8. What activities remain strictly prohibited

  The system prompts required questions **one at a time**, records answers durably, executes atomic persistence, verifies read-back, and explicitly confirms released capabilities and prohibited actions.

- **The Technical Architecture:**
  1. **Single Authoritative Transition Path:** All public transitions route through `TransitionCoordinator` (`coordinate-transition`). The legacy `agent_control.py transition` subcommand is retained as a compatibility alias that routes directly into `TransitionCoordinator`.
  2. **Honest Authority Boundary & Trust Model:**
     - **Semantic Completeness Authority (`TransitionCoordinator` + `TransitionRegistry` + `policy.py`):** The coordinator alone is authoritative for evaluating whether all template-required questions have been answered, required approvals/skips recorded, and deterministic policy checks satisfied before constructing `TransitionCommitRequest`.
     - **Transactional Structural Authority (`PersistencePort` / `SqlitePersistenceAdapter`):** Persistence independently revalidates **authoritative persistable facts only**: task existence, current state == expected from-state, latest occupancy transition ID == source occupancy ID, legal edge match, template ID match, valid decision types, unique question IDs, exact matching of all staged decisions to `(task_id, source_occupancy_transition_id, expected_from_state, to_state)`, guarded update, and atomic inserts. Persistence does **not** evaluate domain policy predicates or attempt to prove semantic completeness against caller-declared requirement metadata.
  3. A dedicated domain component **`TransitionRegistry`** that loads, validates, and serves the single consolidated `transition_templates.yaml` (51 edges matching `ALLOWED_TRANSITIONS` 1:1).
  4. **Unified Check Registry & Policy Migration:** `transition_templates.yaml` owns the edge-to-`check_ids` mapping; `policy.py` owns the closed `check_id`-to-callable implementation registry. Standalone transition edge tables (`TRANSITION_RULES`, `TO_STATE_RULES`) are consolidated into discrete check IDs declared per edge template, while non-transition operations (`OPERATION_RULES` like `worktree_push`) remain separate.
  5. An **Atomic Persistence Contract with Staged Decisions & Receipts** (`apply_transition_with_receipts` & `apply_recovery_transition`) in `PersistencePort` executing in a single SQLite transaction with optimistic locking, preventing orphan receipt stockpiling.
  6. A dedicated typed **`TransitionDecision`** persistence schema for recording durable question answers, approvals, explicit review skips, and recovery authorizations bound to the exact `source_occupancy_transition_id`.
  7. **Exact Recovery Occupancy Binding:** Recovery approval freshness is proven by exact binding to `(task_id, source_occupancy_transition_id, from_state, to_state, decision_type='APPROVAL', consumed_at IS NULL)` rather than comparing cross-table sequence IDs.
  8. **Clean Test Isolation (No Production Test Helpers):** No test seeding methods exist on production `ControlPlane`. Test fixtures (`plugins/agent-agentic-os/tests/helpers/control_plane_fixtures.py`) or fake test adapters handle test state setup.
  9. **Typed records** (`TransitionRecord`, `TransitionCommitRequest`, `TransitionDecision`, `PhaseCapability`) with immutable wrapper identities.
  10. **Optimistic Shadow File Writes** in file wrappers (`.<file>.tmp` with `O_CREAT | O_EXCL | O_NOFOLLOW` + atomic rename via `os.replace` + pre-commit re-verification).
- **Target Subsystems (all within `plugins/agent-agentic-os`):**
  - `plugins/agent-agentic-os/scripts/control_plane/transition_templates.yaml` — single consolidated, runtime-loaded registry for all 51 allowed edges.
  - `plugins/agent-agentic-os/scripts/control_plane/registry.py` — `TransitionRegistry` domain class (schema validation, 1:1 parity with `ALLOWED_TRANSITIONS`, multi-edge capability mapping, closed check ID validation).
  - `plugins/agent-agentic-os/scripts/control_plane/coordinator.py` — `TransitionCoordinator` (pre-transition checklist presentation, interactive Q&A collection, staged receipt aggregation, atomic execution orchestration).
  - `plugins/agent-agentic-os/scripts/control_plane/policy.py` — closed check registry mapping `check_id` strings to deterministic check callables, plus `OPERATION_RULES`.
  - `plugins/agent-agentic-os/scripts/control_plane/ports.py` & `adapters.py` — `PersistencePort` / `SqlitePersistenceAdapter` updates for `apply_transition_with_receipts`, `apply_recovery_transition`, `record_recovery_approval`, and `get_last_transition`.
  - `plugins/agent-agentic-os/scripts/agent_control.py` — facade wiring composing `TransitionRegistry` and `TransitionCoordinator`, fixed CLI verification subcommands, and `transition` compatibility alias.
  - Concrete wrapper scripts in `plugins/agent-agentic-os/scripts/control_plane/wrappers/`: `record_interview_question.py`, `write_plan_document.py`, `run_exit_verification.py`.
  - `plugins/agent-agentic-os/tests/test_agent_control.py` — test suite enforcing the 30-item test contract in test-first slices.
  - `plugins/agent-agentic-os/tests/helpers/control_plane_fixtures.py` — test state seeding utilities.
  - `plugins/agent-agentic-os/skills/interview-spec/SKILL.md` — documentation of wrapper integration, coordinator commands, and host-mediation boundaries.
- **Explicitly out of scope:** `implementation_start` (`dev-utils/issue_worktree_manage.py`) and `code_review` (`dev-utils/context-bundler`) — capability contract defined, enforcement blocked on [#531](https://github.com/richfrem/agent-plugins-skills/issues/531).

## 2. Transition User Experience Specification

### Example Interaction Flow (`DRAFT_PLAN -> MULTI_AGENT_REVIEW`)

```text
============================================================
TRANSITION PROPOSAL: DRAFT_PLAN -> MULTI_AGENT_REVIEW
============================================================

Current phase:   DRAFT_PLAN
Requested phase: MULTI_AGENT_REVIEW

Purpose:
Have independent agents review the proposed plan before implementation.

Checklist:
[✓] Specification exists (docs/plans/issue-529-spec.md)
[✓] Implementation plan exists (docs/plans/issue-529-implementation-plan.md)
[✓] No production code has been modified
[✓] Task is persisted in DRAFT_PLAN

Your Decision:
Would you like to submit the plan for independent review?
  1. Yes, generate the review bundles [Recommended]
  2. No, skip this optional review

Skipping requires:
- Explicit user choice
- Recorded reason
- Persisted skip decision

[User selects: 1]

Decision recorded: Multi-agent plan review requested
Transition committed: DRAFT_PLAN -> MULTI_AGENT_REVIEW
Persisted transition ID: 19
Current state verified: MULTI_AGENT_REVIEW

Capabilities released:
- generate_plan_review_bundle
- record_plan_review

Still prohibited:
- create implementation worktree
- modify production code
- push branch
- create pull request
============================================================
```

## 3. Architecture & Authority Split

```
+-----------------------------------------------------------------------------------+
|                           AUTHORITY BOUNDARIES                                    |
+-----------------------------------------------------------------------------------+
| 1. state_machine.py (ALLOWED_TRANSITIONS)                                         |
|    - Sole authority for structural DAG edge legality                              |
+-----------------------------------------------------------------------------------+
| 2. transition_templates.yaml (Validated by TransitionRegistry)                    |
|    - Sole authority for edge metadata: purpose, plain-language checklist,         |
|      human questions, approval policy, skip policy, capability mappings,          |
|      failure states, and declared check_ids                                       |
+-----------------------------------------------------------------------------------+
| 3. policy.py (Closed Check Registry)                                              |
|    - Sole authority for executable deterministic check implementations            |
|    - Maps check_id strings to callable predicates                                 |
|    - Unknown check_ids fail closed (PolicyConfigurationError)                      |
|    - Retains OPERATION_RULES for non-transition actions (worktree_push)           |
+-----------------------------------------------------------------------------------+
| 4. TransitionCoordinator (Orchestration & Policy Evaluation)                     |
|    - Evaluates edge checks via policy.py, validates decisions & approvals,        |
|      constructs normalized TransitionCommitRequest                                |
+-----------------------------------------------------------------------------------+
| 5. SqlitePersistenceAdapter (PersistencePort)                                     |
|    - Sole authority for ACID transactional persistence, optimistic locking,       |
|      revalidation of persistable invariants (task occupancy, edge match,          |
|      template_id match, decision record structural satisfaction), atomic commit   |
|      (apply_transition_with_receipts), and atomic recovery execution              |
+-----------------------------------------------------------------------------------+
```

### Inbound Flow Architecture
```
Fixed Action Wrapper (e.g. write_plan_document.py)
        │
        ▼
ControlPlane.verify_phase_capability()
        ├── TransitionRegistry (edge capability lookup)
        ├── Policy Check Registry (evaluates check_ids)
        └── PersistencePort (reads latest transition & occupancy)
                │
                ▼
        SqlitePersistenceAdapter
```

### Transition Execution Flow Architecture
```
Agent / User CLI
        │
        ▼
TransitionCoordinator.coordinate_transition()
        ├── TransitionRegistry (loads template, checklist, questions)
        ├── Interactive Prompt (collects human decisions sequentially)
        ├── Policy Check Registry (evaluates edge check_ids)
        └── ControlPlane.commit_authorized_transition(commit_request)
                │
                ▼
        SqlitePersistenceAdapter.apply_transition_with_receipts()
                (Revalidates persistable invariants in SQLite transaction -> Commits)
```

## 4. Atomic Persistence & Recovery Contracts

### Schema Additions: `transition_decisions` Table
```sql
CREATE TABLE IF NOT EXISTS transition_decisions (
    decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    source_occupancy_transition_id INTEGER NOT NULL,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    question_id TEXT NOT NULL,
    answer TEXT NOT NULL,
    decision_type TEXT NOT NULL CHECK(decision_type IN ('ANSWER', 'APPROVAL', 'REJECTION', 'SKIP', 'CONFIRMATION')),
    actor TEXT NOT NULL,
    recorded_at REAL NOT NULL,
    consumed_at REAL,
    bound_transition_id INTEGER REFERENCES task_transitions(transition_id)
);
CREATE INDEX IF NOT EXISTS idx_decisions_lookup ON transition_decisions(task_id, source_occupancy_transition_id);
```

### PersistencePort Interface Extension
```python
@dataclass(frozen=True)
class TransitionDecision:
    task_id: str
    source_occupancy_transition_id: int
    from_state: str
    to_state: str
    question_id: str
    answer: str
    decision_type: str
    actor: str
    recorded_at: float

@dataclass(frozen=True)
class TransitionCommitRequest:
    task_id: str
    expected_from_state: str
    to_state: str
    source_occupancy_transition_id: int
    template_id: str
    actor: str
    reason: str
    staged_decisions: List[TransitionDecision]
    staged_receipts: List[Dict[str, Any]]

@abstractmethod
def apply_transition_with_receipts(
    self,
    request: TransitionCommitRequest,
) -> TransitionRecord:
    """Atomically revalidates authoritative persistable facts in SQLite (BEGIN IMMEDIATE):
    1. Revalidates task exists and current state == request.expected_from_state.
    2. Revalidates latest transition_id == request.source_occupancy_transition_id.
    3. Revalidates edge (expected_from_state -> to_state) legality.
    4. Revalidates template_id non-empty and matching edge convention.
    5. Revalidates structural validity of staged_decisions:
       - Every staged decision matches (task_id, source_occupancy_transition_id, expected_from_state, to_state).
       - No duplicate question_ids exist across staged decisions.
       - Every decision_type is one of ('ANSWER', 'APPROVAL', 'REJECTION', 'SKIP', 'CONFIRMATION').
    6. Updates task state, inserts task_transitions row, inserts transition_decisions
       bound to the new transition_id, and inserts verification_receipts.
    7. Rolls back completely on any mismatch or SQLite error.
    NOTE: Semantic completeness (e.g. whether all template-required questions were asked or approvals
    recorded) and domain policy predicates are authoritatively evaluated upstream by TransitionCoordinator
    and policy.py. PersistencePort enforces transactional invariants and structural consistency only."""
    raise NotImplementedError

@abstractmethod
def record_recovery_approval(
    self,
    task_id: str,
    expected_source_state: str,
    destination_state: str,
    source_occupancy_transition_id: int,
    approver: str,
    decision: str,
    reason: str,
) -> str:
    """Issues and persists a fresh, unconsumed recovery approval decision record
    bound to the current source_occupancy_transition_id. Returns unique approval receipt token."""
    raise NotImplementedError

@abstractmethod
def apply_recovery_transition(
    self,
    task_id: str,
    expected_source_state: str,
    destination_state: str,
    source_occupancy_transition_id: int,
    approval_receipt_token: str,
    actor: str,
    reason: str,
) -> TransitionRecord:
    """Atomically executes recovery transition:
    1. Verifies current task state matches expected_source_state.
    2. Verifies recovery approval exists, is unconsumed, matches task_id and destination_state,
       and matches source_occupancy_transition_id exactly.
    3. Atomically marks the approval as consumed (consumed_at = epoch timestamp).
    4. Updates task state and inserts task_transitions row.
    5. Rolls back completely if any predicate fails."""
    raise NotImplementedError
## 5. Caller Inventory & Migration Strategy

To eliminate bypasses without breaking internal testing:

1. **Production Code & CLI:**
   - `interview_spec_engine.py` / `interview-spec/SKILL.md`: Migrated to invoke `agent_control.py coordinate-transition`.
   - `agent_control.py`: The public CLI exposes `coordinate-transition`. The existing `transition` CLI command is retained as a compatibility alias that routes directly through `TransitionCoordinator.coordinate_transition()`. There is no public raw transition commit subcommand.
2. **ControlPlane API Split:**
   - `ControlPlane.coordinate_transition(...)`: Public orchestration entry point.
   - `ControlPlane.commit_authorized_transition(commit_request)`: Internal method that passes normalized `TransitionCommitRequest` to `PersistencePort.apply_transition_with_receipts()` which performs transactional invariant re-validation.
   - **No Test Helpers in Production Code:** `ControlPlane` contains no test-seeding helpers. Test state setup is isolated in test fixtures (`plugins/agent-agentic-os/tests/helpers/control_plane_fixtures.py`) or fake test adapters.

## 6. Non-Negotiable Acceptance Criteria (DoD)
1. **1:1 Template Coverage:** Every allowed edge in `state_machine.ALLOWED_TRANSITIONS` (51 total) has exactly one template in `transition_templates.yaml`.
2. **Plain-Language Checklist Content:** Every template contains plain-language purpose, checklist, required artifacts, capabilities released, and capabilities prohibited.
3. **Sequential Question Pacing:** Every required human question is visibly presented one at a time with structured options and an explicit `[Recommended]` default.
4. **No Inferred Answers:** No human answer, approval, or skip decision is ever inferred from conversational chat or agent narration.
5. **Exact Decision Binding:** Approval and skip decisions are persistently recorded in `transition_decisions` bound to the exact `(task_id, source_occupancy_transition_id)`.
6. **Strict Authority Boundary:** Coordinator and TransitionRegistry are authoritative for semantic completeness of required questions, approvals, skips, and deterministic policy checks; `PersistencePort` revalidates authoritative persistable structural and transactional facts (task existence, current state, exact occupancy ID, edge, template identity, staged-decision binding, valid types, uniqueness, guarded update, atomic inserts).
7. **Exact Recovery Freshness:** Recovery approval freshness is proven by exact binding to `(task_id, source_occupancy_transition_id, from_state, to_state, decision_type='APPROVAL', consumed_at IS NULL)` rather than comparing cross-table sequence IDs.
8. **Unified Policy Authority:** YAML owns edge-to-check-ID mapping; `policy.py` owns check-ID-to-callable implementations. Standalone transition edge rule tables are consolidated.
9. **Atomic Commit Gate:** Transitions commit only after required questions, decisions, and deterministic checks pass, executed in a single SQLite transaction with staged receipts.
10. **Read-Back Verification:** The committed transition row is verified from SQLite before capability release is authorized.
11. **Visible Capability Boundaries:** The coordinator displays released capabilities and explicitly lists prohibited activities upon transition success.
12. **Informative Denial:** Denied transitions clearly display what check failed, what question was unanswered, or why authorization was withheld on stderr.
13. **Compatibility Alias & No Raw Bypass:** All production transition callers route through `TransitionCoordinator`, and `agent_control.py transition` acts as an alias to coordinator.

## 7. Test Contract (30 Tests, TDD Order)
1. **Allowed-edge -> registry:** Every `ALLOWED_TRANSITIONS` edge has exactly one registry entry.
2. **Registry -> allowed-edge (reverse):** Every registry entry corresponds to a legal edge.
3. **Registry unique keys:** No duplicate `transition_id` or `(from_state, to_state)` pairs.
4. **Per-entry schema validation:** All 13 required fields present and correctly typed.
5. **Malformed/unknown registry fields:** Fail closed with `TransitionRegistryError`.
6. **Closed check-ID validation:** All check IDs declared in YAML exist in `policy.py` check registry.
7. **Legacy policy migration parity:** Every legacy transition and destination-state rule is represented by YAML check IDs.
8. **Action capability mapping:** Every declared capability resolves to valid inbound edges.
9. **Multi-edge action resolution:** Multi-source actions (`plan_write`) authorize correctly from all valid inbound edges (`INTERVIEW->DRAFT_PLAN`, `MULTI_AGENT_REVIEW->DRAFT_PLAN`, etc.).
10. **Unregistered action identity:** Denied closed (`PhaseCapabilityDenied`), not `KeyError`.
11. **Pre-transition coordinator execution:** Displays checklist, collects question responses, and executes transition.
12. **Visible transition output contract:** Asserts coordinator output contains phase, purpose, checklist, questions, decisions, released/prohibited capabilities, and transition ID.
13. **Sequential question pacing:** Asserts required questions are presented one at a time, not batched.
14. **Coordinator rejection on failed check:** Blocks transition if deterministic check fails; no partial receipts committed.
15. **Coordinator atomic rollback on concurrency collision:** No staged decisions/receipts persisted if transition conflicts.
16. **Direct transition command routes through coordinator:** `transition` CLI command functions as an alias to `coordinate-transition`.
17. **Coordinator refuses incomplete request:** `TransitionCoordinator` refuses to construct a commit request when required template questions or decisions are missing.
18. **Persistence structural inconsistency rejection:** `PersistencePort` rejects structurally inconsistent commit requests: wrong occupancy ID, mismatched edge, missing task, invalid template ID, duplicate question IDs, invalid decision type, or mismatched staged decision binding.
19. **Production transition caller migration completeness:** Scan ensures no production code calls raw commit outside coordinator.
20. **Wrapper zero side-effects on denial:** No `interview_log` row, no plan file write, no verifier subprocess.
21. **Wrapper success path:** Side effect occurs only after verified `PhaseCapability`.
22. **Plan write shadow file atomic replacement:** Writes through `.tmp` shadow file with `O_CREAT | O_EXCL | O_NOFOLLOW` and re-verifies occupancy.
23. **Original scenario (#524):** Task in `INTAKE`; `interview_question` wrapper denied.
24. **Opposite-direction scenario (#529):** Task in `INTERVIEW`; `plan_write` wrapper denied.
25. **State/transition-log inconsistency:** Raw SQL state change without transition row denied.
26. **Recovery approval issuance:** `record_recovery_approval` binds to task, edge, and source occupancy ID.
27. **Stale recovery approval:** Approval predating latest entry to `ESCALATED`/`ROLLED_BACK` denied.
28. **Exact recovery occupancy binding after leave/re-enter:** Approval from earlier occupancy cannot authorize subsequent occupancy after leave/re-enter.
29. **Atomic recovery transition success:** Valid approval consumed and transition committed in one transaction.
30. **Recovery approval replay protection:** Sequential and concurrent replay of consumed approval denied.

## 8. Unresolved Cross-Plugin Gaps & Limitations
- **`dev-utils` Actions Deferred:** `implementation_start` (`issue_worktree_manage.py`) and `code_review` (`context-bundler`) require the cross-plugin composition pattern defined in [#531](https://github.com/richfrem/agent-plugins-skills/issues/531).
- **Host-Mediation & Enforcement Boundaries:**
  - Raw LLM chat generation, direct IDE/host tool operations (`Edit`, `Write`), and arbitrary direct in-process Python invocation of private methods are outside the repository-level enforcement boundary. Enforcement applies deterministically to supported CLI subcommands, coordinator entry points, and registered action wrappers.
  - Human provenance scope is strictly limited to proving that an explicit, bound `TransitionDecision` record was created through the coordinator Q&A / approval flow for the exact edge attempt. Repository Python code cannot authenticate physical human identity without host-mediated security. Passing an actor string like `actor="human"` alone does not satisfy human approval gates.
  - Critic Review Provenance Scope: `record_critic_review()` writes advisory review iterations and verdicts to `critic_reviews`. While `transition_decisions` binds questions and approvals to exact occupancy IDs, `critic_reviews` records are currently callable in-process by any persona or script. Without an external cryptographic signing channel (e.g. Issue #519), `critic_review_pass` validates table contents but cannot authenticate independent agent identity.




