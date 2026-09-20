"""
tests/test_approve_transition.py
================================

Purpose:
    Failing-first acceptance tests for T6 (auth-ciba-increment-b, issue #639):
    `agent_control.py show-challenge` and `approve-transition` (control_plane/gate1_approval.py),
    the human-uid half of Gate 1. Spec section 4 cases 2, 20, 23, 24. The request is created by
    the real strict-mode coordinator (a real PENDING transition_request), the signature by the
    real `ssh-keygen` with a throwaway key, and the identity files are real files in tmp_path;
    the agent identity is injected. Nothing is mocked.

Key Input Dependencies:
    - control_plane/gate1_approval.py (show_challenge, approve_transition, GateApprovalError)
    - control_plane/coordinator.py (authorization_preflight, HumanProofRequired)
    - control_plane/identity_layout.py, ssh_signing.py, isolation_check.py
    - agent_control.py (_build_parser: the verbs and the absence of --signature)
    - tests/helpers/gate1_fixtures.py

Key Functions (test cases):
    - test_show_challenge_writes_the_exact_bytes_and_prints_the_sign_command
    - test_show_challenge_is_idempotent / _refuses_when_content_changed / _refuses_when_isolation_fails
    - test_approve_with_a_real_signature_commits
    - test_approve_refuses_when_guidance_blocked_between_request_and_approve
    - test_approve_without_signature_file / _with_another_keys_signature / _expired / _non_proof_edge
    - test_authorization_preflight_reports_a_guidance_block
    - test_cli_registers_the_verbs_and_has_no_signature_argument
"""

import io
import os
import pwd
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

import agent_control
from control_plane.coordinator import HumanProofRequired, TransitionCoordinator
from control_plane.gate1_approval import GateApprovalError, approve_transition, show_challenge
from control_plane.identity_layout import default_layout
from control_plane.snapshot import build_snapshot, gate1_artifact_paths
from control_plane.ssh_signing import SELFTEST_NAMESPACE, SIGN_NAMESPACE, derive_challenge_from_row
from control_plane.transition_request import create_transition_request
from helpers.gate1_fixtures import reach_awaiting_approval

TASK = "approve-task-001"
_FOUND = shutil.which("ssh-keygen")
SSH_KEYGEN: str = _FOUND or "ssh-keygen"

pytestmark = [pytest.mark.no_auto_signer, pytest.mark.skipif(_FOUND is None, reason="ssh-keygen not installed")]


def _other_uid() -> int:
    for name in ("nobody", "daemon"):
        try:
            uid = pwd.getpwnam(name).pw_uid
            if uid != os.geteuid():
                return uid
        except KeyError:
            continue
    return os.geteuid() + 4242


class Gate:
    def __init__(self, tmp_path: Path):
        self.tmp = tmp_path
        self.sim = reach_awaiting_approval(tmp_path, TASK)
        self.cp = self.sim.control_plane
        self.repo = Path(self.cp.repo_root)
        folder = self.repo / "docs" / "plans" / "work-tasks" / TASK
        folder.mkdir(parents=True, exist_ok=True)
        self.spec = folder / f"{TASK}-spec.md"
        self.spec.write_text("spec v1\n")
        (folder / f"{TASK}-implementation-plan.md").write_text("plan v1\n")

        self.layout = default_layout(self.repo)
        for d in (self.layout.root, self.layout.challenge_dir):
            d.mkdir(parents=True, exist_ok=True)
            os.chmod(d, 0o700)
        keys = tmp_path / "keys"
        keys.mkdir()
        self.key = keys / "id"
        self._keygen(self.key)
        pub = (keys / "id.pub").read_text().split()
        self.layout.allowed_signers.write_text(f'op@local namespaces="{SIGN_NAMESPACE}" {pub[0]} {pub[1]}\n')
        self.layout.allowed_signers_selftest.write_text(f'op@local namespaces="{SELFTEST_NAMESPACE}" {pub[0]} {pub[1]}\n')
        os.chmod(self.layout.allowed_signers, 0o600)
        os.chmod(self.layout.allowed_signers_selftest, 0o600)
        self.identity = {"agent_name": "agentic-os-local-agent", "agent_uid": _other_uid(), "agent_gids": set()}
        self.request_id = self._make_request()

    @staticmethod
    def _keygen(path: Path) -> None:
        subprocess.run([SSH_KEYGEN, "-q", "-t", "ed25519", "-N", "", "-C", "op", "-f", str(path)], check=True, capture_output=True)

    def coordinator(self):
        return TransitionCoordinator(
            self.cp, registry=self.sim.registry, output_stream=io.StringIO(),
        )

    def _make_request(self) -> int:
        with pytest.raises(HumanProofRequired) as excinfo:
            self.coordinator().coordinate_transition(
                task_id=TASK, to_state="APPROVED", actor="agent", reason="request", interactive=False,
            )
        return excinfo.value.remediation["request_id"]

    def show(self, **kw):
        out = io.StringIO()
        path = show_challenge(self.cp, self.request_id, layout=self.layout, key_hint=str(self.key), agent_identity=self.identity, out=out, **kw)
        return path, out.getvalue()

    def sign(self, challenge_path: Path, key: Path = None) -> None:
        subprocess.run(
            [SSH_KEYGEN, "-Y", "sign", "-f", str(key or self.key), "-n", SIGN_NAMESPACE, str(challenge_path)],
            check=True, capture_output=True,
        )

    def approve(self, **kw):
        return approve_transition(
            self.cp, self.request_id, layout=self.layout, principal="op@local",
            agent_identity=self.identity, out=io.StringIO(), **kw,
        )

    def db(self):
        return sqlite3.connect(self.cp.db_path)

    def state(self):
        return self.db().execute("SELECT state FROM tasks WHERE task_id = ?", (TASK,)).fetchone()[0]

    def status(self, request_id=None):
        return self.db().execute("SELECT status FROM transition_request WHERE request_id = ?", (request_id or self.request_id,)).fetchone()[0]


@pytest.fixture
def gate(tmp_path):
    return Gate(tmp_path)


def test_show_challenge_writes_the_exact_bytes_and_prints_the_sign_command(gate):
    path, printed = gate.show()
    live = build_snapshot(gate1_artifact_paths(gate.repo, TASK))
    expected = derive_challenge_from_row(gate.db(), gate.request_id, live)
    assert path.parent == gate.layout.challenge_dir
    assert path.read_bytes() == expected
    assert oct(path.stat().st_mode & 0o777) == "0o600"
    assert f"ssh-keygen -Y sign -f {gate.key} -n {SIGN_NAMESPACE} {path}" in printed
    assert expected.decode() in printed  # the human reads exactly what they will sign


def test_show_challenge_is_idempotent(gate):
    first, _ = gate.show()
    second, _ = gate.show()
    assert first == second


def test_show_challenge_refuses_when_the_reviewed_content_changed(gate):
    gate.spec.write_text("spec EDITED after the request\n")
    with pytest.raises(GateApprovalError) as excinfo:
        gate.show()
    assert "changed" in str(excinfo.value)
    assert list(gate.layout.challenge_dir.iterdir()) == []


def test_show_challenge_refuses_when_isolation_fails(gate):
    os.chmod(gate.layout.allowed_signers, 0o644)
    with pytest.raises(GateApprovalError) as excinfo:
        gate.show()
    assert "BAD_MODE" in str(excinfo.value)
    assert list(gate.layout.challenge_dir.iterdir()) == []


def test_approve_with_a_real_signature_commits(gate):
    path, _ = gate.show()
    gate.sign(path)
    record = gate.approve()
    assert record.to_state == "APPROVED" and gate.state() == "APPROVED"
    assert gate.status() == "CONSUMED"
    # The consumed, signature-verified request is the authority: no decision rows and no actor='human' strings.
    rows = gate.db().execute(
        "SELECT question_id, actor FROM transition_decisions WHERE task_id = ? AND to_state = 'APPROVED'", (TASK,)
    ).fetchall()
    assert rows == []
    audit = gate.db().execute("SELECT command_executed FROM verification_receipts WHERE task_id = ? AND gate_name = 'human_gate_proof'", (TASK,)).fetchall()
    assert audit and "proof=sshsig" in audit[0][0]


def test_approve_refuses_when_guidance_blocked_between_request_and_approve(gate):
    path, _ = gate.show()
    gate.sign(path)
    gate.cp.set_guidance_block(TASK, "test: blocked after the request")
    with pytest.raises(GateApprovalError) as excinfo:
        gate.approve()
    assert "guidance" in str(excinfo.value).lower()
    assert gate.state() == "AWAITING_APPROVAL" and gate.status() == "PENDING"


def test_authorization_preflight_reports_a_guidance_block(gate):
    coord = gate.coordinator()
    gate.cp.set_guidance_block(TASK, "test block")
    reasons = coord.authorization_preflight(TASK, "APPROVED")
    assert any("guidance" in r.lower() for r in reasons)


def test_approve_without_a_signature_file_is_refused(gate):
    gate.show()
    with pytest.raises(GateApprovalError):
        gate.approve()
    assert gate.state() == "AWAITING_APPROVAL" and gate.status() == "PENDING"


def test_approve_with_another_keys_signature_is_refused(gate, tmp_path):
    attacker = tmp_path / "attacker"
    attacker.mkdir()
    Gate._keygen(attacker / "id")
    path, _ = gate.show()
    gate.sign(path, key=attacker / "id")
    with pytest.raises(GateApprovalError):
        gate.approve()
    assert gate.state() == "AWAITING_APPROVAL" and gate.status() == "PENDING"


def test_approve_refuses_an_expired_request(gate):
    path, _ = gate.show()
    gate.sign(path)
    conn = gate.db()
    conn.execute("UPDATE transition_request SET expiration = 1.0 WHERE request_id = ?", (gate.request_id,))
    conn.commit()
    with pytest.raises(GateApprovalError) as excinfo:
        gate.approve()
    assert "expired" in str(excinfo.value).lower()
    assert gate.state() == "AWAITING_APPROVAL"


def test_approve_refuses_a_request_for_an_edge_that_takes_no_proof(gate):
    snapshot = build_snapshot(gate1_artifact_paths(gate.repo, TASK))
    other = create_transition_request(
        gate.db(), task_id=TASK, from_state="AWAITING_APPROVAL", to_state="DRAFT_PLAN", occupancy_id=1, content_snapshot=snapshot,
    )
    gate.request_id = other.request_id
    with pytest.raises(GateApprovalError):
        gate.approve()
    assert gate.state() == "AWAITING_APPROVAL"


def test_cli_registers_the_verbs_and_has_no_signature_argument():
    parser = agent_control._build_parser()
    assert parser.parse_args(["show-challenge", "--request-id", "3"]).request_id == 3
    assert parser.parse_args(["approve-transition", "--request-id", "3"]).request_id == 3
    with pytest.raises(SystemExit):
        parser.parse_args(["approve-transition", "--request-id", "3", "--signature", "/tmp/x.sig"])
