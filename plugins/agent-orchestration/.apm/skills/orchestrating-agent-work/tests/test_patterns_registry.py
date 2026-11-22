#!/usr/bin/env python3
"""
test_patterns_registry.py - references/patterns.json is the single strategy registry (S1: B11, B12)
=====================================================================================================

Validates:
- every entry carries the contract fields (pattern, description, plan_artifact, required, next_skill, next_step);
- every validator_script is relative to this skill folder and exists there (no repository or plugin paths);
- every validator argv template names {validator_script} and {artifact}, and its subcommand exists in the script;
- the learning-loop strategy is registered and its next_step reference exists.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent
PATTERNS = json.loads((SKILL_DIR / "references" / "patterns.json").read_text(encoding="utf-8"))
WITH_VALIDATOR = sorted(name for name, entry in PATTERNS.items() if entry.get("validator_script"))


def test_every_entry_has_the_contract_fields():
    for name, entry in PATTERNS.items():
        assert entry["pattern"] == name
        assert isinstance(entry["description"], str) and entry["description"]
        assert isinstance(entry["plan_artifact"], str) and "<task-id>" in entry["plan_artifact"]
        assert isinstance(entry["required"], bool)
        assert "next_skill" in entry and "next_step" in entry


def test_the_validators_are_the_graph_and_dual_loop_scripts():
    assert WITH_VALIDATOR == ["dual-loop", "graph"]


@pytest.mark.parametrize("name", WITH_VALIDATOR)
def test_every_validator_script_exists_relative_to_this_skill(name):
    rel = PATTERNS[name]["validator_script"]
    assert not Path(rel).is_absolute()
    assert not rel.startswith(("skills/", "plugins/", ".agents/", ".claude/")), rel
    script = (SKILL_DIR / rel).resolve()
    script.relative_to(SKILL_DIR.resolve())
    assert script.is_file(), f"{name}: {rel} does not exist in {SKILL_DIR}"


@pytest.mark.parametrize("name", WITH_VALIDATOR)
def test_every_validator_argv_runs_its_script_on_the_artifact(name):
    argv = PATTERNS[name]["validator"]
    assert argv[1] == "{validator_script}" and "{artifact}" in argv
    script = SKILL_DIR / PATTERNS[name]["validator_script"]
    help_argv = [a for a in argv[2:] if not a.startswith("{")][:1]  # the subcommand, if any
    done = subprocess.run([sys.executable, str(script)] + help_argv + ["--help"], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    for flag in (a for a in argv[2:] if a.startswith("--")):
        assert flag in done.stdout, f"{name}: {flag} is not accepted by {script.name} {' '.join(help_argv)}"


def test_learning_loop_is_registered_with_its_reference():
    entry = PATTERNS["learning-loop"]
    assert entry["next_skill"] == "orchestrating-agent-work"
    assert (SKILL_DIR / "references" / f"{entry['next_step']}.md").is_file()
    assert "validator_script" not in entry
