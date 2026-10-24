#!/usr/bin/env python3
"""
control_plane/wrappers/run_verify_exit_bundle.py
=================================================

Purpose:
    Single-call bundle for the VERIFY_EXIT -> RETROSPECTIVE gate. Runs all 3
    required exit verifiers (pytest_full_suite, pytest_unit_tests, leak_check)
    through run_exit_verification() and records the required asymmetric
    persistence log entry, so satisfying done_guard/full_test_suite/leak_check
    never again takes multiple manual round-trips of denied coordinate-transition
    attempts (issue: session repeatedly ran bare `pytest` and had to retry the
    transition 4 times before discovering each missing receipt one at a time).

    Fails fast: any verifier returning a non-zero exit code stops the bundle
    immediately and returns its result without running remaining steps or
    logging asymmetric persistence -- a failing test run must not be papered
    over by a persistence log entry claiming completion.

Key Input Dependencies:
    - agent_control.ControlPlane (task must exist, be in a state that grants
      the 'exit_verification' phase capability)
    - control_plane.wrappers.run_exit_verification.run_exit_verification()

Index:
    - run_verify_exit_bundle() -- runs the 3 verifiers + asymmetric persistence
      log entry in one call, returns a combined result dict
    - main() -- CLI entry point
"""

import sys
from pathlib import Path

_scripts_dir = str(Path(__file__).resolve().parent.parent.parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from typing import Any, Dict, Optional

from agent_control import ControlPlane
from control_plane.wrappers.run_exit_verification import run_exit_verification


def run_verify_exit_bundle(
    task_id: str,
    asymmetric_persistence_details: str,
    asymmetric_persistence_destination: str = "references/map-debt.md",
    control_plane: Optional[ControlPlane] = None,
) -> Dict[str, Any]:
    """Runs pytest once plus leak_check, then logs the required asymmetric
    persistence entry -- the 4 things VERIFY_EXIT -> RETROSPECTIVE's
    done_guard/full_test_suite/leak_check checks require, satisfied in one call
    instead of 4 separate ones.

    pytest_full_suite and pytest_unit_tests previously ran as two SEPARATE
    subprocess invocations (VERIFIER_CATALOG: ["pytest", "-q"] and ["pytest"]
    respectively) -- since this repo has no actual unit/integration marker
    split, both silently collected and ran the identical full test set, doubling
    every VERIFY_EXIT bundle run's wall-clock time for zero additional coverage
    (found live 2026-09-18). Fixed: pytest now runs exactly once
    (pytest_full_suite's command), and its single result is recorded under
    BOTH gate names ("full_test_suite" and "test_suite") -- test_suite_or_
    deferred_to_review and other checks keyed on the "test_suite" gate still
    see a real receipt, just without a second real pytest invocation producing
    it.

    Stops immediately and returns on the first verifier that exits non-zero;
    does not log asymmetric persistence for a run containing a genuine failure.
    """
    cp = control_plane or ControlPlane()
    results: Dict[str, Any] = {"task_id": task_id, "steps": []}

    full_suite_result = run_exit_verification(task_id=task_id, verifier_id="pytest_full_suite", control_plane=cp)
    results["steps"].append({"verifier_id": "pytest_full_suite", **full_suite_result})
    if full_suite_result["exit_code"] != 0:
        results["status"] = "FAILED"
        results["failed_verifier"] = "pytest_full_suite"
        return results

    test_suite_receipt_token = cp.record_verification_receipt(
        task_id=task_id,
        gate_name="test_suite",
        command_executed="pytest -q (same run recorded under full_test_suite -- see that receipt for the actual invocation)",
        exit_code=full_suite_result["exit_code"],
    )
    results["steps"].append({
        "verifier_id": "pytest_unit_tests_same_run_as_full_suite",
        "status": "COMPLETED",
        "exit_code": full_suite_result["exit_code"],
        "receipt_token": test_suite_receipt_token,
    })

    leak_check_result = run_exit_verification(task_id=task_id, verifier_id="leak_check", control_plane=cp)
    results["steps"].append({"verifier_id": "leak_check", **leak_check_result})
    if leak_check_result["exit_code"] != 0:
        results["status"] = "FAILED"
        results["failed_verifier"] = "leak_check"
        return results

    cp.log_asymmetric_persistence(
        task_id=task_id,
        destination=asymmetric_persistence_destination,
        status="RESOLVED",
        details=asymmetric_persistence_details,
    )
    results["status"] = "COMPLETED"
    return results


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Run the full VERIFY_EXIT exit-check bundle in one call")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--details", required=True, help="Asymmetric persistence log details text")
    parser.add_argument("--destination", default="references/map-debt.md")
    args = parser.parse_args()

    result = run_verify_exit_bundle(
        task_id=args.task_id,
        asymmetric_persistence_details=args.details,
        asymmetric_persistence_destination=args.destination,
    )
    print(json.dumps(result, indent=2))
    if result["status"] != "COMPLETED":
        sys.exit(1)


if __name__ == "__main__":
    main()
