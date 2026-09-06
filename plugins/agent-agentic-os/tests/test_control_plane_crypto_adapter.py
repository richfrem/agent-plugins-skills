"""
test_control_plane_crypto_adapter.py — Crypto Extraction (issue-524, Step 6)
================================================================================

Purpose:
    Unit tests for control_plane/adapters.py's CryptoAdapter in isolation, plus integration
    tests proving ControlPlane routes SHA256/receipt-token hashing through the injected
    CryptoPort instead of a raw hashlib call or the old module-level _sha256_file() function.

Key Input Dependencies:
    - Temporary files via pytest's tmp_path fixture

Key Functions:
    - test_crypto_adapter_sha256_file_matches_known_digest()
    - test_crypto_adapter_sha256_hex_matches_known_digest()
    - test_agent_control_no_longer_defines_module_level_sha256_file()
    - test_control_plane_uses_injected_crypto_port_for_verifier_lock_and_verify()
    - test_control_plane_uses_injected_crypto_port_for_receipt_token()
    - test_control_plane_defaults_to_real_crypto_adapter()
"""

import ast
import hashlib
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.adapters import CryptoAdapter
from control_plane.ports import CryptoPort
from agent_control import ControlPlane

AGENT_CONTROL_FILE = SCRIPTS_DIR / "agent_control.py"


def test_crypto_adapter_sha256_file_matches_known_digest(tmp_path):
    """sha256_file() matches Python's own hashlib digest for the same content."""
    target = tmp_path / "verifier.py"
    target.write_text("def check(): return True\n", encoding="utf-8")
    expected = hashlib.sha256(target.read_bytes()).hexdigest()
    assert CryptoAdapter().sha256_file(target) == expected


def test_crypto_adapter_sha256_hex_matches_known_digest():
    """sha256_hex() matches Python's own hashlib digest for the same string."""
    raw = "task-1:test_suite:pytest:0:12345.6"
    expected = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    assert CryptoAdapter().sha256_hex(raw) == expected


def test_agent_control_no_longer_defines_module_level_sha256_file():
    """Structural confirmation: the old module-level _sha256_file() function no longer
    exists in agent_control.py — all hashing routes through the injected CryptoPort."""
    source = AGENT_CONTROL_FILE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    defined_names = {
        node.name for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "_sha256_file" not in defined_names


class _RecordingCryptoPort(CryptoPort):
    """Test double recording every crypto call instead of touching real hashlib."""

    def __init__(self):
        self.file_calls = []
        self.hex_calls = []

    def sha256_file(self, path: Path) -> str:
        self.file_calls.append(path)
        return "recorded-file-digest"

    def sha256_hex(self, raw: str) -> str:
        self.hex_calls.append(raw)
        return "recorded-hex-digest-0123456789ab"


def test_control_plane_uses_injected_crypto_port_for_verifier_lock_and_verify(tmp_path):
    """Integration: lock_verifiers()/verify_sovereignty() call the injected CryptoPort, not
    a raw hashlib call — proves the Step 6 wiring actually took effect."""
    verifier_file = tmp_path / "verifier.py"
    verifier_file.write_text("def check(): return True\n", encoding="utf-8")

    recorder = _RecordingCryptoPort()
    cp = ControlPlane(db_path=tmp_path / "control_plane.db", crypto_adapter=recorder)
    cp.create_task(task_id="t1", title="Crypto Task", runtime_tool="claude")
    cp.lock_verifiers(task_id="t1", file_paths=[verifier_file])

    assert len(recorder.file_calls) == 1
    assert recorder.file_calls[0] == verifier_file.resolve()

    # verify_sovereignty compares curr_sha (from CryptoPort) against the stored expected_sha256
    # (also "recorded-file-digest", stamped by lock_verifiers above) — must match and pass.
    assert cp.verify_sovereignty(task_id="t1") is True
    assert len(recorder.file_calls) == 2


def test_control_plane_uses_injected_crypto_port_for_receipt_token(tmp_path):
    """Integration: record_verification_receipt() calls the injected CryptoPort's sha256_hex(),
    not a raw hashlib call, to generate the receipt token."""
    recorder = _RecordingCryptoPort()
    cp = ControlPlane(db_path=tmp_path / "control_plane.db", crypto_adapter=recorder)
    cp.create_task(task_id="t1", title="Receipt Task", runtime_tool="claude")

    token = cp.record_verification_receipt(task_id="t1", gate_name="test_suite", command_executed="pytest", exit_code=0)

    assert len(recorder.hex_calls) == 1
    assert token == "EVO-INTEGRITY-t1-recorded-hex"  # first 12 chars of "recorded-hex-digest..."


def test_control_plane_defaults_to_real_crypto_adapter(tmp_path):
    """When no crypto_adapter is passed, ControlPlane wires a real CryptoAdapter — preserves
    the original direct-hashlib behavior for all existing callers (backward-compat facade)."""
    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    assert isinstance(cp._crypto, CryptoAdapter)
