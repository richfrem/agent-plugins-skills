"""
Purpose:
    Unit tests verifying dispatch.py's authorization gate fires before any
    subprocess call, plus agent alias index resolution and handoff envelope
    truncation limits.

Key Input Dependencies:
    - dispatch.py (in ../scripts/, invoked both as subprocess and imported directly)
    - pytest tmp_path fixture
"""
import json, subprocess, sys, unittest.mock
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

DISPATCH = Path(__file__).parent.parent / "scripts" / "dispatch.py"
MINIMAL_ARGS = [
    "--agent", "agents/intake-agent.md",
    "--instruction", "run",
    "--output", "/tmp/test_out.md",
]

def _base_cmd(extra: list) -> list:
    """Build a dispatch.py subprocess command line with MINIMAL_ARGS plus extra flags."""
    return [sys.executable, str(DISPATCH)] + MINIMAL_ARGS + extra

def test_dispatch_blocks_without_approval(tmp_path):
    """Gate must fire before CLI subprocess — even with otherwise valid args."""
    # Provide valid-looking but nonexistent db and key so the gate fires, not arg parsing
    db = tmp_path / "test.sqlite"
    db.touch()
    key = tmp_path / "test.key"
    key.write_bytes(b"\x00" * 32)
    envelope = json.dumps({"payload": "x", "hmac": "bad", "nonce": "n1"})
    result = subprocess.run(
        _base_cmd([
            "--db-path", str(db),
            "--approval-id", "nonexistent-id",
            "--dispatch-action", "run_agent",
            "--envelope-json", envelope,
            "--hmac-key-path", str(key),
        ]),
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "authorization" in result.stderr.lower() or "approval" in result.stderr.lower()

def test_dispatch_gate_fires_before_subprocess(tmp_path):
    """Verify the CLI subprocess is never called on auth failure."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("dispatch", DISPATCH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    db = tmp_path / "test.sqlite"
    key = tmp_path / "test.key"
    key.write_bytes(b"\x00" * 32)
    envelope = json.dumps({"payload": "x", "hmac": "bad", "nonce": "n1"})

    test_argv = [str(DISPATCH)] + MINIMAL_ARGS + [
        "--db-path", str(db),
        "--approval-id", "test-id",
        "--envelope-json", envelope,
        "--hmac-key-path", str(key),
    ]

    with unittest.mock.patch("subprocess.run") as mock_run, \
         unittest.mock.patch.object(mod, "check_dispatch_authorization",
                                    return_value=(False, "mock rejection")) as mock_auth, \
         unittest.mock.patch("sys.argv", test_argv):
        with pytest.raises(SystemExit) as exc:
            mod.main()
        assert exc.value.code != 0
    mock_auth.assert_called_once()
    mock_run.assert_not_called()

def test_alias_index_three_way_resolution(tmp_path):
    """Verify build_agent_index resolves an agent by stem, stem-without-suffix, and frontmatter name."""
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "intake-agent.md").write_text("---\nname: Intake Agent\n---\nBody")
    from dispatch import build_agent_index
    idx = build_agent_index(agents)
    assert "intake-agent" in idx          # stem
    assert "intake" in idx                # stem-without-agent
    assert "Intake Agent" in idx          # frontmatter name
    # All three resolve to the same file
    assert idx["intake-agent"] == idx["intake"] == idx["Intake Agent"]

def test_handoff_envelope_caps_turns_and_chars():
    """Verify build_handoff_envelope caps transcript to 8 lines and 300 chars per line."""
    transcript = [("user", "x" * 500), ("agent", "y" * 500)] * 10
    from dispatch import build_handoff_envelope
    env = build_handoff_envelope("intake-agent", "vibe-orchestrator",
                                  "prototype detected", "I have code", transcript)
    lines = [l for l in env.split("\n")
             if l.startswith("user:") or l.startswith("agent:")]
    assert len(lines) <= 8
    for line in lines:
        payload = line.split(": ", 1)[1] if ": " in line else line
        assert len(payload) <= 300
