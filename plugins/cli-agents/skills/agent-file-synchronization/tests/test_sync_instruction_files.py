"""Unit tests for sync_instruction_files.py.

Copyright (c) 2026. All rights reserved.
"""

from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from sync_instruction_files import (
    ANCHOR_LINE,
    extract_anchor_index,
    extract_preserved_header,
    extract_preserved_tail,
    sync_target,
)

SOURCE = [
    "# CLAUDE.md",
    "",
    ANCHOR_LINE,
    "",
    "## Section",
    "content",
]


def test_extract_anchor_index_found():
    assert extract_anchor_index(SOURCE) == 2


def test_extract_anchor_index_missing():
    assert extract_anchor_index(["# X", "no anchor here"]) is None


def test_extract_preserved_header_empty_target():
    assert extract_preserved_header([]) == []


def test_extract_preserved_header_no_extra_content():
    target = ["# GEMINI.md", "", ANCHOR_LINE, "", "body"]
    assert extract_preserved_header(target) == []


def test_extract_preserved_header_with_platform_content():
    target = [
        "# Copilot Instructions for repo",
        "",
        "> Authoritative rules.",
        "> Mirrors CLAUDE.md.",
        "",
        ANCHOR_LINE,
        "",
        "body",
    ]
    header = extract_preserved_header(target)
    assert header == ["> Authoritative rules.", "> Mirrors CLAUDE.md."]


def test_extract_preserved_tail_present():
    target = ["# GEMINI.md", "", "body", "", "## Gemini CLI Tool Mapping", "| a | b |"]
    tail = extract_preserved_tail(target, "## Gemini CLI Tool Mapping")
    assert tail == ["## Gemini CLI Tool Mapping", "| a | b |"]


def test_extract_preserved_tail_absent():
    target = ["# GEMINI.md", "", "body"]
    assert extract_preserved_tail(target, "## Gemini CLI Tool Mapping") == []


def test_extract_preserved_tail_no_marker():
    target = ["# AGENTS.md", "", "body"]
    assert extract_preserved_tail(target, None) == []


def test_sync_target_preserves_gemini_tail(tmp_path):
    target_path = tmp_path / "GEMINI.md"
    target_path.write_text(
        "# GEMINI.md\n\n" + ANCHOR_LINE + "\n\nold body\n\n## Gemini CLI Tool Mapping\n| a | b |\n",
        encoding="utf-8",
    )
    content, summary = sync_target(SOURCE, target_path, "# GEMINI.md", "## Gemini CLI Tool Mapping")
    assert "## Gemini CLI Tool Mapping" in content
    assert "| a | b |" in content
    assert ANCHOR_LINE in content
    assert summary["preserved_tail_lines"] == 2


def test_sync_target_preserves_copilot_header(tmp_path):
    target_path = tmp_path / "copilot-instructions.md"
    target_path.write_text(
        "# Copilot Instructions for repo\n\n> Authoritative rules.\n> Mirrors CLAUDE.md.\n\n"
        + ANCHOR_LINE + "\n\nold body\n",
        encoding="utf-8",
    )
    content, summary = sync_target(
        SOURCE, target_path, "# Copilot Instructions for repo", None
    )
    assert "> Authoritative rules." in content
    assert "> Mirrors CLAUDE.md." in content
    assert summary["preserved_header_lines"] == 2


def test_sync_target_no_existing_file(tmp_path):
    target_path = tmp_path / "AGENTS.md"
    content, summary = sync_target(SOURCE, target_path, "# AGENTS.md", None)
    assert content.startswith("# AGENTS.md\n")
    assert ANCHOR_LINE in content
    assert summary["existed_before"] is False


def test_sync_target_idempotent(tmp_path):
    target_path = tmp_path / "AGENTS.md"
    content1, _ = sync_target(SOURCE, target_path, "# AGENTS.md", None)
    target_path.write_text(content1, encoding="utf-8")
    content2, summary2 = sync_target(SOURCE, target_path, "# AGENTS.md", None)
    assert content1 == content2
    assert summary2["preserved_header_lines"] == 0
