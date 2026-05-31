# plugins/agent-agentic-os/tests/test_kernel_security.py
import sys, os, json, time
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import kernel as K


@pytest.fixture
def tmp_kernel(tmp_path, monkeypatch):
    monkeypatch.setattr(K, "KERNEL_DIR", tmp_path)
    monkeypatch.setattr(K, "EVENTS_FILE", tmp_path / "events.jsonl")
    monkeypatch.setattr(K, "LOCKS_DIR", tmp_path / ".locks")
    monkeypatch.setattr(K, "STATE_FILE", tmp_path / "os-state.json")
    monkeypatch.setattr(K, "AGENTS_FILE", tmp_path / "agents.json")
    monkeypatch.setattr(K, "AGENTS_DIR", tmp_path / "agents")
    (tmp_path / ".locks").mkdir()
    (tmp_path / "agents").mkdir()
    (tmp_path / "agents.json").write_text(
        json.dumps({"permitted_agents": ["test-agent"]})
    )
    return tmp_path


def test_safe_clear_stale_rejects_concurrent_acquisition(tmp_kernel, monkeypatch):
    """_safe_clear_stale must return False if lock is acquired between its two reads.

    Uses monkeypatch on time.sleep to inject a concurrent acquisition deterministically
    rather than relying on thread scheduling jitter.
    """
    lock_path = tmp_kernel / ".locks" / "test.lock"
    lock_path.mkdir()
    meta = {"pid": 99999999, "expires_at": time.time() - 10, "acquired_at": "2000-01-01T00:00:00Z"}
    (lock_path / "meta.json").write_text(json.dumps(meta))

    original_sleep = time.sleep

    def sleep_and_inject(seconds):
        # Simulate concurrent acquisition during the pause between double-reads
        new_meta = {
            "pid": os.getpid(),
            "expires_at": time.time() + 300,
            "acquired_at": "2026-01-01T00:00:00Z",
        }
        (lock_path / "meta.json").write_text(json.dumps(new_meta))
        original_sleep(seconds)

    monkeypatch.setattr(time, "sleep", sleep_and_inject)
    result = K._safe_clear_stale(lock_path)
    assert result is False, "_safe_clear_stale must detect concurrent acquisition via double-read"
    assert lock_path.exists(), "Lock must not be cleared when concurrent acquisition detected"


def test_rotation_happens_inside_write_lock(tmp_kernel, monkeypatch):
    """File size check and rename must happen inside events_write.lock, not before."""
    events_file = tmp_kernel / "events.jsonl"
    events_file.write_bytes(b"x" * (K.EVENTS_MAX_BYTES + 1))

    rotation_order = []
    original_spinlock = K._spinlock

    def tracked_spinlock(lock_path, timeout=30):
        rotation_order.append(("spinlock", str(lock_path)))
        return original_spinlock(lock_path, timeout)

    original_rename = os.rename

    def tracked_rename(src, dst):
        rotation_order.append(("rename", str(src)))
        return original_rename(src, dst)

    monkeypatch.setattr(K, "_spinlock", tracked_spinlock)
    monkeypatch.setattr(os, "rename", tracked_rename)

    K.emit_event("test-agent", "result", "test_action")

    spinlock_indices = [i for i, op in enumerate(rotation_order) if op[0] == "spinlock"]
    rename_indices = [i for i, op in enumerate(rotation_order) if op[0] == "rename"]

    assert rename_indices, "Rotation must have occurred for file above EVENTS_MAX_BYTES (H-1)"
    write_lock_idx = next(
        i for i in spinlock_indices if "events_write" in rotation_order[i][1]
    )
    assert rename_indices[0] > write_lock_idx, (
        "Rotation rename must happen AFTER events_write.lock is acquired (H-1)"
    )
