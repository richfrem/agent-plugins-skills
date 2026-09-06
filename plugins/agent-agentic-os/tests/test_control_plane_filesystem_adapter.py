"""
test_control_plane_filesystem_adapter.py — Filesystem Seam Extraction (issue-524, Step 3)
=============================================================================================

Purpose:
    Unit tests for control_plane/adapters.py's FilesystemAdapter (in isolation, no SQLite),
    plus an integration test proving ControlPlane._log_orphan_merge_conflicts() now routes
    through the injected FilesystemPort instead of a raw open()/write() call. Regression
    oracle for docs/plans/issue-524-spec.md Section 5 Step 3 (filesystem seam, extracted
    before persistence/migration).

Key Input Dependencies:
    - Temporary files via pytest's tmp_path fixture

Key Functions:
    - test_filesystem_adapter_append_text_noop_when_file_absent()
    - test_filesystem_adapter_append_text_appends_when_file_exists()
    - test_filesystem_adapter_read_text_and_exists()
    - test_control_plane_uses_injected_filesystem_port_for_orphan_merge_log()
    - test_control_plane_defaults_to_real_filesystem_adapter()
"""

import sys
from pathlib import Path
from typing import List

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.adapters import FilesystemAdapter
from control_plane.ports import FilesystemPort
from agent_control import ControlPlane


def test_filesystem_adapter_append_text_noop_when_file_absent(tmp_path):
    """Characterizes the exact original guard: appending to a non-existent file is a silent no-op."""
    target = tmp_path / "does-not-exist.md"
    FilesystemAdapter().append_text(target, "\nnew row\n")
    assert not target.exists()


def test_filesystem_adapter_append_text_appends_when_file_exists(tmp_path):
    """Appending to an existing file appends content without truncating it."""
    target = tmp_path / "map-debt.md"
    target.write_text("# Map Debt\n", encoding="utf-8")
    FilesystemAdapter().append_text(target, "| DEBT-1 | ... |\n")
    assert target.read_text(encoding="utf-8") == "# Map Debt\n| DEBT-1 | ... |\n"


def test_filesystem_adapter_read_text_and_exists(tmp_path):
    """read_text() and exists() reflect real filesystem state."""
    target = tmp_path / "file.txt"
    fs = FilesystemAdapter()
    assert fs.exists(target) is False
    target.write_text("hello", encoding="utf-8")
    assert fs.exists(target) is True
    assert fs.read_text(target) == "hello"


class _RecordingFilesystemPort(FilesystemPort):
    """Test double recording every append_text call instead of touching real disk."""

    def __init__(self, existing_paths=None):
        self.existing_paths = set(existing_paths or [])
        self.appended: List[tuple] = []

    def append_text(self, path: Path, content: str) -> None:
        if path not in self.existing_paths:
            return
        self.appended.append((path, content))

    def read_text(self, path: Path) -> str:
        raise NotImplementedError

    def exists(self, path: Path) -> bool:
        return path in self.existing_paths


def test_control_plane_uses_injected_filesystem_port_for_orphan_merge_log(tmp_path):
    """Integration: ControlPlane._log_orphan_merge_conflicts() must call the injected
    FilesystemPort, not a raw open()/write() — proves the Step 3 wiring actually took effect."""
    db_path = tmp_path / "control_plane.db"
    recorder = _RecordingFilesystemPort()

    cp = ControlPlane(db_path=db_path, fs_adapter=recorder)

    # _log_orphan_merge_conflicts() derives its target path from agent_control.py's own
    # __file__ (repo_root / references / map-debt.md) rather than accepting one as a
    # parameter, so we register that real resolved path as "existing" in the recording
    # double instead of touching the real file.
    import agent_control as ac
    assert ac.__file__ is not None
    real_map_debt_path = Path(ac.__file__).resolve().parent.parent.parent.parent / "references" / "map-debt.md"
    recorder.existing_paths.add(real_map_debt_path)

    cp._log_orphan_merge_conflicts(["task-a", "task-b"])

    assert len(recorder.appended) == 1
    appended_path, appended_content = recorder.appended[0]
    assert appended_path == real_map_debt_path
    assert "task-a, task-b" in appended_content
    assert "DEBT-" in appended_content


def test_control_plane_defaults_to_real_filesystem_adapter(tmp_path):
    """When no fs_adapter is passed, ControlPlane wires a real FilesystemAdapter — preserves
    the original direct-filesystem behavior for all existing callers (backward-compat facade)."""
    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    assert isinstance(cp._fs, FilesystemAdapter)
