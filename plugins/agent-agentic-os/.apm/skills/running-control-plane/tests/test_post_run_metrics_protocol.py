"""Verify the metrics Stop hook's stdout protocol with real subprocesses.

Purpose: Keep initialized-project summaries valid JSON and diagnostics on stderr.
Key Input Dependencies: canonical post_run_metrics.py; disposable pytest tmp_path.
Usage: python3 -m pytest <this-file> -v
Key Functions: run_hook; test_summary_is_hook_json; test_failed_write_keeps_json;
    test_uninitialized_project_is_silent.
"""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

HOOK = Path(__file__).resolve().parents[3] / "hooks/scripts/post_run_metrics.py"


# Execute the actual hook against an isolated project rather than mocking I/O.
def run_hook(project: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    """Run the canonical hook with synthetic Stop input and bounded execution."""
    return subprocess.run(
        [sys.executable, str(HOOK), *arguments],
        input=json.dumps({"hook_event_name": "Stop", "cwd": str(project)}),
        cwd=project,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(project)},
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


# Preserve ordinary and cycle-scoped summaries, including existing hook warnings.
@pytest.mark.parametrize("correlation_id", [None, "synthetic-cycle"])
def test_summary_is_hook_json(tmp_path: Path, correlation_id: str | None) -> None:
    """Emit one JSON message and retain the recorded metric event."""
    context = tmp_path / "context"
    (context / "memory").mkdir(parents=True)
    (context / "memory/hook-errors.log").write_text("synthetic error\n")
    arguments = ("--correlation-id", correlation_id) if correlation_id else ()
    result = run_hook(tmp_path, *arguments)
    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert set(output) == {"systemMessage"}
    assert "HOOK_FAILURES:1" in output["systemMessage"]
    scope = f"cycle:{correlation_id}" if correlation_id else "full session"
    assert scope in output["systemMessage"]
    events = [json.loads(line) for line in (context / "events.jsonl").read_text().splitlines()]
    assert len(events) == 1
    assert events[0]["action"] == "session_summary"
    assert events[0]["results"]["correlation_id"] == (correlation_id or "session")
    assert result.stderr == ""


# A directory at the log path reliably forces the error path on every platform.
def test_failed_write_keeps_json(tmp_path: Path) -> None:
    """A failed kernel and fallback write must not contaminate hook stdout."""
    context = tmp_path / "context"
    (context / "events.jsonl").mkdir(parents=True)
    (context / "kernel.py").write_text("raise SystemExit(1)\n")
    result = run_hook(tmp_path)
    assert result.returncode == 0
    assert "SESSION METRICS CAPTURED" in json.loads(result.stdout)["systemMessage"]
    assert "Failed to record metrics:" in result.stderr
    assert "Failed to record metrics:" not in result.stdout


# Preserve the existing no-op behavior outside initialized repositories.
def test_uninitialized_project_is_silent(tmp_path: Path) -> None:
    """Skip an unrelated project without creating state or emitting output."""
    result = run_hook(tmp_path)
    assert result.returncode == 0
    assert result.stdout == result.stderr == ""
    assert not (tmp_path / "context").exists()
