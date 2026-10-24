#!/usr/bin/env python3
"""
control_plane/proof_edges.py
============================

Purpose:
    Edge-specific content binding for the proof-required (human-signed) transitions of
    auth-ciba-increment-b (issue #639). Gate 1 (AWAITING_APPROVAL -> APPROVED) binds the reviewed spec and
    plan files; Gate 3 (WORKTREE_REVIEW / MULTI_AGENT_CODE_REVIEW -> VERIFY_EXIT, human acceptance of the
    agent's code) binds the registered git worktree: commit SHA, tracked-diff hash and untracked-files hash.
    The coordinator (request creation) and the approval flow (challenge rendering and signature
    verification) both call snapshot_for_edge so they always agree on what is being signed.

Key Input Dependencies:
    - control_plane/snapshot.py (build_snapshot, gate1_artifact_paths, code_acceptance_snapshot)
    - the task's registered `worktree_path` (from the control plane) for Gate 3

Key Functions:
    - snapshot_for_edge()  -- the ordered SnapshotEntry tuple to bind for an edge
    - resolve_worktree()   -- the task's registered worktree as an absolute path
    - prefetch_for_edge()  -- database reads needed by the snapshot, done before a commit transaction
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from control_plane.constants import STATE_DONE, STATE_RETROSPECTIVE, STATE_VERIFY_EXIT
from control_plane.snapshot import (
    SnapshotEntry,
    SnapshotError,
    build_snapshot,
    code_acceptance_snapshot,
    gate1_artifact_paths,
)


def resolve_worktree(cp: Any, task_id: str, repo_root: Union[str, Path]) -> Path:
    """The task's registered worktree; a relative path resolves against the shared repository root."""
    task = cp.get_task(task_id) or {}
    raw = task.get("worktree_path")
    if not raw:
        raise SnapshotError(f"task {task_id} has no registered worktree to accept (run update-worktree first)")
    path = Path(raw)
    return path if path.is_absolute() else Path(repo_root) / path


def snapshot_for_edge(
    cp: Any, repo_root: Union[str, Path], task_id: str, from_state: str, to_state: str,
    worktree: Optional[Path] = None, prefetched: Optional[Dict[str, Any]] = None,
) -> Tuple[SnapshotEntry, ...]:
    """Bind the plan artifacts for Gate 1, or the git worktree (and, for closure, the retrospective) for the
    VERIFY_EXIT / DONE edges. Inside a database transaction pass `prefetched` (see prefetch_for_edge) so no second
    connection is opened."""
    if to_state == STATE_VERIFY_EXIT:
        return code_acceptance_snapshot(worktree or (prefetched or {}).get("worktree") or resolve_worktree(cp, task_id, repo_root))
    if to_state == STATE_DONE:
        return _closure_snapshot(cp, repo_root, task_id, from_state, prefetched)
    return build_snapshot(gate1_artifact_paths(repo_root, task_id))


def prefetch_for_edge(cp: Any, repo_root: Union[str, Path], task_id: str, from_state: str, to_state: str) -> Optional[Dict[str, Any]]:
    """Read everything database-backed that snapshot_for_edge needs, BEFORE a commit transaction starts."""
    if to_state == STATE_VERIFY_EXIT:
        return {"worktree": resolve_worktree(cp, task_id, repo_root)}
    if to_state != STATE_DONE:
        return None
    try:
        worktree = resolve_worktree(cp, task_id, repo_root)
    except SnapshotError:
        worktree = None
    summary = cp._persistence.get_retrospective_summary(task_id) if from_state == STATE_RETROSPECTIVE else None
    return {"worktree": worktree, "retrospective": summary}


def _closure_snapshot(cp: Any, repo_root: Union[str, Path], task_id: str, from_state: str, prefetched: Optional[Dict[str, Any]]) -> Tuple[SnapshotEntry, ...]:
    """What a human signs to close a task: the worktree's commit/diff/untracked hashes when a git worktree is
    registered (else an explicit 'none' marker), plus, for normal completion from RETROSPECTIVE, the recorded
    retrospective decision and its digest. The entry list is fixed by these inputs, so it is reproducible."""
    data = prefetched if prefetched is not None else prefetch_for_edge(cp, repo_root, task_id, from_state, STATE_DONE)
    entries: Tuple[SnapshotEntry, ...]
    try:
        if data["worktree"] is None:
            raise SnapshotError("no registered worktree")
        entries = code_acceptance_snapshot(data["worktree"])
    except SnapshotError:
        entries = (SnapshotEntry("worktree", "none"),)
    if from_state == STATE_RETROSPECTIVE:
        summary = data.get("retrospective")
        if summary is None:
            raise SnapshotError(f"task {task_id} has no recorded retrospective to close on")
        entries += (SnapshotEntry("retrospective_decision", summary["decision"]), SnapshotEntry("retrospective", summary["digest"]))
    return entries
