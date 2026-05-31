# plugins/exploration-cycle-plugin/tests/test_path_traversal.py
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from sandbox_runner import _assert_under_root

def test_valid_path_passes(tmp_path):
    allowed = tmp_path / "work"
    allowed.mkdir()
    f = allowed / "file.txt"
    f.touch()
    _assert_under_root(f, allowed)  # must not raise

def test_sibling_prefix_rejected(tmp_path):
    """The classic bypass: /tmp/work_evil passes a naive startswith('/tmp/work') check."""
    allowed = tmp_path / "work"
    allowed.mkdir()
    evil = tmp_path / "work_evil"
    evil.mkdir()
    evil_file = evil / "secret.txt"
    evil_file.touch()
    with pytest.raises(PermissionError, match="Path traversal rejected"):
        _assert_under_root(evil_file, allowed)

def test_parent_escape_rejected(tmp_path):
    allowed = tmp_path / "work"
    allowed.mkdir()
    with pytest.raises(PermissionError):
        _assert_under_root(tmp_path / "outside.txt", allowed)

def test_symlink_escape_rejected(tmp_path):
    allowed = tmp_path / "work"
    allowed.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("secret")
    link = allowed / "escape_link"
    link.symlink_to(outside)
    with pytest.raises(PermissionError):
        _assert_under_root(link, allowed)
