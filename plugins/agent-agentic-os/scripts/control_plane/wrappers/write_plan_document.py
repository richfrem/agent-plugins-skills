#!/usr/bin/env python3
"""
control_plane/wrappers/write_plan_document.py
=============================================

Purpose:
    Fixed-identity wrapper for writing plan specification documents.
    Hardcodes action identity 'plan_write'. Never allows caller-supplied action identity.
    Enforces:
    - Authorized plan destination paths only.
    - Capability and occupancy verification before writing.
    - Shadow file creation using O_CREAT | O_EXCL | O_NOFOLLOW.
    - Occupancy re-verification immediately before os.replace.
    - Shadow file cleanup on every denial or error.
    - No modification of destination file unless all checks pass.
"""

import os
import sys
import tempfile
from pathlib import Path

# Ensure scripts directory is on sys.path for direct script execution
_scripts_dir = str(Path(__file__).resolve().parent.parent.parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from typing import Any, Dict, Optional, Union
from agent_control import ControlPlane, PhaseCapabilityDenied


ACTION_IDENTITY = "plan_write"


def _validate_destination_path(destination_path: Union[str, Path], task_id: str, control_plane: ControlPlane) -> Path:
    """Ensures destination path is an authorized plan document location bound to task_id.

    Fails closed on:
    - '..' traversal in path string.
    - Absolute paths outside the repository (or outside temporary test roots).
    - Symlinked parent directories.
    - Another task's plan (filenames containing other task IDs or not matching task_id).
    - Unregistered plan filenames not associated with task_id.
    """
    raw_str = str(destination_path)
    if ".." in Path(raw_str).parts:
        raise ValueError(f"Path traversal ('..') is strictly prohibited: {raw_str}")

    dest = Path(destination_path)
    resolved_dest = dest.resolve()

    # Determine allowable root directory
    repo_root = getattr(control_plane, "repo_root", None)
    if repo_root is None:
        # Fallback to repo root discovered from db_path or module path
        db_path = getattr(control_plane, "db_path", None)
        if db_path and db_path.parent.name == "context":
            repo_root = db_path.parent.parent.resolve()
        else:
            repo_root = Path(__file__).resolve().parent.parent.parent.parent.resolve()

    # If test tmp_path or repo_root, ensure resolved path is inside repo or allowed temporary directory
    is_inside_repo = False
    try:
        resolved_dest.relative_to(repo_root)
        is_inside_repo = True
    except ValueError:
        # Check if inside a temporary test directory
        temp_dir = Path(tempfile.gettempdir()).resolve()
        try:
            resolved_dest.relative_to(temp_dir)
            is_inside_repo = True
        except ValueError:
            pass

    if not is_inside_repo:
        raise ValueError(f"Destination path {resolved_dest} is outside the repository root {repo_root}.")

    # Check for symlinked parent directories
    # Walk up existing parents and ensure none is a symlink
    parent_check = dest.parent
    while parent_check and parent_check != parent_check.parent:
        if parent_check.is_symlink():
            raise ValueError(f"Symlinked parent directory detected: {parent_check}")
        if not parent_check.exists():
            parent_check = parent_check.parent
            continue
        if parent_check.is_symlink():
            raise ValueError(f"Symlinked parent directory detected: {parent_check}")
        parent_check = parent_check.parent

    # Retrieve registered task information
    task = control_plane.get_task(task_id)
    if not task:
        raise ValueError(f"Task '{task_id}' not found.")

    registered_spec = task.get("spec_path")
    # Allowed plan artifact filenames/patterns for this task:
    # 1. Exact registered spec_path
    # 2. Approved implementation plan path: <task-id>-implementation-plan.md or <task-id>-plan.md
    # 3. Explicit prefix/suffix matching task_id: e.g. docs/plans/<task-id>-*.md
    dest_name = resolved_dest.name
    if not dest_name.endswith(".md"):
        raise ValueError(f"Plan document must have .md extension: {dest_name}")

    # Check that destination filename is bound to this task_id
    if task_id not in dest_name:
        raise ValueError(f"Plan destination '{dest_name}' does not match authorized task '{task_id}'.")

    # If the filename contains another recognizable task ID pattern (e.g. task-other, issue-xxx where xxx != task_id), reject
    # In particular, task_id must be the primary identifier in the filename
    allowed_registered_paths = []
    if registered_spec:
        allowed_registered_paths.append(Path(registered_spec).name)

    valid_names = {
        f"{task_id}-spec.md",
        f"{task_id}-plan.md",
        f"{task_id}-implementation-plan.md",
        f"{task_id}.md",
    }
    if registered_spec:
        valid_names.add(Path(registered_spec).name)

    if dest_name not in valid_names:
        raise ValueError(f"Unregistered plan filename '{dest_name}' for task '{task_id}'.")

    return resolved_dest


def write_plan_document(
    task_id: str,
    destination_path: Union[str, Path],
    content: str,
    control_plane: Optional[ControlPlane] = None,
) -> Dict[str, Any]:
    """Writes a plan document using atomic shadow replacement with zero side effects on denial.

    Sequence:
    1. Validate destination path is authorized.
    2. Authoritative capability & occupancy gate (pre-write check).
    3. Create shadow file using O_CREAT | O_EXCL | O_NOFOLLOW.
    4. Write content to shadow file and sync to disk.
    5. Re-verify capability & occupancy immediately before atomic rename.
    6. Atomic rename: os.replace(shadow_path, destination_path).
    7. Clean up shadow file on ANY denial, exception, or abort.
    """
    cp = control_plane or ControlPlane()
    dest = _validate_destination_path(destination_path, task_id, cp)

    # 1. Capability check before touching filesystem
    # Uses fixed internal ACTION_IDENTITY. Caller cannot supply action identity.
    cap_initial = cp.verify_phase_capability(task_id, ACTION_IDENTITY)

    dest.parent.mkdir(parents=True, exist_ok=True)
    shadow_fd = None
    shadow_path = None

    try:
        # 2. Shadow file creation using O_CREAT | O_EXCL | O_NOFOLLOW
        flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW

        # Generate a unique shadow filename in the same directory for atomic replace
        prefix = f".{dest.name}.tmp_"
        for attempt in range(100):
            cand_name = f"{prefix}{os.urandom(8).hex()}"
            cand_path = dest.parent / cand_name
            try:
                shadow_fd = os.open(str(cand_path), flags, 0o600)
                shadow_path = cand_path
                break
            except FileExistsError:
                continue

        if shadow_path is None or shadow_fd is None:
            raise IOError("Failed to create unique shadow file for atomic write.")

        # 3. Write content into shadow file
        encoded = content.encode("utf-8")
        os.write(shadow_fd, encoded)
        os.fsync(shadow_fd)
        os.close(shadow_fd)
        shadow_fd = None

        # 4. Re-verify occupancy and capability immediately before atomic replacement
        cap_final = cp.verify_phase_capability(task_id, ACTION_IDENTITY)
        if cap_final.transition_id != cap_initial.transition_id or cap_final.current_state != cap_initial.current_state:
            raise PhaseCapabilityDenied(
                f"Occupancy changed during write window: initially {cap_initial.transition_id}, now {cap_final.transition_id}."
            )

        # 5. Atomic replacement
        os.replace(str(shadow_path), str(dest))
        shadow_path = None  # Replaced cleanly, no cleanup needed

        return {
            "status": "WRITTEN",
            "destination": str(dest),
            "bytes_written": len(encoded),
            "task_id": task_id,
            "transition_id": cap_final.transition_id,
            "action_identity": ACTION_IDENTITY,
        }

    finally:
        if shadow_fd is not None:
            try:
                os.close(shadow_fd)
            except OSError:
                pass
        if shadow_path is not None and shadow_path.exists():
            try:
                shadow_path.unlink()
            except OSError:
                pass


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Fixed-identity atomic plan document writer")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--content", required=True)

    args = parser.parse_args()
    try:
        res = write_plan_document(
            task_id=args.task_id,
            destination_path=args.path,
            content=args.content,
        )
        print(json.dumps(res, indent=2))
    except PhaseCapabilityDenied as e:
        print(f"CAPABILITY DENIED: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
