#!/usr/bin/env python3
"""
agent_control.py — Lightweight SQLite Control Plane for Agent Lifecycle
========================================================================

Purpose:
    ACID state machine and audit log for task execution, verifier sovereignty,
    pre-execution review gating, worktree 6-state tracking, and cryptographic
    receipt generation across multi-tool agent environments.

Architecture (issue-524, hexagonal decomposition):
    ControlPlane is a facade composing 5 ports/adapters — it never calls sqlite3, hashlib, or
    time directly. Existing calls made with the original constructor arguments and all public
    method names/CLI behavior remain fully compatible; the constructor gained new *optional*
    adapter-injection parameters (for testing) that did not exist before, so "compatible" is
    the accurate claim here, not "unchanged" — a distinction an external review (round 2)
    correctly required be stated precisely. ControlPlane's remaining code is APPLICATION
    ORCHESTRATION ONLY: it coordinates state-machine validation, policy evaluation,
    persistence, cryptographic integrity, filesystem operations, model recommendation, and
    clock access through the composed components below — it does not itself implement
    state-machine adjacency logic or model tier-selection strategy (both were still embedded
    here as of an earlier revision; external review round 3 correctly required both be fully
    relocated, and this docstring corrected to stop describing that stale state):
      - self._state_machine -> control_plane.state_machine.StateMachine (pure domain class —
                                 no port/adapter pair; it has no infrastructure to abstract)
      - Gate/policy logic   -> control_plane/policy.py (a pure domain module — see the Gate
                                 Policy section below)
      - self._fs            -> control_plane.adapters.FilesystemAdapter        (FilesystemPort)
      - self._crypto        -> control_plane.adapters.CryptoAdapter            (CryptoPort)
      - self._clock         -> control_plane.adapters.ClockAdapter             (ClockPort)
      - self._model_catalog -> control_plane.adapters.ModelCatalogAdapter      (ModelCatalogPort —
                                 full resolve_recommended_model() resolution: tool-alias, tier
                                 strategy, and fallback, not just JSON file reads)
      - self._persistence   -> control_plane.adapters.SqlitePersistenceAdapter (PersistencePort —
                                 connection management, schema migration, AND every task/
                                 transition/receipt/review/verifier/log/worktree CRUD operation;
                                 ControlPlane composes this port, it does not issue SQL itself)
    Every port is constructor-injectable for testing (e.g. `ControlPlane(persistence_adapter=...)`)
    while defaulting to the real infrastructure implementation for all existing callers.

Layer:
    OS Kernel / Execution Control Plane Substrate

Key Input Dependencies:
    - SQLite database: context/control_plane.db (auto-initialized with WAL mode)
    - Optional model catalog references: plugins/cli-agents/references/*.json

Key Functions:
    - ControlPlane.init_db() — Initializes tables and WAL mode
    - ControlPlane.resolve_recommended_model() — Resolves model tier recommendations
    - ControlPlane.create_task() — Creates task in INTAKE
    - ControlPlane.get_task() — Retrieves task record
    - ControlPlane.transition() — Validates and transitions canonical DAG state
    - ControlPlane.lock_verifiers() — Locks SHA256 baseline hashes of verifier files
    - ControlPlane.verify_sovereignty() — Ensures verifier hashes have not been mutated
    - ControlPlane.record_critic_review() — Logs pre-execution review outcomes
    - ControlPlane.record_verification_receipt() — Stamps deterministic exit receipts
    - ControlPlane.get_verification_receipts() — Retrieves verification receipts
    - ControlPlane.update_worktree() — Updates worktree path, branch, and 6-state status
    - ControlPlane.log_asymmetric_persistence() — Logs Layer 2 wiki/map-debt persistence
    - ControlPlane.record_plan_mode_entry() — Records proof Plan Mode was entered (DRAFT_PLAN gate)
    - ControlPlane.record_socratic_intake_complete() — Records proof Socratic intake completed (DRAFT_PLAN gate)
    - ControlPlane.record_human_approval() — Records the human approval receipt (APPROVED->IN_WORKTREE gate, never skippable)
    - ControlPlane.record_review_skip() — Records an explicit, auditable decision to skip a discretionary review phase
    - main() — CLI dispatcher entry point

Usage Examples:
    python3 agent_control.py init --task-id <id> --title <title> --runtime <tool> [--task-type EVOLUTION]
    python3 agent_control.py transition --task-id <id> --to <state> --reason <text>
    python3 agent_control.py lock-verifiers --task-id <id> --paths <file1,file2>
    python3 agent_control.py verify-sovereignty --task-id <id>
    python3 agent_control.py record-receipt --task-id <id> --gate <g> --cmd "<c>" --exit-code <ec>
    python3 agent_control.py update-worktree --task-id <id> --path <p> --branch <b> --state <s>
    python3 agent_control.py status --task-id <id>
    python3 agent_control.py log-prior-art --task-id <id> --summary <text> [--repeat-yes-entries <csv>]
    python3 agent_control.py record-plan-mode-entry --task-id <id> --actor <a>
    python3 agent_control.py record-socratic-intake --task-id <id> --summary <text>
    python3 agent_control.py record-human-approval --task-id <id> --approver <a>
    python3 agent_control.py record-review-skip --task-id <id> --phase <p> --actor <a> --reason <text>

Gate Policy (unified, issue-524 Step 4):
    All gate/policy enforcement — per-edge transition requirements (formerly GATE_REQUIREMENTS),
    the prior-art/done/rolled-back guards (formerly 3 hardcoded _check_*_guard methods), and the
    worktree-push operation guard (formerly update_worktree()'s own independent barrier) — now
    resolves through ONE declarative policy-evaluation mechanism in control_plane/policy.py.
    See that module's TRANSITION_RULES/TO_STATE_RULES (lifecycle transitions) and
    OPERATION_RULES (controlled operations like the worktree push) for the full registry.
    Discretionary review phases (multi_agent_review, multi_agent_code_review) still accept an
    explicit recorded skip (record_review_skip) as an alternative to a real critic review —
    skips are never silent.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from control_plane.ports import (
    FilesystemPort,
    CryptoPort,
    ModelCatalogPort,
    ClockPort,
    PersistencePort,
    PhaseCapability,
    TransitionRecord,
    TransitionDecision,
    TransitionCommitRequest,
)
from control_plane.adapters import (
    FilesystemAdapter, SqlitePersistenceAdapter, CryptoAdapter, ModelCatalogAdapter, ClockAdapter,
    CURRENT_SCHEMA_VERSION,
)
from control_plane import policy as _policy
from control_plane.state_machine import StateMachine, CANONICAL_STATES, ALLOWED_TRANSITIONS, InvalidStateTransition
from control_plane.registry import TransitionRegistry
from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError


WORKTREE_STATES = [
    "written_in_worktree",
    "committed_in_worktree",
    "pushed_to_origin",
    "merged_into_origin_main",
    "local_branch_ref_updated",
    "checked_out_on_disk"
]

# CANONICAL_STATES, ALLOWED_TRANSITIONS, InvalidStateTransition, and state-machine validation
# logic moved to control_plane/state_machine.py's StateMachine (issue-524, post-round-2-review
# correction) — the domain/state-machine-validation responsibility, previously still embedded
# directly in ControlPlane.transition(). Re-imported above for backward-compatible
# `from agent_control import CANONICAL_STATES` (existing test/consumer import surface).

# SCHEMA_SQL, CURRENT_SCHEMA_VERSION, CHILD_TABLES, ALL_REBUILD_TABLES, and SCHEMA_MIGRATIONS
# moved to control_plane/adapters.py's SqlitePersistenceAdapter (issue-524 Step 5). This module
# re-imports CURRENT_SCHEMA_VERSION above for backward-compatible `from agent_control import
# CURRENT_SCHEMA_VERSION` (existing test/consumer import surface, unchanged).


class PhaseCapabilityDenied(Exception):
    """Raised when an action capability is denied for the current phase/occupancy."""
    pass


class VerifierSovereigntyViolation(Exception):
    """Raised when a protected verifier file has been tampered with."""
    pass


from control_plane.ports import PersistenceInvariantViolation


class ConcurrentModificationError(Exception):
    """Raised when a transition's expected prior state no longer matches the stored row,
    indicating a concurrent writer changed it — never silently overwritten (no last-writer-wins)."""
    pass



# Gate/policy enforcement (per-edge transition requirements, prior-art/done/rolled-back
# guards, and the worktree-push operation guard) is unified in control_plane/policy.py's
# TRANSITION_RULES / TO_STATE_RULES / OPERATION_RULES (issue-524 Step 4). This module no
# longer declares its own gate registry.


class ControlPlane:
    """Controller and state machine manager for task lifecycles."""

    def __init__(self, db_path: Optional[Path] = None, fs_adapter: Optional["FilesystemPort"] = None,
                 crypto_adapter: Optional["CryptoPort"] = None,
                 model_catalog_adapter: Optional["ModelCatalogPort"] = None,
                 clock_adapter: Optional["ClockPort"] = None,
                 persistence_adapter: Optional["PersistencePort"] = None):
        """Initializes the ControlPlane instance. All infrastructure is delegated: connection
        management, schema migration, and every task/transition/receipt/review/verifier/log/
        worktree CRUD operation go through a PersistencePort (SqlitePersistenceAdapter by
        default); SHA256/receipt-token hashing through a CryptoAdapter; model-catalog
        resolution through a ModelCatalogAdapter; wall-clock time through a ClockAdapter;
        state-machine legality through a StateMachine. `self.db_path` mirrors the persistence
        adapter's resolved `db_path` attribute where one exists (a fake/test PersistencePort
        may not have one, hence `getattr(..., None)`), for any code that introspects it
        directly. All optional parameters default to real infrastructure adapters; tests/
        callers can substitute any Port implementation — including `persistence_adapter`
        directly at construction, added after external review correctly required this be a
        true constructor-injection point rather than requiring private-attribute monkeypatching
        after construction. Existing calls made with the original `db_path`-only constructor
        argument remain fully compatible — the newly-added optional parameters extend the
        signature, they do not replace it (see docs/plans/issue-524-spec.md Section 3)."""
        self._fs = fs_adapter if fs_adapter is not None else FilesystemAdapter()
        self._crypto = crypto_adapter if crypto_adapter is not None else CryptoAdapter()
        self._clock = clock_adapter if clock_adapter is not None else ClockAdapter()
        self._model_catalog = model_catalog_adapter if model_catalog_adapter is not None else ModelCatalogAdapter()
        self._state_machine = StateMachine()
        if persistence_adapter is not None:
            self._persistence = persistence_adapter
        else:
            self._persistence = SqlitePersistenceAdapter(
                db_path if db_path is None else Path(db_path), self._fs, self._clock, self._crypto
            )
        self.db_path = getattr(self._persistence, "db_path", None)

    def init_db(self):
        """Initializes SQLite tables and WAL mode. Delegates to the SqlitePersistenceAdapter,
        which self-heals FK-corrupted or legacy schemas."""
        self._persistence.ensure_schema()

    def resolve_recommended_model(self, runtime_tool: str, tier: str = "low") -> Dict[str, str]:
        """Resolves model recommendation and model_id from plugins/cli-agents/references/.
        Full resolution (tool-alias, tier strategy, fallback) is delegated to
        self._model_catalog — this method is a pure delegate (issue-524, post-round-2-review
        correction: tier-selection/strategy logic previously still lived in ControlPlane)."""
        return self._model_catalog.resolve_recommended_model(runtime_tool, tier)

    def create_task(
        self,
        task_id: str,
        title: str,
        runtime_tool: str,
        spec_path: Optional[str] = None,
        model_tier: Optional[str] = None,
        model_id: Optional[str] = None,
        task_type: str = "GENERAL"
    ):
        """Creates a new task in INTAKE state and records creation transition."""
        if task_type not in ("GENERAL", "EVOLUTION"):
            raise ValueError(f"Invalid task_type '{task_type}'. Must be 'GENERAL' or 'EVOLUTION'.")
        if model_tier and not model_id:
            rec = self.resolve_recommended_model(runtime_tool=runtime_tool, tier=model_tier)
            model_id = rec["model_id"]

        self._persistence.insert_task(task_id, title, task_type, runtime_tool, spec_path, model_tier, model_id)

    def create_delegation_plan(self, task_id: str, contract: Dict[str, Any]) -> int:
        """Create a persisted delegation boundary; native execution strategy remains model-owned."""
        if not self.get_task(task_id):
            raise _policy.DelegationContractError(f"Task not found: {task_id}")
        _policy.validate_delegation_contract(contract)
        contract = dict(contract)
        contract["status"] = "PENDING_APPROVAL" if _policy.delegation_requires_approval(contract) else "APPROVED"
        return self._persistence.create_delegation_plan(task_id, contract)

    def get_delegation_plan(self, contract_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve one persisted delegation contract."""
        return self._persistence.get_delegation_plan(contract_id)

    def approve_delegation_plan(self, contract_id: int, actor: str) -> None:
        """Approve a high-cost or write-capable delegation through the human gate."""
        if actor != "human":
            raise _policy.DelegationContractError("Delegation approval requires actor='human'")
        self._persistence.approve_delegation_plan(contract_id, actor)

    def record_delegation_receipt(
        self,
        contract_id: int,
        backend: str,
        model_id: str,
        cost_tier: str,
        capability_class: str,
        backend_available: bool = True,
        write_capable: bool = False,
        written_paths: Optional[List[str]] = None,
    ) -> int:
        """Record one bounded execution attempt after contract and approval checks."""
        contract = self.get_delegation_plan(contract_id)
        if not contract:
            raise _policy.DelegationContractError(f"Delegation contract not found: {contract_id}")
        if contract["status"] not in {"APPROVED", "EXECUTING"}:
            raise _policy.DelegationContractError("Delegation requires human approval before execution")
        receipt = {
            "task_id": contract["task_id"], "backend": backend, "model_id": model_id,
            "cost_tier": cost_tier, "capability_class": capability_class,
            "backend_available": backend_available, "write_capable": write_capable,
            "written_paths": written_paths or [],
        }
        try:
            _policy.validate_delegation_receipt(
                contract, receipt, self._persistence.count_delegation_receipts(contract_id)
            )
        except _policy.DelegationContractError as exc:
            if "renewed approval" in str(exc):
                self._persistence.insert_delegation_receipt(contract_id, receipt)
                self._persistence.mark_delegation_status(contract_id, "PENDING_APPROVAL")
            raise
        self._persistence.mark_delegation_status(contract_id, "EXECUTING")
        return self._persistence.insert_delegation_receipt(contract_id, receipt)

    def record_delegation_verifier_receipt(self, contract_id: int, command: str, exit_code: int) -> None:
        """Record the declared verifier result for a delegation."""
        contract = self.get_delegation_plan(contract_id)
        if not contract:
            raise _policy.DelegationContractError(f"Delegation contract not found: {contract_id}")
        if command != contract["verifier"].get("command"):
            raise _policy.DelegationContractError("Verifier command does not match the approved contract")
        self._persistence.insert_delegation_verifier_receipt(contract_id, command, exit_code)

    def accept_delegation_result(self, contract_id: int) -> Dict[str, Any]:
        """Accept a result only after an execution receipt and passing verifier receipt exist."""
        contract = self.get_delegation_plan(contract_id)
        if not contract:
            raise _policy.DelegationContractError(f"Delegation contract not found: {contract_id}")
        if self._persistence.count_delegation_receipts(contract_id) == 0:
            raise _policy.DelegationContractError("Delegation result requires an execution receipt")
        if not self._persistence.has_delegation_verifier_receipt(contract_id):
            raise _policy.DelegationContractError("Delegation result requires a passing verifier receipt")
        self._persistence.mark_delegation_status(contract_id, "ACCEPTED")
        contract["status"] = "ACCEPTED"
        return contract

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a task dictionary by task_id."""
        return self._persistence.get_task(task_id)

    def get_transition_guidance(
        self, task_id: str, requested_to_state: Optional[str] = None
    ) -> Dict[str, Any]:
        """Return advisory guidance derived from the task's persisted state.

        This is intentionally read-only. The returned command is never an
        authorization token and cannot bypass policy, human decisions, or SQLite
        transition triggers.
        """
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        current_state = self._read_current_state_for_update(task_id)
        if current_state is None:
            raise ValueError(f"Task not found: {task_id}")
        if not hasattr(self, "_transition_registry"):
            self._transition_registry = TransitionRegistry.load_default()
        return self._transition_registry.get_transition_guidance(
            current_state, requested_to_state
        )

    def _build_transition_policy_ctx(
        self,
        task_id: str,
        task: Dict[str, Any],
        from_state: Optional[str] = None,
        to_state: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Builds the ctx dict consumed by control_plane.policy's transition/to-state rules.
        Every fact the policy engine needs comes from self._persistence (PersistencePort) —
        this method translates policy needs into port calls, never SQL directly."""
        stage_answers = {}
        get_answers = getattr(self._persistence, "get_unconsumed_transition_answers", None)
        if get_answers and from_state and to_state:
            stage_answers = get_answers(task_id, from_state, to_state)

        def check_implementation_completeness() -> Optional[str]:
            from control_plane.implementation import validate_implementation_ledger

            repo_root = getattr(self, "repo_root", None)
            if repo_root is None and self.db_path is not None and self.db_path.parent.name == "context":
                repo_root = self.db_path.parent.parent
            if repo_root is None:
                repo_root = Path.cwd()
            roots = []
            task_worktree = task.get("worktree_path")
            if task_worktree:
                worktree_root = Path(task_worktree)
                if not worktree_root.is_absolute():
                    worktree_root = Path(repo_root) / worktree_root
                roots.append(worktree_root.resolve())
            roots.append(Path(repo_root).resolve())
            for root in roots:
                plan_path = root / "docs" / "plans" / f"{task_id}-implementation-plan.md"
                if plan_path.exists():
                    return validate_implementation_ledger(plan_path, root)
            return (
                f"Implementation plan ledger missing for task '{task_id}': "
                f"expected docs/plans/{task_id}-implementation-plan.md."
            )

        return {
            "task_id": task_id,
            "task": task,
            "has_receipt": lambda gate_name: self._persistence.has_receipt(task_id, gate_name),
            "has_passing_critic_review": lambda: self._persistence.has_passing_critic_review(task_id),
            "count_receipts": lambda gate_name, exit_code=None: self._persistence.count_receipts(task_id, gate_name, exit_code),
            "count_locked_verifiers": lambda: self._persistence.count_locked_verifiers(task_id),
            "count_asymmetric_persistence": lambda details_like=None, destination_like_any=None:
                self._persistence.count_asymmetric_persistence(task_id, details_like, destination_like_any),
            "has_complete_retrospective": lambda: self._persistence.has_complete_retrospective(task_id),
            "verify_sovereignty": lambda: self.verify_sovereignty(task_id),
            "stage_answers": stage_answers,
            "check_implementation_completeness": check_implementation_completeness,
        }

    def transition(self, task_id: str, to_state: str, actor: str, reason: str):
        """INTERNAL USE ONLY: Validates and applies a deterministic state transition according to the canonical DAG.

        DEPRECATION NOTICE: This method is strictly internal and functional ONLY for deterministic transitions
        that do not require human input or approval. For any transition requiring human questions or approval
        (e.g., AWAITING_APPROVAL -> APPROVED, DRAFT_PLAN -> MULTI_AGENT_REVIEW), callers MUST use
        TransitionCoordinator.coordinate_transition() to interactively capture and persist signed human decisions.
        Any attempt to transition a human-gated edge via this method will be rejected with PersistenceInvariantViolation.

        Known-state and adjacency legality are delegated to self._state_machine (a pure domain component,
        issue-524 post-round-2-review correction); state retrieval, the guarded write, and
        transition-history persistence all go through self._persistence.apply_transition() —
        this method itself owns only coordination (calling the state machine, then the policy
        engine, then persistence), never validation logic or SQL."""
        self._state_machine.validate_known_state(to_state)

        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")

        # Authoritative state read, immediately before the guarded write — closes the race
        # window between the adjacency/policy checks and the write (a concurrent writer
        # changing the row after this point is caught by apply_transition()'s guard rather
        # than silently overwritten).
        current_state = self._read_current_state_for_update(task_id)
        if current_state is None:
            raise ValueError(f"Task not found: {task_id}")

        self._state_machine.validate_adjacency(task_id, current_state, to_state)

        # Unauthorized direct transition to DONE from any state other than RETROSPECTIVE
        # is a force-close attempt that requires explicit human authorization.
        if to_state == "DONE" and current_state != "RETROSPECTIVE":
            raise PersistenceInvariantViolation(
                f"Direct transition to DONE from '{current_state}' is denied: "
                "force-close requires explicit human authorization."
            )

        # --- Unified gate policy: deterministic checks from authoritative YAML registry ---
        if not hasattr(self, "_transition_registry"):
            self._transition_registry = TransitionRegistry.load_default()
        template = self._transition_registry.get_template(current_state, to_state)
        if template:
            ctx = self._build_transition_policy_ctx(task_id, task, current_state, to_state)
            for check_id in template.deterministic_checks:
                try:
                    _policy.evaluate_check(check_id, ctx)
                except _policy.PolicyViolation as e:
                    raise PersistenceInvariantViolation(str(e)) from e

        applied = self._persistence.apply_transition(task_id, current_state, to_state, actor, reason)
        if not applied:
            raise ConcurrentModificationError(
                f"Task '{task_id}' state changed concurrently (expected '{current_state}'). Retry."
            )

    def coordinate_transition(
        self,
        task_id: str,
        to_state: str,
        actor: str,
        reason: str,
        interactive: bool = False,
        provided_answers: Optional[Dict[str, str]] = None,
        approval_decision: Optional[str] = None,
        skip_decision: Optional[Tuple[str, str]] = None,
        skip_review: bool = False,
        skip_reason: Optional[str] = None,
        force_close: bool = False,
        human_authorization: Optional[str] = None,
    ) -> TransitionRecord:
        """Public orchestration entry point: coordinates transition via TransitionCoordinator."""
        if not hasattr(self, "_transition_registry"):
            self._transition_registry = TransitionRegistry.load_default()
        coord = TransitionCoordinator(control_plane=self, registry=self._transition_registry)
        return coord.coordinate_transition(
            task_id=task_id,
            to_state=to_state,
            actor=actor,
            reason=reason,
            interactive=interactive,
            provided_answers=provided_answers,
            approval_decision=approval_decision,
            skip_decision=skip_decision,
            skip_review=skip_review,
            skip_reason=skip_reason,
            force_close=force_close,
            human_authorization=human_authorization,
        )

    def commit_authorized_transition(self, commit_request: TransitionCommitRequest) -> TransitionRecord:
        """Internal atomic commit gate: passes normalized TransitionCommitRequest to PersistencePort.
        PersistencePort re-validates persistable invariants in SQLite transaction and atomically commits."""
        return self._persistence.apply_transition_with_receipts(commit_request)

    def lock_verifiers(self, task_id: str, file_paths: List[Path]):
        """Calculates and locks baseline SHA256 hashes of verifier files. File-existence
        checks are against arbitrary caller-supplied paths (not repo-owned files), so they
        use pathlib directly rather than FilesystemPort — that port's contract covers
        repo-relative side-effect writes (e.g. map-debt.md), a different concern."""
        for fp in file_paths:
            p = Path(fp).resolve()
            if not p.exists():
                raise FileNotFoundError(f"Verifier file to lock does not exist: {p}")
            file_sha = self._crypto.sha256_file(p)
            self._persistence.insert_locked_verifier(task_id, str(p), file_sha)

    def verify_sovereignty(self, task_id: str) -> bool:
        """Verifies that locked baseline verifiers have not been modified."""
        rows = self._persistence.get_locked_verifiers(task_id)
        for r in rows:
            p = Path(r["file_path"])
            if not p.exists():
                raise VerifierSovereigntyViolation(f"Verifier file missing: {p}")
            curr_sha = self._crypto.sha256_file(p)
            if curr_sha != r["expected_sha256"]:
                raise VerifierSovereigntyViolation(
                    f"Verifier sovereignty violated! {p} has been mutated. Expected {r['expected_sha256']}, got {curr_sha}"
                )
        return True

    def record_critic_review(self, task_id: str, iteration: int, model: str, verdict: str, findings: str):
        """Records a clean-context peer critic review iteration and verdict."""
        if verdict == "REQUEST_CHANGES":
            verdict = "REVISE"
        if verdict not in ("PASS", "REVISE", "REJECT"):
            raise ValueError(f"Invalid verdict: {verdict}")
        self._persistence.insert_critic_review(task_id, iteration, model, verdict, findings)

    def record_verification_receipt(self, task_id: str, gate_name: str, command_executed: str, exit_code: int) -> str:
        """Records a deterministic exit receipt and returns an immutable receipt token."""
        raw = f"{task_id}:{gate_name}:{command_executed}:{exit_code}:{self._clock.current_time()}"
        h = self._crypto.sha256_hex(raw)[:12]
        token = f"EVO-INTEGRITY-{task_id}-{h}"
        self._persistence.insert_verification_receipt(task_id, gate_name, command_executed, exit_code, token)
        return token

    def save_retrospective(self, task_id: str, entry: Dict[str, Any], follow_ups: List[Dict[str, Any]]) -> None:
        """Creates or replaces the task's single retrospective record."""
        if entry.get("decision") not in ("opt_in", "skip"):
            raise ValueError("Retrospective decision must be 'opt_in' or 'skip'.")
        if entry.get("completion_mode") not in ("draft", "completed", "skipped"):
            raise ValueError("Retrospective completion_mode must be draft, completed, or skipped.")
        if entry.get("actor") not in ("agent", "human"):
            raise ValueError("Retrospective actor must be agent or human.")
        self._persistence.save_retrospective(task_id, entry, follow_ups)

    def record_plan_mode_entry(self, task_id: str, actor: str) -> str:
        """Records proof that native Plan Mode was entered, satisfying the DRAFT_PLAN gate."""
        return self.record_verification_receipt(
            task_id, gate_name="plan_mode_entry", command_executed=f"plan-mode-entered:{actor}", exit_code=0
        )

    def record_socratic_intake_complete(self, task_id: str, summary: str) -> str:
        """Records proof that Socratic Defaulting intake completed, satisfying the DRAFT_PLAN gate."""
        return self.record_verification_receipt(
            task_id, gate_name="socratic_intake_complete", command_executed=f"socratic-intake:{summary}", exit_code=0
        )

    def record_human_approval(self, task_id: str, approver: str) -> str:
        """Records the human approval receipt required for APPROVED -> IN_WORKTREE (never skippable)."""
        return self.record_verification_receipt(
            task_id, gate_name="human_approval", command_executed=f"approved-by:{approver}", exit_code=0
        )

    def record_review_skip(self, task_id: str, phase: str, actor: str, reason: str) -> str:
        """Records an explicit, auditable decision to skip a user-discretionary review phase
        (e.g. multi_agent_review, multi_agent_code_review) — makes the skip visible, never silent."""
        return self.record_verification_receipt(
            task_id, gate_name=f"{phase}_skipped", command_executed=f"user-skip:{actor}:{reason}", exit_code=0
        )

    def _read_current_state_for_update(self, task_id: str) -> Optional[str]:
        """Reads the task's current state immediately before the guarded write — the value
        used as the WHERE predicate closing the race window. Delegates to self._persistence;
        kept as a named method (rather than inlined) because transition() and its regression
        test (test_transition_race_condition_guarded_by_state_predicate) rely on being able to
        substitute a stale read here to simulate a concurrent writer."""
        return self._persistence.read_current_state(task_id)

    def get_verification_receipts(self, task_id: str) -> List[Dict[str, Any]]:
        """Retrieves all verification receipts stamped for a given task."""
        return self._persistence.get_verification_receipts(task_id)

    def update_worktree(self, task_id: str, worktree_path: str, worktree_branch: str, worktree_state: str):
        """Updates worktree path, branch, and status using the strict 6-state vocabulary."""
        if worktree_state not in WORKTREE_STATES:
            raise ValueError(f"Invalid worktree state '{worktree_state}'. Must be one of {WORKTREE_STATES}")

        # Unified gate policy: worktree_push is a controlled operation, not a lifecycle
        # transition — evaluated via the same policy engine as transition() (issue-524 Step 4).
        if worktree_state == "pushed_to_origin":
            task_state = self._persistence.read_current_state(task_id)
            if task_state is None:
                raise ValueError(f"Task not found: {task_id}")
            op_ctx = {"task_id": task_id, "task_state": task_state}
            try:
                _policy.evaluate_operation(op_ctx, "worktree_push")
            except _policy.PolicyViolation as e:
                raise PersistenceInvariantViolation(str(e)) from e

        self._persistence.update_worktree_fields(task_id, worktree_path, worktree_branch, worktree_state)

    def verify_commit(self, branch: str, staged_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Verifies whether git commit is authorized on `branch` given `staged_files`.
        
        Returns:
            Dict containing {"status": "ALLOWED"|"BLOCKED", "task_id": ..., "state": ..., "message": ...}
        Raises:
            PersistenceInvariantViolation if blocked and callers don't catch.
        """
        # If main/master or untracked branch, allow
        if branch in ("main", "master", ""):
            return {"status": "ALLOWED", "branch": branch, "message": "Non-task branch bypass"}

        task = self._persistence.get_task_by_worktree_branch(branch)
        if task is None:
            return {"status": "ALLOWED", "branch": branch, "task_id": None, "message": "Untracked branch (ungated)"}

        task_id = task["task_id"]
        task_state = task["state"]

        op_ctx = {
            "task_id": task_id,
            "task_state": task_state,
            "staged_files": staged_files or [],
            "validate_transition_history": lambda: self._persistence.validate_task_pipeline_history(task_id, task_state),
        }

        try:
            _policy.evaluate_operation(op_ctx, "commit")
        except _policy.PolicyViolation as e:
            raise PersistenceInvariantViolation(str(e)) from e

        return {
            "status": "ALLOWED",
            "task_id": task_id,
            "state": task_state,
            "branch": branch,
            "message": "Commit authorized"
        }

    def log_asymmetric_persistence(self, task_id: str, destination: str, status: str, details: str):
        """Logs asymmetric Layer 2 persistence entries into the SQLite audit table."""
        self._persistence.insert_asymmetric_persistence(task_id, destination, status, details)

    def verify_phase_capability(self, task_id: str, action_identity: str) -> PhaseCapability:
        """Verifies that an action capability is authorized for the task's current phase occupancy.

        Algorithm:
        1. read task current state;
        2. read the latest transition whose to_state equals that current state;
        3. verify that transition is the current source-occupancy row (most recent transition for task);
        4. resolve its exact (from_state, to_state) template;
        5. authorize only capabilities_released by that exact template;
        6. fail closed if task state, transition history, or registry entry disagree.
        """
        if not hasattr(self, "_transition_registry"):
            self._transition_registry = TransitionRegistry.load_default()

        # Fail-closed check: action identity must be known/registered in registry
        releasing_edges = self._transition_registry.get_edges_releasing_capability(action_identity)
        if not releasing_edges:
            raise PhaseCapabilityDenied(f"Unregistered action identity: '{action_identity}'")

        # Step 1: read task current state
        current_state = self._persistence.read_current_state(task_id)
        if current_state is None:
            raise PhaseCapabilityDenied(f"Task '{task_id}' not found in control plane.")

        # Step 2: read the latest transition whose to_state equals that current state
        occupancy_trans = self._persistence.get_last_transition(task_id, to_state=current_state)
        if not occupancy_trans:
            raise PhaseCapabilityDenied(
                f"No transition found leading into current state '{current_state}' for task '{task_id}'."
            )

        # Step 3: verify that transition is the current source-occupancy row (latest overall transition)
        latest_trans = self._persistence.get_last_transition(task_id)
        if not latest_trans or latest_trans.transition_id != occupancy_trans.transition_id:
            raise PhaseCapabilityDenied(
                f"State tamper detected: latest transition id '{getattr(latest_trans, 'transition_id', None)}' "
                f"does not match current occupancy transition id '{occupancy_trans.transition_id}'."
            )

        # Step 4: resolve its exact (from_state, to_state) template
        template = self._transition_registry.get_template(occupancy_trans.from_state, occupancy_trans.to_state)
        if not template:
            if occupancy_trans.from_state == "NONE":
                raise PhaseCapabilityDenied(
                    "Task has not entered any registered phase yet — no capabilities available."
                )
            raise PhaseCapabilityDenied(
                f"No registry template found for inbound edge "
                f"({occupancy_trans.from_state} -> {occupancy_trans.to_state})."
            )

        # Step 5: authorize only capabilities_released by that exact template
        if action_identity not in template.capabilities_released:
            raise PhaseCapabilityDenied(
                f"Action '{action_identity}' not authorized in state '{current_state}' "
                f"(entered via {occupancy_trans.from_state} -> {occupancy_trans.to_state}). "
                f"Released capabilities: {template.capabilities_released}."
            )

        return PhaseCapability(
            task_id=task_id,
            action_identity=action_identity,
            current_state=current_state,
            releasing_edge=(occupancy_trans.from_state, occupancy_trans.to_state),
            transition_id=occupancy_trans.transition_id,
        )

    def record_decision(
        self,
        task_id: str,
        source_occupancy_transition_id: int,
        from_state: str,
        to_state: str,
        question_id: str,
        answer: str,
        decision_type: str = "ANSWER",
        actor: str = "interviewer",
    ) -> int:
        """Records an occupancy-bound decision via PersistencePort."""
        decision = TransitionDecision(
            task_id=task_id,
            source_occupancy_transition_id=source_occupancy_transition_id,
            from_state=from_state,
            to_state=to_state,
            question_id=question_id,
            answer=answer,
            decision_type=decision_type,
            actor=actor,
            recorded_at=self._clock.current_time(),
        )
        return self._persistence.record_decision(decision)


def _build_parser() -> argparse.ArgumentParser:

    """Constructs and returns CLI argument parser."""
    parser = argparse.ArgumentParser(description="SQLite Control Plane CLI for Agent Lifecycle")
    sub = parser.add_subparsers(dest="subcommand")

    p_init = sub.add_parser("init")
    p_init.add_argument("--task-id", required=True)
    p_init.add_argument("--title", required=True)
    p_init.add_argument("--runtime", default="cli")
    p_init.add_argument("--spec-path", default=None)
    p_init.add_argument("--model-tier", choices=["low", "medium", "high"], default=None)
    p_init.add_argument("--model-id", default=None)
    p_init.add_argument("--task-type", choices=["GENERAL", "EVOLUTION"], default="GENERAL")

    p_rec = sub.add_parser("recommend-model")
    p_rec.add_argument("--runtime", required=True)
    p_rec.add_argument("--tier", choices=["low", "medium", "high"], default="low")

    # Primary transition command: coordinate-transition
    p_ct = sub.add_parser("coordinate-transition")
    p_ct.add_argument("--task-id", required=True)
    p_ct.add_argument("--to", required=True)
    p_ct.add_argument("--actor", default="controller")
    p_ct.add_argument("--reason", default="State transition")
    p_ct.add_argument("--interactive", action="store_true", default=False)
    p_ct.add_argument("--answers", default=None, help="JSON dict of question answers")
    p_ct.add_argument("--approval", choices=["APPROVAL", "REJECTION"], default=None)
    p_ct.add_argument("--skip-review", action="store_true", default=False)
    p_ct.add_argument("--skip-reason", default=None)

    # Compatibility alias: transition routes directly through TransitionCoordinator
    p_tr = sub.add_parser("transition")
    p_tr.add_argument("--task-id", required=True)
    p_tr.add_argument("--to", required=True)
    p_tr.add_argument("--actor", default="controller")
    p_tr.add_argument("--reason", default="State transition")
    p_tr.add_argument("--interactive", action="store_true", default=False)
    p_tr.add_argument("--answers", default=None, help="JSON dict of question answers")
    p_tr.add_argument("--approval", choices=["APPROVAL", "REJECTION"], default=None)
    p_tr.add_argument("--skip-review", action="store_true", default=False)
    p_tr.add_argument("--skip-reason", default=None)

    p_lock = sub.add_parser("lock-verifiers")
    p_lock.add_argument("--task-id", required=True)
    p_lock.add_argument("--paths", required=True, help="Comma-separated file paths")

    p_vsov = sub.add_parser("verify-sovereignty")
    p_vsov.add_argument("--task-id", required=True)

    p_rc = sub.add_parser("record-receipt")
    p_rc.add_argument("--task-id", required=True)
    p_rc.add_argument("--gate", required=True)
    p_rc.add_argument("--cmd", required=True)
    p_rc.add_argument("--exit-code", type=int, required=True)

    p_wt = sub.add_parser("update-worktree")
    p_wt.add_argument("--task-id", required=True)
    p_wt.add_argument("--path", required=True)
    p_wt.add_argument("--branch", required=True)
    p_wt.add_argument("--state", required=True)

    p_st = sub.add_parser("status")
    p_st.add_argument("--task-id", required=True)

    p_tg = sub.add_parser("transition-guidance")
    p_tg.add_argument("--task-id", required=True)
    p_tg.add_argument("--to", default=None, help="Optional requested destination state")

    p_lap = sub.add_parser("log-prior-art")
    p_lap.add_argument("--task-id", required=True)
    p_lap.add_argument("--summary", required=True, help="Summary of prior art scan findings")
    p_lap.add_argument("--repeat-yes-entries", default="", help="Comma-separated Repeat:YES map-debt entries found")

    p_pme = sub.add_parser("record-plan-mode-entry")
    p_pme.add_argument("--task-id", required=True)
    p_pme.add_argument("--actor", required=True)

    p_sic = sub.add_parser("record-socratic-intake")
    p_sic.add_argument("--task-id", required=True)
    p_sic.add_argument("--summary", required=True)

    p_ha = sub.add_parser("record-human-approval")
    p_ha.add_argument("--task-id", required=True)
    p_ha.add_argument("--approver", required=True)

    p_rs = sub.add_parser("record-review-skip")
    p_rs.add_argument("--task-id", required=True)
    p_rs.add_argument("--phase", required=True, help="e.g. multi_agent_review, multi_agent_code_review")
    p_rs.add_argument("--actor", required=True)
    p_rs.add_argument("--reason", required=True)

    p_cr = sub.add_parser("record-critic-review")
    p_cr.add_argument("--task-id", required=True)
    p_cr.add_argument("--iteration", type=int, required=True)
    p_cr.add_argument("--model", required=True)
    p_cr.add_argument("--verdict", choices=["PASS", "REVISE", "REJECT", "REQUEST_CHANGES"], required=True)
    p_cr.add_argument("--findings", required=True)

    # Slice 4: Action wrapper verification & recovery subcommands
    p_viq = sub.add_parser("verify-interview-question")
    p_viq.add_argument("--task-id", required=True)

    p_vpw = sub.add_parser("verify-plan-write")
    p_vpw.add_argument("--task-id", required=True)

    p_vex = sub.add_parser("verify-exit-verification")
    p_vex.add_argument("--task-id", required=True)

    p_rra = sub.add_parser("record-recovery-approval")
    p_rra.add_argument("--task-id", required=True)
    p_rra.add_argument("--from-state", required=True)
    p_rra.add_argument("--to-state", required=True)
    p_rra.add_argument("--source-occupancy-id", type=int, required=True)
    p_rra.add_argument("--approver", required=True)
    p_rra.add_argument("--decision", default="APPROVAL")
    p_rra.add_argument("--reason", required=True)

    p_vc = sub.add_parser("verify-commit")
    p_vc.add_argument("--branch", required=True, help="Git branch to verify commit authorization for")
    p_vc.add_argument("--staged-files", nargs="*", default=[], help="List of staged files")

    return parser


def _dispatch_command(cp: ControlPlane, args: argparse.Namespace):
    """Executes the dispatched CLI command."""
    if args.subcommand == "init":
        cp.create_task(args.task_id, args.title, args.runtime, args.spec_path, args.model_tier, args.model_id, args.task_type)
        print(f"Task {args.task_id} initialized in INTAKE (type={args.task_type}).")
    elif args.subcommand == "recommend-model":
        print(json.dumps(cp.resolve_recommended_model(args.runtime, args.tier), indent=2))
    elif args.subcommand in ("coordinate-transition", "transition"):
        answers_dict = json.loads(args.answers) if getattr(args, "answers", None) else None
        rec = cp.coordinate_transition(
            task_id=args.task_id,
            to_state=args.to,
            actor=args.actor,
            reason=args.reason,
            interactive=getattr(args, "interactive", False),
            provided_answers=answers_dict,
            approval_decision=getattr(args, "approval", None),
            skip_review=getattr(args, "skip_review", False),
            skip_reason=getattr(args, "skip_reason", None),
        )
        print(f"Transitioned task {args.task_id} to {args.to} (transition_id={rec.transition_id}).")
    elif args.subcommand == "record-critic-review":
        cp.record_critic_review(args.task_id, args.iteration, args.model, args.verdict, args.findings)
        canonical_verdict = "REVISE" if args.verdict == "REQUEST_CHANGES" else args.verdict
        print(f"Critic review recorded for task {args.task_id} (verdict={canonical_verdict}).")
    elif args.subcommand == "lock-verifiers":
        paths = [Path(p.strip()) for p in args.paths.split(",")]
        cp.lock_verifiers(args.task_id, paths)
        print(f"Locked {len(paths)} verifiers for {args.task_id}.")
    elif args.subcommand == "verify-sovereignty":
        cp.verify_sovereignty(args.task_id)
        print(f"Verifier sovereignty verified for {args.task_id}.")
    elif args.subcommand == "record-receipt":
        token = cp.record_verification_receipt(args.task_id, args.gate, args.cmd, args.exit_code)
        print(f"Receipt stamped: {token}")
    elif args.subcommand == "update-worktree":
        cp.update_worktree(args.task_id, args.path, args.branch, args.state)
        print(f"Task {args.task_id} worktree state set to {args.state}.")
    elif args.subcommand == "status":
        print(json.dumps(cp.get_task(args.task_id), indent=2, default=str))
    elif args.subcommand == "transition-guidance":
        print(json.dumps(cp.get_transition_guidance(args.task_id, args.to), indent=2))
    elif args.subcommand == "log-prior-art":
        repeat_entries = args.repeat_yes_entries or "none"
        details = f"prior_art_scan: summary={args.summary}; repeat_yes_entries={repeat_entries}"
        cp.log_asymmetric_persistence(
            task_id=args.task_id,
            destination="references/map-debt.md",
            status="OBSERVED",
            details=details
        )
        print(f"Prior art scan logged for task {args.task_id}.")
    elif args.subcommand in (
        "record-plan-mode-entry", "record-socratic-intake", "record-human-approval", "record-review-skip"
    ):
        _dispatch_gate_record_command(cp, args)
    elif args.subcommand == "verify-interview-question":
        cap = cp.verify_phase_capability(args.task_id, "interview_question")
        print(f"Verified interview_question capability for {args.task_id} in {cap.current_state} (transition {cap.transition_id}).")
    elif args.subcommand == "verify-plan-write":
        cap = cp.verify_phase_capability(args.task_id, "plan_write")
        print(f"Verified plan_write capability for {args.task_id} in {cap.current_state} (transition {cap.transition_id}).")
    elif args.subcommand == "verify-exit-verification":
        cap = cp.verify_phase_capability(args.task_id, "exit_verification")
        print(f"Verified exit_verification capability for {args.task_id} in {cap.current_state} (transition {cap.transition_id}).")
    elif args.subcommand == "record-recovery-approval":
        token = cp._persistence.record_recovery_approval(
            task_id=args.task_id,
            expected_source_state=args.from_state,
            destination_state=args.to_state,
            source_occupancy_transition_id=args.source_occupancy_id,
            approver=args.approver,
            decision=args.decision,
            reason=args.reason,
        )
        print(f"Recovery approval recorded: {token}")
    elif args.subcommand == "verify-commit":
        res = cp.verify_commit(args.branch, args.staged_files)
        print(f"Commit check: {res['status']} ({res['message']})")


def _dispatch_gate_record_command(cp: ControlPlane, args: argparse.Namespace):
    """Executes the gate-registry receipt-recording CLI subcommands."""
    if args.subcommand == "record-plan-mode-entry":
        token = cp.record_plan_mode_entry(args.task_id, args.actor)
        print(f"Plan Mode entry recorded: {token}")
    elif args.subcommand == "record-socratic-intake":
        token = cp.record_socratic_intake_complete(args.task_id, args.summary)
        print(f"Socratic intake completion recorded: {token}")
    elif args.subcommand == "record-human-approval":
        token = cp.record_human_approval(args.task_id, args.approver)
        print(f"Human approval recorded: {token}")
    elif args.subcommand == "record-review-skip":
        token = cp.record_review_skip(args.task_id, args.phase, args.actor, args.reason)
        print(f"Review skip recorded: {token}")


def main():
    """Main CLI entry point for SQLite Control Plane."""
    parser = _build_parser()
    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
        sys.exit(1)

    cp = ControlPlane()
    try:
        _dispatch_command(cp, args)
    except Exception as e:
        print(f"{'CONTROL PLANE ERROR' if isinstance(e, (InvalidStateTransition, VerifierSovereigntyViolation, PersistenceInvariantViolation, ConcurrentModificationError)) else 'ERROR'}: {e}", file=sys.stderr)
        sys.exit(_map_exception_to_exit_code(e))


def _map_exception_to_exit_code(e: Exception) -> int:
    """Maps a caught exception to its CLI exit code. ConcurrentModificationError gets its own
    code (3) since it's the one error that's explicitly retryable — indistinguishable from a
    generic crash (exit 1) would prevent callers from retrying only on contention."""
    if isinstance(e, ConcurrentModificationError):
        return 3
    if isinstance(e, (InvalidStateTransition, VerifierSovereigntyViolation, PersistenceInvariantViolation, PhaseCapabilityDenied, TransitionCoordinatorError)):
        return 2
    return 1


if __name__ == "__main__":
    main()
