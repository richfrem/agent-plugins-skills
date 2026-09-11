"""
control_plane/ports.py — Port Interfaces for the ControlPlane Decomposition (issue-524)
=========================================================================================

Purpose:
    Declares the abstract seams that domain and policy code depend on instead of concrete
    infrastructure (sqlite3, subprocess, hashlib, filesystem, model-catalog JSON storage).
    Dependency-direction invariant (docs/plans/issue-524-spec.md, DoD item 5): domain/policy
    modules import ONLY from this file (and stdlib `abc`/`typing`) — never sqlite3, subprocess,
    hashlib, time-based I/O, or concrete filesystem/model-catalog storage. Adapters (added in
    later steps) implement these interfaces against real infrastructure; the application layer
    composes policy with adapters via these ports.

Layer:
    OS Kernel / Execution Control Plane Substrate — Ports (hexagonal boundary)

Key Input Dependencies:
    None — pure interface definitions, no I/O.

Key Functions:
    - ClockPort — current_time() -> float, strftime(fmt) -> str
    - FilesystemPort — append_text(), read_text(), exists()
    - CryptoPort — sha256_file(), sha256_hex()
    - ModelCatalogPort — load_catalog(), load_cheapest()
    - PersistencePort — task/transition/receipt/review/log/baseline CRUD, all keyed by task_id.
      Fully implemented by control_plane.adapters.SqlitePersistenceAdapter (issue-524 Step 5
      revision) — every method here has a concrete SQLite-backed implementation; ControlPlane
      composes this port rather than issuing SQL itself.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class PersistenceInvariantViolation(Exception):
    """Raised when evolution integrity, database trigger enforcement, or asymmetric persistence invariants are violated."""
    pass


@dataclass(frozen=True)
class TransitionRecord:
    transition_id: int
    task_id: str
    from_state: str
    to_state: str
    actor: str
    reason: Optional[str]
    timestamp: str


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


@dataclass(frozen=True)
class PhaseCapability:
    task_id: str
    action_identity: str
    current_state: str
    releasing_edge: Tuple[str, str]
    transition_id: int


class ClockPort(ABC):

    """Abstracts wall-clock time so domain/policy code never imports `time` directly."""

    @abstractmethod
    def current_time(self) -> float:
        """Returns the current time as a float (seconds since epoch, or equivalent)."""
        raise NotImplementedError

    @abstractmethod
    def strftime(self, fmt: str) -> str:
        """Returns the current time formatted per `fmt` (strftime-style), for human-readable
        timestamps in generated text (e.g. map-debt entries)."""
        raise NotImplementedError


class FilesystemPort(ABC):
    """Abstracts filesystem side-effects (e.g. appending to references/map-debt.md)."""

    @abstractmethod
    def append_text(self, path: Path, content: str) -> None:
        """Appends text content to the file at `path`, creating it if absent is NOT implied —
        callers must check `exists()` first if creation-on-missing is not desired."""
        raise NotImplementedError

    @abstractmethod
    def read_text(self, path: Path) -> str:
        """Reads and returns the full text content of the file at `path`."""
        raise NotImplementedError

    @abstractmethod
    def exists(self, path: Path) -> bool:
        """Returns whether a file exists at `path`."""
        raise NotImplementedError


class CryptoPort(ABC):
    """Abstracts cryptographic hashing (verifier sovereignty, receipt tokens)."""

    @abstractmethod
    def sha256_file(self, path: Path) -> str:
        """Returns the SHA256 hex digest of the file at `path`."""
        raise NotImplementedError

    @abstractmethod
    def sha256_hex(self, raw: str) -> str:
        """Returns the SHA256 hex digest of the given string."""
        raise NotImplementedError


class ModelCatalogPort(ABC):
    """Abstracts model-catalog resolution — both the JSON file reads AND the tier-selection/
    strategy logic (issue-524, post-round-2-review correction: the original version only
    declared the file-read methods, leaving resolve_recommended_model()'s tool-alias
    resolution, tier strategy, and fallback logic still embedded in ControlPlane — an
    incomplete separation of the model-catalog responsibility)."""

    @abstractmethod
    def resolve_recommended_model(self, runtime_tool: str, tier: str = "low") -> Dict[str, str]:
        """Resolves a full model recommendation for `runtime_tool`/`tier`: tool-alias
        resolution, catalog file lookup, tier-strategy selection, and fallback — the complete
        behavior formerly split between ControlPlane.resolve_recommended_model() and this
        port's file-read-only methods. Returns {"runtime_tool", "tier", "model_id"}."""
        raise NotImplementedError

    @abstractmethod
    def load_catalog(self, catalog_path: Path) -> Optional[Dict[str, Any]]:
        """Loads and returns a parsed model-catalog JSON file, or None if unavailable/unparsable."""
        raise NotImplementedError

    @abstractmethod
    def load_cheapest(self, cheapest_path: Path, tool_key: str) -> Optional[str]:
        """Loads cheapest_models.json and returns the cheapest model id for `tool_key`, or None."""
        raise NotImplementedError


class PersistencePort(ABC):
    """Abstracts all durable task-lifecycle storage (today: SQLite). Domain and policy code
    depend only on this interface, never on sqlite3 directly."""

    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a task dictionary by task_id, or None if not found."""
        raise NotImplementedError

    @abstractmethod
    def insert_premium_consent(
        self, task_id: str, stage: str, round_id: str, model_id: str, actor: str
    ) -> int:
        """Persist human consent for one exact task/stage/round/model scope."""
        raise NotImplementedError

    @abstractmethod
    def has_premium_consent(self, task_id: str, stage: str, round_id: str, model_id: str) -> bool:
        """Return whether an exact task/stage/round/model consent scope exists."""
        raise NotImplementedError

    @abstractmethod
    def insert_source_assisted_answer_candidate(
        self,
        task_id: str,
        stage: str,
        round_id: str,
        question_id: str,
        answer: str,
        source_path: str,
        source_authorized: bool,
    ) -> int:
        """Persist one source-derived answer candidate and its provenance."""
        raise NotImplementedError

    @abstractmethod
    def confirm_source_assisted_answer_candidate(self, candidate_id: int, actor: str) -> bool:
        """Mark one pending source-derived answer candidate as human-confirmed."""
        raise NotImplementedError

    @abstractmethod
    def has_unconfirmed_source_assisted_answer_candidates(
        self, task_id: str, stage: str, round_id: Optional[str]
    ) -> bool:
        """Return whether the requested scope still has unconfirmed candidates.

        ``round_id=None`` checks every round in the stage, which is used by the
        authoritative lifecycle exit gate.
        """
        raise NotImplementedError

    def create_delegation_plan(self, task_id: str, contract: Dict[str, Any]) -> int:
        """Persist a governed delegation contract and return its identifier."""
        raise NotImplementedError

    def get_delegation_plan(self, contract_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a delegation contract by identifier."""
        raise NotImplementedError

    def approve_delegation_plan(self, contract_id: int, actor: str) -> None:
        """Record the human approval for a contract that requires it."""
        raise NotImplementedError

    def count_delegation_receipts(self, contract_id: int) -> int:
        """Count execution attempts against a delegation contract."""
        raise NotImplementedError

    def insert_delegation_receipt(self, contract_id: int, receipt: Dict[str, Any]) -> int:
        """Persist one execution receipt."""
        raise NotImplementedError

    def insert_delegation_verifier_receipt(self, contract_id: int, command: str, exit_code: int) -> None:
        """Persist the verifier receipt required before accepting a result."""
        raise NotImplementedError

    def mark_delegation_status(self, contract_id: int, status: str) -> None:
        """Update the governed contract status."""
        raise NotImplementedError

    def has_delegation_verifier_receipt(self, contract_id: int) -> bool:
        """Return whether a passing verifier receipt exists."""
        raise NotImplementedError

    @abstractmethod
    def insert_task(self, task_id: str, title: str, task_type: str, runtime_tool: str,
                     spec_path: Optional[str], model_tier: Optional[str], model_id: Optional[str]) -> None:
        """Inserts a new task row in INTAKE state and its creation transition, atomically."""
        raise NotImplementedError

    @abstractmethod
    def read_current_state(self, task_id: str) -> Optional[str]:
        """Reads a task's current state value directly, for use immediately before a guarded write."""
        raise NotImplementedError

    @abstractmethod
    def apply_transition(self, task_id: str, from_state: str, to_state: str, actor: str, reason: str) -> bool:
        """Atomically updates task state (guarded by expected from_state) and records the
        transition row. Returns False if the guard predicate did not match (concurrent write)."""
        raise NotImplementedError

    @abstractmethod
    def count_asymmetric_persistence(self, task_id: str, details_like: Optional[str] = None,
                                      destination_like_any: Optional[List[str]] = None) -> int:
        """Counts asymmetric_persistence_log rows for task_id. `details_like` filters on the
        `details` column (single LIKE pattern); `destination_like_any` filters on the
        `destination` column (OR'd across multiple LIKE patterns). At most one of the two
        should be given; neither given returns the unfiltered count for task_id."""
        raise NotImplementedError

    @abstractmethod
    def count_receipts(self, task_id: str, gate_name: str, exit_code: Optional[int] = None) -> int:
        """Counts verification_receipts rows for task_id matching gate_name (and exit_code if given)."""
        raise NotImplementedError

    @abstractmethod
    def count_locked_verifiers(self, task_id: str) -> int:
        """Counts locked_verifier_baselines rows for task_id."""
        raise NotImplementedError

    @abstractmethod
    def get_locked_verifiers(self, task_id: str) -> List[Dict[str, Any]]:
        """Returns locked_verifier_baselines rows (file_path, expected_sha256) for task_id."""
        raise NotImplementedError

    @abstractmethod
    def has_passing_critic_review(self, task_id: str) -> bool:
        """Returns whether any critic_reviews row for task_id has verdict='PASS'."""
        raise NotImplementedError

    @abstractmethod
    def has_receipt(self, task_id: str, gate_name: str) -> bool:
        """Returns whether any verification_receipts row exists for task_id with the given gate_name."""
        raise NotImplementedError

    @abstractmethod
    def insert_verification_receipt(self, task_id: str, gate_name: str, command_executed: str,
                                     exit_code: int, receipt_token: str) -> None:
        """Inserts a verification_receipts row."""
        raise NotImplementedError

    @abstractmethod
    def insert_critic_review(self, task_id: str, iteration: int, model: str, verdict: str, findings: str) -> None:
        """Inserts a critic_reviews row."""
        raise NotImplementedError

    @abstractmethod
    def insert_locked_verifier(self, task_id: str, file_path: str, expected_sha256: str) -> None:
        """Inserts a locked_verifier_baselines row."""
        raise NotImplementedError

    @abstractmethod
    def insert_asymmetric_persistence(self, task_id: str, destination: str, status: str, details: str) -> None:
        """Inserts an asymmetric_persistence_log row."""
        raise NotImplementedError

    @abstractmethod
    def get_verification_receipts(self, task_id: str) -> List[Dict[str, Any]]:
        """Returns all verification_receipts rows for task_id."""
        raise NotImplementedError

    @abstractmethod
    def save_retrospective(self, task_id: str, entry: Dict[str, Any], follow_ups: List[Dict[str, Any]]) -> None:
        """Creates or replaces the single task retrospective and its follow-up rows."""
        raise NotImplementedError

    @abstractmethod
    def has_complete_retrospective(self, task_id: str) -> bool:
        """Returns whether the task has a complete or explicitly skipped retrospective."""
        raise NotImplementedError

    @abstractmethod
    def update_worktree_fields(self, task_id: str, worktree_path: str, worktree_branch: str, worktree_state: str) -> None:
        """Updates a task's worktree_path/worktree_branch/worktree_state columns."""
        raise NotImplementedError

    @abstractmethod
    def ensure_schema(self) -> None:
        """Ensures the underlying storage schema exists and is at the current version, self-healing if needed."""
        raise NotImplementedError

    @abstractmethod
    def get_last_transition(
        self,
        task_id: str,
        from_state: Optional[str] = None,
        to_state: Optional[str] = None,
    ) -> Optional[TransitionRecord]:
        """Returns the latest TransitionRecord for task_id matching optional from_state/to_state filters."""
        raise NotImplementedError

    @abstractmethod
    def apply_transition_with_receipts(
        self,
        request: TransitionCommitRequest,
    ) -> TransitionRecord:
        """Atomically revalidates authoritative persistable facts in SQLite and applies transition."""
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
        """Issues and persists an unconsumed recovery approval decision record bound to the current source occupancy ID."""
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
        """Atomically executes recovery transition using a verified, unconsumed approval record."""
        raise NotImplementedError

    @abstractmethod
    def record_decision(self, decision: TransitionDecision) -> int:
        """Records an occupancy-bound TransitionDecision. Rejects duplicates within same occupancy."""
        raise NotImplementedError

    @abstractmethod
    def get_task_by_worktree_branch(self, branch: str) -> Optional[Dict[str, Any]]:
        """Returns task dict matching worktree_branch, or None."""
        raise NotImplementedError

    @abstractmethod
    def validate_task_pipeline_history(self, task_id: str, task_state: str) -> Optional[str]:
        """Validates transition history and violations for pipeline commit check. Returns error string or None."""
        raise NotImplementedError
