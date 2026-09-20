#!/usr/bin/env python3
"""
control_plane/ssh_signing.py
============================

Purpose:
    SSHSIG primitives for Gate 1 (AWAITING_APPROVAL -> APPROVED) of
    auth-ciba-increment-b (issue #639, task T3). A human signs a challenge with an
    SSH key (passphrase-protected ed25519, or a FIDO `-sk` key) and the control plane
    verifies that signature against `allowed_signers` before a transition may commit.

    Design rules implemented here:
    - The challenge bytes are REBUILT from the stored `transition_request` row (and
      the live content hashes), never read from a file on agent-writable disk.
    - Production verification uses ONLY `allowed_signers` and the namespace
      `control-plane`. The self-test uses a separate file and the namespace
      `control-plane-selftest@agentic-os.local`; the two can never satisfy each other.
    - The signature file path is derived from the request row (id + nonce prefix) and
      opened `O_NOFOLLOW`, checked with `fstat`, and read once by descriptor.
    - `ssh-keygen` runs with a scrubbed environment (no `SSH_AUTH_SOCK`), a timeout,
      and its own process group so a hung child cannot hold the caller.
    - OpenSSH does NOT enforce FIDO user-presence/verification when verifying a
      signature (it verifies a flags=0x00 signature as "Good"). This module parses the
      raw SSHSIG blob AFTER `ssh-keygen` accepts it and requires UP, and UV by default,
      rejecting unknown flag bits and any non-SK key that claims SK.

Key Input Dependencies:
    - `ssh-keygen` (OpenSSH 8.1+; FIDO needs 8.2+, or Win32-OpenSSH 8.9+) on PATH
    - control_plane/snapshot.py (content snapshot, revision hash, challenge version)
    - control_plane/isolation_check.py (open_protected_readonly)
    - An open sqlite3 connection with the `transition_request` table (T2 columns)
    - Python stdlib only

Key Functions:
    - parse_openssh_version() / fido_supported() / probe_ssh_keygen() -- runtime
      capability probe (never inferred from the OS version).
    - build_challenge() / derive_challenge_from_row() -- deterministic challenge text.
    - request_file_stem() / write_challenge() / sign_command() / read_signature() --
      per-request file names and safe file handling.
    - verify_signature() / verify_selftest_signature() -- ssh-keygen verification then
      the SK flag policy.
    - parse_sshsig() / enforce_sk_policy() -- raw SSHSIG parsing and the FIDO policy.

Exceptions:
    SigningError (base); ChallengeError, SignatureInvalid, SkPolicyError, SshsigError.
"""

import base64
import binascii
import os
import re
import shutil
import signal
import sqlite3
import struct
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union

from control_plane.isolation_check import open_protected_readonly
from control_plane.snapshot import (
    CHALLENGE_VERSION,
    SnapshotEntry,
    SnapshotError,
    compute_revision_hash,
    snapshot_from_json,
)

# OpenSSH recommends application namespaces of the form NAMESPACE@YOUR.DOMAIN so a key used elsewhere
# cannot collide with this application's signatures. The bare names below are the LEGACY namespaces
# used before the domain-qualified change; they are never accepted for verification, only recognised
# so an old allowed_signers file can be migrated (identity_setup.migrate_namespaces).
NAMESPACE_DOMAIN = "agentic-os.local"
SIGN_NAMESPACE = f"control-plane@{NAMESPACE_DOMAIN}"
SELFTEST_NAMESPACE = f"control-plane-selftest@{NAMESPACE_DOMAIN}"
LEGACY_SIGN_NAMESPACE = "control-plane"
LEGACY_SELFTEST_NAMESPACE = "control-plane-selftest"
MAX_SIGNATURE_BYTES = 65536
DEFAULT_TIMEOUT = 10.0
SK_FLAG_UP = 0x01
SK_FLAG_UV = 0x04
SK_KNOWN_FLAGS = SK_FLAG_UP | SK_FLAG_UV

PathLike = Union[str, "os.PathLike[str]"]


class SigningError(Exception):
    """Base class for this module's failures."""


class ChallengeError(SigningError):
    """The challenge cannot be rebuilt safely from the stored request."""


class SignatureInvalid(SigningError):
    """ssh-keygen did not accept the signature (or could not be run)."""


class SkPolicyError(SigningError):
    """A cryptographically valid FIDO signature violates the presence/verification policy."""


class SshsigError(SigningError):
    """The signature is not a well-formed SSHSIG."""


@dataclass(frozen=True)
class SshCapability:
    """What the installed ssh-keygen can do, from a real probe."""

    available: bool
    version: Optional[Tuple[int, int]]
    supports_sshsig: bool
    supports_fido: bool
    reason: str = ""


@dataclass(frozen=True)
class VerifiedSignature:
    """A signature that ssh-keygen accepted and the policy allowed."""

    principal: str
    fingerprint: str
    key_type: str
    namespace: str
    sk_flags: Optional[int] = None


@dataclass(frozen=True)
class ParsedSignature:
    """Fields read from the raw SSHSIG blob."""

    key_type: str
    namespace: str
    is_sk: bool
    flags: Optional[int]
    counter: Optional[int]

    @property
    def user_present(self) -> Optional[bool]:
        return None if self.flags is None else bool(self.flags & SK_FLAG_UP)

    @property
    def user_verified(self) -> Optional[bool]:
        return None if self.flags is None else bool(self.flags & SK_FLAG_UV)


# ------------------------------------------------------------- capability
def parse_openssh_version(text: str) -> Optional[Tuple[int, int]]:
    """(major, minor) from `ssh -V` output, e.g. 'OpenSSH_for_Windows_9.5p1'; None if absent."""
    match = re.search(r"OpenSSH_(?:for_Windows_)?(\d+)\.(\d+)", text or "")
    return (int(match.group(1)), int(match.group(2))) if match else None


def fido_supported(version: Optional[Tuple[int, int]], platform: str = sys.platform) -> bool:
    """FIDO `-sk` signing: OpenSSH 8.2+; on Windows only Win32-OpenSSH 8.9+."""
    if version is None:
        return False
    if platform.startswith("win"):
        return version >= (8, 9)
    return version >= (8, 2)


def _scrubbed_env() -> dict:
    """Minimal environment for ssh-keygen: no SSH_AUTH_SOCK, no inherited secrets."""
    return {"PATH": os.environ.get("PATH", os.defpath), "LC_ALL": "C"}


def _run(argv: Sequence[str], data: Optional[bytes], timeout: float) -> Tuple[int, bytes, bytes]:
    """Run argv in its own process group with a timeout; kill the whole group on expiry."""
    proc = subprocess.Popen(
        list(argv), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=_scrubbed_env(), start_new_session=True,
    )
    try:
        out, err = proc.communicate(data, timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL) if hasattr(os, "killpg") else proc.kill()
        except (ProcessLookupError, PermissionError):
            proc.kill()
        proc.communicate()
        raise
    return proc.returncode, out, err


def probe_ssh_keygen(binary: str = "ssh-keygen") -> SshCapability:
    """Probe the real binary. Never raises: an unusable binary is reported."""
    resolved = shutil.which(binary) or (binary if os.path.isfile(binary) else None)
    if resolved is None:
        return SshCapability(False, None, False, False, f"{binary} not found")
    ssh = shutil.which("ssh", path=str(Path(resolved).parent)) or shutil.which("ssh")
    if ssh is None:
        return SshCapability(True, None, False, False, "ssh not found next to ssh-keygen; cannot read version")
    try:
        _, out, err = _run([ssh, "-V"], None, 5.0)
    except (subprocess.SubprocessError, OSError) as exc:
        return SshCapability(True, None, False, False, f"version probe failed: {exc}")
    version = parse_openssh_version((out + err).decode("utf-8", "replace"))
    if version is None:
        return SshCapability(True, None, False, False, "could not parse the OpenSSH version")
    return SshCapability(True, version, version >= (8, 1), fido_supported(version), "")


# --------------------------------------------------------------- challenge
def build_challenge(
    *,
    task_id: str,
    request_id: int,
    from_state: str,
    to_state: str,
    occupancy_id: int,
    nonce: str,
    expiration: float,
    revision_hash: str,
    snapshot: Sequence[SnapshotEntry],
    version: str = CHALLENGE_VERSION,
) -> bytes:
    """The exact bytes the human sees and signs: deterministic UTF-8, LF, trailing newline."""
    lines: List[str] = [
        version,
        f"task: {task_id}",
        f"request: {request_id}",
        f"transition: {from_state} -> {to_state}",
        f"occupancy: {occupancy_id}",
        f"nonce: {nonce}",
        f"expires: {int(expiration)}",
        f"revision_hash: {revision_hash}",
        "content:",
    ]
    lines += [f"  {entry.label}: {entry.sha256}" for entry in snapshot]
    lines.append(f"approves: {from_state} -> {to_state}")
    return ("\n".join(lines) + "\n").encode("utf-8")


def derive_challenge_from_row(
    conn: sqlite3.Connection, request_id: int, live_snapshot: Optional[Sequence[SnapshotEntry]] = None
) -> bytes:
    """Rebuild the challenge from the stored request row (and optionally live content).

    Refuses (ChallengeError) an unknown request, one that is not content-bound, an
    unsupported challenge version, or a row whose stored snapshot no longer matches its
    stored `revision_hash` (a partially tampered row). With `live_snapshot` the bytes
    reflect the live files, so a content change also breaks signature verification."""
    row = conn.execute(
        """
        SELECT task_id, from_state, to_state, occupancy_id, nonce, expiration, revision_hash,
               challenge_version, content_snapshot
        FROM transition_request WHERE request_id = ?
        """,
        (request_id,),
    ).fetchone()
    if row is None:
        raise ChallengeError(f"no transition_request {request_id}")
    task_id, from_state, to_state, occupancy_id, nonce, expiration, revision_hash, version, stored_json = row
    if stored_json is None or version is None:
        raise ChallengeError(f"transition_request {request_id} is not bound to reviewed content")
    if version != CHALLENGE_VERSION:
        raise ChallengeError(f"unsupported challenge version {version!r}")
    try:
        stored = snapshot_from_json(stored_json)
    except SnapshotError as exc:
        raise ChallengeError(str(exc)) from exc
    if compute_revision_hash(task_id, from_state, to_state, occupancy_id, nonce, stored) != revision_hash:
        raise ChallengeError(f"transition_request {request_id}: stored content does not match its revision_hash")
    return build_challenge(
        task_id=task_id, request_id=request_id, from_state=from_state, to_state=to_state,
        occupancy_id=occupancy_id, nonce=nonce, expiration=expiration, revision_hash=revision_hash,
        snapshot=tuple(live_snapshot) if live_snapshot is not None else stored, version=version,
    )


# ------------------------------------------------------- files and paths
def request_file_stem(request_id: int, nonce: str) -> str:
    """Per-request file stem derived only from the row: '<request_id>-<nonce prefix>'."""
    if not re.fullmatch(r"[0-9a-f]{16,}", nonce or ""):
        raise ChallengeError("request nonce is not a hex token; refusing to derive a file name from it")
    return f"{int(request_id)}-{nonce[:16]}"


def write_challenge(directory: PathLike, stem: str, data: bytes) -> Path:
    """Create the challenge file `<stem>` (0600) exclusively, never following a planted symlink.

    Named exactly `<stem>` so that `ssh-keygen -Y sign` writes its signature to `<stem>.sig`."""
    path = Path(directory) / stem
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    fd = os.open(path, flags, 0o600)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)
    return path


def sign_command(key_path: PathLike, challenge_path: PathLike) -> List[str]:
    """The exact command the human runs (argv form; use shlex.join to display)."""
    return ["ssh-keygen", "-Y", "sign", "-f", str(key_path), "-n", SIGN_NAMESPACE, str(challenge_path)]


def read_signature(directory: PathLike, stem: str, *, expected_uid: Optional[int] = None) -> bytes:
    """Read `<stem>.sig` once by descriptor: no symlink, owner check, no group/other write."""
    path = Path(directory) / f"{stem}.sig"
    fd = open_protected_readonly(path, expected_uid=expected_uid, forbidden_mode_bits=0o022)
    try:
        if os.fstat(fd).st_size > MAX_SIGNATURE_BYTES:
            from control_plane.isolation_check import IsolationError

            raise IsolationError(f"{path} is larger than {MAX_SIGNATURE_BYTES} bytes")
        return os.read(fd, MAX_SIGNATURE_BYTES + 1)
    finally:
        os.close(fd)


# ----------------------------------------------------------------- SSHSIG
class _Reader:
    """Bounds-checked reader for the SSH wire format."""

    def __init__(self, data: bytes) -> None:
        self._data = data
        self._pos = 0

    def take(self, n: int) -> bytes:
        if n < 0 or self._pos + n > len(self._data):
            raise SshsigError("truncated SSHSIG")
        chunk = self._data[self._pos:self._pos + n]
        self._pos += n
        return chunk

    def u32(self) -> int:
        return struct.unpack(">I", self.take(4))[0]

    def string(self) -> bytes:
        return self.take(self.u32())

    def done(self) -> bool:
        return self._pos == len(self._data)


def _dearmor(data: bytes) -> bytes:
    text = data.decode("ascii", "replace").strip().splitlines()
    if len(text) < 3 or text[0].strip() != "-----BEGIN SSH SIGNATURE-----" or text[-1].strip() != "-----END SSH SIGNATURE-----":
        raise SshsigError("not an armored SSH signature")
    try:
        return base64.b64decode("".join(line.strip() for line in text[1:-1]), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise SshsigError(f"invalid base64 in signature: {exc}") from exc


def parse_sshsig(data: bytes) -> ParsedSignature:
    """Parse an armored SSHSIG. For `sk-*` keys the flags byte and counter are read from the
    signature blob; a non-SK key claiming an SK signature (or the reverse) is rejected."""
    blob = _Reader(_dearmor(data))
    if blob.take(6) != b"SSHSIG":
        raise SshsigError("bad SSHSIG magic")
    if blob.u32() != 1:
        raise SshsigError("unsupported SSHSIG version")
    pub = _Reader(blob.string())
    namespace = blob.string().decode("utf-8", "replace")
    blob.string()  # reserved
    blob.string()  # hash algorithm
    sig = _Reader(blob.string())
    if not blob.done():
        raise SshsigError("trailing data after SSHSIG")
    key_type = pub.string().decode("ascii", "replace")
    sig_type = sig.string().decode("ascii", "replace")
    key_is_sk, sig_is_sk = key_type.startswith("sk-"), sig_type.startswith("sk-")
    if key_is_sk != sig_is_sk or (key_is_sk and key_type != sig_type):
        raise SshsigError(f"key type {key_type!r} does not match signature type {sig_type!r}")
    if not sig_is_sk:
        return ParsedSignature(key_type, namespace, False, None, None)
    sig.string()  # the signature itself
    flags = sig.take(1)[0]
    counter = sig.u32()
    if not sig.done():
        raise SshsigError("trailing data in SK signature")
    return ParsedSignature(key_type, namespace, True, flags, counter)


def enforce_sk_policy(parsed: ParsedSignature, require_uv: bool = True) -> None:
    """FIDO policy: user presence always; user verification by default; no unknown bits."""
    if not parsed.is_sk or parsed.flags is None:
        return
    if parsed.flags & ~SK_KNOWN_FLAGS & 0xFF:
        raise SkPolicyError(f"unknown SK flag bits in {parsed.flags:#04x}")
    if not parsed.flags & SK_FLAG_UP:
        raise SkPolicyError("FIDO signature does not assert user presence (no touch)")
    if require_uv and not parsed.flags & SK_FLAG_UV:
        raise SkPolicyError("FIDO signature does not assert user verification (PIN/biometric)")


# ------------------------------------------------------------ verification
_GOOD = re.compile(r'Good "([^"]+)" signature for (\S+) with (\S+) key (\S+)')


def _verify(
    challenge: bytes,
    signature: bytes,
    *,
    allowed: Path,
    namespace: str,
    principal: Optional[str],
    binary: str,
    timeout: float,
    enforce_flags: bool,
    require_uv: bool,
) -> VerifiedSignature:
    if not Path(allowed).is_file():
        raise SignatureInvalid(f"allowed signers file {allowed} is missing")
    with tempfile.TemporaryDirectory(prefix="cp-verify-") as tmp:
        sig_path = Path(tmp) / "signature"
        fd = os.open(sig_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as handle:
            handle.write(signature)
        try:
            if principal is None:
                code, out, err = _run([binary, "-Y", "find-principals", "-f", str(allowed), "-s", str(sig_path)], None, timeout)
                names = [line.strip() for line in out.decode("utf-8", "replace").splitlines() if line.strip()]
                if code != 0 or not names:
                    raise SignatureInvalid("no enrolled principal matches this signature")
                # find-principals reports only the FIRST principal that carries this key, which may be
                # restricted to another namespace; verify against every principal in the file and let
                # `ssh-keygen -Y verify` decide (the security check stays in OpenSSH).
                for extra in _file_principals(Path(allowed)):
                    if extra not in names:
                        names.append(extra)
            else:
                names = [principal]
            for candidate in names:  # every principal enrolled for this key; the first that verifies wins
                code, out, err = _run(
                    [binary, "-Y", "verify", "-f", str(allowed), "-I", candidate, "-n", namespace, "-s", str(sig_path)],
                    challenge, timeout,
                )
                if code == 0:
                    break
        except subprocess.TimeoutExpired as exc:
            raise SignatureInvalid(f"ssh-keygen timed out after {timeout}s") from exc
        except OSError as exc:
            raise SignatureInvalid(f"ssh-keygen could not be run: {exc}") from exc
    text = (out + err).decode("utf-8", "replace").strip()
    if code != 0:
        raise SignatureInvalid(text or "ssh-keygen rejected the signature")
    match = _GOOD.search(text)
    if not match:
        raise SignatureInvalid(f"unparseable ssh-keygen output: {text[:120]!r}")
    got_namespace, got_principal, key_type, fingerprint = match.groups()
    parsed = parse_sshsig(signature)  # only after ssh-keygen accepted it
    if enforce_flags:
        enforce_sk_policy(parsed, require_uv=require_uv)
    return VerifiedSignature(got_principal, fingerprint, key_type, got_namespace, parsed.flags)


def _file_principals(allowed: Path) -> list:
    """Principal patterns named in an allowed_signers file (first token of each non-comment line)."""
    principals = []
    try:
        for line in allowed.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            token = line.split(None, 1)[0]
            for name in token.split(","):  # a principal list `a,b` names two identities
                if name and not name.startswith("!") and name not in principals:
                    principals.append(name)
    except OSError:
        pass
    return principals


def _has_legacy_namespace(allowed: Path, legacy: str) -> bool:
    """True when the allowed_signers file still carries the exact legacy (bare) namespace option."""
    try:
        return f'namespaces="{legacy}"' in allowed.read_text(encoding="utf-8")
    except OSError:
        return False


def verify_signature(
    challenge: bytes,
    signature: bytes,
    *,
    allowed_signers: PathLike,
    principal: Optional[str] = None,
    require_uv: bool = True,
    binary: str = "ssh-keygen",
    timeout: float = DEFAULT_TIMEOUT,
) -> VerifiedSignature:
    """Production verification: `allowed_signers` + namespace `control-plane@agentic-os.local` only.

    Raises SignatureInvalid when ssh-keygen rejects it (wrong bytes, unenrolled key, wrong
    namespace, timeout, missing file) and SkPolicyError when a valid FIDO signature
    violates the presence/verification policy."""
    try:
        return _verify(
            challenge, signature, allowed=Path(allowed_signers), namespace=SIGN_NAMESPACE, principal=principal,
            binary=binary, timeout=timeout, enforce_flags=True, require_uv=require_uv,
        )
    except SignatureInvalid as exc:
        if _has_legacy_namespace(Path(allowed_signers), LEGACY_SIGN_NAMESPACE):
            raise SignatureInvalid(
                f"{exc} | allowed_signers still uses the legacy namespace '{LEGACY_SIGN_NAMESPACE}'. The human must run "
                "setup_ciba_identity.py (it migrates it to the domain-qualified namespace) and sign again."
            ) from exc
        raise


def verify_selftest_signature(
    challenge: bytes,
    signature: bytes,
    *,
    allowed_signers_selftest: PathLike,
    principal: Optional[str] = None,
    binary: str = "ssh-keygen",
    timeout: float = DEFAULT_TIMEOUT,
) -> VerifiedSignature:
    """Self-test verification: the separate self-test file + namespace `control-plane-selftest@agentic-os.local`.

    Reports the SK flags without enforcing them, so the self-test can show what a key does."""
    return _verify(
        challenge, signature, allowed=Path(allowed_signers_selftest), namespace=SELFTEST_NAMESPACE,
        principal=principal, binary=binary, timeout=timeout, enforce_flags=False, require_uv=False,
    )
