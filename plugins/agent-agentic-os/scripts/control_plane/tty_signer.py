#!/usr/bin/env python3
"""
control_plane/tty_signer.py
===========================

Purpose:
    The human's signing step for a cryptographic-proof edge (APPROVED, VERIFY_EXIT, DONE), run by
    `coordinate-transition --interactive` in a real terminal (auth-ciba-increment-b). It shows the exact
    challenge, runs `ssh-keygen -Y sign` with the terminal ATTACHED (no captured stdio) so OpenSSH itself
    prompts for the private-key passphrase, then commits through approve_transition: the signature is verified
    against allowed_signers and the transition_request is consumed inside the commit transaction. The passphrase
    never passes through this code. No terminal (agents, pipes, CI) means no signer: the coordinator stops with
    HUMAN_PROOF_REQUIRED and the human runs show-challenge / ssh-keygen / approve-transition themselves.

Key Input Dependencies:
    - control_plane/gate1_approval.py (show_challenge, approve_transition), ssh_signing.py (sign_command)
    - the human's private key (default ~/.ssh/agentic-os_signing) and ssh-keygen (OpenSSH 8.1+)

Key Functions:
    - terminal_is_interactive() -- stdin and stdout are both terminals
    - make_tty_signer()         -- returns the callable(control_plane, request_id) the coordinator invokes
"""

import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Optional, TextIO

from control_plane.gate1_approval import GateApprovalError, approve_transition, show_challenge
from control_plane.identity_layout import DEFAULT_KEY_HINT, IdentityLayout
from control_plane.ssh_signing import sign_command


def terminal_is_interactive() -> bool:
    """True only when both stdin and stdout are terminals (a pty an agent allocates still counts: D4)."""
    return sys.stdin.isatty() and sys.stdout.isatty()


def make_tty_signer(
    *,
    key: str = DEFAULT_KEY_HINT,
    layout: Optional[IdentityLayout] = None,
    principal: Optional[str] = None,
    out: Optional[TextIO] = None,
    run: Callable[..., Any] = subprocess.run,
) -> Callable[[Any, int], Any]:
    """Build the signer the coordinator calls with (control_plane, request_id); it returns the TransitionRecord."""

    def signer(cp: Any, request_id: int) -> Any:
        stream = out or sys.stdout
        key_path = Path(key).expanduser()
        challenge = show_challenge(cp, request_id, layout=layout, key_hint=str(key_path), out=stream)
        stream.write("\nssh-keygen will now ask for your private-key passphrase.\n")
        stream.flush()
        sig = Path(str(challenge) + ".sig")
        if sig.exists():  # ssh-keygen will not overwrite a signature from an earlier, refused attempt
            sig.unlink()
        completed = run(sign_command(str(key_path), challenge))  # terminal attached: OpenSSH prompts itself
        if getattr(completed, "returncode", 1) != 0:
            raise GateApprovalError("ssh-keygen did not sign the challenge (wrong passphrase, missing key or cancelled).")
        return approve_transition(cp, request_id, layout=layout, principal=principal, out=stream)

    return signer
