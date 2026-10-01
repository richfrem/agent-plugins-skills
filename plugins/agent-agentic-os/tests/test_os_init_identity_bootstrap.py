"""
test_os_init_identity_bootstrap.py - os-init registers the human's identity, but only for a human.

Purpose:
    A first os-init used to leave the repo with gates wired and nobody authorized, and printed a setup
    command that did not exist in consumer repos. Now:
      * run in a human's interactive terminal, os-init OFFERS to enroll the human's key (it delegates to
        setup_ciba_identity.py, which itself refuses without a terminal or as the agent account);
      * run by an agent (no terminal) it enrolls NOTHING and prints a command that exists in the repo,
        naming the key already on the machine;
      * the agent's own simulation identity is created by default (it can never approve real work).
    The invariant under test: os-init never creates or writes the human's trust file without a human.
"""

import os
import select
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

import init_agentic_os as init

INIT = Path(init.__file__).resolve()
HAS_SSH_KEYGEN = shutil.which("ssh-keygen") is not None


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    for cmd in (["git", "init", "-q"], ["git", "config", "user.email", "a@b.c"], ["git", "config", "user.name", "T"],
                ["git", "commit", "--allow-empty", "-q", "-m", "x"]):
        subprocess.run(cmd, cwd=root, check=True, capture_output=True)
    return root


def _install_setup(root, skill):
    script = root / ".agents" / "skills" / skill / "scripts" / "setup_ciba_identity.py"
    script.parent.mkdir(parents=True)
    script.write_text("# fake human setup\n")
    return script


def _boom(*a, **k):
    raise AssertionError("the human setup must not run here")


def _never_asked(prompt):
    raise AssertionError(f"must not prompt here: {prompt!r}")


# ---- finding the right command -----------------------------------------------------------------


def test_command_uses_the_path_that_exists_in_this_repo_layout(repo):
    script = _install_setup(repo, "os-health-check")  # os-signing-setup is removed when the plane is disabled
    assert init.find_setup_script(repo) == script
    assert init.human_setup_command(repo) == "python3 .agents/skills/os-health-check/scripts/setup_ciba_identity.py"


def test_signing_setup_skill_is_preferred_when_both_are_installed(repo):
    preferred = _install_setup(repo, "os-signing-setup")
    _install_setup(repo, "os-health-check")
    assert init.find_setup_script(repo) == preferred


def test_falls_back_to_the_script_beside_init_when_nothing_is_installed(repo):
    found = init.find_setup_script(repo)
    assert found is not None and found.name == "setup_ciba_identity.py"
    assert found.parent == INIT.parent


# ---- the offer: who may enroll -----------------------------------------------------------------


def test_non_interactive_never_enrolls_and_never_prompts(repo, capsys):
    _install_setup(repo, "os-health-check")
    result = init.register_human_identity_step(repo, False, interactive=False, run=_boom, ask=_never_asked)
    assert result == "not-interactive"
    assert not (repo / "context" / "identity").exists()
    out = capsys.readouterr().out
    assert "Not enrolling from a non-interactive/agent context" in out
    assert "python3 .agents/skills/os-health-check/scripts/setup_ciba_identity.py" in out


def test_dry_run_neither_prompts_nor_runs(repo):
    assert init.register_human_identity_step(repo, True, interactive=True, run=_boom, ask=_never_asked) == "dry-run"


def test_already_set_up_is_left_alone(repo, monkeypatch):
    monkeypatch.setattr("control_plane.identity_setup.identity_status", lambda layout, **k: {"ready": True})
    assert init.register_human_identity_step(repo, False, interactive=True, run=_boom, ask=_never_asked) == "already-ready"


def test_interactive_decline_runs_nothing(repo, capsys):
    _install_setup(repo, "os-signing-setup")
    result = init.register_human_identity_step(repo, False, interactive=True, run=_boom, ask=lambda p: "n")
    assert result == "declined"
    assert not (repo / "context" / "identity").exists()
    assert "Skipped. Later, run:" in capsys.readouterr().out


@pytest.mark.parametrize("answer", ["y", "Y", "yes", " YES "])
def test_interactive_accept_delegates_to_the_human_setup_script(repo, answer):
    script = _install_setup(repo, "os-signing-setup")
    calls = []

    def fake_run(cmd, cwd=None, **k):
        calls.append((cmd, cwd))
        return subprocess.CompletedProcess(cmd, 0)

    assert init.register_human_identity_step(repo, False, interactive=True, run=fake_run, ask=lambda p: answer) == "enrolled"
    assert calls == [([sys.executable, str(script), "--repo-root", str(repo)], str(repo))]


def test_a_failed_setup_is_reported_not_swallowed(repo, capsys):
    _install_setup(repo, "os-signing-setup")
    result = init.register_human_identity_step(
        repo, False, interactive=True, ask=lambda p: "y", run=lambda cmd, **k: subprocess.CompletedProcess(cmd, 2))
    assert result == "failed"
    assert "did not complete (exit 2)" in capsys.readouterr().out


def test_missing_setup_script_is_reported(repo, monkeypatch):
    monkeypatch.setattr(init, "find_setup_script", lambda target: None)
    assert init.register_human_identity_step(repo, False, interactive=True, run=_boom, ask=_never_asked) == "unavailable"


# ---- the key already on this machine (public half only) --------------------------------------------


@pytest.mark.skipif(not HAS_SSH_KEYGEN, reason="ssh-keygen not available")
def test_machine_key_note_reports_the_public_fingerprint(tmp_path, monkeypatch):
    home = tmp_path / "home"
    (home / ".ssh").mkdir(parents=True)
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(home / ".ssh" / "agentic-os_signing")],
                   check=True, capture_output=True)
    monkeypatch.setenv("HOME", str(home))
    note = init.machine_key_note()
    assert note and note.startswith("SHA256:") and "agentic-os_signing.pub" in note
    assert "PRIVATE" not in note and not note.endswith("agentic-os_signing)")  # only ever the .pub


def test_machine_key_note_is_none_without_a_key(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "empty-home"))
    assert init.machine_key_note() is None


# ---- end to end through the real CLI ----------------------------------------------------------------


def _run_init(root, *extra):
    return subprocess.run([sys.executable, str(INIT), "--target", str(root), "--retrofit", *extra],
                          capture_output=True, text=True, stdin=subprocess.DEVNULL)


@pytest.mark.skipif(not HAS_SSH_KEYGEN, reason="ssh-keygen not available")
def test_agent_run_init_creates_the_simulation_identity_but_never_the_human_one(repo):
    res = _run_init(repo)
    assert res.returncode == 0, res.stdout + res.stderr
    assert (repo / "context" / "simulation" / "identity" / "simulation_key").exists()
    assert not (repo / "context" / "identity").exists()  # the human's trust file: never, without a human
    assert "Not enrolling from a non-interactive/agent context" in res.stdout
    assert "Simulation: ready" in res.stdout


@pytest.mark.skipif(not HAS_SSH_KEYGEN, reason="ssh-keygen not available")
def test_flags_opt_out_of_each_identity_step(repo):
    res = _run_init(repo, "--no-simulation-identity", "--no-identity-prompt")
    assert res.returncode == 0, res.stdout + res.stderr
    assert not (repo / "context" / "simulation" / "identity").exists()
    assert not (repo / "context" / "identity").exists()
    assert "Not enrolling from a non-interactive/agent context" not in res.stdout


@pytest.mark.skipif(not HAS_SSH_KEYGEN, reason="ssh-keygen not available")
def test_printed_next_step_command_exists_in_the_repo(repo):
    _install_setup(repo, "os-health-check")
    res = _run_init(repo)
    assert "python3 .agents/skills/os-health-check/scripts/setup_ciba_identity.py" in res.stdout
    assert "plugins/agent-agentic-os/scripts/setup_ciba_identity.py" not in res.stdout


@pytest.mark.skipif(sys.platform.startswith("win"), reason="needs a POSIX pseudo-terminal")
@pytest.mark.skipif(not HAS_SSH_KEYGEN, reason="ssh-keygen not available")
def test_the_offer_appears_only_with_a_real_terminal_and_declining_changes_nothing(repo, tmp_path):
    import pty

    master, slave = pty.openpty()
    env = {**os.environ, "HOME": str(tmp_path / "home")}  # never touch the real ~/.ssh
    (tmp_path / "home").mkdir()
    # In a real terminal os-init first asks the plugin-contribution question; answer it by flag so the
    # test reaches the identity offer.
    proc = subprocess.Popen([sys.executable, str(INIT), "--target", str(repo), "--retrofit",
                             "--contribution-mode", "fork-and-pr"],
                            stdin=slave, stdout=slave, stderr=slave, env=env, close_fds=True)
    os.close(slave)
    output, deadline, answered = b"", time.time() + 90, False
    while time.time() < deadline:
        ready, _, _ = select.select([master], [], [], 0.5)
        if ready:
            try:
                chunk = os.read(master, 4096)
            except OSError:
                break
            if not chunk:
                break
            output += chunk
            if not answered and b"Enroll your key in this repo now?" in output:
                os.write(master, b"n\n")  # decline
                answered = True
        elif proc.poll() is not None:
            break
    if proc.poll() is None:
        proc.kill()
    proc.wait(timeout=10)
    os.close(master)
    text = output.decode(errors="replace")
    assert answered, f"the offer never appeared with a real terminal:\n{text[-800:]}"
    assert "Skipped. Later, run:" in text
    assert not (repo / "context" / "identity").exists()  # declined: nothing enrolled
