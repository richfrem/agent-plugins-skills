"""
tests/test_health_check_signing_status.py
=========================================

Purpose:
    Failing-first acceptance tests for T14 (auth-ciba-increment-b, issue #639, spec case 17): the
    os-health-check skill gains a READ-ONLY, ADVISORY phase reporting the Gate 1 signing-identity
    status. The health check is a phased procedure in SKILL.md executed by an agent, so the phase
    text and the spoked status command are the deliverables: the phase must name the exact read-only
    command, state that a green result is not proof of human presence, and forbid the agent from
    running the setup or touching keys. The spoked `setup_ciba_identity.py --check` must run from
    inside the skill folder (a self-contained installed copy) and never write anything.
    The self-test-age record planned in the ledger is deferred (no self-test record exists yet).

Key Input Dependencies:
    - skills/os-health-check/SKILL.md, skills/os-health-check/scripts/ (spokes)
    - scripts/setup_ciba_identity.py (--check), control_plane/identity_*.py

Key Functions (test cases):
    - test_skill_has_a_read_only_advisory_signing_phase
    - test_spoked_status_command_runs_from_the_skill_folder_and_writes_nothing
    - test_status_reports_ready_only_when_isolated_and_enrolled
"""

import os
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
SKILL = PLUGIN / "skills" / "os-health-check"
_scripts_dir = str(PLUGIN / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)


def _status(repo, *extra):
    return subprocess.run(
        [sys.executable, str(SKILL / "scripts" / "setup_ciba_identity.py"), "--check", "--repo-root", str(repo), *extra],
        capture_output=True, text=True,
    )


def test_skill_has_a_read_only_verification_readiness_phase():
    text = (SKILL / "SKILL.md").read_text()
    assert "Cryptographic Verification Readiness" in text
    assert "scripts/setup_ciba_identity.py --check" in text
    lowered = text.lower()
    assert "not proof of human presence" in lowered
    assert "never run" in lowered and "setup_ciba_identity.py" in lowered
    assert "ssh-keygen" in lowered and "allowed_signers" in lowered


def test_spoked_status_command_runs_from_the_skill_folder_and_writes_nothing(tmp_path):
    result = _status(tmp_path)
    assert result.returncode == 1  # not ready
    assert "not set up" in result.stdout.lower()
    assert not (tmp_path / "context").exists()


def test_status_reports_ready_only_when_isolated_and_enrolled(tmp_path):
    from control_plane.identity_layout import default_layout
    from control_plane.identity_setup import enroll_key

    key = tmp_path / "id"
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "pw", "-C", "t", "-f", str(key)], check=True, capture_output=True)
    repo = tmp_path / "repo"
    repo.mkdir()
    enroll_key(default_layout(repo), "op@local", (tmp_path / "id.pub").read_text().strip())
    unresolved = _status(repo, "--agent-name", "no-such-agent-account-xyz")  # deterministic: independent of a real agentic-os-local-agent account: enrolled but not isolated
    assert unresolved.returncode == 1 and "enrolled keys: 1" in unresolved.stdout
    other_uid = os.geteuid() + 4242
    ready = _status(repo, "--agent-uid", str(other_uid))
    assert ready.returncode == 0 and "ready" in ready.stdout.lower() and "SHA256:" in ready.stdout
