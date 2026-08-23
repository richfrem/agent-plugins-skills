"""
sync_instruction_files.py
==========================

Purpose:
    Replicates CLAUDE.md into GEMINI.md, .github/copilot-instructions.md, and
    AGENTS.md as full-copy mirrors (shared body identical, only the title line
    and each target's platform-specific header/tail differ). CLAUDE.md is the
    single source of truth; the other three are never hand-edited directly.

    Blindly overwriting a target with CLAUDE.md's raw content destroys any
    platform-specific section it carries (e.g. GEMINI.md's Gemini CLI Tool
    Mapping table, copilot-instructions.md's authoritative header). This
    script detects and re-preserves those sections across the sync instead
    of requiring a human to manually re-append them after every copy.

Layer: Investigate / Maintain

Usage Examples:
    python sync_instruction_files.py --dry-run
    python sync_instruction_files.py --execute

CLI Arguments:
    --dry-run: Print a diff summary per target file without writing (default).
    --execute: Write the synced content to each target file.
    --project-root: Override the project root (default: cwd).

Key Input Dependencies:
    - CLAUDE.md (source of truth, must exist at project root)
    - GEMINI.md, .github/copilot-instructions.md, AGENTS.md (targets, created if missing)

Output:
    - Updated GEMINI.md, .github/copilot-instructions.md, AGENTS.md (--execute only)
    - Console diff summary (line counts, detected preserved sections)

Key Functions:
    extract_anchor_index(): Finds the shared body's first line in a file.
    extract_preserved_header(): Lines between a target's own title and the anchor.
    extract_preserved_tail(): Lines from a named marker (e.g. "## Gemini CLI Tool
        Mapping") to end of file, if present.
    sync_target(): Builds the new target content from CLAUDE.md's body plus the
        target's preserved header/tail.

Script Dependencies:
    os, sys, argparse, pathlib (standard library only)

Consumed by:
    - plugins/cli-agents/skills/agent-file-synchronization/scripts/sync_instruction_files.py (symlink)
Related:
    - plugins/agent-agentic-os/skills/optimize-agent-instructions/SKILL.md (content-quality audit, different scope)
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple

ANCHOR_LINES: List[str] = [
    (
        "Behavioral guidelines to reduce common LLM coding mistakes. "
        "Merge with project-specific instructions as needed."
    ),
    "## Overview",
]

# Per-target template: (relative path, title_formatter, tail marker to preserve or None)
# title_formatter takes project_name: str and returns the title string.
TARGET_TEMPLATES: List[Tuple[str, str, Optional[str]]] = [
    ("GEMINI.md", "# GEMINI.md", "## Gemini CLI Tool Mapping"),
    (".github/copilot-instructions.md", "# Copilot Instructions for {project_name}", None),
    ("AGENTS.md", "# AGENTS.md", None),
]


def read_lines(path: Path) -> List[str]:
    """Read a file's lines (without trailing newlines), or [] if it doesn't exist."""
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def extract_anchor_index(lines: List[str]) -> Optional[int]:
    """Return the index of the shared body's first line from ANCHOR_LINES, or None if absent."""
    for anchor in ANCHOR_LINES:
        for i, line in enumerate(lines):
            if line.strip() == anchor:
                return i
    return None


def extract_preserved_header(target_lines: List[str]) -> List[str]:
    """Return lines between a target's own title and the anchor line (its platform header).

    Empty if the target doesn't exist yet, has no anchor, or has no extra header
    content beyond the standard blank line after the title.
    """
    if not target_lines:
        return []
    anchor = extract_anchor_index(target_lines)
    if anchor is None:
        return []
    # target_lines[0] is the title; target_lines[1] is normally a blank line.
    # Anything beyond that blank line, up to the anchor, is platform-specific.
    header = target_lines[1:anchor]
    # Trim a single leading/trailing blank line — those are structural, not content.
    while header and header[0] == "":
        header = header[1:]
    while header and header[-1] == "":
        header = header[:-1]
    return header


def extract_preserved_tail(target_lines: List[str], tail_marker: Optional[str]) -> List[str]:
    """Return lines from tail_marker (inclusive) to end of file, or [] if absent/no marker."""
    if not tail_marker or not target_lines:
        return []
    for i, line in enumerate(target_lines):
        if line.strip() == tail_marker:
            return target_lines[i:]
    return []


def sync_target(
    source_lines: List[str],
    target_path: Path,
    title: str,
    tail_marker: Optional[str],
) -> Tuple[str, dict]:
    """Build the new content for one target file from CLAUDE.md's body plus its preserved sections.

    Returns (new_content_text, summary_dict) where summary_dict reports what was preserved.
    """
    existing = read_lines(target_path)
    preserved_header = extract_preserved_header(existing)
    preserved_tail = extract_preserved_tail(existing, tail_marker)

    source_anchor = extract_anchor_index(source_lines)
    if source_anchor is None:
        raise ValueError(
            f"CLAUDE.md is missing any expected anchor line from: {ANCHOR_LINES!r}. "
            "Refusing to sync — the body-boundary detection would be unreliable."
        )
    body = source_lines[1:]  # drop CLAUDE.md's own title line

    parts: List[str] = [title, ""]
    if preserved_header:
        parts.extend(preserved_header)
        parts.append("")
    parts.extend(body)
    if preserved_tail:
        if parts[-1] != "":
            parts.append("")
        parts.extend(preserved_tail)

    new_content = "\n".join(parts) + "\n"
    summary = {
        "target": str(target_path),
        "existed_before": bool(existing),
        "preserved_header_lines": len(preserved_header),
        "preserved_tail_lines": len(preserved_tail),
        "new_line_count": len(parts),
        "old_line_count": len(existing),
    }
    return new_content, summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync CLAUDE.md into GEMINI.md, copilot-instructions.md, AGENTS.md."
    )
    parser.add_argument("--execute", action="store_true", help="Write changes (default: dry-run)")
    parser.add_argument("--project-root", default=".", help="Project root (default: cwd)")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    claude_md = root / "CLAUDE.md"
    if not claude_md.exists():
        print(f"ERROR: {claude_md} not found.", file=sys.stderr)
        sys.exit(1)

    source_lines = read_lines(claude_md)
    # Detect project name from first line if "# <name>" or fallback to directory name
    project_name = root.name
    if source_lines and source_lines[0].startswith("# "):
        first_title = source_lines[0][2:].strip()
        if first_title and not first_title.endswith(".md"):
            project_name = first_title

    for rel_path, title_tmpl, tail_marker in TARGET_TEMPLATES:
        target_path = root / rel_path
        title = title_tmpl.format(project_name=project_name)
        content, summary = sync_target(source_lines, target_path, title, tail_marker)
        print(
            f"{summary['target']}: {summary['old_line_count']} -> {summary['new_line_count']} lines "
            f"(preserved header: {summary['preserved_header_lines']} lines, "
            f"preserved tail: {summary['preserved_tail_lines']} lines, "
            f"existed before: {summary['existed_before']})"
        )
        if args.execute:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content, encoding="utf-8")
            print(f"  -> written")
        else:
            print(f"  -> dry-run, not written (pass --execute to write)")


if __name__ == "__main__":
    main()
