#!/usr/bin/env python3
"""
verify_gate_evidence.py
=======================

Purpose:
    CLI used by the pre-push guard: re-verify, against the repository's human trust anchor, the
    signed gates behind the DONE of the task registered for a branch. Exits 0 only when the DONE is
    authenticated (real-work database, human key, one key for every gate); otherwise prints every
    problem and exits 1. Cross-platform (macOS, Linux, Windows).

Key Input Dependencies:
    - control_plane/gate_evidence.py (the checks), control_plane/approver_policy.py, control_plane/ssh_signing.py
    - <repo>/context/control_plane.db and <repo>/context/identity/allowed_signers

Key Functions:
    - main() -- parse --repo-root and --branch, run verify_branch_done, report, exit

Usage:
    python3 verify_gate_evidence.py --repo-root <repo> --branch <branch>
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from control_plane.gate_evidence import verify_branch_done  # noqa: E402


# Parse arguments, verify, report, exit 0/1
def main() -> int:
    """Return 0 when the branch's DONE is authenticated, 1 otherwise."""
    parser = argparse.ArgumentParser(description="Authenticate a branch's DONE from its signed gate evidence.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--branch", required=True)
    args = parser.parse_args()
    problems = verify_branch_done(Path(args.repo_root), args.branch)
    for problem in problems:
        print(f"   - {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
