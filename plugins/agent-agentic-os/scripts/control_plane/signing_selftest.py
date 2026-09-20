#!/usr/bin/env python3
"""
control_plane/signing_selftest.py
=================================

Purpose:
    The interactive signing self-test for the Gate 1 identity (auth-ciba-increment-b, issue #639,
    task T12), run by the HUMAN as `agent_control.py test-signing-mechanics` (and offered at the end of
    the setup helper) before their first live approval. It generates a one-off challenge, has the human
    sign it through the REAL `ssh-keygen` prompt (a passphrase, or a hardware touch), verifies it against
    the SEPARATE `allowed_signers_selftest` under namespace `control-plane-selftest@agentic-os.local`, reports the FIDO
    user-presence/verification flags, proves the same signature cannot act as a Gate 1 approval (it does
    not verify in the production namespace), and removes the temporary files. It never creates a
    transition_request, never touches the production `allowed_signers`, and refuses to run without a
    terminal (a prompt that no human sees proves nothing).

Key Input Dependencies:
    - control_plane/identity_layout.py, isolation_check.py, ssh_signing.py, identity_setup.py
    - the human's private key path; `context/identity/allowed_signers_selftest`
    - `ssh-keygen` on PATH (OpenSSH 8.1+)

Key Functions:
    - run_selftest() -- returns a process exit code (0 = verified and confirmed not an approval).
    - _interactive_sign() -- the default signer: ssh-keygen -Y sign with the terminal attached.
"""

import secrets
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Optional

from control_plane.identity_layout import IdentityLayout
from control_plane.isolation_check import IsolationError, check_isolation
from control_plane.ssh_signing import (
    SELFTEST_NAMESPACE,
    SigningError,
    SignatureInvalid,
    probe_ssh_keygen,
    read_signature,
    verify_selftest_signature,
    verify_signature,
    write_challenge,
)


def _interactive_sign(key: Path, namespace: str, challenge: Path) -> int:
    """Run ssh-keygen -Y sign with stdio attached so it prompts the human (passphrase / touch)."""
    return subprocess.run(["ssh-keygen", "-Y", "sign", "-f", str(key), "-n", namespace, str(challenge)]).returncode


def run_selftest(
    layout: IdentityLayout,
    key: Path,
    *,
    tty_fn: Optional[Callable[[], bool]] = None,
    out: Callable[[str], None] = print,
    sign_fn: Optional[Callable[[Path, str, Path], int]] = None,
) -> int:
    """Sign, verify and report. Exit codes: 0 ok; 2 refused; 3 setup problem; 4 signing failed; 5 not verified; 6 unsafe."""
    is_tty = (tty_fn or (lambda: sys.stdin.isatty() and sys.stdout.isatty()))()
    if not is_tty:
        out("REFUSED: the signing self-test must run in an interactive terminal (no terminal detected).")
        return 2
    key = Path(key).expanduser()
    if not key.exists():
        out(f"REFUSED: private key {key} not found. Run setup_ciba_identity.py first, or pass --key.")
        return 3
    capability = probe_ssh_keygen()
    if not capability.supports_sshsig:
        out(f"REFUSED: ssh-keygen with SSHSIG support (OpenSSH 8.1+) is required: {capability.reason or capability.version}")
        return 3

    preflight = check_isolation(
        allowed_signers=layout.allowed_signers, allowed_signers_selftest=layout.allowed_signers_selftest,
        challenge_dir=layout.challenge_dir, environ={},
    )
    blocking = []
    for failure in preflight.failures:
        if failure.code == "IDENTITY_UNRESOLVED":
            out("  note: the unprivileged agent account is not created yet; strict Gate 1 approvals will need it (see setup output).")
        elif failure.path and Path(failure.path) == layout.allowed_signers:
            continue  # the production file is not needed for the self-test
        else:
            blocking.append(failure)
    if blocking:
        out("REFUSED: the self-test files are not safely set up:")
        for failure in blocking:
            out(f"  - {failure.code}: {failure.message}")
        out("Run: python3 plugins/agent-agentic-os/scripts/setup_ciba_identity.py")
        return 3

    nonce = secrets.token_hex(16)
    stem = f"selftest-{nonce[:16]}"
    challenge = (
        f"control-plane-selftest-challenge/1\nnonce: {nonce}\ncreated: {int(time.time())}\n"
        "purpose: prove the signing key works; this is NOT an approval\n"
    ).encode("utf-8")
    challenge_path = write_challenge(layout.challenge_dir, stem, challenge)
    signature_path = layout.challenge_dir / f"{stem}.sig"
    try:
        out("")
        out("Self-test challenge (this is NOT an approval):")
        out("  " + challenge.decode("utf-8").replace("\n", "\n  ").rstrip())
        out(f"Signing now under namespace {SELFTEST_NAMESPACE}. Expect a passphrase prompt (or a touch request for a hardware key).")
        code = (sign_fn or _interactive_sign)(key, SELFTEST_NAMESPACE, challenge_path)
        if code != 0:
            out("Signing failed (wrong passphrase, no touch, or an unusable key). Nothing was verified.")
            return 4
        try:
            signature = read_signature(layout.challenge_dir, stem)
        except IsolationError as exc:
            out(f"Could not read the signature safely: {exc}")
            return 4
        try:
            verified = verify_selftest_signature(challenge, signature, allowed_signers_selftest=layout.allowed_signers_selftest)
        except SigningError as exc:
            out(f"The signature did not verify against allowed_signers_selftest: {exc}")
            out("The key may not be enrolled. Run setup_ciba_identity.py to enroll it.")
            return 5
        out("")
        out(f"Signature verified: principal {verified.principal}, {verified.key_type} key {verified.fingerprint}, namespace {verified.namespace}.")
        if verified.sk_flags is not None:
            out(f"  FIDO flags {verified.sk_flags:#04x}: user presence {'yes' if verified.sk_flags & 0x01 else 'NO'}, "
                f"user verification {'yes' if verified.sk_flags & 0x04 else 'NO'} (Gate 1 requires both by default).")
        try:
            verify_signature(challenge, signature, allowed_signers=layout.allowed_signers)
        except SignatureInvalid:
            out("Confirmed: this self-test signature cannot be used as an approval (it does not verify in the production namespace).")
        else:
            out("WARNING: this self-test signature also verified in the production namespace. Do not use this identity setup.")
            return 6
        return 0
    finally:
        for leftover in (challenge_path, signature_path):
            try:
                leftover.unlink()
            except FileNotFoundError:
                pass
