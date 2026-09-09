"""Native-first worktree planning with a governed portable fallback."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from capability_probe import RuntimeCapabilities


@dataclass(frozen=True)
class WorktreePlan:
    task_id: str
    branch_name: str
    strategy: str
    path: Path
    activation_guidance: str
    fallback_command: str


def validate_portable_placement(path: Path, repo_root: Path) -> Path:
    """Require portable worktrees to remain below the repository's .worktrees dir."""
    worktree_root = (repo_root / ".worktrees").resolve()
    candidate = path.resolve()
    if candidate != worktree_root and worktree_root not in candidate.parents:
        raise ValueError(f"Portable worktree must be below {worktree_root}")
    return path


def build_worktree_plan(
    task_id: str,
    branch_name: str,
    repo_root: Path,
    capabilities: RuntimeCapabilities,
) -> WorktreePlan:
    """Prefer confirmed native worktrees; otherwise retain the portable placement."""
    portable_path = repo_root / ".worktrees" / task_id
    if capabilities.native_worktree:
        return WorktreePlan(task_id, branch_name, "native", portable_path,
                            capabilities.worktree_activation, capabilities.portable_fallback)
    validate_portable_placement(portable_path, repo_root)
    return WorktreePlan(task_id, branch_name, "portable", portable_path,
                        capabilities.worktree_activation, capabilities.portable_fallback)


def cleanup_command(path: Path, strategy: str) -> list[str]:
    """Return an explicit cleanup command without executing it."""
    if strategy == "native":
        return ["native-worktree-cleanup", str(path)]
    if strategy == "portable":
        return ["git", "worktree", "remove", str(path)]
    raise ValueError(f"Unknown worktree strategy: {strategy}")

