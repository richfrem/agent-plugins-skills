"""
tests/test_ssh_signing.py
=========================

Purpose:
    Failing-first acceptance tests for T3 (auth-ciba-increment-b, issue #639):
    control_plane/ssh_signing.py, the SSHSIG primitives behind Gate 1. Spec
    section 4 cases 2, 7, 8, 23 (signature half). Everything uses the real
    `ssh-keygen` binary, throwaway keys in tmp_path and real files; nothing is
    mocked. FIDO cases use synthetic `sk-ssh-ed25519` signatures built with a
    software key (the `cryptography` library, dev-only): `ssh-keygen -Y verify`
    genuinely accepts them, which is how the tests show that OpenSSH itself does
    NOT enforce user-presence/user-verification and that our policy must.
    Live hardware touch remains a documented human step (case 6b / T12).

Key Input Dependencies:
    - control_plane/ssh_signing.py (module under test)
    - control_plane/isolation_check.py (open_protected_readonly, used for the
      signature file)
    - control_plane/transition_request.py + snapshot.py (real request rows)
    - ssh-keygen (OpenSSH 8.1+) on PATH; `cryptography` for synthetic SK signatures

Key Functions (test cases):
    - test_parse_openssh_version_* / test_fido_supported_rules / test_probe_*
    - test_challenge_* (deterministic bytes, content, tamper detection, rebuild from row)
    - test_request_file_stem_* / test_write_challenge_* / test_sign_command
    - test_read_signature_* (O_NOFOLLOW, owner, mode, size)
    - test_verify_* (real signatures: good, wrong bytes, wrong key, wrong namespace,
      env scrub, timeout, principal discovery, selftest separation)
    - test_sk_* (flags policy against ssh-keygen-verified synthetic SK signatures)
    - test_parse_sshsig_* (armor and blob parsing, malformed input)
"""

import base64
import hashlib
import os
import shutil
import shlex
import stat
import struct
import subprocess
import sys
import time
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from agent_control import ControlPlane
from control_plane.isolation_check import IsolationError
from control_plane.snapshot import SnapshotEntry, build_snapshot, gate1_artifact_paths, snapshot_to_json
from control_plane.ssh_signing import (
    SELFTEST_NAMESPACE,
    SIGN_NAMESPACE,
    ChallengeError,
    SignatureInvalid,
    SkPolicyError,
    SshsigError,
    build_challenge,
    derive_challenge_from_row,
    fido_supported,
    parse_openssh_version,
    parse_sshsig,
    probe_ssh_keygen,
    read_signature,
    request_file_stem,
    sign_command,
    verify_selftest_signature,
    verify_signature,
    write_challenge,
)
from control_plane.transition_request import create_transition_request

TASK = "ssh-task-001"
_FOUND = shutil.which("ssh-keygen")
SSH_KEYGEN: str = _FOUND or "ssh-keygen"

pytestmark = pytest.mark.skipif(_FOUND is None, reason="ssh-keygen not installed")


# ----------------------------------------------------------------- helpers
def _keypair(directory: Path, name: str = "id", passphrase: str = ""):
    key = directory / name
    subprocess.run(
        [SSH_KEYGEN, "-q", "-t", "ed25519", "-N", passphrase, "-C", f"{name}@test", "-f", str(key)],
        check=True, capture_output=True,
    )
    return key, (directory / f"{name}.pub").read_text().split()


def _allowed(path: Path, principal: str, pub_fields, namespaces: str = SIGN_NAMESPACE):
    path.write_text(f'{principal} namespaces="{namespaces}" {pub_fields[0]} {pub_fields[1]}\n')
    os.chmod(path, 0o600)
    return path


def _sign(key: Path, message: bytes, workdir: Path, namespace: str = SIGN_NAMESPACE) -> bytes:
    target = workdir / "challenge"
    target.write_bytes(message)
    subprocess.run(
        [SSH_KEYGEN, "-Y", "sign", "-f", str(key), "-n", namespace, str(target)],
        check=True, capture_output=True,
    )
    return (workdir / "challenge.sig").read_bytes()


def _lp(b: bytes) -> bytes:
    return struct.pack(">I", len(b)) + b


def _armor(blob: bytes) -> bytes:
    b64 = base64.b64encode(blob).decode()
    body = "\n".join(b64[i:i + 70] for i in range(0, len(b64), 70))
    return f"-----BEGIN SSH SIGNATURE-----\n{body}\n-----END SSH SIGNATURE-----\n".encode()


def _sk_signature(message: bytes, flags: int, namespace: str = SIGN_NAMESPACE, tamper_flags: bool = False):
    """A valid synthetic sk-ssh-ed25519 SSHSIG plus its allowed_signers key fields.

    Signs application_hash || flags || counter || H(SSHSIG blob), which is what a real
    FIDO2 authenticator signs, using a software key. The signature blob carries the
    flags byte after the signature (optionally flipped afterwards)."""
    from cryptography.hazmat.primitives import serialization as ser
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    private = Ed25519PrivateKey.generate()
    pub = private.public_key().public_bytes(ser.Encoding.Raw, ser.PublicFormat.Raw)
    application = b"ssh:"
    key_type = b"sk-ssh-ed25519@openssh.com"
    pub_blob = _lp(key_type) + _lp(pub) + _lp(application)
    counter = 7
    message_hash = hashlib.sha512(message).digest()
    signed_data = b"SSHSIG" + _lp(namespace.encode()) + _lp(b"") + _lp(b"sha512") + _lp(message_hash)
    to_sign = hashlib.sha256(application).digest() + bytes([flags]) + struct.pack(">I", counter) + hashlib.sha256(signed_data).digest()
    signature = private.sign(to_sign)
    carried = flags ^ 0x01 if tamper_flags else flags
    sig_blob = _lp(key_type) + _lp(signature) + bytes([carried]) + struct.pack(">I", counter)
    blob = b"SSHSIG" + struct.pack(">I", 1) + _lp(pub_blob) + _lp(namespace.encode()) + _lp(b"") + _lp(b"sha512") + _lp(sig_blob)
    return _armor(blob), ("sk-ssh-ed25519@openssh.com", base64.b64encode(pub_blob).decode())


@pytest.fixture
def work(tmp_path):
    d = tmp_path / "work"
    d.mkdir()
    return d


@pytest.fixture
def enrolled(tmp_path):
    """A throwaway key enrolled in a production allowed_signers (namespace control-plane@agentic-os.local)."""
    d = tmp_path / "keys"
    d.mkdir()
    key, pub = _keypair(d)
    allowed = _allowed(d / "allowed_signers", "op@local", pub)
    return {"key": key, "pub": pub, "allowed": allowed, "dir": d}


# ------------------------------------------------------------ capability
@pytest.mark.parametrize(
    "text,expected",
    [
        ("OpenSSH_10.0p2, LibreSSL 3.3.6", (10, 0)),
        ("OpenSSH_for_Windows_9.5p1, LibreSSL 3.8.2", (9, 5)),
        ("OpenSSH_8.1p1 Ubuntu-1", (8, 1)),
        ("OpenSSH_7.7p1, OpenSSL 1.0.2", (7, 7)),
        ("not an ssh version", None),
        ("", None),
    ],
)
def test_parse_openssh_version(text, expected):
    assert parse_openssh_version(text) == expected


@pytest.mark.parametrize(
    "version,platform,expected",
    [
        ((8, 1), "linux", False),
        ((8, 2), "linux", True),
        ((10, 0), "darwin", True),
        ((8, 8), "win32", False),
        ((8, 9), "win32", True),
        ((9, 5), "win32", True),
        (None, "linux", False),
    ],
)
def test_fido_supported_rules(version, platform, expected):
    assert fido_supported(version, platform) is expected


def test_probe_real_ssh_keygen():
    cap = probe_ssh_keygen()
    if not cap.available or cap.version is None or cap.version < (8, 1):
        pytest.skip("installed OpenSSH is older than 8.1")
    assert cap.supports_sshsig is True
    assert isinstance(cap.version, tuple)


def test_probe_missing_binary_is_reported_not_raised():
    cap = probe_ssh_keygen(binary="/nonexistent/ssh-keygen-xyz")
    assert cap.available is False
    assert cap.supports_sshsig is False
    assert cap.reason


# ------------------------------------------------------------- challenge
def _fields(**over):
    base = dict(
        task_id=TASK, request_id=7, from_state="AWAITING_APPROVAL", to_state="APPROVED",
        occupancy_id=3, nonce="a" * 32, expiration=1789000000.5, revision_hash="b" * 64,
        snapshot=(SnapshotEntry("spec", "1" * 64), SnapshotEntry("plan", "2" * 64)),
    )
    base.update(over)
    return base


def test_challenge_is_deterministic_and_complete():
    a = build_challenge(**_fields())
    assert a == build_challenge(**_fields())
    text = a.decode("utf-8")
    assert text.startswith("control-plane-challenge/1\n")
    assert text.endswith("\n") and "\r" not in text
    for needle in (TASK, "AWAITING_APPROVAL", "APPROVED", "a" * 32, "b" * 64, "1" * 64, "2" * 64):
        assert needle in text
    # auth-ciba-increment-b (2026-09-20): the signature IS the authority. The challenge no longer carries
    # pre-typed "decision answers" for a human to sign, and there is no assertion table to import.
    for removed in ("human_implementation_approval", "guidance_compliance_confirmation", "actor: human", "Yes, approve implementation"):
        assert removed not in text, removed
    import control_plane.ssh_signing as _ssh_signing

    assert not hasattr(_ssh_signing, "GATE1_ASSERTIONS") and not hasattr(_ssh_signing, "GATE1_DECISION_TYPES")


@pytest.mark.parametrize(
    "change",
    [
        dict(task_id="other"), dict(request_id=8), dict(from_state="PLAN_REVIEW"),
        dict(to_state="DONE"), dict(occupancy_id=4), dict(nonce="c" * 32),
        dict(expiration=1789000001.0), dict(revision_hash="d" * 64),
        dict(snapshot=(SnapshotEntry("spec", "9" * 64), SnapshotEntry("plan", "2" * 64))),
    ],
)
def test_challenge_changes_when_any_field_changes(change):
    assert build_challenge(**_fields(**change)) != build_challenge(**_fields())


@pytest.fixture
def request_row(tmp_path):
    folder = tmp_path / "repo" / "docs" / "plans" / "work-tasks" / TASK
    folder.mkdir(parents=True)
    (folder / f"{TASK}-spec.md").write_text("spec v1\n")
    (folder / f"{TASK}-implementation-plan.md").write_text("plan v1\n")
    db_path = tmp_path / "cp.db"
    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    cp.create_task(task_id=TASK, title="ssh signing", runtime_tool="test")
    import sqlite3

    conn = sqlite3.connect(db_path)
    snapshot = build_snapshot(gate1_artifact_paths(tmp_path / "repo", TASK))
    record = create_transition_request(
        conn, task_id=TASK, from_state="AWAITING_APPROVAL", to_state="APPROVED",
        occupancy_id=1, content_snapshot=snapshot,
    )
    return {"conn": conn, "record": record, "snapshot": snapshot, "repo": tmp_path / "repo"}


def test_challenge_rebuilt_from_row_matches_build(request_row):
    rec = request_row["record"]
    from_row = derive_challenge_from_row(request_row["conn"], rec.request_id)
    expected = build_challenge(
        task_id=TASK, request_id=rec.request_id, from_state="AWAITING_APPROVAL", to_state="APPROVED",
        occupancy_id=1, nonce=rec.nonce, expiration=rec.expiration, revision_hash=rec.revision_hash,
        snapshot=request_row["snapshot"],
    )
    assert from_row == expected


def test_challenge_from_row_uses_live_content(request_row):
    rec = request_row["record"]
    stored = derive_challenge_from_row(request_row["conn"], rec.request_id)
    changed = (SnapshotEntry("spec", "f" * 64), request_row["snapshot"][1])
    live = derive_challenge_from_row(request_row["conn"], rec.request_id, live_snapshot=changed)
    assert live != stored and ("f" * 64) in live.decode()


def test_challenge_from_row_detects_tampered_snapshot(request_row):
    rec = request_row["record"]
    forged = snapshot_to_json((SnapshotEntry("spec", "0" * 64), request_row["snapshot"][1]))
    request_row["conn"].execute("UPDATE transition_request SET content_snapshot = ? WHERE request_id = ?", (forged, rec.request_id))
    request_row["conn"].commit()
    with pytest.raises(ChallengeError):
        derive_challenge_from_row(request_row["conn"], rec.request_id)


def test_challenge_from_row_detects_tampered_hash(request_row):
    rec = request_row["record"]
    request_row["conn"].execute("UPDATE transition_request SET revision_hash = ? WHERE request_id = ?", ("e" * 64, rec.request_id))
    request_row["conn"].commit()
    with pytest.raises(ChallengeError):
        derive_challenge_from_row(request_row["conn"], rec.request_id)


def test_challenge_from_row_requires_bound_content(request_row):
    legacy = create_transition_request(
        request_row["conn"], task_id=TASK, from_state="AWAITING_APPROVAL", to_state="APPROVED", occupancy_id=1,
    )
    with pytest.raises(ChallengeError):
        derive_challenge_from_row(request_row["conn"], legacy.request_id)


def test_challenge_from_row_unknown_request(request_row):
    with pytest.raises(ChallengeError):
        derive_challenge_from_row(request_row["conn"], 99999)


# ------------------------------------------------------ paths and files
def test_request_file_stem_is_derived_from_the_row(request_row):
    rec = request_row["record"]
    stem = request_file_stem(rec.request_id, rec.nonce)
    assert stem == f"{rec.request_id}-{rec.nonce[:16]}"
    other = create_transition_request(
        request_row["conn"], task_id=TASK, from_state="AWAITING_APPROVAL", to_state="APPROVED",
        occupancy_id=1, content_snapshot=request_row["snapshot"],
    )
    assert request_file_stem(other.request_id, other.nonce) != stem


def test_write_challenge_creates_private_file_once(work):
    os.chmod(work, 0o700)
    path = write_challenge(work, "7-abcdef", b"bytes\n")
    # Named exactly <stem>: `ssh-keygen -Y sign <file>` writes <file>.sig, i.e. <stem>.sig,
    # which is where read_signature() looks.
    assert path == work / "7-abcdef"
    assert path.read_bytes() == b"bytes\n"
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    with pytest.raises(FileExistsError):
        write_challenge(work, "7-abcdef", b"other\n")


def test_write_challenge_refuses_preplanted_symlink(work, tmp_path):
    os.chmod(work, 0o700)
    target = tmp_path / "victim"
    target.write_text("keep")
    (work / "7-abcdef").symlink_to(target)
    with pytest.raises(OSError):
        write_challenge(work, "7-abcdef", b"x")
    assert target.read_text() == "keep"


def test_sign_command_is_exact(work):
    argv = sign_command(Path("/home/human/.ssh/id_ed25519"), work / "7-abc.challenge")
    assert argv[:2] == ["ssh-keygen", "-Y"] and argv[2] == "sign"
    assert argv[argv.index("-n") + 1] == SIGN_NAMESPACE
    assert argv[argv.index("-f") + 1] == "/home/human/.ssh/id_ed25519"
    assert argv[-1] == str(work / "7-abc.challenge")
    assert shlex.split(shlex.join(argv)) == argv


# -------------------------------------------------------- signature read
def test_read_signature_reads_by_fd(work):
    os.chmod(work, 0o700)
    sig = work / "7-abc.sig"
    sig.write_bytes(b"-----BEGIN SSH SIGNATURE-----\nabc\n-----END SSH SIGNATURE-----\n")
    os.chmod(sig, 0o644)
    assert read_signature(work, "7-abc").startswith(b"-----BEGIN SSH SIGNATURE-----")


def test_read_signature_rejects_symlink(work, tmp_path):
    os.chmod(work, 0o700)
    real = tmp_path / "real.sig"
    real.write_bytes(b"x")
    os.chmod(real, 0o600)
    (work / "7-abc.sig").symlink_to(real)
    with pytest.raises(IsolationError):
        read_signature(work, "7-abc")


@pytest.mark.parametrize("mode", [0o666, 0o664, 0o646])
def test_read_signature_rejects_group_or_other_writable(work, mode):
    os.chmod(work, 0o700)
    sig = work / "7-abc.sig"
    sig.write_bytes(b"x")
    os.chmod(sig, mode)
    with pytest.raises(IsolationError):
        read_signature(work, "7-abc")


def test_read_signature_rejects_wrong_owner(work):
    os.chmod(work, 0o700)
    sig = work / "7-abc.sig"
    sig.write_bytes(b"x")
    os.chmod(sig, 0o600)
    with pytest.raises(IsolationError):
        read_signature(work, "7-abc", expected_uid=os.geteuid() + 1)


def test_read_signature_rejects_oversized_file(work):
    os.chmod(work, 0o700)
    sig = work / "7-abc.sig"
    sig.write_bytes(b"A" * 70000)
    os.chmod(sig, 0o600)
    with pytest.raises(IsolationError):
        read_signature(work, "7-abc")


def test_read_signature_rejects_missing_file(work):
    os.chmod(work, 0o700)
    with pytest.raises(IsolationError):
        read_signature(work, "7-abc")


# ----------------------------------------------------- real verification
def test_verify_good_signature(enrolled, work):
    challenge = build_challenge(**_fields())
    sig = _sign(enrolled["key"], challenge, work)
    verified = verify_signature(challenge, sig, allowed_signers=enrolled["allowed"], principal="op@local")
    assert verified.principal == "op@local"
    assert verified.fingerprint.startswith("SHA256:")
    assert verified.key_type.upper().startswith("ED25519")
    assert verified.namespace == SIGN_NAMESPACE
    assert verified.sk_flags is None


def test_verify_wrong_bytes_denied(enrolled, work):
    sig = _sign(enrolled["key"], build_challenge(**_fields()), work)
    with pytest.raises(SignatureInvalid):
        verify_signature(build_challenge(**_fields(nonce="z" * 32)), sig, allowed_signers=enrolled["allowed"], principal="op@local")


def test_verify_unenrolled_key_denied(enrolled, work, tmp_path):
    other = tmp_path / "other"
    other.mkdir()
    key2, _ = _keypair(other, "attacker")
    challenge = build_challenge(**_fields())
    sig = _sign(key2, challenge, work)
    with pytest.raises(SignatureInvalid):
        verify_signature(challenge, sig, allowed_signers=enrolled["allowed"], principal="op@local")


def test_verify_other_namespace_denied(enrolled, work):
    challenge = build_challenge(**_fields())
    sig = _sign(enrolled["key"], challenge, work, namespace=SELFTEST_NAMESPACE)
    with pytest.raises(SignatureInvalid):
        verify_signature(challenge, sig, allowed_signers=enrolled["allowed"], principal="op@local")


def test_verify_requires_production_namespace_on_the_signer_line(enrolled, work):
    """A signer line scoped only to the self-test namespace can never approve."""
    _allowed(enrolled["allowed"], "op@local", enrolled["pub"], namespaces=SELFTEST_NAMESPACE)
    challenge = build_challenge(**_fields())
    sig = _sign(enrolled["key"], challenge, work)
    with pytest.raises(SignatureInvalid):
        verify_signature(challenge, sig, allowed_signers=enrolled["allowed"], principal="op@local")


def test_verify_missing_allowed_signers_denied(enrolled, work, tmp_path):
    challenge = build_challenge(**_fields())
    sig = _sign(enrolled["key"], challenge, work)
    with pytest.raises(SignatureInvalid):
        verify_signature(challenge, sig, allowed_signers=tmp_path / "nope", principal="op@local")


def test_verify_discovers_principal_when_not_given(enrolled, work):
    challenge = build_challenge(**_fields())
    sig = _sign(enrolled["key"], challenge, work)
    assert verify_signature(challenge, sig, allowed_signers=enrolled["allowed"]).principal == "op@local"


def test_verify_garbage_signature_is_signature_invalid(enrolled):
    with pytest.raises(SignatureInvalid):
        verify_signature(b"x\n", b"not a signature", allowed_signers=enrolled["allowed"], principal="op@local")


def test_verify_scrubs_ssh_auth_sock(enrolled, work, tmp_path, monkeypatch):
    dump = tmp_path / "env.dump"
    wrapper = tmp_path / "ssh-keygen-wrapper"
    wrapper.write_text(f'#!/bin/sh\nenv > "{dump}"\nexec "{SSH_KEYGEN}" "$@"\n')
    os.chmod(wrapper, 0o755)
    monkeypatch.setenv("SSH_AUTH_SOCK", "/tmp/should-not-leak.sock")
    challenge = build_challenge(**_fields())
    sig = _sign(enrolled["key"], challenge, work)
    verify_signature(challenge, sig, allowed_signers=enrolled["allowed"], principal="op@local", binary=str(wrapper))
    assert dump.exists()
    assert "SSH_AUTH_SOCK" not in dump.read_text()


def test_verify_times_out_instead_of_hanging(enrolled, work, tmp_path):
    slow = tmp_path / "slow-ssh-keygen"
    slow.write_text("#!/bin/sh\nsleep 5\n")
    os.chmod(slow, 0o755)
    challenge = build_challenge(**_fields())
    sig = _sign(enrolled["key"], challenge, work)
    started = time.monotonic()
    with pytest.raises(SignatureInvalid):
        verify_signature(challenge, sig, allowed_signers=enrolled["allowed"], principal="op@local", binary=str(slow), timeout=0.5)
    assert time.monotonic() - started < 3.5


def test_selftest_and_production_are_separate(enrolled, work, tmp_path):
    """Self-test signatures verify only against the self-test file; production only against production."""
    selftest_allowed = _allowed(tmp_path / "keys" / "allowed_signers_selftest", "op@local", enrolled["pub"], namespaces=SELFTEST_NAMESPACE)
    challenge = b"selftest challenge\n"
    selftest_sig = _sign(enrolled["key"], challenge, work, namespace=SELFTEST_NAMESPACE)
    assert verify_selftest_signature(challenge, selftest_sig, allowed_signers_selftest=selftest_allowed, principal="op@local").namespace == SELFTEST_NAMESPACE
    with pytest.raises(SignatureInvalid):
        verify_signature(challenge, selftest_sig, allowed_signers=enrolled["allowed"], principal="op@local")
    prod_dir = work / "prod"
    prod_dir.mkdir()
    prod_sig = _sign(enrolled["key"], challenge, prod_dir, namespace=SIGN_NAMESPACE)
    with pytest.raises(SignatureInvalid):
        verify_selftest_signature(challenge, prod_sig, allowed_signers_selftest=selftest_allowed, principal="op@local")


# ----------------------------------------------------- FIDO flag policy
def _sk_verify(tmp_path, flags, **kwargs):
    message = build_challenge(**_fields())
    armored, (kt, b64) = _sk_signature(message, flags, tamper_flags=kwargs.pop("tamper_flags", False))
    allowed = tmp_path / f"allowed_sk_{flags:02x}"
    allowed.write_text(f'op@local namespaces="{SIGN_NAMESPACE}" {kt} {b64}\n')
    os.chmod(allowed, 0o600)
    return verify_signature(message, armored, allowed_signers=allowed, principal="op@local", **kwargs)


def test_sk_up_and_uv_accepted(tmp_path):
    verified = _sk_verify(tmp_path, 0x05)
    assert verified.sk_flags == 0x05
    assert verified.key_type.upper().startswith("ED25519-SK")


def test_sk_no_touch_rejected_even_though_openssh_accepts_it(tmp_path):
    """The point of the policy: ssh-keygen says Good for flags=0x00; we must refuse."""
    with pytest.raises(SkPolicyError):
        _sk_verify(tmp_path, 0x00)


def test_sk_up_without_uv_rejected_by_default(tmp_path):
    with pytest.raises(SkPolicyError):
        _sk_verify(tmp_path, 0x01)


def test_sk_up_without_uv_allowed_when_policy_relaxed(tmp_path):
    assert _sk_verify(tmp_path, 0x01, require_uv=False).sk_flags == 0x01


def test_sk_uv_without_up_always_rejected(tmp_path):
    with pytest.raises(SkPolicyError):
        _sk_verify(tmp_path, 0x04, require_uv=False)


def test_sk_unknown_flag_bits_rejected(tmp_path):
    with pytest.raises(SkPolicyError):
        _sk_verify(tmp_path, 0x0D)


def test_sk_flags_flipped_after_signing_fail_verification(tmp_path):
    with pytest.raises(SignatureInvalid):
        _sk_verify(tmp_path, 0x05, tamper_flags=True)


# --------------------------------------------------------- SSHSIG parser
def test_parse_sshsig_software_key(enrolled, work):
    sig = _sign(enrolled["key"], b"m\n", work)
    parsed = parse_sshsig(sig)
    assert parsed.key_type == "ssh-ed25519"
    assert parsed.namespace == SIGN_NAMESPACE
    assert parsed.is_sk is False and parsed.flags is None


def test_parse_sshsig_sk_flags():
    armored, _ = _sk_signature(b"m\n", 0x05)
    parsed = parse_sshsig(armored)
    assert parsed.is_sk is True
    assert parsed.flags == 0x05
    assert parsed.user_present and parsed.user_verified


def test_parse_sshsig_rejects_non_sk_key_claiming_sk_signature():
    key_type = b"ssh-ed25519"
    pub_blob = _lp(key_type) + _lp(b"\x00" * 32)
    sig_blob = _lp(b"sk-ssh-ed25519@openssh.com") + _lp(b"\x00" * 64) + b"\x05" + struct.pack(">I", 1)
    blob = b"SSHSIG" + struct.pack(">I", 1) + _lp(pub_blob) + _lp(b"control-plane") + _lp(b"") + _lp(b"sha512") + _lp(sig_blob)
    with pytest.raises(SshsigError):
        parse_sshsig(_armor(blob))


@pytest.mark.parametrize(
    "bad",
    [
        b"",
        b"garbage",
        b"-----BEGIN SSH SIGNATURE-----\n!!!notbase64!!!\n-----END SSH SIGNATURE-----\n",
        b"-----BEGIN SSH SIGNATURE-----\n" + base64.b64encode(b"NOTSSH" + b"\x00" * 20) + b"\n-----END SSH SIGNATURE-----\n",
        b"-----BEGIN SSH SIGNATURE-----\n" + base64.b64encode(b"SSHSIG\x00\x00\x00\x01\x00\x00") + b"\n-----END SSH SIGNATURE-----\n",
    ],
)
def test_parse_sshsig_rejects_malformed_input(bad):
    with pytest.raises(SshsigError):
        parse_sshsig(bad)
