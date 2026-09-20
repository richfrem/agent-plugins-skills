"""
tests/helpers/human_signer.py
=============================

Purpose:
    A stand-in HUMAN for the test suites (auth-ciba-increment-b). The three gates into APPROVED, VERIFY_EXIT and
    DONE accept only an OpenSSH signature over a transition_request, so any test that walks a task through them
    needs a human who signs. This helper IS that human: it holds a throwaway, unprotected ed25519 key, enrolls it in
    the task repository's `context/identity/` (real files, real modes), and completes a request through the SAME
    production flow (show_challenge -> `ssh-keygen -Y sign` -> approve_transition: signature verified against
    allowed_signers, request consumed in the commit transaction). Nothing is bypassed or mocked; only the passphrase
    prompt is absent because the test key has none. Tests that assert the strict behaviour (halting with
    HUMAN_PROOF_REQUIRED) opt out with `@pytest.mark.no_auto_signer`.

Key Input Dependencies:
    - control_plane/gate1_approval.py, identity_layout.py, ssh_signing.py; ssh-keygen (OpenSSH 8.1+)

Key Functions:
    - TestHuman.sign_request() -- complete a PENDING request as the enrolled human; returns the TransitionRecord
    - TestHuman.ensure_identity() -- create context/identity for a repository root with this human's public key
    - get_test_human() -- the process-wide TestHuman
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict

from control_plane.gate1_approval import approve_transition, show_challenge
from control_plane.identity_layout import default_layout
from control_plane.ssh_signing import SELFTEST_NAMESPACE, SIGN_NAMESPACE, sign_command

__test__ = False  # not a test class


class TestHuman:
    __test__ = False

    def __init__(self) -> None:
        self._dir = Path(tempfile.mkdtemp(prefix="test-human-")).resolve()
        self.key = self._dir / "id"
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "test-human", "-f", str(self.key)], check=True, capture_output=True)
        fields = (self._dir / "id.pub").read_text().split()
        self._pub = (fields[0], fields[1])
        # an agent identity that is not this process, so the isolation check passes as in an isolated setup
        self.agent_identity: Dict[str, Any] = {"agent_name": "no-such-agent-account", "agent_uid": os.geteuid() + 4242, "agent_gids": set()}

    def ensure_identity(self, repo_root: Path):
        layout = default_layout(Path(repo_root).resolve())
        for directory in (layout.root, layout.challenge_dir):
            directory.mkdir(parents=True, exist_ok=True)
            os.chmod(directory, 0o700)
        for path, namespace in ((layout.allowed_signers, SIGN_NAMESPACE), (layout.allowed_signers_selftest, SELFTEST_NAMESPACE)):
            path.write_text(f'test-human@local namespaces="{namespace}" {self._pub[0]} {self._pub[1]}\n')
            os.chmod(path, 0o600)
        return layout

    def sign_request(self, cp: Any, request_id: int) -> Any:
        repo_root = Path(cp.repo_root) if getattr(cp, "repo_root", None) else Path.cwd()
        layout = self.ensure_identity(repo_root)
        challenge = show_challenge(
            cp, request_id, layout=layout, key_hint=str(self.key), agent_identity=self.agent_identity, out=open(os.devnull, "w"),
        )
        sig = Path(str(challenge) + ".sig")
        if sig.exists():
            sig.unlink()
        subprocess.run(sign_command(str(self.key), challenge), check=True, capture_output=True)
        return approve_transition(
            cp, request_id, layout=layout, principal="test-human@local", agent_identity=self.agent_identity, out=open(os.devnull, "w"),
        )

    def close(self) -> None:
        shutil.rmtree(self._dir, ignore_errors=True)


_SINGLETON = None


def get_test_human() -> "TestHuman":
    """One throwaway human (key) per test process; also used by fixtures that must sign during setup."""
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = TestHuman()
    return _SINGLETON
