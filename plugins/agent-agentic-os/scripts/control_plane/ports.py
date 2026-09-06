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
from pathlib import Path
from typing import Any, Dict, List, Optional


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
    """Abstracts reading model-catalog JSON reference files."""

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
    def update_worktree_fields(self, task_id: str, worktree_path: str, worktree_branch: str, worktree_state: str) -> None:
        """Updates a task's worktree_path/worktree_branch/worktree_state columns."""
        raise NotImplementedError

    @abstractmethod
    def ensure_schema(self) -> None:
        """Ensures the underlying storage schema exists and is at the current version, self-healing if needed."""
        raise NotImplementedError
