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
