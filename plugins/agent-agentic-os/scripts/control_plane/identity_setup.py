#!/usr/bin/env python3
"""
control_plane/identity_setup.py
===============================

Purpose:
    Logic for creating and inspecting the Gate 1 signing identity (auth-ciba-increment-b, issue
    #639, tasks T11/T12/T13/T14): create the `context/identity/` layout with safe modes, enroll a
    public key into the production `allowed_signers` (namespace control-plane@agentic-os.local) and the SEPARATE
    `allowed_signers_selftest` (namespace control-plane-selftest@agentic-os.local), list enrolled keys with their
    fingerprints, check that a private key is passphrase-protected, and report a read-only status
    (also used by os-init and os-health-check). Stdlib only; uses the real `ssh-keygen`.
    The setup CLI (scripts/setup_ciba_identity.py) is the interactive front end; nothing here
    prompts, and nothing here runs privileged commands.

Key Input Dependencies:
    - control_plane/identity_layout.py, isolation_check.py, ssh_signing.py (namespaces)
    - `ssh-keygen` on PATH (OpenSSH 8.1+)

Key Functions:
    - ensure_layout() -- create context/identity and challenges/ (0700).
    - key_fingerprint() -- SHA256 fingerprint of a public key via ssh-keygen -l.
    - key_is_passphrase_protected() -- True if the private key cannot be read without a passphrase.
    - enroll_key() -- append a key to both allowed_signers files (0600, atomic, never removes).
    - enrolled_keys() -- parse the production allowed_signers.
    - identity_status() -- read-only readiness report (isolation preflight + enrolled keys).
    - privileged_account_commands() -- the account-creation commands to PRINT for the human.
"""

import os
import shlex
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from control_plane.identity_layout import IdentityLayout
from control_plane.isolation_check import DEFAULT_AGENT_NAME, check_isolation
from control_plane.ssh_signing import (
    LEGACY_SELFTEST_NAMESPACE, LEGACY_SIGN_NAMESPACE, SELFTEST_NAMESPACE, SIGN_NAMESPACE, probe_ssh_keygen,
)


@dataclass(frozen=True)
class EnrolledKey:
    """One line of allowed_signers."""

    principal: str
    key_type: str
    fingerprint: str
    namespaces: str


def _run(argv: List[str], data: Optional[bytes] = None) -> subprocess.CompletedProcess:
    return subprocess.run(argv, input=data, capture_output=True, timeout=20)


def ensure_layout(layout: IdentityLayout) -> None:
    """Create the identity directory and its challenge directory, both mode 0700."""
    for directory in (layout.root, layout.challenge_dir):
        directory.mkdir(parents=True, exist_ok=True)
        os.chmod(directory, 0o700)


def key_fingerprint(public_key_text: str, binary: str = "ssh-keygen") -> str:
    """SHA256:... fingerprint of an OpenSSH public key line (`<type> <base64> [comment]`)."""
    result = _run([binary, "-l", "-f", "-"], public_key_text.encode("utf-8"))
    parts = result.stdout.decode("utf-8", "replace").split()
    if result.returncode != 0 or len(parts) < 2:
        raise ValueError(f"not a valid public key: {result.stderr.decode('utf-8', 'replace').strip()}")
    return parts[1]


def key_is_passphrase_protected(private_key: Path, binary: str = "ssh-keygen") -> bool:
    """True if reading the key needs a passphrase (an empty passphrase does not work)."""
    result = _run([binary, "-y", "-P", "", "-f", str(private_key)])
    return result.returncode != 0


def _write_private_file(path: Path, text: str) -> None:
    """Atomically write `text` to `path` with mode 0600 (temp file in the same directory, then replace)."""
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".new")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _line(principal: str, namespace: str, key_type: str, blob: str) -> str:
    return f'{principal} namespaces="{namespace}" {key_type} {blob}\n'


def enroll_key(layout: IdentityLayout, principal: str, public_key_text: str) -> bool:
    """Enroll a public key in BOTH files (production and self-test). Returns False if already enrolled.

    Existing entries are never removed; each file keeps its own single namespace."""
    fields = public_key_text.split()
    if len(fields) < 2:
        raise ValueError("public key must look like '<type> <base64> [comment]'")
    key_type, blob = fields[0], fields[1]
    ensure_layout(layout)
    changed = False
    for path, namespace in ((layout.allowed_signers, SIGN_NAMESPACE), (layout.allowed_signers_selftest, SELFTEST_NAMESPACE)):
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        new_line = _line(principal, namespace, key_type, blob)
        if any(line.split()[-2:] == [key_type, blob] for line in existing.splitlines() if line.strip()):
            os.chmod(path, 0o600)
            continue
        _write_private_file(path, existing + new_line)
        changed = True
    return changed


def migrate_namespaces(layout: IdentityLayout) -> int:
    """Rewrite legacy bare-namespace options (`control-plane`, `control-plane-selftest`) in the human-owned
    allowed_signers files to the domain-qualified namespaces. Idempotent; keeps every key and the 0600 mode;
    returns how many lines changed. Run by the human-run setup, never by the agent."""
    changed = 0
    for path, legacy, current in (
        (layout.allowed_signers, LEGACY_SIGN_NAMESPACE, SIGN_NAMESPACE),
        (layout.allowed_signers_selftest, LEGACY_SELFTEST_NAMESPACE, SELFTEST_NAMESPACE),
    ):
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        old, new = f'namespaces="{legacy}"', f'namespaces="{current}"'
        rewritten = [line.replace(old, new) for line in lines]
        count = sum(1 for a, b in zip(lines, rewritten) if a != b)
        if count:
            _write_private_file(path, "".join(rewritten))
            changed += count
    return changed


def _legacy_namespace_failures(layout: IdentityLayout) -> List[str]:
    failures: List[str] = []
    for path, legacy in ((layout.allowed_signers, LEGACY_SIGN_NAMESPACE), (layout.allowed_signers_selftest, LEGACY_SELFTEST_NAMESPACE)):
        if path.exists() and f'namespaces="{legacy}"' in path.read_text(encoding="utf-8"):
            failures.append(
                f"LEGACY_NAMESPACE: {path.name} still uses the bare namespace '{legacy}'; run setup_ciba_identity.py to migrate it."
            )
    return failures


def enrolled_keys(layout: IdentityLayout, binary: str = "ssh-keygen") -> List[EnrolledKey]:
    """Parse the production allowed_signers into (principal, type, fingerprint, namespaces)."""
    if not layout.allowed_signers.exists():
        return []
    keys: List[EnrolledKey] = []
    for line in layout.allowed_signers.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        tokens = shlex.split(line)
        if len(tokens) < 4:
            continue
        principal, namespaces_opt, key_type, blob = tokens[0], tokens[1], tokens[-2], tokens[-1]
        namespaces = namespaces_opt.split("=", 1)[1] if namespaces_opt.startswith("namespaces=") else ""
        keys.append(EnrolledKey(principal, key_type, key_fingerprint(f"{key_type} {blob}", binary), namespaces))
    return keys


def _verification_failures(layout: IdentityLayout, keys: List[EnrolledKey], capability: Any) -> List[str]:
    """Why cryptographic verification could not work even if the files exist: no usable ssh-keygen, an
    allowed_signers with no parseable key, or keys scoped to a namespace the gates never sign under."""
    failures: List[str] = []
    if not capability.available:
        failures.append(f"SSH_KEYGEN_UNAVAILABLE: {capability.reason or 'ssh-keygen was not found'}; install OpenSSH (>= 8.1).")
    elif not capability.supports_sshsig:
        found = ".".join(str(n) for n in capability.version) if capability.version else "unknown version"
        failures.append(f"SSHSIG_UNSUPPORTED: {found} cannot verify SSHSIG signatures ({capability.reason or 'OpenSSH >= 8.1 is required'}).")
    if layout.allowed_signers.exists() and not keys and capability.available:
        failures.append(f"NO_ENROLLED_KEYS: {layout.allowed_signers.name} contains no parseable public key; a human runs setup_ciba_identity.py to enroll one.")
    for key in keys:
        if SIGN_NAMESPACE not in key.namespaces.split(","):
            failures.append(
                f"NAMESPACE_MISMATCH: {key.principal} ({key.fingerprint}) is scoped to '{key.namespaces or 'no namespace'}', "
                f"not '{SIGN_NAMESPACE}', so no gate signature can verify against it."
            )
    return failures


def identity_status(layout: IdentityLayout, *, ssh_keygen_binary: str = "ssh-keygen", **identity: Any) -> Dict[str, Any]:
    """Read-only readiness report for cryptographic verification: isolation preflight failures, enrolled keys,
    the ssh-keygen capability and whether allowed_signers can actually verify a gate signature. Never writes."""
    result = check_isolation(
        allowed_signers=layout.allowed_signers, allowed_signers_selftest=layout.allowed_signers_selftest,
        challenge_dir=layout.challenge_dir, environ={}, **identity,
    )
    capability = probe_ssh_keygen(binary=ssh_keygen_binary)
    keys = enrolled_keys(layout, binary=ssh_keygen_binary) if capability.available and layout.allowed_signers.exists() else []
    failures = (
        [f"{f.code}: {f.message}" for f in result.failures]
        + _legacy_namespace_failures(layout)
        + _verification_failures(layout, keys, capability)
    )
    return {
        "ready": result.ok and bool(keys) and not failures,
        "enrolled_keys": len(keys),
        "keys": [k.__dict__ for k in keys],
        "failures": failures,
        "layout": str(layout.root),
        "ssh_keygen": {
            "available": capability.available,
            "supports_sshsig": capability.supports_sshsig,
            "version": ".".join(str(n) for n in capability.version) if capability.version else None,
            "reason": capability.reason,
        },
    }


def privileged_account_commands(agent_name: str = DEFAULT_AGENT_NAME, platform: str = sys.platform) -> List[str]:
    """Commands the HUMAN runs (as an administrator) to create the unprivileged agent account.
    They are printed by the setup CLI and never executed by it."""
    if platform == "darwin":
        return [
            f"sudo sysadminctl -addUser {agent_name} -fullName 'Agentic OS agent' -password -",
            f"# then run the agent as that account, e.g.: sudo -u {agent_name} <agent command>",
        ]
    if platform.startswith("win"):
        return [
            f"net user {agent_name} * /add",
            f"# run the agent as that account, e.g.: runas /user:{agent_name} <agent command>",
        ]
    return [f"sudo useradd --create-home --shell /bin/bash {agent_name}", f"# run the agent with: sudo -u {agent_name} <agent command>"]
