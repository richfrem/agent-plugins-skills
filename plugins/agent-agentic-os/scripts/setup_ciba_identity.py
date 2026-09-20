#!/usr/bin/env python3
"""
scripts/setup_ciba_identity.py
==============================

Purpose:
    Interactive, cross-platform (macOS, Windows, Linux) helper that creates the human's Gate 1
    signing identity for the Agentic OS (auth-ciba-increment-b, issue #639, task T11):
      Step 1  a dedicated SSH signing key (passphrase-protected ed25519 by default, or a FIDO
              hardware key with --type ecdsa-sk); an existing key is reused (idempotent);
      Step 2  the identity folder `context/identity/` (0700) with a challenge folder (0700);
      Step 3  the key enrolled in `allowed_signers` (namespace control-plane@agentic-os.local, 0600) and in a SEPARATE
              `allowed_signers_selftest` (namespace control-plane-selftest@agentic-os.local, 0600) - old keys stay;
      Step 4  the isolation check against the agent account, with the privileged account-creation
              commands PRINTED for you to run yourself (never executed here);
      Step 5  optionally, the interactive signing self-test (passphrase prompt or hardware touch).
    The signing key is an SSH key, not an X.509 certificate; its SHA256 fingerprint plays the role a
    certificate thumbprint would. This script is a human tool: it refuses to run without a terminal
    and refuses to run as the agent account, otherwise an agent could enroll its own key.

Key Input Dependencies:
    - `ssh-keygen` (OpenSSH 8.1+; Windows 10/11 ships it; FIDO needs 8.2+ or Win32-OpenSSH 8.9+)
    - control_plane/identity_setup.py, identity_layout.py, isolation_check.py, ssh_signing.py
    - the repository root (defaults to the current directory's git root)

Key Functions:
    - main() -- the CLI entry point; returns a process exit code.

Usage:
    python3 setup_ciba_identity.py                # guided setup
    python3 setup_ciba_identity.py --check        # read-only status, no terminal needed
    python3 setup_ciba_identity.py --type ecdsa-sk --key ~/.ssh/agentic-os_signing_sk
    python3 setup_ciba_identity.py --force        # add another key; existing keys stay enrolled
"""

import argparse
import getpass
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here))

from control_plane.identity_layout import DEFAULT_KEY_HINT, canonical_repo_root, default_layout  # noqa: E402
from control_plane.identity_setup import (  # noqa: E402
    enroll_key,
    enrolled_keys,
    ensure_layout,
    identity_status,
    key_is_passphrase_protected,
    migrate_namespaces,
    privileged_account_commands,
)
from control_plane.isolation_check import DEFAULT_AGENT_NAME  # noqa: E402
from control_plane.ssh_signing import probe_ssh_keygen  # noqa: E402

DEFAULT_PRINCIPAL = "operator@control-plane"


def _repo_root(explicit: Optional[str]) -> Path:
    if explicit:
        return Path(explicit).resolve()
    return canonical_repo_root(".")


def _agent_identity(args: argparse.Namespace, injected: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if injected is not None:
        return dict(injected)
    identity: Dict[str, Any] = {"agent_name": args.agent_name or DEFAULT_AGENT_NAME}
    if args.agent_uid is not None:
        identity["agent_uid"] = args.agent_uid
        identity["agent_gids"] = set()
    return identity


def _banner(out: Callable[[str], None], text: str) -> None:
    out("")
    out("=" * 62)
    out(f"  {text}")
    out("=" * 62)


def _ssh_keygen_generate(key: Path, key_type: str, out: Callable[[str], None]) -> int:
    """Run the real ssh-keygen with the terminal attached so it asks for the passphrase / touch."""
    key.parent.mkdir(parents=True, exist_ok=True)
    out(f"Creating a {key_type} key at {key}. ssh-keygen will now ask you for a passphrase (or a touch).")
    return subprocess.run(["ssh-keygen", "-t", key_type, "-C", f"agentic-os-approval@{getpass.getuser()}", "-f", str(key)]).returncode


def main(
    argv: Optional[List[str]] = None,
    *,
    tty_fn: Optional[Callable[[], bool]] = None,
    input_fn: Callable[[str], str] = input,
    out: Callable[[str], None] = print,
    agent_identity: Optional[Dict[str, Any]] = None,
) -> int:
    parser = argparse.ArgumentParser(description="Create the human's Gate 1 signing identity (SSH key + allowed_signers).")
    parser.add_argument("--repo-root", default=None, help="Repository root (default: the canonical repo root, shared by worktrees)")
    parser.add_argument("--key", default=os.path.expanduser(DEFAULT_KEY_HINT), help="Private key path (created if missing, reused if present)")
    parser.add_argument("--type", default="ed25519", choices=("ed25519", "ecdsa-sk", "ed25519-sk"), help="Key type for a new key")
    parser.add_argument("--principal", default=DEFAULT_PRINCIPAL, help="Principal name written into allowed_signers")
    parser.add_argument("--force", action="store_true", help="Create a new key even if the key path exists (old keys stay enrolled)")
    parser.add_argument("--check", action="store_true", help="Read-only status report; needs no terminal")
    parser.add_argument("--ssh-keygen-binary", default="ssh-keygen", help=argparse.SUPPRESS)  # test seam
    parser.add_argument("--agent-uid", type=int, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--agent-name", default=None, help=argparse.SUPPRESS)  # test seam: name of the agent account to look up
    parser.add_argument("--no-selftest-prompt", action="store_true", help="Do not offer the signing self-test at the end")
    args = parser.parse_args(argv)

    repo_root = _repo_root(args.repo_root)
    layout = default_layout(repo_root)
    identity = _agent_identity(args, agent_identity)

    if args.check:
        status = identity_status(layout, ssh_keygen_binary=args.ssh_keygen_binary, **identity)
        out("Signing identity status: " + ("ready" if status["ready"] else "NOT set up"))
        cap = status["ssh_keygen"]
        out("  ssh-keygen: " + (f"OpenSSH {cap['version']} (SSHSIG {'supported' if cap['supports_sshsig'] else 'NOT supported'})" if cap["available"] else f"unavailable ({cap['reason']})"))
        out(f"  enrolled keys: {status['enrolled_keys']}    folder: {status['layout']}")
        for key in status["keys"]:
            out(f"  - {key['principal']}  {key['key_type']}  {key['fingerprint']}")
        for failure in status["failures"]:
            out(f"  missing/unsafe: {failure}")
        return 0 if status["ready"] else 1

    is_tty = (tty_fn or (lambda: sys.stdin.isatty() and sys.stdout.isatty()))()
    if not is_tty:
        out("REFUSED: this setup must be run by a human in an interactive terminal (no terminal detected).")
        return 2
    agent_uid = identity.get("agent_uid")
    if agent_uid is None and hasattr(os, "geteuid"):
        try:
            import pwd

            agent_uid = pwd.getpwnam(identity["agent_name"]).pw_uid
        except (KeyError, ImportError):
            agent_uid = None
    if (agent_uid is not None and hasattr(os, "geteuid") and agent_uid == os.geteuid()) or getpass.getuser() == identity["agent_name"]:
        out(f"REFUSED: you are running as the agent account ({identity['agent_name']}). Run this as yourself, the human.")
        return 2

    _banner(out, "Agentic OS - Gate 1 signing identity setup")
    capability = probe_ssh_keygen()
    if not capability.supports_sshsig:
        out(f"REFUSED: ssh-keygen with SSHSIG support (OpenSSH 8.1+) is required: {capability.reason or capability.version}")
        return 3
    out(f"  ssh-keygen OpenSSH {capability.version[0]}.{capability.version[1]}   platform {sys.platform}   repo {repo_root}")
    if args.type.endswith("-sk") and not capability.supports_fido:
        out("REFUSED: this OpenSSH cannot use FIDO hardware keys (needs 8.2+, or Win32-OpenSSH 8.9+ on Windows).")
        return 3

    migrated = migrate_namespaces(layout)
    if migrated:
        out(f"  [MIGRATED] {migrated} allowed_signers line(s) moved from the bare namespaces to the domain-qualified ones (existing keys kept).")

    _banner(out, "Step 1 - signing key")
    key = Path(args.key).expanduser()
    created = False
    if key.exists() and not args.force:
        out(f"  [REUSE] {key} already exists (use --force to create another).")
    else:
        if key.exists() and args.force:
            key = key.with_name(key.name + "-" + str(len(list(key.parent.glob(key.name + "*"))) + 1))
        if _ssh_keygen_generate(key, args.type, out) != 0:
            out("REFUSED: ssh-keygen did not create the key.")
            return 3
        created = True
    if not args.type.endswith("-sk") and not key_is_passphrase_protected(key):
        out("REFUSED: that key has no passphrase, so anyone who can read the file could approve as you. Use a passphrase.")
        if created:
            for leftover in (key, key.with_name(key.name + ".pub")):
                if leftover.exists():
                    leftover.unlink()
            out("  (the new unprotected key was removed; run the setup again and set a passphrase)")
        return 3
    pub_path = key.with_name(key.name + ".pub")
    if not pub_path.exists():
        out(f"REFUSED: {pub_path} (the public key) is missing.")
        return 3
    public_text = pub_path.read_text(encoding="utf-8").strip()

    _banner(out, "Step 2 - identity folder")
    ensure_layout(layout)
    out(f"  {layout.root} (0700)   challenges: {layout.challenge_dir} (0700)")

    _banner(out, "Step 3 - enroll the key")
    if enroll_key(layout, args.principal, public_text):
        out("  [OK] key enrolled in allowed_signers (namespace control-plane@agentic-os.local) and allowed_signers_selftest (namespace control-plane-selftest@agentic-os.local).")
    else:
        out("  [SKIP] this key is already enrolled.")
    out("  Enrolled keys (older keys stay valid):")
    for enrolled in enrolled_keys(layout):
        out(f"    - {enrolled.principal}  {enrolled.key_type}  {enrolled.fingerprint}")

    _banner(out, "Step 4 - isolation check")
    status = identity_status(layout, **identity)
    if status["ready"]:
        out("  [OK] the trust anchors are safely owned and protected from the agent account.")
    else:
        for failure in status["failures"]:
            out(f"  [TODO] {failure}")
        out(f"  To create the unprivileged agent account, run these yourself as an administrator (they are NOT run here):")
        for command in privileged_account_commands(identity["agent_name"]):
            out(f"      {command}")
        out("  See plugins/agent-agentic-os/references/isolation-setup.md.")

    if not args.no_selftest_prompt:
        _banner(out, "Step 5 - signing self-test (optional)")
        answer = input_fn("  Run the interactive signing self-test now? [y/N] ").strip().lower()
        if answer in ("y", "yes"):
            out("  Run:  python3 plugins/agent-agentic-os/scripts/agent_control.py test-signing-mechanics --key " + str(key))

    _banner(out, "Next steps")
    out(f"  Key fingerprint (thumbprint analogue): see the list above. Private key stays in {key} - never share it.")
    out("  Prove it works:  python3 plugins/agent-agentic-os/scripts/agent_control.py test-signing-mechanics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
