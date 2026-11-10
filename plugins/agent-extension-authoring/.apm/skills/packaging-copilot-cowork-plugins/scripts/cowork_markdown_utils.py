"""
Copilot Cowork Markdown utilities
=================================

Purpose:
    Shared, dependency-free Markdown helpers for the Cowork packaging scripts: walk
    lines while respecting code fences, build GitHub-style heading anchors, and parse
    the small YAML subset used in SKILL.md frontmatter (plain, quoted and folded scalars).

Key Input Dependencies:
    Python standard library only; cowork_package_constants.py in this skill.

Key Functions:
    normalize_newlines, iter_lines, first_heading, github_slug, heading_anchors,
    split_frontmatter, parse_frontmatter.

Output:
    Plain strings, sets and dictionaries consumed by cowork_content_checks.py and
    bundle_skill_companions.py. Nothing is written to disk.
"""

from __future__ import annotations

import re
from typing import Dict, Iterator, List, Optional, Set, Tuple

from cowork_package_constants import CODE_FENCE_PREFIX, FRONTMATTER_DELIMITER

HEADING_PATTERN = re.compile(r"^(#{1,6}) +(.+?)\s*$")
FOLDED_MARKERS = (">", ">-", ">+", "|", "|-", "|+")
SLUG_STRIP_PATTERN = re.compile(r"[^\w\- ]")


# Convert Windows and old-Mac line endings to LF so line-based parsing is uniform.
def normalize_newlines(text: str) -> str:
    """Return text with LF line endings only."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


# Yield each line with a flag that is True while inside a fenced code block.
def iter_lines(text: str) -> Iterator[Tuple[bool, str]]:
    """Yield (in_code_block, line) pairs; fence lines are reported as code."""
    in_fence = False
    for line in normalize_newlines(text).split("\n"):
        if line.lstrip().startswith(CODE_FENCE_PREFIX):
            yield True, line
            in_fence = not in_fence
        else:
            yield in_fence, line


# Return the text of the first level-one heading outside code fences.
def first_heading(text: str) -> Optional[str]:
    """Return the first H1 title, or None when the document has none."""
    for in_code, line in iter_lines(text):
        if not in_code and line.startswith("# "):
            return line[2:].strip()
    return None


# Build the anchor GitHub generates for a heading title.
def github_slug(title: str) -> str:
    """Return the GitHub-style anchor for a heading title."""
    cleaned = SLUG_STRIP_PATTERN.sub("", title.replace("`", "").lower())
    return cleaned.replace(" ", "-")


# Collect every heading anchor in a document, ignoring code fences.
def heading_anchors(text: str) -> Set[str]:
    """Return the set of heading anchors defined by a Markdown document."""
    anchors: Set[str] = set()
    for in_code, line in iter_lines(text):
        if in_code:
            continue
        match = HEADING_PATTERN.match(line)
        if match:
            anchors.add(github_slug(match.group(2)))
    return anchors


# Separate leading YAML frontmatter from the Markdown body.
def split_frontmatter(text: str) -> Tuple[Optional[str], str]:
    """Return (frontmatter_text, body); frontmatter_text is None when absent."""
    lines = normalize_newlines(text).split("\n")
    if not lines or lines[0].strip() != FRONTMATTER_DELIMITER:
        return None, "\n".join(lines)
    for index in range(1, len(lines)):
        if lines[index].strip() == FRONTMATTER_DELIMITER:
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1:])
    return None, "\n".join(lines)


# Remove surrounding single or double quotes from a scalar value.
def _unquote(value: str) -> str:
    """Strip one matching pair of surrounding quotes."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


# Read a block scalar's indented continuation lines, folding them with spaces.
def _read_block(lines: List[str], start: int) -> Tuple[str, int]:
    """Return (folded_text, next_index) for the indented block beginning at start."""
    parts: List[str] = []
    index = start
    while index < len(lines) and (not lines[index].strip() or lines[index].startswith((" ", "\t"))):
        if lines[index].strip():
            parts.append(lines[index].strip())
        index += 1
    return " ".join(parts), index


# Parse top-level `key: value` pairs, including quoted and folded scalars.
def parse_frontmatter(frontmatter: str) -> Dict[str, str]:
    """Parse the YAML subset used by SKILL.md frontmatter into a flat dictionary."""
    result: Dict[str, str] = {}
    lines = normalize_newlines(frontmatter).split("\n")
    index = 0
    while index < len(lines):
        line = lines[index]
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not match:
            index += 1
            continue
        key, value = match.group(1), match.group(2).strip()
        if value in FOLDED_MARKERS or not value:
            folded, index = _read_block(lines, index + 1)
            result[key] = folded
            continue
        result[key] = _unquote(value)
        index += 1
    return result
