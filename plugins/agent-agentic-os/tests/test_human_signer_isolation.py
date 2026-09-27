#!/usr/bin/env python
"""
test_human_signer_isolation.py
==============================

Purpose:
    Regression tests for the test-suite stand-in human (tests/helpers/human_signer.py).
    On 2026-09-24 the agentic-os suite was run from the real repository root; tests
    whose ControlPlane had no repo_root made the helper fall back to Path.cwd() and
    overwrite the operator's real context/identity/allowed_signers (and
    allowed_signers_selftest) with the throwaway test key, silently revoking the
    human's Gate 1 enrollment. The helper must never write outside a temp directory
    and must never drop lines already present in an allowed_signers file.

Key Input Dependencies:
    plugins/agent-agentic-os/tests/helpers/human_signer.py — TestHuman under test
    ssh-keygen (TestHuman generates a throwaway ed25519 key)

Layer: Development / Testing

Functions:
    - test_ensure_identity_refuses_real_repo_root
    - test_identity_root_is_temp_when_control_plane_has_no_repo_root
    - test_ensure_identity_keeps_existing_signers

Usage:
    python -m pytest plugins/agent-agentic-os/tests/test_human_signer_isolation.py
"""

import hashlib
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

_TESTS_DIR = Path(__file__).resolve().parent
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))

from helpers.human_signer import TestHuman

REPO_ROOT = Path(__file__).resolve().parents[3]
REAL_IDENTITY = REPO_ROOT / "context" / "identity"


def _digest(folder: Path) -> dict:
    """Hash every allowed_signers* file so any mutation is detectable."""
    if not folder.is_dir():
        return {}
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.glob("allowed_signers*"))}


@pytest.fixture
def human():
    h = TestHuman()
    yield h
    h.close()


def test_ensure_identity_refuses_real_repo_root(human):
    before = _digest(REAL_IDENTITY)
    with pytest.raises(RuntimeError, match="temp"):
        human.ensure_identity(REPO_ROOT)
    assert _digest(REAL_IDENTITY) == before


def test_identity_root_is_temp_when_control_plane_has_no_repo_root(human, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    root = human.identity_root_for(SimpleNamespace())
    assert root.resolve().is_relative_to(Path(tempfile.gettempdir()).resolve())
    assert not root.resolve().is_relative_to(REPO_ROOT)


def test_ensure_identity_keeps_existing_signers(human, tmp_path):
    identity = tmp_path / "context" / "identity"
    identity.mkdir(parents=True)
    operator = 'operator@control-plane namespaces="control-plane@agentic-os.local" ssh-ed25519 AAAAoperatorkey\n'
    (identity / "allowed_signers").write_text(operator, encoding="utf-8")

    human.ensure_identity(tmp_path)

    text = (identity / "allowed_signers").read_text(encoding="utf-8")
    assert operator.strip() in text
    assert "test-human@local" in text


def test_real_identity_trusting_test_signer_is_refused(tmp_path):
    from control_plane.gate1_approval import GateApprovalError, refuse_test_signer_outside_temp
    from control_plane.identity_layout import default_layout

    layout = default_layout(tmp_path)
    layout.root.mkdir(parents=True)
    layout.allowed_signers.write_text(
        'operator@control-plane namespaces="control-plane@agentic-os.local" ssh-ed25519 AAAAop\n'
        'test-human@local namespaces="control-plane@agentic-os.local" ssh-ed25519 AAAAtest\n',
        encoding="utf-8",
    )
    elsewhere = tmp_path / "not-the-temp-dir"
    elsewhere.mkdir()
    with pytest.raises(GateApprovalError, match="test-human@local"):
        refuse_test_signer_outside_temp(layout, temp_dir=elsewhere)
    refuse_test_signer_outside_temp(layout)  # inside the real temp dir: allowed (test suites)


def test_test_human_temp_dir_removed_at_exit(tmp_path):
    import subprocess
    marker = tmp_path / "dir.txt"
    code = (
        "import sys; sys.path.insert(0, %r)\n"
        "from helpers.human_signer import get_test_human\n"
        "open(%r, 'w').write(str(get_test_human()._dir))\n"
    ) % (str(_TESTS_DIR), str(marker))
    subprocess.run([sys.executable, "-c", code], check=True, cwd=_TESTS_DIR.parent / "scripts")
    assert not Path(marker.read_text()).exists()
