#!/usr/bin/env python
"""
optimize-context (CLI)
=====================================

Purpose:
    Scans a project directory for duplicate Claude agent skill definitions
    loaded from more than one source. Plugin-installed skills (under
    .agents/skills/<name>/ where the plugin installed them) are the
    canonical source of truth. Any duplicate found in a secondary location
    (e.g. .agents/skills/ installed via npx without a matching plugin) is
    added to `.claudeignore` so it is loaded exactly once.

Layer: Codify

Usage Examples:
    pythonscripts/optimize_context.py
    pythonscripts/optimize_context.py --project-root /path/to/my-project
    pythonscripts/optimize_context.py --dry-run
    pythonscripts/optimize_context.py --verbose

CLI Arguments:
    --project-root PATH   Root of the project to scan (default: CWD)
    --dry-run             Report duplicates without modifying .claudeignore
    --verbose             Print every skill found, not just conflicts
    --ignore-file PATH    Path to .claudeignore (default: <project-root>/.claudeignore)

Input Files:
    - .agents/skills/*/SKILL.md  (npx-installed / fallback skills)
    - plugins/*/skills/*/SKILL.md (plugin-canonical skills)
    - .claudeignore (read + patched)

Output:
    - Updated .claudeignore with duplicate suppression lines
    - Exit code 0: clean (no duplicates or all suppressed)
    - Exit code 1: argument or filesystem error
    - Exit code 2: duplicates found (only when --dry-run is active)

Key Functions:
    - collect_skills()     Discover skill slugs from each source directory
    - find_duplicates()    Cross-reference the two slug sets
    - read_claudeignore()  Parse existing .claudeignore entries
    - patch_claudeignore() Append suppression lines for each duplicate found

Script Dependencies:
    - argparse
    - os
    - pathlib
    - sys

Consumed by:
    - optimize-context SKILL.md (claude-cli plugin)
    - Antigravity AI Agent
"""

import argparse
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SKILL_MARKER = "SKILL.md"
_CLAUDEIGNORE_HEADER = (
    "# optimize-context: auto-suppressed duplicate skills\n"
    "# (plugin-installed version is canonical; npx copy suppressed)\n"
)
_SECTION_SENTINEL = "# --- optimize-context managed block ---"


# ---------------------------------------------------------------------------
# Skill discovery
# ---------------------------------------------------------------------------

def collect_skills(base_dir: Path, depth: int = 1) -> dict[str, Path]:
    """
    Walk *base_dir* looking for SKILL.md files at exactly *depth* levels deep.

    Returns a mapping of skill-slug -> SKILL.md parent directory.

    Args:
        base_dir: Directory to scan.
        depth:    How many directory levels below base_dir to look.
                  depth=1 means base_dir/<slug>/SKILL.md
                  depth=2 means base_dir/<plugin>/<slug>/SKILL.md (unused currently)

    Returns:
        dict[str, Path]: slug → skill_directory mapping.
    """
    skills: dict[str, Path] = {}
    if not base_dir.exists():
        return skills

    for entry in base_dir.iterdir():
        if not entry.is_dir():
            continue
        candidate = entry / _SKILL_MARKER
        if candidate.exists():
            slug = entry.name
            skills[slug] = entry
    return skills


def collect_plugin_skills(plugins_dir: Path) -> dict[str, Path]:
    """
    Walk plugins/<plugin>/skills/<skill>/SKILL.md and return slug → path.

    Args:
        plugins_dir: Top-level plugins/ directory.

    Returns:
        dict[str, Path]: skill-slug → skill_directory mapping.
    """
    skills: dict[str, Path] = {}
    if not plugins_dir.exists():
        return skills

    for plugin_entry in plugins_dir.iterdir():
        if not plugin_entry.is_dir():
            continue
        skills_subdir = plugin_entry / "skills"
        skills.update(collect_skills(skills_subdir, depth=1))
    return skills


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

def find_duplicates(
    plugin_skills: dict[str, Path],
    local_skills: dict[str, Path],
) -> list[tuple[str, Path, Path]]:
    """
    Identify skill slugs present in both sources.

    Args:
        plugin_skills: Skills discovered under plugins/.
        local_skills:  Skills discovered under .agents/skills/.

    Returns:
        List of (slug, plugin_path, local_path) tuples for every conflict.
    """
    duplicates = []
    for slug, local_path in local_skills.items():
        if slug in plugin_skills:
            duplicates.append((slug, plugin_skills[slug], local_path))
    return duplicates


def partition_duplicates(
    duplicates: list[tuple[str, Path, Path]],
    ignore_lines: list[str],
    project_root: Path,
) -> tuple[list[tuple[str, Path, Path]], list[tuple[str, Path, Path]]]:
    """
    Split duplicates into unsuppressed (need action) and already-suppressed.

    Args:
        duplicates:    All detected (slug, plugin_path, local_path) tuples.
        ignore_lines:  Current .claudeignore raw lines.
        project_root:  Used to compute relative patterns.

    Returns:
        (unsuppressed, already_suppressed) tuple of duplicate lists.
    """
    unsuppressed = []
    suppressed = []
    for entry in duplicates:
        _, _, local_path = entry
        try:
            rel = local_path.relative_to(project_root)
        except ValueError:
            rel = local_path
        pattern = str(rel) + "/"
        if _already_ignored(ignore_lines, pattern):
            suppressed.append(entry)
        else:
            unsuppressed.append(entry)
    return unsuppressed, suppressed


# ---------------------------------------------------------------------------
# .claudeignore management
# ---------------------------------------------------------------------------

def read_claudeignore(ignore_file: Path) -> list[str]:
    """
    Read .claudeignore, return lines (including newlines).

    Args:
        ignore_file: Path to .claudeignore.

    Returns:
        List of raw string lines (may be empty if file does not exist).
    """
    if not ignore_file.exists():
        return []
    return ignore_file.read_text(encoding="utf-8").splitlines(keepends=True)


def _already_ignored(lines: list[str], pattern: str) -> bool:
    """Return True if *pattern* is already present as a non-comment line."""
    clean = pattern.strip()
    return any(line.strip() == clean for line in lines if not line.startswith("#"))


def patch_claudeignore(
    ignore_file: Path,
    duplicate_local_paths: list[Path],
    project_root: Path,
    dry_run: bool = False,
) -> list[str]:
    """
    Append suppression lines for each duplicate path to .claudeignore.

    Lines are written relative to *project_root*. Already-suppressed paths
    are skipped (idempotent). A managed-block header is inserted once.

    Args:
        ignore_file:           Path to .claudeignore.
        duplicate_local_paths: .agents/skills/<slug> paths to suppress.
        project_root:          Used to compute relative ignore patterns.
        dry_run:               If True, return proposed lines without writing.

    Returns:
        List of new lines that were (or would be) appended.
    """
    existing_lines = read_claudeignore(ignore_file)
    new_lines: list[str] = []

    # Ensure the managed block header is present
    if _SECTION_SENTINEL not in "".join(existing_lines):
        new_lines.append(f"\n{_SECTION_SENTINEL}\n")
        new_lines.append(_CLAUDEIGNORE_HEADER)

    for skill_dir in duplicate_local_paths:
        try:
            rel = skill_dir.relative_to(project_root)
        except ValueError:
            rel = skill_dir  # absolute fallback
        pattern = str(rel) + "/"
        if _already_ignored(existing_lines, pattern):
            continue
        new_lines.append(f"{pattern}\n")

    if not dry_run and new_lines:
        with ignore_file.open("a", encoding="utf-8") as fh:
            fh.writelines(new_lines)

    return new_lines


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------

def _print_header(label: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")


def _print_duplicate(slug: str, plugin_path: Path, local_path: Path) -> None:
    print(f"  ⚠  DUPLICATE: {slug!r}")
    print(f"       canonical : {plugin_path}")
    print(f"       suppressed: {local_path}")


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    """Parse CLI arguments and run the optimize-context pipeline."""
    parser = argparse.ArgumentParser(
        prog="optimize-context",
        description=(
            "Detect and suppress duplicate Claude skill definitions. "
            "Plugin-installed skills are canonical; .agents/skills copies are suppressed."
        ),
    )
    parser.add_argument(
        "--project-root",
        default=os.getcwd(),
        metavar="PATH",
        help="Root directory of the project to scan (default: CWD).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report duplicates without modifying .claudeignore.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print every skill found, not just conflicts.",
    )
    parser.add_argument(
        "--ignore-file",
        default=None,
        metavar="PATH",
        help="Path to .claudeignore (default: <project-root>/.claudeignore).",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    plugins_dir = project_root / "plugins"
    local_skills_dir = project_root / ".agents" / "skills"
    ignore_file = Path(args.ignore_file) if args.ignore_file else project_root / ".claudeignore"

    # --- Discovery ---
    _print_header("optimize-context: skill scan")
    print(f"  project root : {project_root}")
    print(f"  plugins dir  : {plugins_dir} {'(found)' if plugins_dir.exists() else '(not found)'}")
    print(f"  local skills : {local_skills_dir} {'(found)' if local_skills_dir.exists() else '(not found)'}")

    plugin_skills = collect_plugin_skills(plugins_dir)
    local_skills = collect_skills(local_skills_dir)

    if args.verbose:
        _print_header("All plugin-canonical skills")
        for slug in sorted(plugin_skills):
            print(f"  ✓ {slug}")
        _print_header("All .agents/skills (local) skills")
        for slug in sorted(local_skills):
            print(f"  ✓ {slug}")

    # --- Duplicate detection ---
    all_duplicates = find_duplicates(plugin_skills, local_skills)

    _print_header("Duplicate analysis")
    if not all_duplicates:
        print("  ✅ No duplicates found. Context is clean.")
        sys.exit(0)

    existing_ignore_lines = read_claudeignore(ignore_file)
    unsuppressed, already_suppressed = partition_duplicates(
        all_duplicates, existing_ignore_lines, project_root
    )

    if already_suppressed:
        print(f"  ℹ  {len(already_suppressed)} duplicate(s) already suppressed in .claudeignore (skipped):")
        for slug, _, local_path in already_suppressed:
            print(f"       {slug!r} → {local_path}")

    if unsuppressed:
        print(f"  ⚠  {len(unsuppressed)} unsuppressed duplicate(s) found:")
        for slug, plugin_path, local_path in unsuppressed:
            _print_duplicate(slug, plugin_path, local_path)
    else:
        print("  ✅ All duplicates are already suppressed in .claudeignore. Context is clean.")
        sys.exit(0)

    # --- Patch .claudeignore (only unsuppressed entries need action) ---
    duplicate_local_paths = [local_path for _, _, local_path in unsuppressed]
    added_lines = patch_claudeignore(
        ignore_file=ignore_file,
        duplicate_local_paths=duplicate_local_paths,
        project_root=project_root,
        dry_run=args.dry_run,
    )

    _print_header("Result")
    if args.dry_run:
        print("  🔬 DRY RUN — no files modified.")
        if added_lines:
            print("  Lines that WOULD be added to .claudeignore:")
            for line in added_lines:
                print(f"    {line}", end="")
        sys.exit(2)
    else:
        if added_lines:
            print(f"  ✅ Patched {ignore_file} with {len(duplicate_local_paths)} suppression rule(s).")
        else:
            print("  ℹ  All duplicates were already suppressed in .claudeignore.")
        sys.exit(0)


if __name__ == "__main__":
    main()
