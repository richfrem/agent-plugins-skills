"""
tests/test_os_init_identity_status.py
=====================================

Purpose:
    Failing-first acceptance tests for T13 (auth-ciba-increment-b, issue #639, spec case 16): os-init
    reports the Gate 1 signing-identity status and prints the exact human setup command, but is a
    READ-ONLY reporter. It never creates a key, never writes `context/identity/` or `allowed_signers*`,
    and never runs the setup. os-init is an agent-run surface, so anything else would be an enrollment
    path for an agent. Real subprocess runs of init_agentic_os.py on a real throwaway git repo, the
    same pattern as test_init_agentic_os_scaffolding.py.

Key Input Dependencies:
    - scripts/init_agentic_os.py (signing_identity_notice, print_next_steps)
    - control_plane/identity_setup.py (identity_status), identity_layout.py

Key Functions (test cases):
    - test_init_reports_signing_identity_status_and_the_human_command
    - test_init_never_creates_keys_or_identity_files
    - test_init_reports_enrolled_keys_when_a_human_already_set_it_up
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
INIT_SCRIPT = REPO_ROOT / "plugins" / "agent-agentic-os" / "scripts" / "init_agentic_os.py"
_scripts_dir = str(REPO_ROOT / "plugins" / "agent-agentic-os" / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)


@pytest.fixture
def target_repo(tmp_path):
    repo = tmp_path / "test_project"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    (repo / "README.md").write_text("# Test Project\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, check=True, capture_output=True)
    return repo


def _init(repo):
    return subprocess.run([sys.executable, str(INIT_SCRIPT), "--target", str(repo), "--retrofit"], capture_output=True, text=True)


def test_init_reports_signing_identity_status_and_the_human_command(target_repo):
    res = _init(target_repo)
    assert res.returncode == 0, res.stderr
    out = res.stdout
    assert "Signing identity" in out and "not set up" in out.lower()
    assert "setup_ciba_identity.py" in out
    assert "human" in out.lower() and "never" in out.lower()  # says it is not run by init


def test_init_never_creates_keys_or_identity_files(target_repo):
    _init(target_repo)
    assert not (target_repo / "context" / "identity").exists()
    assert not list(target_repo.rglob("allowed_signers*"))
    assert not list(target_repo.rglob("id_ed25519*"))


def test_init_reports_enrolled_keys_when_a_human_already_set_it_up(target_repo, tmp_path):
    from control_plane.identity_layout import default_layout
    from control_plane.identity_setup import enroll_key

    key = tmp_path / "id"
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "pw", "-C", "t", "-f", str(key)], check=True, capture_output=True)
    enroll_key(default_layout(target_repo), "op@local", (tmp_path / "id.pub").read_text().strip())
    res = _init(target_repo)
    assert res.returncode == 0
    assert "SHA256:" in res.stdout and "enrolled" in res.stdout.lower()
