"""
test_control_plane_mode_manifest.py - keeps os-control-plane-mode's knowledge honest.

Purpose:
    The toggle only knows what the control plane consists of from control-plane.manifest.json.
    Without these tests that list would silently rot: a renamed skill would make `disable`
    fail, and a NEW skill/rule/agent that depends on the control plane would be left installed
    (and gating) when the user disables it. The tests force every component that mentions the
    control plane to be either a member or an explicitly excluded one, with a reason.
"""

import json
import re
from pathlib import Path

import pytest
import yaml

import control_plane_hooks as cph

PLUGIN = Path(__file__).resolve().parent.parent
REPO = PLUGIN.parent.parent
SKILL = PLUGIN / "skills" / "os-control-plane-mode"
MANIFEST = json.loads((SKILL / "control-plane.manifest.json").read_text())

MENTIONS = re.compile(r"work-intake|control[_ -]plane|agent_control", re.IGNORECASE)
SELF = "skills/os-control-plane-mode"


def _defs():
    """Every top-level definition file of a skill, rule or agent -> 'kind/name'."""
    for p in sorted((PLUGIN / "skills").glob("*/SKILL.md")):
        yield f"skills/{p.parent.name}", p
    for p in sorted((PLUGIN / "rules").glob("*.md")):
        yield f"rules/{p.stem}", p
    for p in sorted((PLUGIN / "agents").glob("*.md")):
        yield f"agents/{p.stem}", p


def _members():
    return {f"{k}/{n}" for k, names in MANIFEST["members"].items() for n in names}


def test_every_component_that_mentions_the_control_plane_is_classified():
    classified = _members() | {e["component"] for e in MANIFEST["excluded"]} | {SELF}
    unclassified = [
        comp for comp, path in _defs()
        if MENTIONS.search(path.read_text(encoding="utf-8")) and comp not in classified
    ]
    assert not unclassified, (
        f"{unclassified} mention the control plane but are neither members nor excluded in "
        "control-plane.manifest.json. Decide: should disabling the control plane switch them off "
        "(add to members) or must they stay (add to excluded with a reason)?"
    )


def test_members_and_excluded_exist_and_do_not_overlap():
    existing = {comp for comp, _ in _defs()}
    members, excluded = _members(), {e["component"] for e in MANIFEST["excluded"]}
    assert members <= existing, f"members that do not exist: {members - existing}"
    assert excluded <= existing, f"excluded that do not exist: {excluded - existing}"
    assert not (members & excluded)
    assert all(e.get("reason", "").strip() for e in MANIFEST["excluded"]), "every exclusion needs a reason"


def test_the_substrate_skills_are_never_members():
    # os-init creates the substrate and os-health-check verifies it, in both modes.
    assert not ({"skills/os-init", "skills/os-health-check", SELF} & _members())


def test_manifest_guards_match_the_helper_and_exist():
    names = [g["name"] for g in MANIFEST["git_guards"]]
    assert names == [g.name for g in cph.CONTROL_PLANE_GUARDS]
    for name in names:
        assert (PLUGIN / "scripts" / name).is_file()
    assert "pre-commit-evolution-guard" not in names  # a separate feature


def test_skills_are_registered_in_plugin_yaml():
    declared = set(yaml.safe_load((PLUGIN / "plugin.yaml").read_text())["skills"])
    assert "os-control-plane-mode" in declared
    assert set(MANIFEST["members"]["skills"]) <= declared


def test_skill_definition_is_well_formed_and_triggers_on_plain_language():
    text = (SKILL / "SKILL.md").read_text()
    front = yaml.safe_load(text.split("---")[1])
    assert front["name"] == "os-control-plane-mode" and front["plugin"] == "agent-agentic-os"
    description = front["description"].lower()
    for phrase in ("enable the control plane", "disable the control plane", "control plane status"):
        assert phrase in description, f"description must trigger on {phrase!r}"


def test_shared_helper_symlinks_are_registered_and_resolve():
    registry = json.loads((REPO / "symlinks.json").read_text())["links"]
    wanted = {
        "plugins/agent-agentic-os/skills/os-init/scripts/control_plane_hooks.py",
        "plugins/agent-agentic-os/skills/os-control-plane-mode/scripts/control_plane_hooks.py",
    }
    registered = {l["dst"] for l in registry if l["src"] == "plugins/agent-agentic-os/scripts/control_plane_hooks.py"}
    assert wanted <= registered
    for dst in wanted:
        link = REPO / dst
        assert link.is_symlink() and link.resolve() == (PLUGIN / "scripts" / "control_plane_hooks.py").resolve()


def test_no_member_is_a_plugin_hook_or_the_evolution_feature():
    flat = json.dumps(MANIFEST["members"])
    assert "hooks" not in flat and "evolution" not in flat
