"""
tests/test_review_option_menus.py
=================================

Purpose:
    Failing-first tests for validated menus on the review-selection questions (auth-ciba-increment-b,
    human request 2026-09-20; H1 option A). The three conditional internal-review questions (runtime, model,
    effort) carry `choices_from` in the YAML; at ask time the coordinator resolves a numbered menu from
    review_options.choices_for (the runtime CLI's own `models` command, else the project capability profile,
    else free text with a visible warning) and REJECTS typed answers that are not in the menu, so a slip like
    "astra 6" cannot be recorded. Real coordinator, real SQLite; the CLIs are fake executables on a temp PATH
    injected through the coordinator's `review_choices_fn` seam.

Key Input Dependencies:
    - control_plane/review_options.py (choices_for, ChoiceSet), coordinator.py (review_choices_fn), registry.py
      (choices_from validation), transition_templates.yaml
    - tests/test_review_selection.py helpers

Key Functions (test cases):
    - test_runtime_choices_mark_installed_and_missing
    - test_agy_model_and_effort_choices_come_from_the_cli
    - test_unknown_runtime_models_fall_back_with_a_warning
    - test_profile_supplies_models_for_a_runtime_without_a_probe
    - test_every_conditional_review_question_declares_choices_from
    - test_menu_accepts_a_number_and_records_the_canonical_id
    - test_a_typed_answer_outside_the_menu_is_rejected
    - test_a_missing_menu_falls_back_to_free_text_with_a_warning
"""

import io
import json
import stat
import sys
from functools import partial
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError
from control_plane.registry import TransitionRegistry
from control_plane.review_options import ChoiceSet, choices_for
from control_plane.review_selection import REVIEW_EDGES, conditional_questions
from test_review_selection import INTERNAL, TASK, YES, _plan_review_task


def _fake(bindir: Path, name: str, body: str) -> None:
    exe = bindir / name
    exe.write_text("#!/bin/sh\n" + body + "\n")
    exe.chmod(exe.stat().st_mode | stat.S_IXUSR)


AGY_MODELS = 'if [ "$1" = "models" ]; then printf "Fetching...\\ngemini-3.8-flash-medium\\tGemini 3.8 Flash (Medium)\\ngemini-3.1-pro-high\\tGemini 3.1 Pro (High)\\n"; fi'


def test_runtime_choices_mark_installed_and_missing(tmp_path):
    _fake(tmp_path, "agy", "true")
    items = {i["id"]: i["installed"] for i in choices_for("runtime", path=str(tmp_path)).items}
    assert set(items) == {"codex", "claude", "agy", "copilot"} and items["agy"] and not items["codex"]


def test_agy_model_and_effort_choices_come_from_the_cli(tmp_path):
    _fake(tmp_path, "agy", AGY_MODELS)
    models = choices_for("model", runtime="agy", path=str(tmp_path))
    assert [i["id"] for i in models.items] == ["gemini-3.8-flash-medium", "gemini-3.1-pro-high"] and models.warning is None
    assert [i["id"] for i in choices_for("effort", runtime="agy", path=str(tmp_path)).items] == ["low", "medium", "high"]


def test_unknown_runtime_models_fall_back_with_a_warning(tmp_path):
    result = choices_for("model", runtime="codex", path=str(tmp_path), profile_path=tmp_path / "missing.json")
    assert result.items == [] and "cannot be validated" in result.warning


def test_profile_supplies_models_for_a_runtime_without_a_probe(tmp_path):
    profile = tmp_path / "agent-capability-profile.json"
    profile.write_text(json.dumps({"providers": {"codex": {"model_tiers": {"low": "gpt-5.6-luna", "high": "gpt-6-astra"}}}}))
    result = choices_for("model", runtime="codex", path=str(tmp_path), profile_path=profile)
    assert sorted(i["id"] for i in result.items) == ["gpt-5.6-luna", "gpt-6-astra"] and result.warning is None


def test_every_conditional_review_question_declares_choices_from():
    registry = TransitionRegistry.load_default()
    for edge in REVIEW_EDGES:
        kinds = [q["choices_from"]["kind"] for q in conditional_questions(registry.get_template(*edge))]
        assert kinds == ["runtime", "model", "effort"]


def _go(sim, answers, choices_fn):
    feed = iter(answers)
    coordinator = TransitionCoordinator(
        sim.control_plane, registry=sim.registry, input_fn=lambda _p: next(feed), output_stream=(out := io.StringIO()),
        review_choices_fn=choices_fn,
    )
    coordinator.coordinate_transition(task_id=TASK, to_state="MULTI_AGENT_REVIEW", actor="human", reason="review", interactive=True)
    return out.getvalue()


def _recorded(sim):
    import sqlite3

    rows = sqlite3.connect(sim.control_plane.db_path).execute(
        "SELECT question_id, answer FROM transition_decisions WHERE task_id = ? AND to_state = 'MULTI_AGENT_REVIEW'", (TASK,)
    ).fetchall()
    return {q.rsplit("_", 1)[-1] if q.endswith(("model", "effort")) else q: a for q, a in rows}


def test_menu_accepts_a_number_and_records_the_canonical_id(tmp_path):
    _fake(tmp_path, "agy", AGY_MODELS)
    sim = _plan_review_task(tmp_path / "w")
    printed = _go(sim, [YES, INTERNAL, "1", "1", "2", "YES"], partial(choices_for, path=str(tmp_path)))
    # only installed runtimes are selectable, so agy is menu item 1; then model 1, effort 2 (medium)
    assert "gemini-3.8-flash-medium" in printed
    recorded = _recorded(sim)
    assert recorded["model"] == "gemini-3.8-flash-medium" and recorded["effort"] in ("low", "medium", "high")


def test_a_typed_answer_outside_the_menu_is_rejected(tmp_path):
    _fake(tmp_path, "agy", AGY_MODELS)
    sim = _plan_review_task(tmp_path / "w")
    with pytest.raises(TransitionCoordinatorError):
        _go(sim, [YES, INTERNAL, "agy", "astra 6", "medium", "YES"], partial(choices_for, path=str(tmp_path)))
    assert sim.control_plane._persistence.read_current_state(TASK) == "PLAN_REVIEW"


def test_a_missing_menu_falls_back_to_free_text_with_a_warning(tmp_path):
    sim = _plan_review_task(tmp_path / "w")
    printed = _go(sim, [YES, INTERNAL, "anything", "any-model", "medium", "YES"], lambda kind, runtime=None: ChoiceSet([], "no menu available; the answer cannot be validated"))
    assert "cannot be validated" in printed


def test_default_profile_path_uses_the_shared_repository_root():
    """The identity folder resolves against the canonical (main) repo root; the profile must too, so it is
    found when the command runs from a worktree."""
    from control_plane.identity_layout import canonical_repo_root
    from control_plane.review_options import default_profile_path

    assert default_profile_path() == canonical_repo_root(".") / "context" / "agent-capability-profile.json"
