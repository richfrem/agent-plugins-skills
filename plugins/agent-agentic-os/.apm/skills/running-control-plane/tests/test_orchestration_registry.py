"""
test_orchestration_registry.py - one strategy registry through the APM dependency (S1: B8, B9, B11, B12, B13)
================================================================================================================

Validates:
1. Sibling skills are found only at <skills root>/<name>; a missing one fails closed with the exact apm install message.
2. Strategies come from the sibling orchestrating-agent-work's patterns.json; the YAML adds only triple-loop-learning.
3. Validators resolve relative to their owning sibling skill (graph -> scripts/validate_manifest.py).
4. The cli-agent catalogs are read from the sibling cli-agent skill (ModelCatalogAdapter, review model menus).
5. The coordinator's plan-artifact gate uses the registry: valid graph passes with a fixture root, an empty root fails
   closed with the install message, and no retired graph-planner or repository path is consulted.
6. The dual-loop validator (agent_orchestrator.py validate-packet) accepts a valid packet and refuses an invalid one.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from control_plane import orchestration_registry as reg
from control_plane.adapters import ModelCatalogAdapter
from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError
from control_plane.registry import TransitionRegistry
from control_plane.review_options import choices_for
from helpers.orchestration_fixture import make_skills_root

from test_strategy_artifacts import MockControlPlane, MockFilesystemPort, VALID_GRAPH_MANIFEST

INSTALL_HINT = (
    "It ships in the agent-orchestration APM package: apm install richfrem/agent-plugins-skills/plugins/"
    "agent-orchestration --global --target claude,copilot,codex,agy"
)
OWNED_BY_ORCHESTRATION = {"graph", "dual-loop", "agent-swarm", "direct", "red-team-review", "learning-loop"}


def _graph_task(repo: Path, task_id: str, manifest: dict) -> None:
    task_dir = repo / "docs" / "plans" / "work-tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / f"{task_id}-spec.md").write_text("# Spec", encoding="utf-8")
    (task_dir / f"{task_id}-implementation-plan.md").write_text("# Plan\n\nstrategy: graph\n", encoding="utf-8")
    (task_dir / f"{task_id}-graph-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def _coordinator(repo: Path, skills_root: Path) -> TransitionCoordinator:
    coord = TransitionCoordinator(MockControlPlane(repo), fs=MockFilesystemPort(), skills_root=skills_root)
    coord._resolve_repo_root = lambda: repo
    return coord


# --- sibling resolution ---------------------------------------------------------------------------------------

def test_default_skills_root_is_the_folder_this_skill_is_installed_in():
    module_file = Path(reg.__file__).resolve()
    assert reg._THIS_SKILLS_ROOT == module_file.parents[3]
    assert reg._THIS_SKILLS_ROOT / "running-control-plane" / "scripts" / "control_plane" / module_file.name == module_file


def test_skills_root_override_is_returned_as_given(tmp_path):
    assert reg.skills_root(tmp_path) == tmp_path


def test_missing_sibling_raises_the_exact_install_message(tmp_path):
    root = make_skills_root(tmp_path, skills=())
    with pytest.raises(reg.OrchestrationDependencyMissing) as exc_info:
        reg.sibling_skill("orchestrating-agent-work", root)
    assert str(exc_info.value) == (
        f"orchestrating-agent-work is not installed beside running-control-plane ({root}). {INSTALL_HINT}"
    )


def test_a_folder_without_skill_md_is_not_a_sibling(tmp_path):
    root = make_skills_root(tmp_path, skills=())
    (root / "cli-agent" / "references").mkdir(parents=True)
    with pytest.raises(reg.OrchestrationDependencyMissing, match="cli-agent is not installed beside running-control-plane"):
        reg.cli_agent_references(root)


def test_cli_agent_references_come_from_the_sibling(tmp_path):
    root = make_skills_root(tmp_path)
    refs = reg.cli_agent_references(root)
    assert refs == root / "cli-agent" / "references"
    assert (refs / "claude-models.json").is_file() and (refs / "cheapest_models.json").is_file()


# --- strategy registry ----------------------------------------------------------------------------------------

def test_patterns_come_from_the_sibling_and_carry_the_contract_fields(tmp_path):
    patterns = reg.load_patterns(make_skills_root(tmp_path))
    assert set(patterns) == OWNED_BY_ORCHESTRATION
    for name, entry in patterns.items():
        assert entry["pattern"] == name
        assert isinstance(entry["description"], str) and entry["description"]
        assert isinstance(entry["plan_artifact"], str) and "<task-id>" in entry["plan_artifact"]
        assert isinstance(entry["required"], bool)
        assert entry["next_skill"] is None or isinstance(entry["next_skill"], str)
        assert entry["next_step"] is None or isinstance(entry["next_step"], str)


def test_graph_validator_resolves_inside_the_fixture_root(tmp_path):
    root = make_skills_root(tmp_path)
    cfg = reg.strategy_config("graph", root)
    assert cfg["plan_artifact"].endswith("<task-id>-graph-manifest.json") and cfg["required"] is True
    script = reg.resolve_validator(cfg, root)
    assert script == (root / "orchestrating-agent-work" / "scripts" / "validate_manifest.py").resolve()
    assert script.is_file()


def test_dual_loop_validator_resolves_to_agent_orchestrator(tmp_path):
    root = make_skills_root(tmp_path)
    cfg = reg.strategy_config("dual-loop", root)
    assert reg.resolve_validator(cfg, root).name == "agent_orchestrator.py"
    assert "validate-packet" in cfg["validator"]


def test_a_strategy_without_a_validator_resolves_to_none(tmp_path):
    root = make_skills_root(tmp_path)
    assert reg.resolve_validator(reg.strategy_config("direct", root), root) is None


def test_a_missing_validator_file_fails_closed(tmp_path):
    root = make_skills_root(tmp_path, skills=())
    fake = root / "orchestrating-agent-work"
    (fake / "references").mkdir(parents=True)
    (fake / "SKILL.md").write_text("---\nname: orchestrating-agent-work\n---\n", encoding="utf-8")
    cfg = {"validator_script": "scripts/validate_manifest.py", "next_skill": "orchestrating-agent-work"}
    with pytest.raises(reg.OrchestrationDependencyMissing, match="is not installed beside running-control-plane"):
        reg.resolve_validator(cfg, root)


def test_a_validator_outside_its_skill_is_refused(tmp_path):
    root = make_skills_root(tmp_path)
    with pytest.raises(ValueError, match="must stay inside"):
        reg.resolve_validator({"validator_script": "../cli-agent/SKILL.md"}, root)


def test_triple_loop_learning_comes_from_the_yaml(tmp_path):
    cfg = reg.strategy_config("triple-loop-learning", make_skills_root(tmp_path))
    assert cfg["plan_artifact"] == "docs/plans/work-tasks/<task-id>/<task-id>-learning-contract.md"
    assert cfg["required"] is False and "artifact" not in cfg


def test_an_unknown_strategy_is_none(tmp_path):
    assert reg.strategy_config("grahp", make_skills_root(tmp_path)) is None


def test_the_yaml_keeps_only_strategies_the_orchestration_skill_does_not_own(tmp_path):
    yaml_keys = set(TransitionRegistry.load_default().strategy_artifacts)
    assert yaml_keys == {"triple-loop-learning"}
    assert not yaml_keys & set(reg.load_patterns(make_skills_root(tmp_path)))


def test_strategy_config_fails_closed_without_the_sibling(tmp_path):
    with pytest.raises(reg.OrchestrationDependencyMissing):
        reg.strategy_config("direct", make_skills_root(tmp_path, skills=()))


# --- coordinator plan-artifact gate --------------------------------------------------------------------------

def test_coordinator_validates_a_graph_manifest_through_the_fixture_root(tmp_path):
    repo = tmp_path / "repo"
    task_id = "task-registry-graph"
    _graph_task(repo, task_id, VALID_GRAPH_MANIFEST)
    coord = _coordinator(repo, make_skills_root(tmp_path))
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")
    receipt = coord._stage_plan_artifact_submission(task_id, {"task_id": task_id}, template)
    assert f"graph:{task_id}-graph-manifest.json=" in receipt["command_executed"]


def test_coordinator_rejects_an_invalid_manifest_through_the_fixture_root(tmp_path):
    repo = tmp_path / "repo"
    task_id = "task-registry-bad-graph"
    _graph_task(repo, task_id, {"graph_id": "x", "nodes": [{"id": "n", "type": "parallel_read"}]})
    coord = _coordinator(repo, make_skills_root(tmp_path))
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")
    with pytest.raises(TransitionCoordinatorError, match="artifact validation failed"):
        coord._stage_plan_artifact_submission(task_id, {"task_id": task_id}, template)


def test_coordinator_with_an_empty_root_fails_closed_with_the_install_message(tmp_path):
    repo = tmp_path / "repo"
    task_id = "task-registry-empty"
    _graph_task(repo, task_id, VALID_GRAPH_MANIFEST)
    # A retired-layout validator planted in the repo must not be found: there is no folder search any more.
    planted = repo / ".agents" / "skills" / "graph-planner" / "scripts"
    planted.mkdir(parents=True)
    (planted / "validate_manifest.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
    root = make_skills_root(tmp_path, skills=())
    coord = _coordinator(repo, root)
    template = coord._registry.get_template("DRAFT_PLAN", "PLAN_REVIEW")
    with pytest.raises(TransitionCoordinatorError) as exc_info:
        coord._stage_plan_artifact_submission(task_id, {"task_id": task_id}, template)
    assert str(exc_info.value) == (
        f"orchestrating-agent-work is not installed beside running-control-plane ({root}). {INSTALL_HINT}"
    )


def test_draft_plan_advisory_routes_to_the_orchestration_skill(tmp_path):
    import io

    repo = tmp_path / "repo"
    repo.mkdir()
    coord = _coordinator(repo, make_skills_root(tmp_path))
    coord._out = io.StringIO()
    coord._write_transition_guidance("DRAFT_PLAN", "PLAN_REVIEW", "pre-transition")
    text = coord._out.getvalue()
    assert "`orchestrating-agent-work` skill" in text
    assert "references/strategy-selection.md, then references/graph-planning.md" in text
    assert "select-loop-strategy" not in text and "graph-planner" not in text

    missing = _coordinator(repo, make_skills_root(tmp_path / "empty", skills=()))
    missing._out = io.StringIO()
    missing._write_transition_guidance("DRAFT_PLAN", "PLAN_REVIEW", "pre-transition")
    assert INSTALL_HINT in missing._out.getvalue()


# --- cli-agent catalogs ---------------------------------------------------------------------------------------

def test_model_catalog_adapter_reads_the_sibling_cli_agent_catalogs(tmp_path):
    result = ModelCatalogAdapter(skills_root=make_skills_root(tmp_path)).resolve_recommended_model("claude", "low")
    assert result["model_id"]


def test_model_catalog_adapter_without_cli_agent_fails_closed(tmp_path):
    adapter = ModelCatalogAdapter(skills_root=make_skills_root(tmp_path, skills=()))
    with pytest.raises(ValueError, match="cli-agent is not installed beside running-control-plane"):
        adapter.resolve_recommended_model("claude", "low")


def test_review_model_menu_falls_back_to_the_cli_agent_catalog(tmp_path):
    root = make_skills_root(tmp_path)
    catalog = json.loads((root / "cli-agent" / "references" / "codex-models.json").read_text(encoding="utf-8"))
    hidden = {"withdrawn", "deprecated", "unavailable", "retired"}
    expected = []
    for model in catalog["models"]:
        if model.get("cli_id") and str(model.get("status", "GA")).casefold() not in hidden and model["cli_id"] not in expected:
            expected.append(model["cli_id"])
    assert expected, "fixture catalog has no usable codex model"
    menu = choices_for("model", runtime="codex", path=str(tmp_path), profile_path=tmp_path / "missing.json", skills_root=root)
    assert [i["id"] for i in menu.items] == expected and menu.warning is None


def test_review_model_menu_without_a_catalog_warns(tmp_path):
    menu = choices_for("model", runtime="codex", path=str(tmp_path), profile_path=tmp_path / "missing.json",
                       skills_root=make_skills_root(tmp_path, skills=()))
    assert menu.items == [] and "cannot be validated" in menu.warning


# --- dual-loop packet validator -------------------------------------------------------------------------------

def _validate_packet(root: Path, packet: Path) -> subprocess.CompletedProcess:
    script = reg.resolve_validator(reg.strategy_config("dual-loop", root), root)
    return subprocess.run([sys.executable, str(script), "validate-packet", "--packet-path", str(packet)],
                          capture_output=True, text=True, cwd=str(packet.parent))


def test_validate_packet_accepts_a_packet_from_the_template(tmp_path):
    root = make_skills_root(tmp_path)
    packet = tmp_path / "task_packet_t1.md"
    packet.write_text(
        "# Strategy Packet: t1\n\n## Objective\nDo it.\n\n## Context\nNone.\n\n## Implementation Tasks\n1. Edit x.\n\n"
        "## Acceptance Criteria\n- x passes.\n",
        encoding="utf-8",
    )
    done = _validate_packet(root, packet)
    assert done.returncode == 0, done.stderr


@pytest.mark.parametrize("body", [
    "## Objective\nDo it.\n\n## Implementation Tasks\n1. x\n\n## Acceptance Criteria\n- y\n",   # no title line
    "# Strategy Packet: t1\n\n## Objective\nDo it.\n\n## Implementation Tasks\n1. x\n",          # no acceptance criteria
    "# Strategy Packet: t1\n\n## Objective\n\n## Implementation Tasks\n1. x\n\n## Acceptance Criteria\n- y\n",  # empty objective
])
def test_validate_packet_refuses_an_incomplete_packet(tmp_path, body):
    root = make_skills_root(tmp_path)
    packet = tmp_path / "task_packet_t1.md"
    packet.write_text(body, encoding="utf-8")
    done = _validate_packet(root, packet)
    assert done.returncode == 1 and "INVALID" in done.stderr


def test_validate_packet_refuses_a_missing_file_and_rejects_bad_usage(tmp_path):
    root = make_skills_root(tmp_path)
    assert _validate_packet(root, tmp_path / "absent.md").returncode == 1
    script = reg.resolve_validator(reg.strategy_config("dual-loop", root), root)
    usage = subprocess.run([sys.executable, str(script), "validate-packet"], capture_output=True, text=True, cwd=str(tmp_path))
    assert usage.returncode == 2
