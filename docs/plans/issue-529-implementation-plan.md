# Implementation Plan: issue-529 — Universal Transition-Authority Gate (APPROVED)

See `docs/plans/issue-529-spec.md` for the full spec. This document sequences the work into strict Test-Driven Development (TDD) slices.
All multi-agent review rounds have converged and been approved (TDD contract approved, security approved, architecture approved).
1. **Strict Authority Boundary (Coordinator Domain Validation vs Persistence Transactional Invariants):**
   `TransitionCoordinator` resolves templates via `TransitionRegistry`, evaluates domain policy predicates via `policy.py`, checks decision rules, and constructs an immutable normalized `TransitionCommitRequest`. `PersistencePort.apply_transition_with_receipts()` revalidates **persistable invariants only** (task exists, expected `from_state`/`to_state`, current occupancy transition ID, matching `template_id`, structural satisfaction of required decision records, atomic commit). It does not import or evaluate domain policy predicates.
2. **Accurate Human-Provenance Scope:**
   Repository Python code proves an explicit, bound `TransitionDecision` record exists for the exact edge attempt. Passing an actor string like `actor="human"` or `approver="Richard"` without a bound decision record fails closed.
3. **Clean Test Isolation (No Production Test Helpers):**
   `ControlPlane` has no `_seed_task_state_for_testing` or test-specific methods. Test seeding is handled in dedicated test fixtures (`plugins/agent-agentic-os/tests/helpers/control_plane_fixtures.py`) or fake test adapters.
4. **CLI Compatibility Alias:**
   The legacy `agent_control.py transition` CLI command is retained as a compatibility alias that routes directly into `TransitionCoordinator.coordinate_transition()`.
5. **Exact Recovery Occupancy Binding:**
   Freshness is proven by matching `(task_id, source_occupancy_transition_id, from_state, to_state, decision_type='APPROVAL', consumed_at IS NULL)` without cross-table sequence ID comparisons.

## Architectural Design

### 1. Inbound Action Execution Flow
```
Fixed Action Wrapper (record_interview_question.py / write_plan_document.py / run_exit_verification.py)
        │
        ▼
ControlPlane.verify_phase_capability(task_id, action_identity)
        ├── TransitionRegistry (releasing inbound edges lookup)
        ├── Policy Check Registry (evaluates declared check_ids)
        └── PersistencePort.get_last_transition()
                │
                ▼
        SqlitePersistenceAdapter (verifies current occupancy & latest edge)
```

### 2. Transition Execution Flow
```
Agent / User CLI (`agent_control.py coordinate-transition` / `agent_control.py transition`)
        │
        ▼
TransitionCoordinator.coordinate_transition(task_id, to_state)
        ├── TransitionRegistry (loads template, checklist, questions)
        ├── Interactive Prompt (presents checklist & collects 1-at-a-time decisions)
        ├── Policy Check Registry (evaluates declared check_ids)
        └── ControlPlane.commit_authorized_transition(commit_request)
                │
                ▼
        SqlitePersistenceAdapter.apply_transition_with_receipts()
                (Revalidates persistable invariants in SQLite transaction -> Commits state, decisions & receipts)
```

## Caller Migration Inventory
| File / Component | Existing Usage | Target Migration |
|---|---|---|
| `interview_spec_engine.py` | Calls `agent_control.py transition` | Calls `agent_control.py coordinate-transition` |
| `interview-spec/SKILL.md` | Documents `agent_control.py transition` | Documents `coordinate-transition` + registered wrappers |
| `agent_control.py` CLI | Public `transition` subcommand | Public `coordinate-transition` subcommand; `transition` acts as compatibility alias |
| `test_agent_control.py` | Direct `transition()` calls in test setups | Uses `coordinate_transition()` for workflow tests; uses `tests/helpers/control_plane_fixtures.py` for isolated unit setups |

## TDD Implementation Slices (Strict Test-First Order)

Each slice MUST begin by writing its failing tests in `plugins/agent-agentic-os/tests/test_agent_control.py` (or a dedicated test module), observing the test fail, implementing the minimal code to satisfy the contract, and verifying that the full regression test suite passes before moving to the next slice.

---

### Slice 1: TransitionRegistry, Schema Conformance & Bidirectional Parity
- **Failing Tests First:**
  - `test_registry_covers_every_allowed_edge` (Test 1)
  - `test_registry_has_no_orphan_entries` (Test 2)
  - `test_registry_no_duplicate_transition_ids_or_edges` (Test 3)
  - `test_registry_schema_validation_per_entry` (Test 4: verifies all 13 schema fields)
  - `test_registry_malformed_field_fails_closed` (Test 5)
  - `test_closed_check_id_validation` (Test 6)
  - `test_legacy_policy_migration_parity` (Test 7: verifies all legacy rules are mapped in YAML check IDs)
  - `test_action_capability_mapping` (Test 8)
- **Implementation:**
  - Create `plugins/agent-agentic-os/scripts/control_plane/transition_templates.yaml` with all 51 edges from `ALLOWED_TRANSITIONS`.
  - Create `plugins/agent-agentic-os/scripts/control_plane/registry.py` defining `TransitionRegistry` and `TransitionTemplate`.
  - Consolidate legacy transition rules in `control_plane/policy.py` into discrete check IDs.
  - Validate schema, field presence, and 1:1 bidirectional parity with `state_machine.ALLOWED_TRANSITIONS`.
- **Verification:** Run pytest for Slice 1 tests (`pytest plugins/agent-agentic-os/tests/test_agent_control.py -k registry`).

---

### Slice 2: Typed Records, Adapter Read-Back & Multi-Edge Capability Resolution
- **Failing Tests First:**
  - `test_multi_edge_action_resolution` (Test 9: verifies multi-source actions like `plan_write` authorize from all valid inbound edges)
  - `test_unregistered_action_identity_denies_closed` (Test 10)
  - `test_get_last_transition_scoped_to_current_occupancy` (Test 28: leave-and-reenter occupancy isolation)
- **Implementation:**
  - In `control_plane/ports.py` and `adapters.py`, define typed records `TransitionRecord`, `TransitionDecision`, `TransitionCommitRequest`, and `PhaseCapability`.
  - Implement `SqlitePersistenceAdapter.get_last_transition(task_id, from_state, to_state)` returning `Optional[TransitionRecord]`.
  - In `agent_control.py`, wire `ControlPlane.verify_phase_capability(task_id, action_identity)` using `TransitionRegistry` mapping.
- **Verification:** Run pytest for Slice 2 tests.

---

### Slice 3: Atomic Persistence Contracts, Decisions Schema & Recovery Lifecycle
- **Failing Tests First:**
  - `test_persistence_structural_inconsistency_rejection` (Test 18)
  - `test_recovery_approval_issuance` (Test 26)
  - `test_recovery_approval_denies_when_stale` (Test 27)
  - `test_exact_recovery_occupancy_binding_after_leave_reenter` (Test 28)
  - `test_atomic_recovery_transition_success` (Test 29)
  - `test_recovery_approval_denies_on_sequential_and_concurrent_replay` (Test 30)
- **Implementation:**
  - Add `transition_decisions` table in `control_plane/adapters.py` schema with migration.
  - Implement `apply_transition_with_receipts`, `record_recovery_approval`, and `apply_recovery_transition` in `PersistencePort` and `SqlitePersistenceAdapter`.
  - Ensure single SQLite transaction (`BEGIN IMMEDIATE`) atomically validates persistable transactional invariants (occupancy ID, edge, template ID, decision record structural integrity) and commits staged records.
  - Add recovery transition check IDs in `control_plane/policy.py`.
- **Verification:** Run pytest for Slice 3 tests.

---

### Slice 4: Action Wrappers, Shadow Writes & Zero-Side-Effect Enforcement
- **Failing Tests First:**
  - `test_wrapper_zero_side_effects_on_denial` (Test 20)
  - `test_wrapper_success_path` (Test 21)
  - `test_plan_write_shadow_file_atomic_replacement` (Test 22: verifies `O_CREAT | O_EXCL | O_NOFOLLOW` shadow file pattern)
  - `test_interview_wrapper_denies_in_intake_no_log_row` (Test 23 — original #524 bug)
  - `test_plan_write_wrapper_denies_in_interview_no_file_write` (Test 24 — live-reproduced #529 bug)
  - `test_verify_phase_capability_denies_state_transition_log_inconsistency` (Test 25)
- **Implementation:**
  - Implement `plugins/agent-agentic-os/scripts/control_plane/wrappers/record_interview_question.py`.
  - Implement `plugins/agent-agentic-os/scripts/control_plane/wrappers/write_plan_document.py` (shadow `.tmp` file pattern using `os.open` with `O_CREAT | O_EXCL | O_NOFOLLOW` + atomic `os.replace`).
  - Implement `plugins/agent-agentic-os/scripts/control_plane/wrappers/run_exit_verification.py`.
  - Add fixed CLI verification subcommands in `agent_control.py` (`verify-interview-question`, `verify-plan-write`, `verify-exit-verification`, `record-recovery-approval`).
- **Verification:** Run pytest for Slice 4 tests.

---

### Slice 5: Pre-Transition Checklist Coordinator & Single Entry Path
- **Failing Tests First:**
  - `test_coordinator_interactive_checklist_and_question_flow` (Test 11)
  - `test_visible_transition_output_contract` (Test 12)
  - `test_sequential_question_pacing` (Test 13)
  - `test_coordinator_rejection_on_failed_check_no_orphan_receipts` (Test 14)
  - `test_coordinator_atomic_rollback_on_concurrency_collision` (Test 15)
  - `test_direct_transition_command_routes_through_coordinator` (Test 16)
  - `test_coordinator_refuses_incomplete_request` (Test 17)
  - `test_production_transition_caller_migration_completeness` (Test 19)
- **Implementation:**
  - Create `plugins/agent-agentic-os/scripts/control_plane/coordinator.py` (`TransitionCoordinator`).
  - Implement `ControlPlane.coordinate_transition` and `ControlPlane.commit_authorized_transition`.
  - Update `agent_control.py` CLI: `coordinate-transition` becomes the primary transition command; `transition` acts as compatibility alias routing to `coordinate-transition`.
  - Create test fixture helper `plugins/agent-agentic-os/tests/helpers/control_plane_fixtures.py` for isolated unit test state setup.
  - Update `plugins/agent-agentic-os/skills/interview-spec/SKILL.md` to reference `coordinate-transition` and registered wrappers.
- **Verification:** Run pytest for Slice 5 tests.

---

### Slice 6: Full Regression, Symlink Audit & Plugin Reinstall
- **Verification Steps:**
  1. Run full test suite: `python3 -m pytest plugins/agent-agentic-os/tests/ -v`.
  2. Run compliance audit: `python3 plugins/agent-scaffolders/scripts/audit.py --path plugins/agent-agentic-os`.
  3. Run structural audit: `python3 plugins/agent-scaffolders/scripts/audit_plugin_structure.py plugins/agent-agentic-os`.
  4. Run symlink diagnostics: `python3 .agents/skills/symlink-manager/scripts/symlink_manager.py diagnose`.
  5. Reinstall plugin: `python3 plugins/plugin-manager/scripts/plugin_add.py plugins/agent-agentic-os -y`.




