"""Contract tests for the first-time-agent control-plane simulation protocol."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = REPO_ROOT / "plugins/agent-agentic-os/references/control-plane-simulation-protocol.md"


def test_protocol_names_the_full_round_contract():
    text = PROTOCOL.read_text().lower()
    for marker in (
        "orientation",
        "authority",
        "preconditions",
        "one question at a time",
        "denial invariant",
        "state-preserving",
        "sqlite",
        "friction",
        "surgical fix",
        "handoff_block",
    ):
        assert marker in text


def test_protocol_requires_two_independent_rounds_and_no_silent_defaults():
    text = PROTOCOL.read_text().lower()
    assert "round 1" in text
    assert "round 2" in text
    assert "defaults are not inferred" in text
    assert "production" in text and "controlplane" in text
