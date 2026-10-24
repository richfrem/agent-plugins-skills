#!/usr/bin/env python3
"""
control_plane/proof_policy.py
=============================

Purpose:
    Proof policy for the cryptographic-proof gates (APPROVED, VERIFY_EXIT, DONE) of auth-ciba-increment-b.
    There is exactly one mode: STRICT. The earlier audited `legacy_input` fallback (an interactive prompt standing
    in for a signature) was REMOVED on 2026-09-20 by human decision: no typed word, prompt, flag or actor string
    authorizes these edges. `context/isolation-policy.json` is still read so that a file that tries to select
    `legacy_input` is reported and ignored rather than silently honored; the answer is always STRICT.

Key Input Dependencies:
    - `context/isolation-policy.json` (optional; ignored apart from the diagnostic reason)
    - Python stdlib only

Key Functions:
    - load_proof_policy() -- always returns ProofPolicy(STRICT, reason); never raises for bad input.

Constants:
    - STRICT, POLICY_RELATIVE_PATH
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Set, Union

STRICT = "strict"
POLICY_RELATIVE_PATH = "context/isolation-policy.json"
_MAX_POLICY_BYTES = 4096

PathLike = Union[str, "os.PathLike[str]"]


@dataclass(frozen=True)
class ProofPolicy:
    """The proof mode in force and why. `mode` is always STRICT."""

    mode: str
    reason: str


def load_proof_policy(
    policy_path: PathLike,
    *,
    agent_name: Optional[str] = None,
    agent_uid: Optional[int] = None,
    agent_gids: Optional[Set[int]] = None,
    euid: Optional[int] = None,
) -> ProofPolicy:
    """Return STRICT. A policy file that asks for the removed `legacy_input` mode is named in the reason and ignored."""
    reason = "strict: only a verified OpenSSH signature authorizes APPROVED, VERIFY_EXIT and DONE"
    try:
        path = Path(policy_path)
        if path.is_file() and not path.is_symlink():
            data: Any = json.loads(path.read_bytes()[: _MAX_POLICY_BYTES + 1].decode("utf-8"))
            if isinstance(data, dict) and data.get("human_only_proof") not in (None, "strict"):
                reason = f"strict: the requested mode {data.get('human_only_proof')!r} was removed and is ignored"
    except (OSError, ValueError):
        pass
    return ProofPolicy(STRICT, reason)
