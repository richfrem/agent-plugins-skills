"""
tests/test_setup_ciba_identity.py
=================================

Purpose:
    Failing-first acceptance tests for T11 (auth-ciba-increment-b, issue #639): the cross-platform
    signing-identity setup helper `scripts/setup_ciba_identity.py` and its logic module
    `control_plane/identity_setup.py`. Spec section 4 case 10. It refuses non-TTY use and refuses to
    run as the agent uid (else an agent could self-enroll a key); creates `context/identity/` (0700) and
    the production `allowed_signers` (0600, namespace control-plane@agentic-os.local) plus the SEPARATE
    `allowed_signers_selftest` (0600, namespace control-plane-selftest@agentic-os.local); never enrolls a key without a
    passphrase; is idempotent; never removes an already-enrolled key; prints (never runs) privileged
    account-creation commands. Real ssh-keygen, real files; one pty-driven test types the real
    passphrase prompt. Identity (agent uid, TTY) is injected, nothing is mocked.

Key Input Dependencies:
    - scripts/setup_ciba_identity.py (main), control_plane/identity_setup.py, identity_layout.py,
      isolation_check.py; ssh-keygen (OpenSSH 8.1+)

Key Functions (test cases):
    - test_refuses_without_a_tty / test_refuses_when_running_as_the_agent_uid
    - test_check_mode_is_read_only_and_needs_no_tty
    - test_setup_with_an_existing_protected_key_enrolls_it_and_sets_modes
    - test_setup_is_idempotent / test_second_key_is_added_without_removing_the_first
    - test_unprotected_software_key_is_refused
    - test_selftest_file_is_separate_with_its_own_namespace
    - test_privileged_commands_are_printed_not_run
    - test_enrolled_keys_lists_fingerprints
    - test_generate_a_key_through_the_real_passphrase_prompt (pty)
"""

import os
import pty
import pwd
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

import setup_ciba_identity
from control_plane.identity_layout import canonical_repo_root, default_layout
from control_plane.ssh_signing import SELFTEST_NAMESPACE, SIGN_NAMESPACE
from control_plane.identity_setup import enrolled_keys, identity_status, key_is_passphrase_protected

_FOUND = shutil.which("ssh-keygen")
SSH_KEYGEN: str = _FOUND or "ssh-keygen"
pytestmark = pytest.mark.skipif(_FOUND is None, reason="ssh-keygen not installed")


def _other_uid() -> int:
    for name in ("nobody", "daemon"):
        try:
            uid = pwd.getpwnam(name).pw_uid
            if uid != os.geteuid():
                return uid
        except KeyError:
            continue
    return os.geteuid() + 4242


def _key(path: Path, passphrase: str = "correct horse") -> Path:
    subprocess.run([SSH_KEYGEN, "-q", "-t", "ed25519", "-N", passphrase, "-C", "test", "-f", str(path)], check=True, capture_output=True)
    return path


@pytest.fixture
def env(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    return {"repo": repo, "layout": default_layout(repo), "tmp": tmp_path}


def _run(env, *extra, tty=True, agent_uid=None, answers=("n",), key=None):
    out = []
    feed = iter(answers)
    args = ["--repo-root", str(env["repo"])] + (["--key", str(key)] if key else []) + list(extra)
    code = setup_ciba_identity.main(
        args, tty_fn=lambda: tty, input_fn=lambda _p: next(feed, "n"), out=lambda s="": out.append(str(s)),
        agent_identity={"agent_name": "agentic-os-local-agent", "agent_uid": agent_uid or _other_uid(), "agent_gids": set()},
    )
    return code, "\n".join(out)


def test_refuses_without_a_tty(env):
    code, printed = _run(env, tty=False, key=_key(env["tmp"] / "k"))
    assert code != 0 and "terminal" in printed.lower()
    assert not env["layout"].root.exists()


def test_refuses_when_running_as_the_agent_uid(env):
    code, printed = _run(env, agent_uid=os.geteuid(), key=_key(env["tmp"] / "k"))
    assert code != 0 and "agent" in printed.lower()
    assert not env["layout"].root.exists()


def test_check_mode_is_read_only_and_needs_no_tty(env):
    code, printed = _run(env, "--check", tty=False)
    assert code == 1  # not ready: a nonzero exit lets os-init / the health check use the exit code
    assert "not set up" in printed.lower() or "missing" in printed.lower()
    assert not env["layout"].root.exists()


def test_setup_with_an_existing_protected_key_enrolls_it_and_sets_modes(env):
    key = _key(env["tmp"] / "k")
    code, printed = _run(env, key=key)
    assert code == 0, printed
    layout = env["layout"]
    assert stat.S_IMODE(layout.root.stat().st_mode) == 0o700
    assert stat.S_IMODE(layout.challenge_dir.stat().st_mode) == 0o700
    assert stat.S_IMODE(layout.allowed_signers.stat().st_mode) == 0o600
    assert stat.S_IMODE(layout.allowed_signers_selftest.stat().st_mode) == 0o600
    text = layout.allowed_signers.read_text()
    assert f'namespaces="{SIGN_NAMESPACE}"' in text and "ssh-ed25519" in text
    assert "SHA256:" in printed  # the fingerprint is the thumbprint analogue


def test_selftest_file_is_separate_with_its_own_namespace(env):
    _run(env, key=_key(env["tmp"] / "k"))
    layout = env["layout"]
    selftest = layout.allowed_signers_selftest.read_text()
    assert f'namespaces="{SELFTEST_NAMESPACE}"' in selftest and f'namespaces="{SIGN_NAMESPACE}"' not in selftest
    assert SELFTEST_NAMESPACE not in layout.allowed_signers.read_text()


def test_setup_is_idempotent(env):
    key = _key(env["tmp"] / "k")
    _run(env, key=key)
    before = env["layout"].allowed_signers.read_text()
    code, printed = _run(env, key=key)
    assert code == 0 and env["layout"].allowed_signers.read_text() == before
    assert "already enrolled" in printed.lower()


def test_second_key_is_added_without_removing_the_first(env):
    first = _key(env["tmp"] / "k1")
    second = _key(env["tmp"] / "k2")
    _run(env, key=first)
    _run(env, key=second)
    keys = enrolled_keys(env["layout"])
    assert len(keys) == 2 and len({k.fingerprint for k in keys}) == 2


def test_enrolled_keys_lists_fingerprints(env):
    _run(env, key=_key(env["tmp"] / "k"))
    keys = enrolled_keys(env["layout"])
    assert keys and keys[0].fingerprint.startswith("SHA256:") and keys[0].namespaces == SIGN_NAMESPACE


def test_unprotected_software_key_is_refused(env):
    key = _key(env["tmp"] / "open", passphrase="")
    assert key_is_passphrase_protected(key) is False
    code, printed = _run(env, key=key)
    assert code != 0 and "passphrase" in printed.lower()
    layout = env["layout"]
    assert not layout.allowed_signers.exists() or layout.allowed_signers.read_text() == ""


def test_privileged_commands_are_printed_not_run(env):
    """With no agent account on this machine the setup prints the commands; it never runs them."""
    out = []
    code = setup_ciba_identity.main(
        ["--repo-root", str(env["repo"]), "--key", str(_key(env["tmp"] / "k")), "--no-selftest-prompt"],
        tty_fn=lambda: True, out=lambda s="": out.append(str(s)),
        agent_identity={"agent_name": "agentic-os-test-nonexistent-agent"},
    )
    printed = "\n".join(out)
    assert code == 0
    assert "agentic-os-test-nonexistent-agent" in printed
    assert "sysadminctl" in printed or "net user" in printed or "useradd" in printed
    assert "NOT run here" in printed


def test_identity_status_reports_missing_and_present(env):
    status = identity_status(env["layout"], agent_name="agentic-os-local-agent", agent_uid=_other_uid(), agent_gids=set())
    assert status["ready"] is False and status["enrolled_keys"] == 0
    _run(env, key=_key(env["tmp"] / "k"))
    status = identity_status(env["layout"], agent_name="agentic-os-local-agent", agent_uid=_other_uid(), agent_gids=set())
    assert status["ready"] is True and status["enrolled_keys"] == 1 and status["failures"] == []


def _drive_in_a_pty(argv, script, timeout=60):
    """Run argv in a real pseudo-terminal, answering prompts from `script` [(expect, send)]."""
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp(argv[0], argv)
    output, deadline, step = b"", time.time() + timeout, 0
    while time.time() < deadline:
        try:
            chunk = os.read(fd, 4096)
        except OSError:
            break
        if not chunk:
            break
        output += chunk
        while step < len(script) and script[step][0].encode() in output:
            os.write(fd, script[step][1].encode())
            output = output.replace(script[step][0].encode(), b"", 1)
            step += 1
    _, status = os.waitpid(pid, 0)
    return os.waitstatus_to_exitcode(status), output.decode("utf-8", "replace")


def test_generate_a_key_through_the_real_passphrase_prompt(env):
    key = env["tmp"] / "generated"
    argv = [
        sys.executable, str(Path(_scripts_dir) / "setup_ciba_identity.py"),
        "--repo-root", str(env["repo"]), "--key", str(key), "--agent-uid", str(_other_uid()), "--no-selftest-prompt",
    ]
    code, output = _drive_in_a_pty(argv, [
        ("Enter passphrase", "correct horse battery\n"),
        ("Enter same passphrase again", "correct horse battery\n"),
    ])
    assert code == 0, output
    assert key.exists() and key_is_passphrase_protected(key) is True
    assert len(enrolled_keys(env["layout"])) == 1


def test_repo_root_is_the_canonical_one_even_from_inside_a_worktree(tmp_path):
    """The coordinator resolves the shared (main) repository root; setup and self-test must agree,
    otherwise the key is enrolled in one place and the approval looks in another."""
    main = tmp_path / "main"
    main.mkdir()
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    subprocess.run(["git", "init", "-q", str(main)], check=True, env=env)
    (main / "f.txt").write_text("x")
    subprocess.run(["git", "-C", str(main), "add", "."], check=True, env=env)
    subprocess.run(["git", "-C", str(main), "commit", "-q", "-m", "init"], check=True, env=env)
    worktree = tmp_path / "wt"
    subprocess.run(["git", "-C", str(main), "worktree", "add", "-q", str(worktree), "-b", "feature/x"], check=True, env=env)
    assert canonical_repo_root(worktree) == main.resolve()
    assert canonical_repo_root(main) == main.resolve()
    assert canonical_repo_root(tmp_path / "not-a-repo") == (tmp_path / "not-a-repo").resolve()
