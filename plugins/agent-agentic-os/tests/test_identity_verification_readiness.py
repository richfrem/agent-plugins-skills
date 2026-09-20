"""
tests/test_identity_verification_readiness.py
=============================================

Purpose:
    Failing-first acceptance tests for Item C (auth-ciba-increment-b, 2026-09-20): os-init and os-health-check
    report whether cryptographic verification can actually WORK, not just whether files exist. Readiness means
    (1) an `ssh-keygen` that supports SSHSIG (OpenSSH >= 8.1) is available, (2) `allowed_signers` parses to at
    least one key, and (3) every enrolled entry is scoped to the production namespace (otherwise no signature
    could ever verify). os-init and the health check stay READ-ONLY reporters: they never create keys or write
    `allowed_signers*` (an agent-run surface that enrolled a key would be an enrollment path for an agent).
    Real ssh-keygen, real files in tmp_path; the missing-binary case points at a path that does not exist.

Key Input Dependencies:
    - control_plane/identity_setup.py (identity_status, enroll_key), identity_layout.py, ssh_signing.py
    - scripts/setup_ciba_identity.py (--check), scripts/init_agentic_os.py (signing_identity_notice)

Key Functions (test cases):
    - test_status_reports_ssh_keygen_capability
    - test_missing_ssh_keygen_makes_status_not_ready_with_an_actionable_failure
    - test_allowed_signers_without_any_key_is_not_ready
    - test_key_scoped_to_the_wrong_namespace_is_not_ready
    - test_check_cli_prints_the_ssh_keygen_line_and_exit_code
    - test_init_notice_reports_ssh_keygen_readiness_without_writing
    - test_health_check_skill_asserts_verification_readiness_not_actor_strings
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parent.parent
_scripts_dir = str(PLUGIN / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from control_plane.identity_layout import default_layout
from control_plane.identity_setup import enroll_key, identity_status
from control_plane.ssh_signing import SIGN_NAMESPACE

pytestmark = pytest.mark.skipif(shutil.which("ssh-keygen") is None, reason="ssh-keygen required")
OTHER_UID = os.geteuid() + 4242  # a distinct agent uid, so isolation checks pass deterministically


def _enrolled_repo(tmp_path):
    key = tmp_path / "id"
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "pw", "-C", "t", "-f", str(key)], check=True, capture_output=True)
    repo = tmp_path / "repo"
    repo.mkdir()
    layout = default_layout(repo)
    enroll_key(layout, "op@local", (tmp_path / "id.pub").read_text().strip())
    return repo, layout


def _status(layout, **extra):
    return identity_status(layout, agent_uid=OTHER_UID, **extra)


def test_status_reports_ssh_keygen_capability(tmp_path):
    repo, layout = _enrolled_repo(tmp_path)
    status = _status(layout)
    assert status["ssh_keygen"]["available"] is True
    assert status["ssh_keygen"]["supports_sshsig"] is True
    assert status["ssh_keygen"]["version"]
    assert status["ready"] is True, status["failures"]


def test_missing_ssh_keygen_makes_status_not_ready_with_an_actionable_failure(tmp_path):
    repo, layout = _enrolled_repo(tmp_path)
    status = _status(layout, ssh_keygen_binary="/nonexistent/ssh-keygen-xyz")
    assert status["ready"] is False
    assert status["ssh_keygen"]["available"] is False
    assert any(f.startswith("SSH_KEYGEN_UNAVAILABLE") for f in status["failures"]), status["failures"]


def test_allowed_signers_without_any_key_is_not_ready(tmp_path):
    repo, layout = _enrolled_repo(tmp_path)
    layout.allowed_signers.write_text("# no keys\n")
    os.chmod(layout.allowed_signers, 0o600)
    status = _status(layout)
    assert status["ready"] is False
    assert any(f.startswith("NO_ENROLLED_KEYS") for f in status["failures"]), status["failures"]


def test_key_scoped_to_the_wrong_namespace_is_not_ready(tmp_path):
    repo, layout = _enrolled_repo(tmp_path)
    text = layout.allowed_signers.read_text()
    assert SIGN_NAMESPACE in text
    layout.allowed_signers.write_text(text.replace(SIGN_NAMESPACE, "some-other-namespace@example.com"))
    os.chmod(layout.allowed_signers, 0o600)
    status = _status(layout)
    assert status["ready"] is False
    assert any(f.startswith("NAMESPACE_MISMATCH") for f in status["failures"]), status["failures"]


def test_check_cli_prints_the_ssh_keygen_line_and_exit_code(tmp_path):
    repo, layout = _enrolled_repo(tmp_path)
    script = PLUGIN / "scripts" / "setup_ciba_identity.py"
    ok = subprocess.run([sys.executable, str(script), "--check", "--repo-root", str(repo), "--agent-uid", str(OTHER_UID)], capture_output=True, text=True)
    assert ok.returncode == 0 and "ssh-keygen: OpenSSH" in ok.stdout, ok.stdout
    bad = subprocess.run(
        [sys.executable, str(script), "--check", "--repo-root", str(repo), "--agent-uid", str(OTHER_UID), "--ssh-keygen-binary", "/nonexistent/ssh-keygen-xyz"],
        capture_output=True, text=True,
    )
    assert bad.returncode == 1 and "SSH_KEYGEN_UNAVAILABLE" in bad.stdout, bad.stdout


def test_init_notice_reports_ssh_keygen_readiness_without_writing(tmp_path):
    from init_agentic_os import signing_identity_notice

    target = tmp_path / "proj"
    target.mkdir()
    lines = "\n".join(signing_identity_notice(target))
    assert "ssh-keygen" in lines
    assert not (target / "context").exists()  # os-init's notice never creates the identity folder or any key


def test_health_check_skill_asserts_verification_readiness_not_actor_strings():
    text = (PLUGIN / "skills" / "os-health-check" / "SKILL.md").read_text()
    lowered = text.lower()
    assert "ssh-keygen" in lowered and "allowed_signers" in lowered and "sshsig" in lowered
    for stale in ("actor = 'human'", "actor='human'", "force_done", "force_close", "--skip-review"):
        assert stale not in lowered, stale
