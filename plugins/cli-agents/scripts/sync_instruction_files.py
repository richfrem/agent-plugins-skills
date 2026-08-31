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

    A second, independent mode (--check-rules) reports content drift between
    `.agent/rules/<name>.md` and its matching `plugins/<plugin>/rules/<name>.md`
    source. Unlike the CLAUDE.md mirrors, drift direction here isn't reliably
    one-way (either side can be the one that's stale), so this mode is
    report-only — it never writes. A human applies the fix on whichever side
    is actually behind.

Layer: Investigate / Maintain

Usage Examples:
    python sync_instruction_files.py --dry-run
    python sync_instruction_files.py --execute
    python sync_instruction_files.py --check-rules

CLI Arguments:
    --dry-run: Print a diff summary per target file without writing (default).
    --execute: Write the synced content to each target file.
    --project-root: Override the project root (default: cwd).
    --check-rules: Report drift between .agent/rules/*.md and matching
        plugins/*/rules/*.md files. Report-only; ignores --execute.

Key Input Dependencies:
    - CLAUDE.md (source of truth, must exist at project root)
    - GEMINI.md, .github/copilot-instructions.md, AGENTS.md (targets, created if missing)
    - .agent/rules/*.md and plugins/*/rules/*.md (--check-rules mode only)

Output:
    - Updated GEMINI.md, .github/copilot-instructions.md, AGENTS.md (--execute only)
    - Console diff summary (line counts, detected preserved sections)
    - --check-rules: console report of IDENTICAL / DIFFERS / NO PLUGIN COUNTERPART per rule file

Key Functions:
    extract_anchor_index(): Finds the shared body's first line in a file.
    extract_preserved_header(): Lines between a target's own title and the anchor.
    extract_preserved_tail(): Lines from a named marker (e.g. "## Gemini CLI Tool
        Mapping") to end of file, if present.
    sync_target(): Builds the new target content from CLAUDE.md's body plus the
        target's preserved header/tail.
    find_rule_pairs(): Matches each .agent/rules/*.md to its plugins/*/rules/*.md
        counterpart by filename.
    check_rule_drift(): Diffs each matched pair and reports status.

Script Dependencies:
    os, sys, argparse, pathlib, difflib (standard library only)

Consumed by:
    - plugins/cli-agents/skills/agent-file-synchronization/scripts/sync_instruction_files.py (symlink)
Related:
    - plugins/agent-agentic-os/skills/optimize-agent-instructions/SKILL.md (content-quality audit, different scope)
"""

import argparse
import difflib
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
ANCHOR_LINE: str = ANCHOR_LINES[0]

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


def find_rule_pairs(root: Path) -> List[Tuple[str, Path, Optional[Path]]]:
    """Match each .agent/rules/*.md to its plugins/*/rules/*.md counterpart by filename.

    Returns a list of (name, agent_rules_path, plugin_rules_path_or_None).
    None means no plugin-side rules/ source was found for that filename.
    """
    agent_rules_dir = root / ".agent" / "rules"
    pairs: List[Tuple[str, Path, Optional[Path]]] = []
    if not agent_rules_dir.is_dir():
        return pairs
    for agent_path in sorted(agent_rules_dir.glob("*.md")):
        matches = sorted(root.glob(f"plugins/*/rules/{agent_path.name}"))
        pairs.append((agent_path.name, agent_path, matches[0] if matches else None))
    return pairs


def check_rule_drift(pairs: List[Tuple[str, Path, Optional[Path]]]) -> None:
    """Print an IDENTICAL / DIFFERS / NO PLUGIN COUNTERPART report for each rule pair."""
    for name, agent_path, plugin_path in pairs:
        if plugin_path is None:
            print(f"{name}: NO PLUGIN COUNTERPART FOUND under plugins/*/rules/")
            continue
        agent_text = agent_path.read_text(encoding="utf-8")
        plugin_text = plugin_path.read_text(encoding="utf-8")
        if agent_text == plugin_text:
            print(f"{name}: IDENTICAL")
            continue
        print(f"{name}: DIFFERS ({agent_path} vs {plugin_path})")
        diff = difflib.unified_diff(
            plugin_text.splitlines(keepends=True),
            agent_text.splitlines(keepends=True),
            fromfile=str(plugin_path),
            tofile=str(agent_path),
        )
        sys.stdout.writelines(diff)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync CLAUDE.md into GEMINI.md, copilot-instructions.md, AGENTS.md."
    )
    parser.add_argument("--execute", action="store_true", help="Write changes (default: dry-run)")
    parser.add_argument("--project-root", default=".", help="Project root (default: cwd)")
    parser.add_argument(
        "--check-rules",
        action="store_true",
        help="Report drift between .agent/rules/*.md and plugins/*/rules/*.md (report-only, ignores --execute)",
    )
    args = parser.parse_args()

    root = Path(args.project_root).resolve()

    if args.check_rules:
        check_rule_drift(find_rule_pairs(root))
        return

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
