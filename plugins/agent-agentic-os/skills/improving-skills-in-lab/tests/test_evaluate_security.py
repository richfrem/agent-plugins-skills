"""
Purpose:
    Security-focused unit tests for evaluate.py: SHA256 gate-script locking
    during --baseline, and exclusive/no-follow trace file writes.

Key Input Dependencies:
    - evaluate.py (in ../scripts/, imported directly)
    - pytest tmp_path and monkeypatch fixtures
"""
import sys, os, json
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import evaluate as E


def test_baseline_still_checks_gate_scripts(tmp_path):
    """During --baseline, SHA256 of evaluate.py and eval_runner.py must still be checked."""
    lock_hashes_path = tmp_path / ".lock.hashes"
    lock_hashes_path.write_text(json.dumps({
        str(E.LOCKED_FILES[0]): "0" * 64,
        str(E.LOCKED_FILES[1]): "0" * 64,
    }))
    with pytest.raises(SystemExit) as exc:
        E.check_sha256_hashes(tmp_path / "results.tsv", E.LOCKED_FILES)
    assert exc.value.code == 3


def test_trace_write_uses_o_excl(tmp_path, monkeypatch):
    """Trace files must be written with O_CREAT|O_EXCL|O_NOFOLLOW."""
    traces_dir = tmp_path / "traces"
    traces_dir.mkdir()
    opens_seen = []
    original_open = os.open

    def tracked_open(path, flags, mode=0o777, **kwargs):
        """Record the flags passed to os.open, then delegate to the real os.open."""
        opens_seen.append((path, flags))
        return original_open(path, flags, mode, **kwargs)

    monkeypatch.setattr(os, "open", tracked_open)
    E._write_trace_exclusive(traces_dir, "iter_001_KEEP_score0.95.json", '{"test": true}')

    assert opens_seen
    _, flags = opens_seen[0]
    assert flags & os.O_EXCL
    assert flags & os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        assert flags & os.O_NOFOLLOW


def test_trace_write_adds_nonce_on_collision(tmp_path):
    """When trace filename is taken, a nonce variant must be written instead."""
    traces_dir = tmp_path / "traces"
    traces_dir.mkdir()
    filename = "iter_001_KEEP_score0.95.json"
    (traces_dir / filename).write_text("{}")

    E._write_trace_exclusive(traces_dir, filename, '{"collision": true}')

    written = list(traces_dir.iterdir())
    assert len(written) == 2
    nonce_file = [f for f in written if f.name != filename][0]
    assert nonce_file.read_text() == '{"collision": true}'
