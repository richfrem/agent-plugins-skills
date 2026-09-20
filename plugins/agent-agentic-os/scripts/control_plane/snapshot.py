#!/usr/bin/env python3
"""
control_plane/snapshot.py
=========================

Purpose:
    Content snapshot and content-bound `revision_hash` for Gate 1
    (AWAITING_APPROVAL -> APPROVED) of auth-ciba-increment-b (issue #639, task T2,
    design gap (b) of DEBT-20260918-TRANSITION-REQUEST-DESIGN-GAPS). At Gate 1 the
    reviewed artifacts are documents (the spec and implementation plan under
    `docs/plans/work-tasks/<task-id>/`); no worktree or diff exists yet. A human
    approval must therefore bind those exact files, so that changing either one
    after the request invalidates the approval. The snapshot is an ordered list of
    (label, sha256) pairs; the same list is hashed into `revision_hash`, stored on
    the `transition_request` row as JSON, and later displayed in the challenge
    (T3/T6) and compared against the live files at approval time (T4).

Key Input Dependencies:
    - Python stdlib only (hashlib, json, dataclasses, pathlib)
    - The repository root and the task id (to locate the two plan artifacts)

Key Functions:
    - gate1_artifact_paths() -- the ordered (label, path) pairs for spec and plan.
    - code_acceptance_snapshot() -- Gate 3: HEAD sha, tracked-diff hash, untracked-files hash of a git worktree.
    - build_snapshot() -- read and hash artifacts; fails closed on missing, non-regular
      or symlinked files.
    - compute_revision_hash() -- content-bound hash; with no snapshot it reproduces the
      Increment A metadata-only formula unchanged.
    - snapshot_to_json() / snapshot_from_json() -- canonical JSON round trip.
    - snapshot_matches() / diff_snapshot() -- compare a stored snapshot with live content.

Constants:
    - CHALLENGE_VERSION -- format tag stored with the request ("control-plane-challenge/1").
"""

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple, Union

CHALLENGE_VERSION = "control-plane-challenge/1"

# Ordered artifact labels and their file-name templates under the task's work-tasks folder.
GATE1_ARTIFACTS: Tuple[Tuple[str, str], ...] = (
    ("spec", "{task_id}-spec.md"),
    ("plan", "{task_id}-implementation-plan.md"),
)


class SnapshotError(Exception):
    """A required artifact is missing, not a regular file, or is a symlink."""


@dataclass(frozen=True)
class SnapshotEntry:
    """One bound artifact: its label and the SHA-256 of its bytes."""

    label: str
    sha256: str


# External comment: canonical locations of the two Gate 1 artifacts.
def gate1_artifact_paths(repo_root: Union[str, Path], task_id: str) -> Tuple[Tuple[str, Path], ...]:
    """Return ((label, path), ...) for the spec and plan under docs/plans/work-tasks/<task-id>/."""
    folder = Path(repo_root) / "docs" / "plans" / "work-tasks" / task_id
    return tuple((label, folder / name.format(task_id=task_id)) for label, name in GATE1_ARTIFACTS)


def build_snapshot(paths: Sequence[Tuple[str, Union[str, Path]]]) -> Tuple[SnapshotEntry, ...]:
    """Hash each (label, path) in order. Raises SnapshotError instead of skipping a file."""
    entries: List[SnapshotEntry] = []
    for label, raw in paths:
        path = Path(raw)
        if path.is_symlink():
            raise SnapshotError(f"{label}: {path} is a symlink; refusing to bind it")
        if not path.is_file():
            raise SnapshotError(f"{label}: {path} is missing or not a regular file")
        entries.append(SnapshotEntry(label=label, sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    return tuple(entries)


def compute_revision_hash(
    task_id: str,
    from_state: str,
    to_state: str,
    occupancy_id: int,
    nonce: str,
    snapshot: Optional[Sequence[SnapshotEntry]] = None,
) -> str:
    """Return the request's revision_hash.

    Without a snapshot this is exactly the Increment A formula (transition metadata plus
    nonce), so existing callers are unaffected. With a snapshot the ordered content
    hashes are appended, binding the approval to the reviewed files."""
    material = f"{task_id}:{from_state}:{to_state}:{occupancy_id}:{nonce}"
    if snapshot:
        material += "||" + "|".join(f"{entry.label}={entry.sha256}" for entry in snapshot)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def snapshot_to_json(snapshot: Sequence[SnapshotEntry]) -> str:
    """Canonical compact JSON (ordered list of {label, sha256})."""
    return json.dumps(
        [{"label": entry.label, "sha256": entry.sha256} for entry in snapshot], separators=(",", ":")
    )


def snapshot_from_json(text: str) -> Tuple[SnapshotEntry, ...]:
    """Inverse of snapshot_to_json(). Malformed input raises SnapshotError."""
    try:
        return tuple(SnapshotEntry(label=item["label"], sha256=item["sha256"]) for item in json.loads(text))
    except (ValueError, KeyError, TypeError) as exc:
        raise SnapshotError(f"stored content snapshot is malformed: {exc}") from exc


def snapshot_matches(stored_json: str, live: Sequence[SnapshotEntry]) -> bool:
    """True only when the live entries equal the stored ones, same order and hashes."""
    return snapshot_from_json(stored_json) == tuple(live)


def diff_snapshot(stored_json: str, live: Sequence[SnapshotEntry]) -> List[str]:
    """Labels whose hash differs, or that were added or removed, versus the stored snapshot."""
    stored = {entry.label: entry.sha256 for entry in snapshot_from_json(stored_json)}
    current = {entry.label: entry.sha256 for entry in live}
    changed = [label for label in stored if current.get(label) != stored[label]]
    changed += [label for label in current if label not in stored]
    return changed


# ---------------------------------------------------------------- code acceptance (Gate 3)
_GIT_TIMEOUT_SECONDS = 60


def _git(worktree: Path, *args: str) -> bytes:
    """Run a read-only git command in the worktree; a failure is a SnapshotError, never a partial hash."""
    try:
        done = subprocess.run(
            ["git", "-C", str(worktree), "-c", "core.quotepath=off", *args],
            capture_output=True, timeout=_GIT_TIMEOUT_SECONDS, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SnapshotError(f"git could not be run in {worktree}: {exc}") from exc
    if done.returncode != 0:
        raise SnapshotError(f"git {' '.join(args)} failed in {worktree}: {done.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return done.stdout


def code_acceptance_snapshot(worktree: Union[str, Path]) -> Tuple[SnapshotEntry, ...]:
    """What a human accepts at Gate 3: the commit SHA, the SHA-256 of the tracked diff against HEAD, and the
    SHA-256 of the untracked (non-ignored) files' names and contents. A plain `git diff` omits new untracked
    files, so they are bound separately; symlinks are hashed by their target, never followed."""
    root = Path(worktree)
    if not root.is_dir():
        raise SnapshotError(f"the registered worktree {root} is not a directory")
    head = _git(root, "rev-parse", "HEAD").decode("utf-8").strip()
    diff = _git(root, "diff", "HEAD", "--binary", "--no-ext-diff", "--no-textconv")
    names = sorted(n for n in _git(root, "ls-files", "--others", "--exclude-standard", "-z").decode("utf-8", "surrogateescape").split("\0") if n)
    lines: List[str] = []
    for name in names:
        path = root / name
        if path.is_symlink():
            digest = "symlink:" + hashlib.sha256(os.readlink(path).encode("utf-8", "surrogateescape")).hexdigest()
        else:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{name}\0{digest}")
    return (
        SnapshotEntry("head", head),
        SnapshotEntry("tracked_diff", hashlib.sha256(diff).hexdigest()),
        SnapshotEntry("untracked", hashlib.sha256("\n".join(lines).encode("utf-8", "surrogateescape")).hexdigest()),
    )
