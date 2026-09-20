#!/usr/bin/env python3
"""
control_plane/identity_layout.py
================================

Purpose:
    The canonical on-disk locations of the Gate 1 signing trust anchors (auth-ciba-increment-b,
    issue #639, tasks T6/T7/T11). Everything lives under `<repo>/context/identity/` (gitignored,
    local to the human's machine); the human's private signing key is NOT stored here (it stays in
    the human's own `~/.ssh`). The isolation preflight (T1) checks the ownership and modes of these
    paths; the setup helper (T11) creates them; show-challenge / approve-transition (T6) use them.

Key Input Dependencies:
    - The repository root (supplied by the caller)

Key Functions:
    - default_layout() -- IdentityLayout for a repository root.
    - canonical_repo_root() -- the shared (main) repository root, the same one the coordinator uses,
      even when called from inside a git worktree.

Layout:
    context/identity/allowed_signers            production trust anchor (namespace control-plane@agentic-os.local), 0600
    context/identity/allowed_signers_selftest   self-test trust anchor (namespace control-plane-selftest@agentic-os.local), 0600
    context/identity/challenges/                per-request challenge and signature files, 0700
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Union

DEFAULT_KEY_HINT = "~/.ssh/agentic-os_signing"


@dataclass(frozen=True)
class IdentityLayout:
    """Paths of the signing trust anchors for one repository."""

    root: Path

    @property
    def allowed_signers(self) -> Path:
        return self.root / "allowed_signers"

    @property
    def allowed_signers_selftest(self) -> Path:
        return self.root / "allowed_signers_selftest"

    @property
    def challenge_dir(self) -> Path:
        return self.root / "challenges"


def canonical_repo_root(start: Union[str, Path] = ".") -> Path:
    """The canonical repository root shared by all worktrees (the parent of the common `.git`).

    The coordinator and approve-transition resolve this root, so setup and the self-test must too;
    `git rev-parse --show-toplevel` would return the worktree and enroll the key in the wrong place.
    Outside a git repository the directory itself is returned."""
    start = Path(start).resolve()
    try:
        result = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return start
    common = result.stdout.strip()
    if result.returncode != 0 or not common:
        return start
    common_path = Path(common).resolve()
    return common_path.parent if common_path.name == ".git" else start


def default_layout(repo_root: Union[str, Path]) -> IdentityLayout:
    """The standard layout under `<repo_root>/context/identity`."""
    return IdentityLayout(root=Path(repo_root) / "context" / "identity")
