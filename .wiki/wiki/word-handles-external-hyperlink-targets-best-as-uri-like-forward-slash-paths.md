---
concept: word-handles-external-hyperlink-targets-best-as-uri-like-forward-slash-paths
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/markdown-to-msword-converter/scripts/md_to_docx.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.252742+00:00
cluster: resolved
content_hash: 4d2522b579b9f86b
---

# Word handles external hyperlink targets best as URI-like forward-slash paths.

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

"""
md_to_docx.py (CLI)
=====================================

Purpose:
    Markdown -> Word (.docx) converter.
    Converts a single Markdown file into a Word document using `python-docx`.
    Includes best-effort support for headings, lists, tables, quotes, and hyperlinks.

Layer: Cli_Entry_Points

Usage Examples:
    python3 md_to_docx.py input.md --output output.docx

Supported Object Types:
    - Generic

CLI Arguments:
    input: Path to source Markdown file.
    --output, -o: Path to output DOCX file.

Input Files:
    - Markdown files (.md).

Output:
    - Word document (.docx).

Key Functions:
    strip_inline_markdown(): Remove common inline markdown formatting.
    strip_text_markdown_only(): Remove inline markdown formatting.
    resolve_word_link_target(): Resolve a Markdown link target to a Word-friendly external hyperlink target.
    normalize_link_label(): Normalize visible link text for Word output.
    add_hyperlink(): Add an external hyperlink run to a paragraph.
    add_markdown_runs(): Add markdown runs and hyperlinks to a paragraph.
    is_table_line(): Check if a line is a table line.
    parse_table(): Parse a table from lines starting at a given index.
    convert_markdown_to_docx(): Main conversion logic.

Script Dependencies:
    argparse, os, re, pathlib, urllib.parse, python-docx

Consumed by:
    - markdown-to-msword-converter skill
"""

import argparse
import os
import re
from pathlib import Path
from urllib.parse import quote, unquote
from typing import Any


LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def strip_inline_markdown(text: str) -> str:
    """Remove common inline markdown formatting, including links."""
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return text


def strip_text_markdown_only(text: str) -> str:
    """Remove inline markdown formatting but preserve link structure elsewhere."""
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    return text


def resolve_word_link_target(source_md: Path, target: str) -> str:
    """Resolve a Markdown link target to a Word-friendly external hyperlink target.

    - Absolute URLs are returned unchanged.
    - Fragment-only links are returned unchanged.
    - Relative paths are resolved against `source_md` parent.
    - Internal file links are converted to relative targets.
    - `.md` targets are rewritten to `.docx`.
    """
    cleaned = target.strip().strip("<>")
    if not cleaned:
        return target

    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", cleaned):
        return cleaned

    if cleaned.startswith("#"):
        return cleaned

    path_part, frag = (cleaned.split("#", 1) + [""])[:2]
    path_part = path_part.split("?", 1)[0]
    if not path_part:
        return cleaned

    resolved = (source_md.parent / unquote(path_part)).resolve()

    if resolved.exists() and resolved.is_dir():
        directory_candidates = [
            resolved / "index.docx",
            resolved / "README.docx",
            (resolved / "index.md").with_suffix(".docx"),
            (resolved / "README.md").with_suffix(".docx"),
        ]
        for candidate in directory_candidates:
            if candidate.exists() and candidate.is_file():
                resolved = candidate
                break

    if resolved.exists() and resolved.is_dir():
        markdown_candidates = [
            resolved / "Overview.md",
            resolved / "README.md",
            resolved / "index.md",
        ]

        top_level_markdowns = sorted(resolved.glob("*.md"))
        recursive_markdowns = sorted(resolved.rglob("*.md"))

        for candidate in markdown_candidates + top_level_markdowns + recursive_markdowns:
            if candidate.exists() and candidate.is_file():
                resolv

*(content truncated)*

## See Also

- [[1-handle-absolute-paths-from-repo-root]]
- [[1-test-ms-word-zip-archive-integrity]]
- [[as-a-library]]
- [[fix-patterns-like-or]]
- [[match-pythonexecution-paths-that-are-hardcoded-to-the-repo-root-plugins-folder]]
- [[paths]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/markdown-to-msword-converter/scripts/md_to_docx.py`
- **Indexed:** 2026-04-27T05:21:04.252742+00:00
