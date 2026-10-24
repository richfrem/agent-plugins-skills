"""
tests/test_signing_mechanics_selftest.py
========================================

Purpose:
    Failing-first acceptance tests for T12 (auth-ciba-increment-b, issue #639):
    `agent_control.py test-signing-mechanics` (control_plane/signing_selftest.py), also the last
    step of the setup helper. Spec section 4 case 11. It signs a generated challenge with the human's
    key through the REAL ssh-keygen prompt (a passphrase, or a hardware touch), verifies it against the
    SEPARATE `allowed_signers_selftest` under namespace `control-plane-selftest@agentic-os.local`, reports the FIDO
    user-presence/verification flags, proves the same signature can never act as a Gate 1 approval, and
    cleans up. Non-TTY use is refused. Real ssh-keygen and real files; a pty-driven test types the real
    passphrase prompt (that a prompt actually appears is asserted from the captured terminal output).
    Case 6b-style live proof with a hardware key remains a documented human step.

Key Input Dependencies:
    - control_plane/signing_selftest.py (run_selftest), identity_setup.py (enroll_key), ssh_signing.py
    - agent_control.py (_build_parser: the test-signing-mechanics verb)
    - ssh-keygen (OpenSSH 8.1+)

Key Functions (test cases):
    - test_refuses_without_a_tty
    - test_signs_verifies_reports_and_cleans_up
    - test_selftest_signature_cannot_act_as_an_approval
    - test_wrong_key_is_reported_not_enrolled
    - test_missing_key_is_reported
    - test_production_allowed_signers_is_never_modified
    - test_the_real_passphrase_prompt_appears_and_verification_succeeds (pty)
    - test_a_wrong_passphrase_fails_in_the_real_prompt (pty)
    - test_cli_registers_the_verb
"""

import os
import pty
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

import agent_control
from control_plane.identity_layout import default_layout
from control_plane.identity_setup import enroll_key
from control_plane.signing_selftest import run_selftest
from control_plane.ssh_signing import SELFTEST_NAMESPACE

_FOUND = shutil.which("ssh-keygen")
SSH_KEYGEN: str = _FOUND or "ssh-keygen"
pytestmark = pytest.mark.skipif(_FOUND is None, reason="ssh-keygen not installed")


def _key(path: Path, passphrase: str) -> Path:
    subprocess.run([SSH_KEYGEN, "-q", "-t", "ed25519", "-N", passphrase, "-C", "test", "-f", str(path)], check=True, capture_output=True)
    return path


class Identity:
    def __init__(self, tmp_path: Path, passphrase: str = ""):
        self.tmp = tmp_path
        self.repo = tmp_path / "repo"
        self.repo.mkdir()
        self.layout = default_layout(self.repo)
        self.key = _key(tmp_path / "id", passphrase)
        enroll_key(self.layout, "op@local", (tmp_path / "id.pub").read_text().strip())

    def run(self, key=None, tty=True, sign_fn=None):
        out = []
        code = run_selftest(
            self.layout, key or self.key, tty_fn=lambda: tty, out=lambda s="": out.append(str(s)), sign_fn=sign_fn,
        )
        return code, "\n".join(out)


def _noninteractive_sign(key: Path, namespace: str, challenge: Path) -> int:
    """Test seam for an unprotected key: ssh-keygen without a terminal prompt."""
    return subprocess.run([SSH_KEYGEN, "-Y", "sign", "-f", str(key), "-n", namespace, str(challenge)], capture_output=True).returncode


@pytest.fixture
def ident(tmp_path):
    return Identity(tmp_path)


def test_refuses_without_a_tty(ident):
    code, printed = ident.run(tty=False)
    assert code != 0 and "terminal" in printed.lower()
    assert list(ident.layout.challenge_dir.iterdir()) == []


def test_signs_verifies_reports_and_cleans_up(ident):
    code, printed = ident.run(sign_fn=_noninteractive_sign)
    assert code == 0, printed
    assert "verified" in printed.lower() and "SHA256:" in printed and SELFTEST_NAMESPACE in printed
    assert list(ident.layout.challenge_dir.iterdir()) == []  # challenge and signature removed


def test_selftest_signature_cannot_act_as_an_approval(ident):
    _, printed = ident.run(sign_fn=_noninteractive_sign)
    assert "cannot be used as an approval" in printed.lower()


def test_wrong_key_is_reported_not_enrolled(ident, tmp_path):
    other = _key(tmp_path / "other", "")
    code, printed = ident.run(key=other, sign_fn=_noninteractive_sign)
    assert code != 0 and ("not enrolled" in printed.lower() or "did not verify" in printed.lower())
    assert list(ident.layout.challenge_dir.iterdir()) == []


def test_missing_key_is_reported(ident, tmp_path):
    code, printed = ident.run(key=tmp_path / "does-not-exist")
    assert code != 0 and "key" in printed.lower()


def test_production_allowed_signers_is_never_modified(ident):
    before = ident.layout.allowed_signers.read_bytes()
    ident.run(sign_fn=_noninteractive_sign)
    assert ident.layout.allowed_signers.read_bytes() == before


def _drive(argv, script, timeout=60):
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
    return os.waitstatus_to_exitcode(status), output.decode("utf-8", "replace"), step


def _cli(ident):
    return [
        sys.executable, str(Path(_scripts_dir) / "agent_control.py"), "test-signing-mechanics",
        "--key", str(ident.key), "--repo-root", str(ident.repo),
    ]


def test_the_real_passphrase_prompt_appears_and_verification_succeeds(tmp_path):
    ident = Identity(tmp_path, passphrase="correct horse battery")
    code, output, prompts_answered = _drive(_cli(ident), [("Enter passphrase", "correct horse battery\n")])
    assert prompts_answered == 1, "the real passphrase prompt never appeared"
    assert code == 0, output
    assert "verified" in output.lower()
    assert list(ident.layout.challenge_dir.iterdir()) == []


def test_a_wrong_passphrase_fails_in_the_real_prompt(tmp_path):
    ident = Identity(tmp_path, passphrase="correct horse battery")
    code, output, prompts_answered = _drive(
        _cli(ident), [("Enter passphrase", "wrong\n"), ("Enter passphrase", "wrong\n"), ("Enter passphrase", "wrong\n")]
    )
    assert prompts_answered >= 1 and code != 0
    assert "signature verified" not in output.lower()
    assert "signing failed" in output.lower()
    assert list(ident.layout.challenge_dir.iterdir()) == []


def test_cli_registers_the_verb():
    parser = agent_control._build_parser()
    args = parser.parse_args(["test-signing-mechanics", "--key", "/tmp/k"])
    assert args.key == "/tmp/k"
