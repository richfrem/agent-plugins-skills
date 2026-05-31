# plugins/agent-agentic-os/tests/test_update_memory_security.py
import sys, json, subprocess
from pathlib import Path
import pytest

HOOK = Path(__file__).parent.parent / "hooks" / "update_memory.py"


def _make_env(tmp_path):
    ctx = tmp_path / "context"
    ctx.mkdir()
    (ctx / "os-state.json").write_text(json.dumps({"active_agent": "test"}))
    return {"CLAUDE_PROJECT_DIR": str(tmp_path)}


def _payload(event="SessionStart"):
    return json.dumps({"event": event})


def test_no_direct_os_state_write(tmp_path):
    """Hook must NOT write to os-state.json directly (C-1)."""
    env = _make_env(tmp_path)
    before = (tmp_path / "context" / "os-state.json").read_text()
    subprocess.run(
        [sys.executable, str(HOOK), _payload("SessionStart")],
        env={**{"PATH": "/usr/bin:/bin"}, **env},
        timeout=10,
    )
    after = (tmp_path / "context" / "os-state.json").read_text()
    assert before == after, "Hook must not write os-state.json directly (C-1)"


def test_no_fallback_events_write_when_kernel_absent(tmp_path):
    """When kernel.py is absent the hook must NOT write events.jsonl (C-3)."""
    env = _make_env(tmp_path)
    events_file = tmp_path / "context" / "events.jsonl"
    subprocess.run(
        [sys.executable, str(HOOK), _payload("SessionStart")],
        env={**{"PATH": "/usr/bin:/bin"}, **env},
        timeout=10,
    )
    assert not events_file.exists(), "Hook must fail closed without kernel.py (C-3)"
