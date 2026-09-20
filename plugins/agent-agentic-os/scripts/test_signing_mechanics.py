#!/usr/bin/env python3
"""
test_signing_mechanics.py
=========================

Purpose:
    Standalone, self-contained CLI for the interactive signing self-test (auth-ciba-increment-b,
    issue #639). Signs a generated challenge with YOUR key through the real ssh-keygen prompt
    (passphrase or hardware touch), verifies it against the SEPARATE `allowed_signers_selftest`
    (namespace control-plane-selftest@agentic-os.local), and proves the signature can never act as a Gate 1 approval.
    Same behavior as `agent_control.py test-signing-mechanics`, but usable from the os-signing-setup
    skill without the rest of the control plane. A human tool: it refuses to run without a terminal.

Key Input Dependencies:
    - control_plane/signing_selftest.py (run_selftest), identity_layout.py
    - ssh-keygen (OpenSSH 8.1+); the key created by setup_ciba_identity.py

Usage:
    python3 scripts/test_signing_mechanics.py [--key ~/.ssh/agentic-os_signing] [--repo-root PATH]

Key Functions:
    - main() -- parse arguments and run the self-test; returns the run_selftest exit code
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from control_plane.identity_layout import DEFAULT_KEY_HINT, canonical_repo_root, default_layout  # noqa: E402
from control_plane.signing_selftest import run_selftest  # noqa: E402


def main(argv: Optional[List[str]] = None) -> int:
    """Run the interactive signing self-test and return its exit code."""
    parser = argparse.ArgumentParser(description="Interactive self-test of your approval-signing key")
    parser.add_argument("--key", default=DEFAULT_KEY_HINT, help="Path of your private signing key")
    parser.add_argument("--repo-root", default=None, help="Repository root (default: the canonical root shared by worktrees)")
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve() if args.repo_root else canonical_repo_root(".")
    return run_selftest(default_layout(root), Path(args.key).expanduser())


if __name__ == "__main__":
    raise SystemExit(main())
