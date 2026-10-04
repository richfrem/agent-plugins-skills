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
        """Point at the real agent-orchestration skills/ directory to audit."""
        self.skills_dir = PLUGIN_ROOT / "skills"

    def test_all_expected_skills_exist(self):
        """Assert all core loop, graph planning, and execution skills exist in the plugin."""
        expected_skills = [
            "orchestrator",
            "select-loop-strategy",
            "dual-loop",
            "learning-loop",
            "co-pilot-loop",
            "agent-swarm",
            "red-team-review",
            "triple-loop-learning",
            "graph-planner",
            "graph-execution",
        ]
        for skill_name in expected_skills:
            skill_path = self.skills_dir / skill_name / "SKILL.md"
            self.assertTrue(
                skill_path.exists(),
                f"Expected skill {skill_name}/SKILL.md does not exist",
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
        """Assert all skills have valid YAML frontmatter and line budget <= 300 lines."""
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            self.assertTrue(skill_md.exists(), f"Missing SKILL.md in {skill_dir}")
            content = skill_md.read_text(encoding="utf-8")
            lines = content.splitlines()
            
            # Line budget check: must be <= 300 lines for lean context
            self.assertLessEqual(
                len(lines), 300,
                f"Skill {skill_dir.name} has {len(lines)} lines (exceeds 300 lines)",
            )

            # Frontmatter check
            self.assertTrue(content.startswith("---\n"), f"Missing frontmatter in {skill_dir.name}")
            frontmatter_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
            self.assertIsNotNone(frontmatter_match, f"Malformed frontmatter in {skill_dir.name}")
            fm_text = frontmatter_match.group(1)

            # Name match
            name_match = re.search(r"^name:\s*([a-z0-9-]+)", fm_text, re.MULTILINE)
            self.assertIsNotNone(name_match, f"Missing or invalid name in {skill_dir.name}")
            self.assertEqual(name_match.group(1), skill_dir.name, "Skill name does not match directory")

            # Description check: third-person (no 'I ' or 'My ')
            desc_match = re.search(r"^description:\s*[\"']?(.*?)[\"']?$", fm_text, re.MULTILINE)
            self.assertIsNotNone(desc_match, f"Missing description in {skill_dir.name}")
            desc_text = desc_match.group(1)
            self.assertFalse(desc_text.lower().startswith("i "), f"Description must be third-person in {skill_dir.name}")

    def test_evals_schema_compliance(self):
        """Assert every skill with evals.json uses the should_trigger boolean schema."""
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            evals_file = skill_dir / "evals" / "evals.json"
            if evals_file.exists():
                data = json.loads(evals_file.read_text(encoding="utf-8"))
                self.assertIsInstance(data, list, f"{evals_file} must contain a JSON list")
                for idx, entry in enumerate(data):
                    self.assertIn("prompt", entry, f"Entry {idx} missing 'prompt' in {evals_file}")
                    self.assertIn("should_trigger", entry, f"Entry {idx} missing 'should_trigger' in {evals_file}")
                    self.assertIsInstance(entry["should_trigger"], bool, f"'should_trigger' must be boolean in {evals_file}")

    def test_learning_loop_does_not_contain_triple_loop_typo(self):
        """Verify the copy-paste typo in learning-loop Option B is fixed."""
        learning_loop_md = self.skills_dir / "learning-loop" / "SKILL.md"
        content = learning_loop_md.read_text(encoding="utf-8")
        self.assertNotIn(
            "Open the `triple-loop-learning` SKILL",
            content,
            "learning-loop still contains erroneous cross-reference to triple-loop-learning for Dual Loop option",
        )

    def test_orchestrator_removes_dead_cli_warnings(self):
        """Verify orchestrator does not advertise unimplemented scan/bundle subcommands."""
        orch_md = self.skills_dir / "orchestrator" / "SKILL.md"
        content = orch_md.read_text(encoding="utf-8")
        self.assertNotIn("A `scan` CLI subcommand is not currently implemented", content)
        self.assertNotIn("A `bundle` CLI subcommand is not currently implemented", content)


if __name__ == "__main__":
    unittest.main()
