"""S5 tests (B5): plan-outline marker merge preserves hand-written content and fails closed on malformed markers."""

from __future__ import annotations

import pytest

from agent_control import (
    OUTLINE_MARKER_END,
    OUTLINE_MARKER_START,
    OutlineMarkerError,
    merge_outline_block,
)


def test_merge_appends_when_no_markers_present():
    existing = "# My hand-written notes\n\nKeep this exact paragraph.\n"
    out = merge_outline_block(existing, "- bullet 1\n- bullet 2")
    assert "# My hand-written notes" in out
    assert "Keep this exact paragraph." in out
    assert OUTLINE_MARKER_START in out and OUTLINE_MARKER_END in out
    assert "- bullet 1" in out


def test_merge_replaces_only_between_single_marker_pair():
    existing = (
        "# Top Notes\n\n"
        f"{OUTLINE_MARKER_START}\nold bullet\n{OUTLINE_MARKER_END}\n\n"
        "# Bottom Notes\n"
    )
    out = merge_outline_block(existing, "new bullet")
    assert "# Top Notes" in out
    assert "# Bottom Notes" in out
    assert "new bullet" in out
    assert "old bullet" not in out


def test_merge_refuses_duplicate_single_or_fenced_markers():
    # Single unmatched marker
    with pytest.raises(OutlineMarkerError):
        merge_outline_block(f"notes\n{OUTLINE_MARKER_START}\nonly start\n", "x")

    # Duplicate start markers
    dup = f"{OUTLINE_MARKER_START}\na\n{OUTLINE_MARKER_START}\nb\n{OUTLINE_MARKER_END}\n"
    with pytest.raises(OutlineMarkerError):
        merge_outline_block(dup, "x")

    # End before start
    rev = f"{OUTLINE_MARKER_END}\na\n{OUTLINE_MARKER_START}\n"
    with pytest.raises(OutlineMarkerError):
        merge_outline_block(rev, "x")

    # Marker inside fenced code block
    fenced = f"# Notes\n```markdown\n{OUTLINE_MARKER_START}\n{OUTLINE_MARKER_END}\n```\n"
    with pytest.raises(OutlineMarkerError):
        merge_outline_block(fenced, "x")
