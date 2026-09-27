#!/usr/bin/env python
"""
test_os_init_dual_identity.py
=============================

Purpose:
    os-init onboarding for both approval identities (round-3 review follow-up):
      - the readiness report lists human approval, simulation and isolation separately;
      - --with-simulation-identity creates (and on reruns reuses) the agent's simulation identity in
        context/simulation/identity/ and never creates or writes the human's production trust file;
      - without the flag nothing is created (the existing contract in test_os_init_identity_status.py).

Key Input Dependencies:
    plugins/agent-agentic-os/scripts/init_agentic_os.py (run as a real subprocess)
    plugins/agent-agentic-os/scripts/control_plane/simulation_identity.py

Layer: Development / Testing

Functions:
    - test_init_reports_three_readiness_items
    - test_with_simulation_identity_creates_only_the_simulation_identity
    - test_simulation_identity_rerun_reuses_the_key

Usage:
    python -m pytest plugins/agent-agentic-os/tests/test_os_init_dual_identity.py
"""

import subprocess
import sys
from pathlib import Path

import pytest

INIT = Path(__file__).resolve().parent.parent / "scripts" / "init_agentic_os.py"


@pytest.fixture
def target_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    return repo


def _init(repo: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(INIT), "--target", str(repo), "--retrofit", "--contribution-mode", "fork-and-pr", *extra],
        capture_output=True, text=True, timeout=180,
    )


def _sim_fingerprint(repo: Path) -> str:
    sys.path.insert(0, str(INIT.parent))
    from control_plane.approver_policy import key_fingerprint

    return key_fingerprint((repo / "context" / "simulation" / "identity" / "simulation_key.pub").read_text().split()[1])


def test_init_reports_three_readiness_items(target_repo):
    res = _init(target_repo)
    assert res.returncode == 0, res.stderr
    out = res.stdout
    for item in ("Human approval", "Simulation", "Isolation"):
        assert item in out, item
    assert "--with-simulation-identity" in out


def test_with_simulation_identity_creates_only_the_simulation_identity(target_repo):
    res = _init(target_repo, "--with-simulation-identity")
    assert res.returncode == 0, res.stderr
    sim = target_repo / "context" / "simulation" / "identity"
    assert (sim / "simulation_key").exists() and (sim / "allowed_signers").exists()
    assert not (target_repo / "context" / "identity").exists()  # the human's production identity is never created
    assert "Simulation: ready" in res.stdout


def test_simulation_identity_rerun_reuses_the_key(target_repo):
    assert _init(target_repo, "--with-simulation-identity").returncode == 0
    first = _sim_fingerprint(target_repo)
    assert _init(target_repo, "--with-simulation-identity").returncode == 0
    assert _sim_fingerprint(target_repo) == first


def test_setup_check_reports_three_readiness_items(target_repo):
    setup = INIT.parent / "setup_ciba_identity.py"
    res = subprocess.run([sys.executable, str(setup), "--check", "--repo-root", str(target_repo)], capture_output=True, text=True, timeout=120)
    for item in ("Human approval", "Simulation", "Isolation"):
        assert item in res.stdout, res.stdout
