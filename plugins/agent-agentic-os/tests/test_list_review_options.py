"""
tests/test_list_review_options.py
=================================

Purpose:
    Failing-first tests for H1 (auth-ciba-increment-b, #639): the read-only `list-review-options` verb prints
    the exact runtime and model identifiers the review-selection questions expect, so the human copies them
    instead of remembering or mistyping them (a hand-typed "gemini flash 3.8" was recorded once). It probes each
    installed CLI through the CLI's own `models` command (no runtime dependency on the cli-agents catalog),
    lists effort levels, mentions the capability profile when present, and never writes anything.
    A real (fake-content) `agy` executable on a temporary PATH exercises the real subprocess path.

Key Input Dependencies:
    - control_plane/review_options.py (collect_review_options, format_review_options)
    - agent_control.py (_build_parser: list-review-options)

Key Functions (test cases):
    - test_lists_ids_from_the_cli_models_command
    - test_a_missing_runtime_is_reported_not_invented
    - test_a_failing_probe_is_reported
    - test_output_writes_nothing
    - test_cli_registers_the_verb
"""

import os
import stat
import sys
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

import agent_control
from control_plane.review_options import collect_review_options, format_review_options


def _fake_agy(directory: Path, body: str) -> None:
    exe = directory / "agy"
    exe.write_text("#!/bin/sh\n" + body + "\n")
    exe.chmod(exe.stat().st_mode | stat.S_IXUSR)


def test_lists_ids_from_the_cli_models_command(tmp_path):
    _fake_agy(tmp_path, 'if [ "$1" = "models" ]; then printf "Fetching available models...\\ngemini-3.8-flash-medium\\tGemini 3.8 Flash (Medium)\\ngemini-3.1-pro-high\\tGemini 3.1 Pro (High)\\n"; fi')
    text = format_review_options(collect_review_options(path=str(tmp_path)))
    assert "agy" in text and "gemini-3.8-flash-medium" in text and "gemini-3.1-pro-high" in text
    assert "Fetching available models" not in text
    assert "low" in text and "medium" in text and "high" in text  # effort levels
    assert "copy" in text.lower()


def test_a_missing_runtime_is_reported_not_invented(tmp_path):
    text = format_review_options(collect_review_options(path=str(tmp_path)))
    assert "not found on PATH" in text and "gemini-3.8" not in text


def test_a_failing_probe_is_reported(tmp_path):
    _fake_agy(tmp_path, "exit 3")
    text = format_review_options(collect_review_options(path=str(tmp_path)))
    assert "agy" in text and "probe failed" in text.lower()


def test_output_writes_nothing(tmp_path, monkeypatch):
    work = tmp_path / "work"
    work.mkdir()
    bindir = tmp_path / "bin"
    bindir.mkdir()
    _fake_agy(bindir, 'printf "gemini-3.8-flash-medium\\tx\\n"')
    monkeypatch.chdir(work)
    format_review_options(collect_review_options(path=str(bindir)))
    assert list(work.iterdir()) == []


def test_cli_registers_the_verb():
    args = agent_control._build_parser().parse_args(["list-review-options"])
    assert args.subcommand == "list-review-options"
