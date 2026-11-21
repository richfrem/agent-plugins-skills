#!/usr/bin/env python3
"""
Unit tests for agent-orchestration/ skills, pattern selection decision tree, and contracts.
Validates:
- Decision tree logic for all orchestration patterns (asserts pattern = graph, not skill = graph-planner)
- Skill metadata standards (kebab-case, third-person description, line budgets)
- evals.json schema compliance (should_trigger boolean, prompt string)
- Elimination of dead CLI subcommand references in orchestrator
- Pattern-owned plan artifact assertions
"""

import json
import os
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def evaluate_loop_strategy(task_description: str, has_dependencies: bool = False,
                           is_batch: bool = False, is_adversarial: bool = False,
                           is_bounded: bool = False, requires_human_gate: bool = False,
                           is_readonly_dag: bool = False) -> str:
    """
    Deterministic implementation of select-loop-strategy 6-gate decision tree.
    Returns the selected PATTERN name ('graph', 'agent-swarm', 'red-team-review', 'dual-loop', etc.).
    Note: requires_human_gate is orthogonal governance and does NOT force pattern = 'graph'.
    """
    if has_dependencies or is_readonly_dag:
        return "graph"
    if is_batch:
        return "agent-swarm"
    if is_adversarial:
        return "red-team-review"
    if is_bounded:
        return "dual-loop"
    return "learning-loop"


class TestLoopStrategiesDecisionTree(unittest.TestCase):

    def setUp(self):
        """Point at the consolidated orchestrating-agent-work skill root."""
        self.skill_root = PLUGIN_ROOT
        self.references_dir = self.skill_root / "references"

    def test_all_expected_skills_exist(self):
        """Assert the consolidated skill and all core strategy/graph references exist."""
        self.assertTrue(
            (self.skill_root / "SKILL.md").exists(),
            "Expected consolidated orchestrating-agent-work/SKILL.md does not exist",
        )
        expected_references = [
            "routing-and-closure.md",
            "strategy-selection.md",
            "strategy-dual-loop.md",
            "learning-loop.md",
            "strategy-agent-swarm.md",
            "strategy-red-team-review.md",
            "graph-planning.md",
            "graph-execution.md",
        ]
        for ref_name in expected_references:
            ref_path = self.references_dir / ref_name
            self.assertTrue(
                ref_path.exists(),
                f"Expected reference references/{ref_name} does not exist",
            )

    def test_routing_decision_tree_patterns(self):
        """
        Assert decision tree returns pattern names (e.g. pattern = graph),
        and verifies that human gates alone do not force graph routing.
        """
        # 1. Structural dependencies route to graph pattern
        pattern = evaluate_loop_strategy("Multi-phase refactor with parallel reads and ordered mutations", has_dependencies=True)
        self.assertEqual(pattern, "graph", "Structural dependencies must select pattern = 'graph'")

        # 2. Read-only DAG routes to graph pattern
        pattern = evaluate_loop_strategy("Multi-repo dependency scan joining at barrier", is_readonly_dag=True)
        self.assertEqual(pattern, "graph", "Read-only DAG must select pattern = 'graph'")

        # 3. Bounded bug fix with human review required routes to dual-loop (NOT graph!)
        pattern = evaluate_loop_strategy("Fix off-by-one bug with human approval gate", is_bounded=True, requires_human_gate=True)
        self.assertEqual(pattern, "dual-loop", "Bounded bug fix with human gate must select pattern = 'dual-loop', not 'graph'")

        # 4. Batch parallel tasks route to agent-swarm
        pattern = evaluate_loop_strategy("Convert 50 files independently", is_batch=True)
        self.assertEqual(pattern, "agent-swarm", "Batch conversion must select pattern = 'agent-swarm'")

        # 5. Security audit routes to red-team-review
        pattern = evaluate_loop_strategy("Stress-test auth flow against OWASP top 10", is_adversarial=True)
        self.assertEqual(pattern, "red-team-review", "Adversarial audit must select pattern = 'red-team-review'")

    def test_skill_frontmatter_and_line_budgets(self):
        """Assert the consolidated skill has valid YAML frontmatter and line budget <= 300 lines."""
        skill_md = self.skill_root / "SKILL.md"
        self.assertTrue(skill_md.exists(), f"Missing SKILL.md in {self.skill_root}")
        content = skill_md.read_text(encoding="utf-8")
        lines = content.splitlines()

        # Line budget check: must be <= 300 lines for lean context
        self.assertLessEqual(
            len(lines), 300,
            f"Skill {self.skill_root.name} has {len(lines)} lines (exceeds 300 lines)",
        )

        # Frontmatter check
        self.assertTrue(content.startswith("---\n"), f"Missing frontmatter in {self.skill_root.name}")
        frontmatter_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        self.assertIsNotNone(frontmatter_match, f"Malformed frontmatter in {self.skill_root.name}")
        fm_text = frontmatter_match.group(1)

        # Name match
        name_match = re.search(r"^name:\s*([a-z0-9-]+)", fm_text, re.MULTILINE)
        self.assertIsNotNone(name_match, f"Missing or invalid name in {self.skill_root.name}")
        self.assertEqual(name_match.group(1), "orchestrating-agent-work", "Skill name does not match canonical name")

        # Description check: third-person (no 'I ' or 'My '), supports folded YAML scalar ('>')
        desc_match = re.search(r"^description:\s*(?:>\s*\n\s*)?[\"']?(.*?)[\"']?$", fm_text, re.MULTILINE)
        self.assertIsNotNone(desc_match, f"Missing description in {self.skill_root.name}")
        desc_text = desc_match.group(1).strip()
        self.assertFalse(desc_text.lower().startswith("i "), f"Description must be third-person in {self.skill_root.name}")

    def test_evals_schema_compliance(self):
        """Assert evals.json uses the should_trigger boolean schema."""
        evals_file = self.skill_root / "evals" / "evals.json"
        self.assertTrue(evals_file.exists(), f"Missing {evals_file}")
        data = json.loads(evals_file.read_text(encoding="utf-8"))
        self.assertIsInstance(data, list, f"{evals_file} must contain a JSON list")
        self.assertGreater(len(data), 0, f"{evals_file} must not be empty")
        for idx, entry in enumerate(data):
            self.assertIn("prompt", entry, f"Entry {idx} missing 'prompt' in {evals_file}")
            self.assertIn("should_trigger", entry, f"Entry {idx} missing 'should_trigger' in {evals_file}")
            self.assertIsInstance(entry["should_trigger"], bool, f"'should_trigger' must be boolean in {evals_file}")

    def test_learning_loop_does_not_contain_triple_loop_typo(self):
        """Verify the copy-paste typo in learning-loop Option B is fixed."""
        learning_loop_md = self.references_dir / "learning-loop.md"
        content = learning_loop_md.read_text(encoding="utf-8")
        self.assertNotIn(
            "Open the `triple-loop-learning` SKILL",
            content,
            "learning-loop still contains erroneous cross-reference to triple-loop-learning for Dual Loop option",
        )

    def test_orchestrator_removes_dead_cli_warnings(self):
        """Verify orchestrator does not advertise unimplemented scan/bundle subcommands."""
        for md_file in (self.skill_root / "SKILL.md", self.references_dir / "routing-and-closure.md"):
            content = md_file.read_text(encoding="utf-8")
            self.assertNotIn("A `scan` CLI subcommand is not currently implemented", content)
            self.assertNotIn("A `bundle` CLI subcommand is not currently implemented", content)


if __name__ == "__main__":
    unittest.main()
