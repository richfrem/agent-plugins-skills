"""
tests/test_domain_namespaces.py
===============================

Purpose:
    Failing-first tests for the domain-qualified signature namespaces (auth-ciba-increment-b, #639):
    OpenSSH recommends application namespaces of the form NAMESPACE@YOUR.DOMAIN, so production is
    `control-plane@agentic-os.local` and the self-test `control-plane-selftest@agentic-os.local`.
    Existing human-owned `allowed_signers*` files enrolled under the bare names are migrated by the
    human-run setup (`migrate_namespaces`, idempotent, mode 0600 kept, no key removed); until then the
    status view reports not-ready and verification fails with an actionable message. A signature made
    under a bare (legacy) namespace never verifies. Real ssh-keygen and real files; nothing mocked.

Key Input Dependencies:
    - control_plane/ssh_signing.py (SIGN_NAMESPACE, SELFTEST_NAMESPACE, verify_signature)
    - control_plane/identity_setup.py (enroll_key, migrate_namespaces, identity_status)
    - scripts/setup_ciba_identity.py; ssh-keygen (OpenSSH 8.1+)

Key Functions (test cases):
    - test_namespaces_are_domain_qualified
    - test_enroll_writes_the_qualified_namespaces
    - test_migrate_rewrites_legacy_lines_in_both_files_and_is_idempotent
    - test_status_flags_a_legacy_namespace_as_not_ready
    - test_verification_with_a_legacy_allowed_signers_is_actionable
    - test_a_signature_under_the_bare_namespace_never_verifies
    - test_setup_migrates_an_existing_identity
"""

import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

import setup_ciba_identity
from control_plane.identity_layout import default_layout
from control_plane.identity_setup import enroll_key, identity_status, migrate_namespaces
from control_plane.ssh_signing import SELFTEST_NAMESPACE, SIGN_NAMESPACE, SignatureInvalid, verify_signature

_FOUND = shutil.which("ssh-keygen")
SSH_KEYGEN = _FOUND or "ssh-keygen"
pytestmark = pytest.mark.skipif(_FOUND is None, reason="ssh-keygen not installed")

LEGACY_SIGN, LEGACY_SELFTEST = "control-plane", "control-plane-selftest"


def _key(path: Path) -> str:
    subprocess.run([SSH_KEYGEN, "-q", "-t", "ed25519", "-N", "", "-C", "t", "-f", str(path)], check=True, capture_output=True)
    return (path.parent / (path.name + ".pub")).read_text().strip()


def _legacy_identity(tmp_path):
    layout = default_layout(tmp_path / "repo")
    layout.root.mkdir(parents=True)
    layout.challenge_dir.mkdir()
    pub = _key(tmp_path / "id").split()
    layout.allowed_signers.write_text(f'op@local namespaces="{LEGACY_SIGN}" {pub[0]} {pub[1]}\n')
    layout.allowed_signers_selftest.write_text(f'op@local namespaces="{LEGACY_SELFTEST}" {pub[0]} {pub[1]}\n')
    for path in (layout.allowed_signers, layout.allowed_signers_selftest):
        os.chmod(path, 0o600)
    for d in (layout.root, layout.challenge_dir):
        os.chmod(d, 0o700)
    return layout, tmp_path / "id"


def _sign(key: Path, namespace: str, data: Path) -> bytes:
    subprocess.run([SSH_KEYGEN, "-Y", "sign", "-f", str(key), "-n", namespace, str(data)], check=True, capture_output=True)
    return Path(str(data) + ".sig").read_bytes()


def test_namespaces_are_domain_qualified():
    assert SIGN_NAMESPACE == "control-plane@agentic-os.local"
    assert SELFTEST_NAMESPACE == "control-plane-selftest@agentic-os.local"
    assert SIGN_NAMESPACE != SELFTEST_NAMESPACE


def test_enroll_writes_the_qualified_namespaces(tmp_path):
    layout = default_layout(tmp_path / "repo")
    enroll_key(layout, "op@local", _key(tmp_path / "id"))
    assert f'namespaces="{SIGN_NAMESPACE}"' in layout.allowed_signers.read_text()
    assert f'namespaces="{SELFTEST_NAMESPACE}"' in layout.allowed_signers_selftest.read_text()


def test_migrate_rewrites_legacy_lines_in_both_files_and_is_idempotent(tmp_path):
    layout, _ = _legacy_identity(tmp_path)
    before = layout.allowed_signers.read_text().split()[-1]
    changed = migrate_namespaces(layout)
    assert changed == 2
    assert f'namespaces="{SIGN_NAMESPACE}"' in layout.allowed_signers.read_text()
    assert f'namespaces="{SELFTEST_NAMESPACE}"' in layout.allowed_signers_selftest.read_text()
    assert layout.allowed_signers.read_text().split()[-1] == before  # the key itself is untouched
    assert stat.S_IMODE(layout.allowed_signers.stat().st_mode) == 0o600
    assert migrate_namespaces(layout) == 0


def test_status_flags_a_legacy_namespace_as_not_ready(tmp_path):
    layout, _ = _legacy_identity(tmp_path)
    status = identity_status(layout, agent_name="no-such-agent-xyz", agent_uid=os.geteuid() + 4242, agent_gids=set())
    assert status["ready"] is False
    assert any("LEGACY_NAMESPACE" in f for f in status["failures"])
    migrate_namespaces(layout)
    status = identity_status(layout, agent_name="no-such-agent-xyz", agent_uid=os.geteuid() + 4242, agent_gids=set())
    assert not any("LEGACY_NAMESPACE" in f for f in status["failures"])


def test_verification_with_a_legacy_allowed_signers_is_actionable(tmp_path):
    layout, key = _legacy_identity(tmp_path)
    data = tmp_path / "challenge"
    data.write_bytes(b"challenge bytes")
    signature = _sign(key, SIGN_NAMESPACE, data)
    with pytest.raises(SignatureInvalid) as excinfo:
        verify_signature(b"challenge bytes", signature, allowed_signers=layout.allowed_signers, principal="op@local")
    assert "setup_ciba_identity.py" in str(excinfo.value)
    migrate_namespaces(layout)
    assert verify_signature(b"challenge bytes", signature, allowed_signers=layout.allowed_signers, principal="op@local").principal == "op@local"


def test_a_signature_under_the_bare_namespace_never_verifies(tmp_path):
    layout, key = _legacy_identity(tmp_path)
    migrate_namespaces(layout)
    data = tmp_path / "challenge"
    data.write_bytes(b"challenge bytes")
    signature = _sign(key, LEGACY_SIGN, data)
    with pytest.raises(SignatureInvalid):
        verify_signature(b"challenge bytes", signature, allowed_signers=layout.allowed_signers, principal="op@local")


def test_setup_migrates_an_existing_identity(tmp_path):
    layout, key = _legacy_identity(tmp_path)
    out = []
    code = setup_ciba_identity.main(
        ["--repo-root", str(tmp_path / "repo"), "--key", str(key), "--no-selftest-prompt"],
        tty_fn=lambda: True, out=lambda s="": out.append(str(s)),
        agent_identity={"agent_name": "agentic-os-test-nonexistent-agent"},
    )
    printed = "\n".join(out)
    assert f'namespaces="{SIGN_NAMESPACE}"' in layout.allowed_signers.read_text()
    assert "migrated" in printed.lower()
