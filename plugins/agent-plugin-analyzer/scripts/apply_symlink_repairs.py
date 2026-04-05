#!/usr/bin/env python3
"""
apply_symlink_repairs.py
=====================================

Purpose:
    Applies a curated set of known broken symlink repairs to the plugin
    ecosystem. Each repair force-creates a file-level symlink at the
    destination path, replacing any pre-existing link or file.

Layer: Codify

Usage:
    python3 apply_symlink_repairs.py
"""
import os


# Atomically replace an existing path with a new symlink pointing to src
def force_symlink(src: str, dst: str) -> None:
    """
    Create a symlink at `dst` pointing to `src`, replacing any existing entry.

    Args:
        src: Symlink target (relative or absolute path).
        dst: Destination path where the symlink will be created.
    """
    if os.path.lexists(dst):
        os.remove(dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    os.symlink(src, dst)
    print(f"  Linked: {dst} -> {src}")


# Entry point: apply all known symlink repairs in sequence
def main() -> None:
    """
    Apply all curated symlink repairs and report each fix.

    Raises:
        SystemExit: Implicitly exits 0 on success.
    """
    print("Repairing symlinks...")
    force_symlink(
        '../SKILL.md',
        'plugins/agent-scaffolders/skills/create-command/references/examples/SKILL.md',
    )
    force_symlink(
        '../../../references/post-run-survey.md',
        'plugins/exploration-cycle-plugin/skills/deferred/exploration-orchestrator/references/post-run-survey.md',
    )
    force_symlink(
        '../../../references/acceptance-criteria.md',
        'plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/acceptance-criteria.md',
    )
    print("Done.")


if __name__ == "__main__":
    main()
