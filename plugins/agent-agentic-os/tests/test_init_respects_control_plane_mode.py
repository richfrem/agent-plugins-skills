"""
test_init_respects_control_plane_mode.py - os-init must never silently re-enable a gate.

Purpose:
    `init_agentic_os.py --install-hooks` (and --retrofit, which shares the same code) used to
    re-install and re-wire the control-plane guards unconditionally. With a declared mode of
    `disabled` it must skip pipeline + push guards, while still installing the independent
    evolution guard. A missing mode file must behave exactly as before (everything installed).
"""

import subprocess
import sys
from pathlib import Path

import pytest

INIT = Path(__file__).resolve().parent.parent / "scripts" / "init_agentic_os.py"
HOOKS = ".git/hooks"


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    for cmd in (["git", "init", "-q"], ["git", "config", "user.email", "a@b.c"], ["git", "config", "user.name", "T"],
                ["git", "commit", "--allow-empty", "-q", "-m", "x"]):
        subprocess.run(cmd, cwd=root, check=True, capture_output=True)
    return root


def _install(root):
    return subprocess.run([sys.executable, str(INIT), "--target", str(root), "--install-hooks"],
                          capture_output=True, text=True)


def test_no_mode_file_installs_and_wires_every_guard_as_before(repo):
    res = _install(repo)
    assert res.returncode == 0, res.stdout + res.stderr
    hooks = repo / HOOKS
    for guard in ("pre-commit-evolution-guard", "pre-commit-pipeline-guard", "pre-push-review-guard"):
        assert (hooks / guard).is_file(), guard
    assert "pre-commit-pipeline-guard" in (hooks / "pre-commit").read_text()
    assert "pre-commit-evolution-guard" in (hooks / "pre-commit").read_text()
    assert "pre-push-review-guard" in (hooks / "pre-push").read_text()


def test_disabled_mode_skips_the_control_plane_guards_but_keeps_the_evolution_guard(repo):
    (repo / "context").mkdir()
    (repo / "context" / "control-plane-mode").write_text("disabled\n")
    res = _install(repo)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "Control plane is DISABLED" in res.stdout
    hooks = repo / HOOKS
    assert not (hooks / "pre-commit-pipeline-guard").exists()
    assert not (hooks / "pre-push-review-guard").exists()
    assert not (hooks / "pre-push").exists()  # nothing to wire, so no dispatcher was created
    assert (hooks / "pre-commit-evolution-guard").is_file()  # independent feature, still installed
    assert "pre-commit-pipeline-guard" not in (hooks / "pre-commit").read_text()


def test_rerunning_the_installer_does_not_re_enable_a_disabled_gate(repo):
    (repo / "context").mkdir()
    (repo / "context" / "control-plane-mode").write_text("disabled\n")
    _install(repo)
    _install(repo)
    assert not (repo / HOOKS / "pre-push-review-guard").exists()
    assert (repo / "context" / "control-plane-mode").read_text().strip() == "disabled"


def test_a_corrupt_mode_file_fails_closed_and_installs_the_guards(repo):
    (repo / "context").mkdir()
    (repo / "context" / "control-plane-mode").write_text("maybe\n")
    res = _install(repo)
    assert res.returncode == 0
    assert "Treating the control plane as enabled" in res.stdout
    assert (repo / HOOKS / "pre-push-review-guard").is_file()


def test_installer_is_idempotent_when_enabled(repo):
    _install(repo)
    first = (repo / HOOKS / "pre-commit").read_text(), (repo / HOOKS / "pre-push").read_text()
    _install(repo)
    assert ((repo / HOOKS / "pre-commit").read_text(), (repo / HOOKS / "pre-push").read_text()) == first


def test_an_install_missing_the_shared_helper_fails_with_a_clear_instruction(repo, tmp_path):
    lonely = tmp_path / "lonely" / "init_agentic_os.py"
    lonely.parent.mkdir()
    lonely.write_text(INIT.read_text())  # a copy with no control_plane_hooks.py beside it
    res = subprocess.run([sys.executable, str(lonely), "--target", str(repo), "--install-hooks"],
                         capture_output=True, text=True)
    assert res.returncode != 0
    assert "control_plane_hooks.py was not found" in res.stderr and "plugin sync" in res.stderr
    assert "Traceback" not in res.stderr  # an instruction, not a double traceback
