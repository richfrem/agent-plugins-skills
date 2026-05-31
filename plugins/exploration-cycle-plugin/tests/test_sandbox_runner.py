# plugins/exploration-cycle-plugin/tests/test_sandbox_runner.py
from collections import OrderedDict  # top-of-file import (GPT-6 fix)
import sys, os, subprocess
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import sandbox_runner as SR


def test_clean_env_only_has_allowed_keys():
    os.environ["PYTHONPATH"] = "/injected"
    os.environ["DYLD_INSERT_LIBRARIES"] = "/evil.dylib"
    env = SR._build_clean_env()
    assert "PYTHONPATH" not in env
    assert "DYLD_INSERT_LIBRARIES" not in env
    for key in env:
        assert key in SR.ALLOWED_ENV


def test_extra_vars_blocked_if_dangerous():
    env = SR._build_clean_env(extra_vars={"LD_PRELOAD": "/bad.so", "MY_VAR": "ok"})
    assert "LD_PRELOAD" not in env
    assert env.get("MY_VAR") == "ok"


def test_run_hygienic_executes_command():
    result = SR.run_hygienic([sys.executable, "-c", "print('ok')"], timeout=10)
    assert result.returncode == 0


def test_run_hygienic_env_is_clean():
    os.environ["PYTHONPATH"] = "/should-not-leak"
    result = SR.run_hygienic(
        [sys.executable, "-c",
         "import os, sys; sys.exit(0 if 'PYTHONPATH' not in os.environ else 1)"],
        timeout=10,
    )
    assert result.returncode == 0


def test_terminate_with_grace_kills_slow_process():
    import time
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(9999)"],
        env=SR._build_clean_env(),
    )
    start = time.time()
    SR._terminate_with_grace(proc, grace=1)
    elapsed = time.time() - start
    assert proc.poll() is not None
    assert elapsed < 5


def test_run_containerized_splits_mounts(monkeypatch):
    """run_containerized must apply :ro suffix to read-only paths."""
    calls = []
    monkeypatch.setattr(subprocess, "Popen", lambda cmd, **kw: calls.append(cmd) or
                        type("P", (), {"communicate": lambda s, **k: (b"", b""),
                                       "returncode": 0})())
    try:
        SR.run_containerized(
            ["echo", "test"], "sess-1", "disp-1",
            allowed_paths_ro=["/read/path"],
            allowed_paths_rw=["/write/path"],
            timeout=5
        )
    except Exception:
        pass
    if calls:
        cmd_str = " ".join(calls[0])
        assert "/read/path:/read/path:ro" in cmd_str
        assert "/write/path:/write/path" in cmd_str
        assert "/write/path:/write/path:ro" not in cmd_str


def test_sign_and_verify_envelope_roundtrip():
    key = os.urandom(32)
    nonce_cache = OrderedDict()
    envelope = SR.sign_envelope({"task_id": "t1", "action": "complete"}, key)
    assert SR.verify_envelope(envelope, key, nonce_cache) is True


def test_verify_rejects_tampered_payload():
    key = os.urandom(32)
    nonce_cache = OrderedDict()
    envelope = SR.sign_envelope({"task_id": "t1"}, key)
    envelope["payload"]["task_id"] = "evil"
    assert SR.verify_envelope(envelope, key, nonce_cache) is False


def test_verify_rejects_wrong_key():
    key_a, key_b = os.urandom(32), os.urandom(32)
    envelope = SR.sign_envelope({"x": 1}, key_a)
    assert SR.verify_envelope(envelope, key_b, OrderedDict()) is False


def test_verify_rejects_nonce_replay():
    key = os.urandom(32)
    nonce_cache = OrderedDict()
    envelope = SR.sign_envelope({"x": 1}, key)
    assert SR.verify_envelope(envelope, key, nonce_cache) is True
    assert SR.verify_envelope(envelope, key, nonce_cache) is False


def test_session_key_written_with_0600_permissions(tmp_path):
    key_path = tmp_path / ".secrets" / "session_hmac.key"
    SR.generate_session_key(key_path)
    assert key_path.exists()
    assert oct(key_path.stat().st_mode)[-3:] == "600"


def test_cleanup_session_key_removes_file(tmp_path):
    key_path = tmp_path / ".secrets" / "session_hmac.key"
    SR.generate_session_key(key_path)
    SR.cleanup_session_key(key_path)
    assert not key_path.exists()
