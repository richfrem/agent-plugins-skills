#!/usr/bin/env python3
"""Exploration Session Substrate Adapter.

Connects Exploration Cycle skills to the Agentic OS runtime substrate.
Provides:
- Canonical substrate readiness checks via installation_probe.py
- Authoritative lifecycle context enforcement against Agentic OS control plane (INTAKE, INTERVIEW, DRAFT_PLAN)
- Single authoritative source of truth in Agentic OS asymmetric persistence ledger
- Derived human-readable JSON projection (context/exploration_session.json) with auto-healing
- Programmatic phase advancement and gate validation (approved plan required for prototyping)
- Re-entry and resumption support without simulated prompt state machines
"""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent
REPO_ROOT = PLUGIN_ROOT.parent.parent
AGENTIC_OS_SCRIPTS = REPO_ROOT / "plugins" / "agent-agentic-os" / "scripts"

if str(AGENTIC_OS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(AGENTIC_OS_SCRIPTS))

try:
    from control_plane.installation_probe import classify_target  # type: ignore
except ImportError:
    classify_target = None  # type: ignore

VALID_EXPLORATION_LIFECYCLE_STATES = (
    "INTAKE",
    "INTERVIEW",
    "DRAFT_PLAN",
)

EXPLORATION_PHASES = (
    "1-discovery",
    "2-requirements",
    "3-prototyping",
    "4-handoff",
)

DEFAULT_STORAGE_PATH = REPO_ROOT / "context" / "exploration_session.json"
PERSISTENCE_DESTINATION = "context/exploration_session.json"


class LifecycleContextError(Exception):
    """Raised when an exploration action is attempted in a disallowed lifecycle state."""
    pass


def resolve_repository_root() -> Path:
    """Resolves the physical repository root even when executing in a worktree."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=str(SCRIPT_DIR),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if res.returncode == 0:
            common = Path(res.stdout.strip())
            if not common.is_absolute():
                common = (SCRIPT_DIR / common).resolve()
            return common.parent
    except Exception:
        pass
    return REPO_ROOT


def get_control_plane(db_path: Optional[Path] = None):
    """Obtains the canonical Agentic OS ControlPlane instance."""
    repo = resolve_repository_root()
    agentic_os_scripts = repo / "plugins" / "agent-agentic-os" / "scripts"
    if str(agentic_os_scripts) not in sys.path:
        sys.path.insert(0, str(agentic_os_scripts))
    try:
        from agent_control import ControlPlane
        return ControlPlane(db_path=db_path)
    except Exception as e:
        raise RuntimeError(f"Cannot initialize Agentic OS ControlPlane: {e}")


def check_substrate_readiness(target: Optional[Path] = None) -> Tuple[bool, str]:
    """Verifies that the Agentic OS execution substrate is complete and active.

    Reuses canonical installation_probe.py to inspect the 4 required substrates
    and database schema parity.
    """
    repo = target.resolve() if target else resolve_repository_root()
    if classify_target is None:
        return False, "Agentic OS execution substrate is not initialized (installation_probe missing)."

    result = classify_target(repo)
    if result.state == "COMPLETE":
        return True, ""
    return (
        False,
        "Agentic OS execution substrate is not initialized. "
        "Please run 'os-init' to establish repository control plane infrastructure before starting an exploration session.",
    )


def validate_lifecycle_context(state: str) -> Tuple[bool, str]:
    """Advisory check: ensures state name is in permitted exploratory lifecycle phases."""
    state_upper = state.strip().upper()
    if state_upper in VALID_EXPLORATION_LIFECYCLE_STATES:
        return True, ""
    return (
        False,
        f"Exploration sessions are not permitted during {state_upper}. "
        "Routing back to active engineering phase.",
    )


def enforce_lifecycle_context(task_id: str, db_path: Optional[Path] = None) -> str:
    """Enforces that task is in a permitted exploratory lifecycle state in Agentic OS.

    Queries the authoritative Agentic OS control plane.
    Fails closed: raises LifecycleContextError if task is not found or in a disallowed state.
    """
    cp = get_control_plane(db_path=db_path)
    task = cp.get_task(task_id)
    if not task:
        raise LifecycleContextError(
            f"Task '{task_id}' not found in Agentic OS control plane. "
            "An exploration session requires an active Agentic OS task context."
        )
    state = task.get("state", "").strip().upper()
    if state not in VALID_EXPLORATION_LIFECYCLE_STATES:
        raise LifecycleContextError(
            f"Exploration sessions are not permitted during {state}. "
            f"Permitted states are: {sorted(list(VALID_EXPLORATION_LIFECYCLE_STATES))}."
        )
    return state


def get_default_storage_path(custom_path: Optional[Path] = None) -> Path:
    if custom_path:
        return custom_path
    repo = resolve_repository_root()
    return repo / "context" / "exploration_session.json"


def _persist_to_authoritative_ledger(
    task_id: str,
    session: Dict[str, Any],
    event: str,
    db_path: Optional[Path] = None,
) -> None:
    """Records session state via the canonical Agentic OS asymmetric persistence interface.

    Fails closed: If authoritative persistence fails, raises an exception so projection is not mutated.
    Uses canonical Layer 2 taxonomy ('CONFIRMED' status).
    """
    cp = get_control_plane(db_path=db_path)
    cp.log_asymmetric_persistence(
        task_id=task_id,
        destination=PERSISTENCE_DESTINATION,
        status="CONFIRMED",
        details=json.dumps(session),
    )


def _heal_projection(path: Path, session_data: Dict[str, Any]) -> None:
    """Refreshes derived JSON projection with authoritative data atomically."""
    try:
        if path.is_symlink():
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(session_data, indent=2), encoding="utf-8")
        os.replace(tmp_path, path)
    except OSError:
        pass


def _get_from_authoritative_ledger(
    task_id: str, db_path: Optional[Path] = None
) -> Optional[Dict[str, Any]]:
    """Retrieves authoritative session state via the canonical Agentic OS interface.

    Fails closed: Any infrastructure or database errors raise immediately.
    Corrupted ledger details (invalid JSON) raise immediately.
    Returns None ONLY when the authoritative ledger contains no record for task_id.
    """
    cp = get_control_plane(db_path=db_path)
    rec = cp.get_latest_asymmetric_persistence(task_id, destination=PERSISTENCE_DESTINATION)
    if not rec:
        return None
    details = rec.get("details")
    if not details:
        return None
    try:
        return json.loads(details)
    except (json.JSONDecodeError, TypeError) as e:
        raise RuntimeError(
            f"Authoritative persistence ledger contains corrupted JSON for task '{task_id}': {e}"
        )


def get_exploration_session(
    task_id: Optional[str] = None,
    storage_path: Optional[Path] = None,
    db_path: Optional[Path] = None,
) -> Optional[Dict[str, Any]]:
    """Retrieves current exploration session metadata.

    Single Source of Truth Invariant:
    The Agentic OS persistence ledger is the single authoritative source of truth.
    When task_id is provided, authoritative lookup is definitive:
      1. If the authoritative ledger query fails (DB error or corrupted record), the call
         fails closed and raises immediately. Stale JSON is NEVER returned.
      2. If the authoritative ledger has no record for task_id, returns None immediately.
         Stale JSON on disk is NEVER promoted to authority.
      3. If authoritative state exists, it is returned and heals the derived JSON projection.

    When task_id is None (detached / non-authoritative read), returns the derived JSON
    projection file if it exists, or None.
    """
    path = get_default_storage_path(storage_path)

    # 1. Authoritative Agentic OS ledger read (definitive when task_id is provided)
    if task_id:
        ledger_data = _get_from_authoritative_ledger(task_id, db_path=db_path)
        if ledger_data is None:
            return None
        _heal_projection(path, ledger_data)
        return ledger_data

    # 2. Detached / non-authoritative projection read (only when task_id is None)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def create_exploration_session(
    task_id: str,
    session_type: str = "greenfield",
    storage_path: Optional[Path] = None,
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Creates and persists an exploration sub-workflow session.

    Enforces authoritative Agentic OS lifecycle state before mutation.
    Persists to authoritative Agentic OS ledger first (failing closed if persistence fails),
    then writes derived JSON projection.
    """
    # 1. Enforce authoritative lifecycle context
    enforce_lifecycle_context(task_id, db_path=db_path)

    path = get_default_storage_path(storage_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    session: Dict[str, Any] = {
        "session_id": f"exp-{task_id}",
        "task_id": task_id,
        "session_type": session_type,
        "active_phase": "1-discovery",
        "phase_state": "IN_PROGRESS",
        "approved_plan": False,
        "artifacts": [],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    # 2. Authoritative persistence in Agentic OS ledger (fails closed if error occurs)
    _persist_to_authoritative_ledger(task_id, session, "SESSION_CREATED", db_path=db_path)

    # 3. Derived human-readable JSON projection written only after authoritative commit
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(session, indent=2), encoding="utf-8")
    os.replace(tmp_path, path)

    return session


def advance_exploration_phase(
    task_id: str,
    target_phase: str,
    storage_path: Optional[Path] = None,
    approved_plan: Optional[bool] = None,
    evidence: str = "",
    db_path: Optional[Path] = None,
) -> Tuple[bool, str]:
    """Advances exploration phase, enforcing gate prerequisites (e.g. plan approval).

    Enforces authoritative Agentic OS lifecycle state before mutation.
    Updates authoritative Agentic OS ledger first (failing closed if persistence fails),
    then updates derived JSON projection.
    """
    # 1. Enforce authoritative lifecycle context
    enforce_lifecycle_context(task_id, db_path=db_path)

    session = get_exploration_session(task_id=task_id, storage_path=storage_path, db_path=db_path)
    if not session:
        return False, f"No active exploration session found for task {task_id}"

    if target_phase not in EXPLORATION_PHASES:
        return False, f"Invalid exploration phase: {target_phase}. Valid: {EXPLORATION_PHASES}"

    if approved_plan is not None:
        session["approved_plan"] = approved_plan

    # Hard gate check for prototyping
    if target_phase == "3-prototyping" and not session.get("approved_plan"):
        return (
            False,
            "Cannot advance to prototyping without an approved plan from the SME. "
            "Please obtain explicit approval first.",
        )

    session["active_phase"] = target_phase
    if target_phase == "4-handoff":
        session["phase_state"] = "COMPLETED"
    else:
        session["phase_state"] = "IN_PROGRESS"

    session["updated_at"] = datetime.now(timezone.utc).isoformat()
    if evidence and evidence not in session.get("artifacts", []):
        session.setdefault("artifacts", []).append(evidence)

    # 2. Authoritative persistence in Agentic OS ledger (fails closed if error occurs)
    _persist_to_authoritative_ledger(task_id, session, f"PHASE_ADVANCED_{target_phase}", db_path=db_path)

    # 3. Derived human-readable JSON projection
    path = get_default_storage_path(storage_path)
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(session, indent=2), encoding="utf-8")
    os.replace(tmp_path, path)

    return True, f"Successfully advanced to {target_phase}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Exploration Session Substrate Adapter.")
    parser.add_argument("--check", action="store_true", help="Read-only substrate readiness check.")
    parser.add_argument("--task-id", type=str, help="Target task ID.")
    parser.add_argument("--session-type", type=str, default="greenfield", help="Session type.")
    parser.add_argument("--phase", type=str, help="Target phase to advance to.")
    parser.add_argument("--approve-plan", action="store_true", help="Mark Discovery Plan as approved.")
    parser.add_argument("--evidence", type=str, default="", help="Artifact path evidence.")
    parser.add_argument("--db-path", type=Path, default=None, help="Custom control_plane.db path.")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("get-session", help="Get active exploration session.")
    subparsers.add_parser("create-session", help="Create a new exploration session.")
    subparsers.add_parser("advance-phase", help="Advance exploration phase.")

    args = parser.parse_args()

    if args.check:
        ready, msg = check_substrate_readiness()
        if not ready:
            print(f"Check failed: {msg}", file=sys.stderr)
            return 1
        print("Check passed: Agentic OS execution substrate is active and ready.")
        return 0

    if args.command == "get-session":
        session = get_exploration_session(task_id=args.task_id, db_path=args.db_path)
        if not session:
            print(f"No active session found for task {args.task_id}")
            return 1
        print(json.dumps(session, indent=2))
        return 0

    if args.command == "create-session":
        if not args.task_id:
            print("Error: --task-id is required for create-session", file=sys.stderr)
            return 1
        try:
            session = create_exploration_session(
                task_id=args.task_id,
                session_type=args.session_type,
                db_path=args.db_path,
            )
            print(json.dumps(session, indent=2))
            return 0
        except LifecycleContextError as e:
            print(f"Lifecycle error: {e}", file=sys.stderr)
            return 1

    if args.command == "advance-phase":
        if not args.task_id or not args.phase:
            print("Error: --task-id and --phase are required for advance-phase", file=sys.stderr)
            return 1
        try:
            success, msg = advance_exploration_phase(
                task_id=args.task_id,
                target_phase=args.phase,
                approved_plan=True if args.approve_plan else None,
                evidence=args.evidence,
                db_path=args.db_path,
            )
            if not success:
                print(f"Error: {msg}", file=sys.stderr)
                return 1
            print(msg)
            return 0
        except LifecycleContextError as e:
            print(f"Lifecycle error: {e}", file=sys.stderr)
            return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
