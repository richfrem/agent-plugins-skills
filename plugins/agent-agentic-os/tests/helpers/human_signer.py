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
    - TestHuman.ensure_identity() -- append this human's public key to a temp repository root's context/identity (refuses non-temp roots)
    - TestHuman.identity_root_for() -- temp repo root to sign against (never the real checkout or cwd)
    - TestHuman.signer_for() -- agent key in a simulation database, operator (human) key in any other
    - get_test_human() -- the process-wide TestHuman
"""

import atexit
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict

from control_plane.approver_policy import AGENT_SIMULATION_PRINCIPAL, CONTEXT_SIMULATION, is_repository_db, pipeline_context
from control_plane.gate1_approval import approve_transition, show_challenge
from control_plane.identity_layout import default_layout
from control_plane.ssh_signing import SELFTEST_NAMESPACE, SIGN_NAMESPACE, sign_command

__test__ = False  # not a test class

OPERATOR_PRINCIPAL = "test-operator@local"  # the stand-in HUMAN key for regular (non-simulation) pipelines


class TestHuman:
    __test__ = False

    def __init__(self) -> None:
        self._dir = Path(tempfile.mkdtemp(prefix="test-human-")).resolve()
        # Two keys, mirroring a real repository: the agent's simulation key and a human (operator) key.
        self.key = self._dir / "id"
        self.operator_key = self._dir / "operator_id"
        for key, comment in ((self.key, "test-human"), (self.operator_key, "test-operator")):
            subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", comment, "-f", str(key)], check=True, capture_output=True)
        fields = (self._dir / "id.pub").read_text().split()
        self._pub = (fields[0], fields[1])
        op_fields = (self._dir / "operator_id.pub").read_text().split()
        self._operator_pub = (op_fields[0], op_fields[1])
        # an agent identity that is not this process, so the isolation check passes as in an isolated setup
        current_uid = os.geteuid() if hasattr(os, "geteuid") else 1000
        self.agent_identity: Dict[str, Any] = {"agent_name": "no-such-agent-account", "agent_uid": current_uid + 4242, "agent_gids": set()}

    def ensure_identity(self, repo_root: Path):
        """Enroll the test key under repo_root's context/identity, which must be inside the temp dir.

        Appends only; existing signer lines are never dropped. Refusing non-temp roots stops a
        suite run from a real checkout overwriting the operator's enrollment (2026-09-24 incident).
        """
        root = Path(repo_root).resolve()
        if not root.is_relative_to(Path(tempfile.gettempdir()).resolve()):
            raise RuntimeError(f"TestHuman refuses to enroll outside the temp dir: {root}")
        layout = default_layout(root)
        for directory in (layout.root, layout.challenge_dir):
            directory.mkdir(parents=True, exist_ok=True)
            os.chmod(directory, 0o700)
        for path, namespace in ((layout.allowed_signers, SIGN_NAMESPACE), (layout.allowed_signers_selftest, SELFTEST_NAMESPACE)):
            for principal, pub in ((AGENT_SIMULATION_PRINCIPAL, self._pub), (OPERATOR_PRINCIPAL, self._operator_pub)):
                line = f'{principal} namespaces="{namespace}" {pub[0]} {pub[1]}'
                existing = path.read_text(encoding="utf-8") if path.exists() else ""
                if line not in existing.splitlines():
                    with open(path, "a", encoding="utf-8") as f:
                        f.write(("" if not existing or existing.endswith("\n") else "\n") + line + "\n")
            os.chmod(path, 0o600)
        return layout

    def signer_for(self, cp: Any, request_id: int) -> tuple:
        """(key, principal) that approves in this control plane's database: the agent key in a
        simulation database (approver_policy.SIMULATION_DB_NAME), the operator (human) key in any
        other, mirroring one approver per pipeline."""
        if pipeline_context(cp.db_path) == CONTEXT_SIMULATION:
            return self.key, AGENT_SIMULATION_PRINCIPAL
        return self.operator_key, OPERATOR_PRINCIPAL

    def identity_root_for(self, cp: Any) -> Path:
        """Repo root whose context/identity this human signs against.

        A repository-shaped database (<repo>/context/control_plane.db) in the temp dir signs against
        that repository's own identity folder, as production does (approver_policy requires it). A
        control plane rooted in a temp dir keeps its own identity folder; anything else (no
        repo_root, or a real checkout) gets a private root inside this human's temp dir.
        """
        temp = Path(tempfile.gettempdir()).resolve()
        db_path = getattr(cp, "db_path", None)
        if db_path and is_repository_db(db_path) and Path(db_path).resolve().is_relative_to(temp):
            return Path(db_path).resolve().parent.parent
        repo_root = getattr(cp, "repo_root", None)
        if repo_root and Path(repo_root).resolve().is_relative_to(Path(tempfile.gettempdir()).resolve()):
            return Path(repo_root)
        return self._dir / "repo"

    def sign_request(self, cp: Any, request_id: int) -> Any:
        layout = self.ensure_identity(self.identity_root_for(cp))
        key, principal = self.signer_for(cp, request_id)
        challenge = show_challenge(
            cp, request_id, layout=layout, key_hint=str(key), agent_identity=self.agent_identity, out=open(os.devnull, "w"),
        )
        sig = Path(str(challenge) + ".sig")
        if sig.exists():
            sig.unlink()
        subprocess.run(sign_command(str(key), challenge), check=True, capture_output=True)
        return approve_transition(
            cp, request_id, layout=layout, principal=principal, agent_identity=self.agent_identity, out=open(os.devnull, "w"),
        )

    def close(self) -> None:
        shutil.rmtree(self._dir, ignore_errors=True)


_SINGLETON = None


def get_test_human() -> "TestHuman":
    """One throwaway human (key) per test process; also used by fixtures that must sign during setup."""
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = TestHuman()
        atexit.register(_SINGLETON.close)  # remove the throwaway key dir instead of leaking it into $TMPDIR
    return _SINGLETON
