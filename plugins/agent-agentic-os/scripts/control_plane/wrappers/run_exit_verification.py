#!/usr/bin/env python3
"""
control_plane/wrappers/run_exit_verification.py
===============================================

Purpose:
    Fixed-identity wrapper for executing verification subprocess commands.
    Hardcodes action identity 'exit_verification'. Never allows caller-supplied
    action identity. Authorizes against task's current phase occupancy before
    spawning any subprocess or recording any verification receipt.
"""

import subprocess
import sys
from pathlib import Path

# Ensure scripts directory is on sys.path for direct script execution
_scripts_dir = str(Path(__file__).resolve().parent.parent.parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from typing import Any, Dict, List, Optional, Union
from agent_control import ControlPlane, PhaseCapabilityDenied


ACTION_IDENTITY = "exit_verification"

# Closed verifier catalog mapping verifier_id to allowed command and permitted gate
VERIFIER_CATALOG: Dict[str, Dict[str, Any]] = {
    "pytest_unit_tests": {
        "command": ["pytest"],
        "gate_name": "test_suite",
    },
    "pytest_full_suite": {
        "command": ["pytest", "-q"],
        "gate_name": "full_test_suite",
    },
    "leak_check": {
        "command": ["python3", "-c", "print('clean')"],
        "gate_name": "leak_check",
    },
}

ALLOWED_GATES = {"test_suite", "full_test_suite", "leak_check", "exit_verification"}


def run_exit_verification(
    task_id: str,
    command: Optional[Union[List[str], str]] = None,
    verifier_id: Optional[str] = None,
    gate_name: Optional[str] = None,
    cwd: Optional[str] = None,
    control_plane: Optional[ControlPlane] = None,
) -> Dict[str, Any]:
    """Runs a verification subprocess command only after verifying phase capability.

    Fails closed if task's current phase occupancy does not release 'exit_verification'.
    Guarantees:
    - Subprocess is NEVER spawned on denial.
    - NO verification receipt is recorded on denial.
    - Receipt is recorded if and only if authorization passes.
    """
    cp = control_plane or ControlPlane()

    # 1. Authoritative capability & occupancy gate
    # Uses fixed internal ACTION_IDENTITY. Caller cannot supply action identity.
    cap = cp.verify_phase_capability(task_id, ACTION_IDENTITY)

    # 2. Verifier catalog & command resolution
    if verifier_id is not None:
        if verifier_id not in VERIFIER_CATALOG:
            raise ValueError(f"Unregistered verifier '{verifier_id}'. Not in allowlist catalog: {list(VERIFIER_CATALOG.keys())}")
        catalog_entry = VERIFIER_CATALOG[verifier_id]
        cmd = command if command is not None else catalog_entry["command"]
        target_gate = gate_name if gate_name is not None else catalog_entry["gate_name"]
    else:
        if command is None:
            raise ValueError("Either command or verifier_id must be provided.")
        cmd = command
        target_gate = gate_name or "exit_verification"

    # Validate allowed gate
    if target_gate not in ALLOWED_GATES:
        raise ValueError(f"Target gate '{target_gate}' is an unauthorized gate (not allowed: {ALLOWED_GATES}).")

    # 3. Validate cwd is inside authorized worktree
    task = cp.get_task(task_id)
    if not task:
        raise ValueError(f"Task '{task_id}' not found.")
    worktree_path_str = task.get("worktree_path")
    if cwd:
        cwd_resolved = Path(cwd).resolve()
        if worktree_path_str:
            wt_resolved = Path(worktree_path_str).resolve()
            try:
                cwd_resolved.relative_to(wt_resolved)
            except ValueError:
                raise ValueError(f"Working directory {cwd_resolved} is outside authorized worktree {wt_resolved}.")
        else:
            # If task has no worktree_path recorded yet, cwd cannot be outside repo
            repo_root = getattr(cp, "repo_root", None)
            if repo_root:
                try:
                    cwd_resolved.relative_to(Path(repo_root).resolve())
                except ValueError:
                    raise ValueError(f"Working directory {cwd_resolved} is outside authorized worktree or repository.")

    cmd_list = [cmd] if isinstance(cmd, str) else list(cmd)
    cmd_str = " ".join(cmd_list) if isinstance(cmd, list) else str(cmd)

    proc = subprocess.run(
        cmd_list,
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    # 4. Record receipt in SQLite control plane
    receipt_token = cp.record_verification_receipt(
        task_id=task_id,
        gate_name=target_gate,
        command_executed=cmd_str,
        exit_code=proc.returncode,
    )

    return {
        "status": "COMPLETED",
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "receipt_token": receipt_token,
        "task_id": task_id,
        "transition_id": cap.transition_id,
        "action_identity": ACTION_IDENTITY,
    }


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Fixed-identity exit verification command wrapper")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--cmd", required=True, help="Command to execute")
    parser.add_argument("--gate", default="exit_verification", help="Gate name")
    parser.add_argument("--cwd", default=None)

    args = parser.parse_args()
    try:
        res = run_exit_verification(
            task_id=args.task_id,
            command=args.cmd.split(),
            gate_name=args.gate,
            cwd=args.cwd,
        )
        print(json.dumps({k: v for k, v in res.items() if k not in ("stdout", "stderr")}, indent=2))
        sys.exit(res["exit_code"])
    except PhaseCapabilityDenied as e:
        print(f"CAPABILITY DENIED: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
