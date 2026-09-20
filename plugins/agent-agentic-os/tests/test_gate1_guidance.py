"""
tests/test_gate1_guidance.py
============================

Purpose:
    Failing-first test for the T7 YAML remainder (auth-ciba-increment-b, issue #639): the Gate 1
    edge's `next_steps_hint` must describe the signed two-phase flow (request, show-challenge,
    sign, approve-transition), must not mention the removed legacy_input fallback, and must no longer tell
    anyone to approve with `--answers` or a scripted prompt. The YAML guidance is an executable contract for agents.

Key Input Dependencies:
    - control_plane/transition_templates.yaml (awaiting_approval_to_approved) via TransitionRegistry

Key Functions (test cases):
    - test_gate1_hint_describes_the_signed_flow
    - test_gate1_hint_no_longer_recommends_scripted_approval
"""

import sys
from pathlib import Path

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from control_plane.registry import TransitionRegistry


def _hint() -> str:
    template = TransitionRegistry.load_default().get_template("AWAITING_APPROVAL", "APPROVED")
    return template.next_steps_hint or ""


def test_gate1_hint_describes_the_signed_flow():
    hint = _hint()
    for needed in ("HUMAN_PROOF_REQUIRED", "show-challenge", "approve-transition", "ssh-keygen -Y sign", "passphrase", "allowed_signers"):
        assert needed in hint, needed
    assert "legacy_input" not in hint


def test_gate1_hint_no_longer_recommends_scripted_approval():
    hint = _hint().lower()
    assert "--answers '<json>'" not in hint  # the old recommendation
    assert "answer this edge's yaml questions" not in hint
    assert "can authorize this edge" in hint  # it now warns that no prompt, word or flag can approve it
    assert "no prompt, typed word, --answers, --human-confirmed or flag can authorize" in hint
