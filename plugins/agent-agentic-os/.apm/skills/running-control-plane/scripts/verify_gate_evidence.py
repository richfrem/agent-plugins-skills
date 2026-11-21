#!/usr/bin/env python3
"""
verify_gate_evidence.py
=======================

CLI used by the pre-push guard (DONE) and by orchestrating-agent-work's graph_runner.py (APPROVED):
  - DONE check:     verify_gate_evidence.py --repo-root <repo> --branch <branch>
  - APPROVED check: verify_gate_evidence.py --repo-root <repo> --task-id <id> --gate APPROVED [--manifest-sha256 <sha>] [--json]

Exit codes:
    0 = verified
    1 = refused (verification failed)
    2 = usage error
    3 = DB or identity unreadable / missing
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from control_plane.gate_evidence import verify_branch_done, verify_task_approved  # noqa: E402


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Authenticate signed control-plane gate evidence.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--branch", default=None, help="Branch to verify DONE evidence for")
    parser.add_argument("--task-id", default=None, help="Task ID to verify Gate 1 APPROVED evidence for")
    parser.add_argument("--gate", choices=["APPROVED", "DONE"], default=None, help="Gate to verify")
    parser.add_argument("--manifest-sha256", default=None, help="Manifest SHA-256 to verify binding against")
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root)

    if args.task_id and args.gate == "APPROVED":
        db = repo_root / "context" / "control_plane.db"
        anchor = repo_root / "context" / "identity" / "allowed_signers"
        if not db.is_file() or db.is_symlink() or not anchor.is_file():
            problems = [f"DB ({db}) or trust anchor ({anchor}) is missing, unreadable, or symlinked."]
            if args.json:
                print(json.dumps({"verified": False, "problems": problems, "binding": "none"}, indent=2))
            else:
                for p in problems:
                    print(f"   - {p}")
            return 3
        problems, binding = verify_task_approved(repo_root, args.task_id, manifest_sha256=args.manifest_sha256)
        verified = not problems
        if args.json:
            print(json.dumps({"verified": verified, "problems": problems, "binding": binding}, indent=2))
        else:
            for p in problems:
                print(f"   - {p}")
        return 0 if verified else 1

    if args.branch:
        problems = verify_branch_done(repo_root, args.branch)
        if args.json:
            print(json.dumps({"verified": not problems, "problems": problems, "binding": "done"}, indent=2))
        else:
            for problem in problems:
                print(f"   - {problem}")
        return 1 if problems else 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
