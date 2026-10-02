"""Observable contracts for read-only, navigable, portable skill auditing.

Purpose: Verify rule evidence and real CLI/discovery behavior.
Key Input Dependencies: scripts/audit_skill.py and the authoring contract.
"""
import json
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "scripts"))
from audit_skill import audit_skill, load_contract


def make_skill(root, name="sample-skill", body="## Workflow\nProcess samples.\n"):
    """Create a real minimal skill fixture with explicit routing cases."""
    skill = root / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(f'---\nname: {name}\ndescription: "Processes data: {{rows}} # safely."\n---\n# Sample\n{body}')
    (skill / "evals").mkdir()
    (skill / "evals/evals.json").write_text(json.dumps([{"query": "process samples", "should_trigger": True}]))
    return skill


def cli(root, *flags):
    """Run the public auditor without mocking filesystem discovery."""
    return subprocess.run([sys.executable, str(PLUGIN / "scripts/audit_skill.py"), str(root), *flags], capture_output=True, text=True)


def test_broken_direct_link_has_rule_and_location(tmp_path):
    skill = make_skill(tmp_path, body="See [workflow](references/missing.md).\n")
    report = audit_skill(skill).to_dict()
    assert not report["passed"]
    assert any(f["rule_id"] == "links.resolve" and f["line"] for f in report["findings"])


def test_long_reference_needs_early_contents(tmp_path):
    skill = make_skill(tmp_path, body="See [workflow](references/workflow.md).\n")
    (skill / "references").mkdir()
    (skill / "references/workflow.md").write_text("# Workflow\n" + "Instruction\n" * 110)
    report = audit_skill(skill).to_dict()
    assert any(f["rule_id"] == "navigation.reference-toc" for f in report["findings"])


def test_nonboolean_routing_is_error(tmp_path):
    skill = make_skill(tmp_path)
    (skill / "evals/evals.json").write_text('[{"query":"samples","should_trigger":"false"}]')
    assert not audit_skill(skill).passed


def test_installed_real_scripts_are_accepted(tmp_path):
    skill = make_skill(tmp_path)
    (skill / "scripts").mkdir()
    (skill / "scripts/process.py").write_text('print("samples")\n')
    result = cli(skill, "--mode", "installed", "--json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["representation"] == "installed"


def test_bulk_fix_refused_without_mutation(tmp_path):
    skill = make_skill(tmp_path / "plugins/sample/skills")
    original = (skill / "SKILL.md").read_bytes()
    result = cli(tmp_path, "--all", "--fix", "--json")
    assert result.returncode == 2
    assert (skill / "SKILL.md").read_bytes() == original


def test_empty_inventory_is_input_failure(tmp_path):
    result = cli(tmp_path, "--all", "--json")
    assert result.returncode == 2


def test_inventory_classifies_nested_fixture_and_installed_copy(tmp_path):
    skill = make_skill(tmp_path / "plugins/sample/skills")
    make_skill(tmp_path / "plugins/sample/tests/fixtures/plugins/nested/skills", name="fixture-skill")
    copy = make_skill(tmp_path / ".agents/skills")
    result = cli(tmp_path, "--all", "--json")
    report = json.loads(result.stdout)
    assert report["schema_version"] == 2
    assert report["summary"]["skills"] == 1
    assert len(report["skills"]) == 1
    assert report["skills"][0]["canonical_path"] == str(skill)
    assert any(item["classification"] == "fixture" for item in report["noncanonical"])
    assert any(item["path"] == str(copy) and item["classification"] == "installed" for item in report["noncanonical"])


def test_duplicate_anchor_and_fenced_examples(tmp_path):
    skill = make_skill(tmp_path, body="[Next](#step-1)\n## Step\n````md\n## Step\n````\n## Step\n")
    report = audit_skill(skill).to_dict()
    assert not any(f["rule_id"] == "links.resolve" for f in report["findings"])


def test_reference_backtick_routes_use_skill_root(tmp_path):
    skill = make_skill(tmp_path, body="[Workflow](references/workflow.md)\n[Details](references/details.md)\n")
    (skill / "references").mkdir()
    (skill / "references/workflow.md").write_text("Read `references/details.md` before proceeding.\n")
    (skill / "references/details.md").write_text("# Details\nValidate output.\n")
    report = audit_skill(skill, mode="installed").to_dict()
    assert not any(f["rule_id"] == "links.resolve" for f in report["findings"])


def test_single_scan_read_failure_is_structured(tmp_path):
    skill = make_skill(tmp_path, body="[Workflow](references/workflow.md)\n")
    (skill / "references").mkdir()
    (skill / "references/workflow.md").write_bytes(b"\xff")
    result = cli(skill, "--json")
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    assert json.loads(result.stdout)["scan_failures"]


def test_directory_route_link_resolves(tmp_path):
    skill = make_skill(tmp_path, body="See [templates](assets/templates/).\n")
    (skill / "assets/templates").mkdir(parents=True)
    report = audit_skill(skill).to_dict()
    assert report["passed"]
    assert not any(f["rule_id"] == "links.resolve" for f in report["findings"])


def test_yaml_frontmatter_block_with_trailing_comment(tmp_path):
    skill = tmp_path / "block-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: block-skill\n"
        "description: > # safe block description with comment\n"
        "  Processes data safely\n"
        "  across multiple lines.\n"
        "---\n"
        "# Block Skill\n"
        "## Workflow\n"
        "Process samples.\n"
    )
    (skill / "evals").mkdir()
    (skill / "evals/evals.json").write_text(json.dumps([{"query": "process samples", "should_trigger": True}]))
    report = audit_skill(skill).to_dict()
    assert report["passed"]
    from audit_skill import parse_frontmatter
    fm = parse_frontmatter((skill / "SKILL.md").read_text())
    assert fm is not None
    assert fm["description"] == "Processes data safely across multiple lines."


def test_installed_hard_copy_alias_mapping_and_corroboration(tmp_path):
    canonical = make_skill(tmp_path / "plugins/sample/skills", name="sample-skill")
    copy = make_skill(tmp_path / ".agents/skills", name="sample-skill")
    ownership_dir = tmp_path / ".agents/ownership"
    ownership_dir.mkdir(parents=True)
    (ownership_dir / "sample.json").write_text(json.dumps({
        "plugin": "sample",
        "components": {
            "skills": {
                "sample-skill": {
                    "artifacts": [".agents/skills/sample-skill"]
                }
            }
        }
    }))
    from audit_skill import discover
    canonical_list, noncanonical, aliases = discover(tmp_path)
    assert canonical in canonical_list
    installed_items = [item for item in noncanonical if item["path"] == str(copy)]
    assert len(installed_items) == 1
    assert installed_items[0]["classification"] == "installed"
    assert installed_items[0]["canonical_path"] == str(canonical)
    assert installed_items[0].get("hash_match") is True
    assert canonical in aliases
    assert str(copy) in aliases[canonical]


def test_ai_review_schema_and_scenarios():
    contract = load_contract()
    assert "ai_review_schema" in contract
    schema = contract["ai_review_schema"]
    assert "properties" in schema
    assert "status" in schema["properties"]
    assert "findings" in schema["properties"]

    # Validate the 3 semantic scenarios against the contract definition
    scenarios = contract.get("semantic_scenarios", {})
    assert "concise_complete" in scenarios
    assert "verbose_history" in scenarios
    assert "short_incomplete" in scenarios

    assert scenarios["concise_complete"]["expected_action"] == "preserve"
    assert scenarios["verbose_history"]["expected_action"] == "compress_history"
    assert scenarios["short_incomplete"]["expected_action"] == "flag_missing_behavior"


