"""
control_plane/adapters.py — Concrete Port Implementations (issue-524)
========================================================================

Purpose:
    Concrete adapters implementing the port interfaces declared in control_plane/ports.py
    against real infrastructure. Populated incrementally as agent_control.py's ControlPlane
    responsibilities are extracted (docs/plans/issue-524-spec.md, Section 5): this step adds
    only FilesystemAdapter (Step 3 — extracted first per external plan review, since migration
    already depends on it). Persistence/Crypto/ModelCatalog adapters land in later steps.

Layer:
    OS Kernel / Execution Control Plane Substrate — Adapters (hexagonal boundary)

Key Input Dependencies:
    - Local filesystem (FilesystemAdapter)

Key Functions:
    - FilesystemAdapter.append_text() — appends text to a file, no-op if the file doesn't exist
    - FilesystemAdapter.read_text() — reads a file's full text content
    - FilesystemAdapter.exists() — checks file existence
"""

from pathlib import Path

from control_plane.ports import FilesystemPort


class FilesystemAdapter(FilesystemPort):
    """Real-filesystem implementation of FilesystemPort. Mirrors the exact current behavior
    of agent_control.py's _log_orphan_merge_conflicts(): silently does nothing if the target
    file does not already exist (never creates it), matching the original guard
    `if not map_debt_path.exists(): return`."""

    def append_text(self, path: Path, content: str) -> None:
        """Appends `content` to the file at `path`. No-op if the file does not already exist —
        preserves the original _log_orphan_merge_conflicts() behavior exactly."""
        if not path.exists():
            return
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)

    def read_text(self, path: Path) -> str:
        """Reads and returns the full text content of the file at `path`."""
        return path.read_text(encoding="utf-8")

    def exists(self, path: Path) -> bool:
        """Returns whether a file exists at `path`."""
        return path.exists()
