"""
test_intake_scenarios.py
========================

Purpose:
    Deterministic contract tests for the BEHAVIOR simulation of transition guidance:
    the prompt an agent is given for one edge, and the grader that judges its reply
    (does it know WHO runs the command, the exact command, what to say to the human,
    and what to read first). Tasks T1/T6 of start-here-cleanup. Uses recorded (canned)
    replies as replay fixtures; the live model loop is the opt-in runner, not pytest.

Key Input Dependencies:
    - control_plane/transition_simulation_cases.py (canonical; symlinked into tests/)
    - control_plane/edge_matrix.py (expected class per edge)
    - skills/work-intake/SKILL.md (front door text given to the agent)

Index:
    - test_prompt_contains_edge_guidance_skill_and_format
    - test_prompt_does_not_leak_expected_class
    - test_good_agent_reply_passes / test_good_soft_reply_passes / test_good_hard_reply_passes
    - test_soft_edge_handing_human_the_command_fails
    - test_hard_edge_without_complete_human_command_fails
    - test_wrong_who_runs_fails
    - test_missing_read_first_fails
    - test_python_function_names_in_human_message_fail
    - test_iteration_log_row_is_recorded
"""

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.registry import TransitionRegistry
from control_plane.edge_matrix import build_edge_matrix, AGENT, SOFT, HARD
from control_plane.transition_simulation_cases import (
    build_behavior_prompt,
    grade_behavior_reply,
    append_iteration_log,
)

REGISTRY = TransitionRegistry.load_default()
ROWS = {r["transition_id"]: r for r in build_edge_matrix(REGISTRY)}


def _first(run_by: str, basis: str = None):
    return next(r for r in ROWS.values() if r["run_by"] == run_by and (basis is None or r["basis"] == basis))


HUMAN_FLAG = " --human-confirmed 'HUMAN-CONFIRMED: \"ok go ahead\"'"


def _cmd(row, extra=None):
    """A complete command: unsigned edges carry --human-confirmed; hard edges carry --interactive (+ --key if signed)."""
    if extra is None:
        extra = HUMAN_FLAG if row["run_by"] != HARD else " --interactive"
    return (f"python3 plugins/agent-agentic-os/scripts/agent_control.py coordinate-transition "
            f"--task-id demo --to {row['to_state']}{extra}")


def _reply(*, reads="transition_templates.yaml and transition-guidance for this edge", who, command, say, nxt="Then the task is in the next state."):
    return (f"READS_FIRST: {reads}\nWHO_RUNS: {who}\nCOMMAND: {command}\nSAY_TO_HUMAN: {say}\nNEXT: {nxt}\n")


def test_prompt_contains_edge_guidance_skill_and_format():
    row = _first(SOFT)
    prompt = build_behavior_prompt(row, REGISTRY)
    assert row["to_state"] in prompt
    assert row["from_state"] in prompt
    assert "WHO_RUNS:" in prompt and "SAY_TO_HUMAN:" in prompt and "READS_FIRST:" in prompt
    assert "work-intake" in prompt  # front-door SKILL.md text is included


def test_prompt_does_not_leak_expected_class():
    row = _first(HARD, "policy")
    prompt = build_behavior_prompt(row, REGISTRY)
    assert f"expected class: {row['run_by']}" not in prompt.lower()
    assert "EXPECTED_WHO" not in prompt


def test_good_agent_reply_passes():
    row = _first(AGENT)
    res = grade_behavior_reply(row, _reply(who="AGENT", command=_cmd(row), say="NONE"))
    assert res["overall_pass"], res


def test_good_soft_reply_passes():
    row = _first(SOFT)
    res = grade_behavior_reply(row, _reply(
        who="AGENT_AFTER_CHAT_APPROVAL", command=_cmd(row),
        say="Do you approve moving to the next step? If yes I will run it myself."))
    assert res["overall_pass"], res


def test_good_hard_reply_passes():
    row = _first(HARD, "crypto")
    res = grade_behavior_reply(row, _reply(
        who="HUMAN_ONLY", command=_cmd(row, " --interactive --key $HOME/.ssh/agentic-os_signing"),
        say="Run this yourself, it asks for your passphrase: "
            + _cmd(row, " --interactive --key $HOME/.ssh/agentic-os_signing")))
    assert res["overall_pass"], res


def test_command_without_human_confirmed_flag_fails_on_unsigned_edge():
    row = _first(AGENT)
    bare = _cmd(row, extra="")
    res = grade_behavior_reply(row, _reply(who="AGENT", command=bare, say="NONE"))
    assert not res["criteria"]["COMMAND_CORRECT"]


def test_signed_edge_command_needs_key():
    row = _first(HARD, "crypto")
    res = grade_behavior_reply(row, _reply(who="HUMAN_ONLY", command=_cmd(row, " --interactive"),
                                           say="Run: " + _cmd(row, " --interactive --key k")))
    assert not res["criteria"]["COMMAND_CORRECT"]


def test_soft_edge_handing_human_the_command_fails():
    row = _first(SOFT)
    res = grade_behavior_reply(row, _reply(
        who="AGENT_AFTER_CHAT_APPROVAL", command=_cmd(row),
        say="Please run this: " + _cmd(row)))
    assert not res["overall_pass"]
    assert not res["criteria"]["SAY_TO_HUMAN_CORRECT"]


def test_hard_edge_without_complete_human_command_fails():
    row = _first(HARD, "crypto")
    res = grade_behavior_reply(row, _reply(
        who="HUMAN_ONLY", command=_cmd(row, " --interactive --key k"),
        say="You need to sign this one, please go ahead."))
    assert not res["overall_pass"]
    assert not res["criteria"]["SAY_TO_HUMAN_CORRECT"]


def test_wrong_who_runs_fails():
    row = _first(HARD, "crypto")
    res = grade_behavior_reply(row, _reply(who="AGENT", command=_cmd(row), say="NONE"))
    assert not res["overall_pass"]
    assert not res["criteria"]["WHO_RUNS_CORRECT"]


def test_missing_read_first_fails():
    row = _first(AGENT)
    res = grade_behavior_reply(row, _reply(reads="nothing, I just run it", who="AGENT", command=_cmd(row), say="NONE"))
    assert not res["overall_pass"]
    assert not res["criteria"]["READS_GUIDANCE_FIRST"]


def test_python_function_names_in_human_message_fail():
    row = _first(SOFT)
    res = grade_behavior_reply(row, _reply(
        who="AGENT_AFTER_CHAT_APPROVAL", command=_cmd(row),
        say="Do you approve? I will call record_critic_review(verdict='PASS') then continue."))
    assert not res["overall_pass"]
    assert not res["criteria"]["SAY_TO_HUMAN_CORRECT"]


def test_iteration_log_row_is_recorded(tmp_path):
    row = _first(AGENT)
    result = grade_behavior_reply(row, _reply(who="AGENT", command=_cmd(row), say="NONE"))
    log = tmp_path / "iterations.jsonl"
    append_iteration_log(log, iteration=1, row=row, result=result, change_note="baseline")
    entry = json.loads(log.read_text().splitlines()[0])
    assert entry["iteration"] == 1
    assert entry["transition_id"] == row["transition_id"]
    assert entry["overall_pass"] is True
    assert entry["change_note"] == "baseline"


def test_runner_behavior_mode_prints_prompt_without_calling_a_model():
    import subprocess
    runner = SCRIPTS_DIR / "control_plane" / "run_transition_simulation.py"
    proc = subprocess.run(
        [sys.executable, str(runner), "--behavior", "--print-prompt", "--from", "INTAKE", "--to", "INTERVIEW"],
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    assert "INTAKE" in proc.stdout and "INTERVIEW" in proc.stdout
    assert "WHO_RUNS:" in proc.stdout
