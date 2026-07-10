# -*- coding: utf-8 -*-
"""
test_scaffold_github_agent.py
=====================================
Unit and integration tests for scaffold_github_agent, gh_agent_templates,
and validate_github_agent scripts.
"""

import os
import sys
import unittest
import tempfile
import json
from pathlib import Path
import yaml

# Resolve imports cleanly from the real directory (resolving symlinks)
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import gh_agent_templates as templates
import validate_github_agent as validator
import scaffold_github_agent as scaffolder


class TestGHAgentTemplates(unittest.TestCase):

    def test_target_a_template(self):
        result = templates.agent_md_github(
            name="test-agent",
            description="Test Target A description: containing colons",
            body="Step 1: Run checks",
            target="both"
        )
        # Parse the result as frontmatter and body to avoid raw string dump search fragility
        fm, body = validator.parse_frontmatter(result)
        self.assertEqual(fm["description"], "Test Target A description: containing colons")
        self.assertEqual(fm["name"], "test-agent")
        self.assertEqual(fm["target"], "both")
        self.assertEqual(body.strip(), "Step 1: Run checks")

    def test_target_b_template(self):
        result = templates.gh_aw_workflow_md(
            name="test-workflow",
            description="Test Target B description",
            instructions="Run workflow",
            on_trigger={"schedule": "daily"},
            engine="copilot"
        )
        fm, body = validator.parse_frontmatter(result)
        self.assertEqual(fm["engine"], "copilot")
        self.assertEqual(fm["on"], {"schedule": "daily"})
        self.assertIn("Run workflow", body)

    def test_target_c_template(self):
        result = templates.smart_failure_agent_md(
            name="test-fail",
            description="Test Target C description",
            instructions="Audit repository",
            kill_switch="FAILED_MERGE"
        )
        fm, body = validator.parse_frontmatter(result)
        self.assertIn("FAILED_MERGE", body)
        self.assertIn("Escalation Trigger Taxonomy", body)


class TestGHAgentValidator(unittest.TestCase):

    def test_validate_target_a_missing_desc(self):
        fm = {"name": "test-agent"}
        body = "body content"
        errors = validator.validate_target_a(fm, body)
        self.assertTrue(any("description" in err for err in errors))

    def test_validate_target_b_missing_on(self):
        fm = {"engine": "copilot"}
        body = "body content"
        errors = validator.validate_target_b(fm, body)
        self.assertTrue(any("on" in err for err in errors))

    def test_validate_target_b_boolean_on_trap(self):
        # YAML 1.1 round-trip: "on:" loads as boolean True
        # Parse frontmatter should normalize True -> "on"
        raw_yaml = "---\non:\n  push:\n    branches: [main]\nengine: copilot\n---\nbody content"
        fm, body = validator.parse_frontmatter(raw_yaml)
        self.assertIn("on", fm)
        self.assertEqual(fm["on"], {"push": {"branches": ["main"]}})

    def test_validate_target_c_missing_kill_switch(self):
        fm = {"name": "test"}
        body = "escalation trigger taxonomy"
        errors = validator.validate_target_c(fm, body, kill_switch="KILL")
        self.assertTrue(any("kill" in err.lower() for err in errors))

    def test_validate_target_c_case_insensitive(self):
        # Should pass even if case differs
        fm = {"name": "test"}
        body = "ESCALATION TRIGGER TAXONOMY\nkill switch: FAILED_TEST"
        errors = validator.validate_target_c(fm, body, kill_switch="failed_test")
        self.assertEqual(len(errors), 0)


class TestGHAgentScaffolder(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_scaffold_target_a_writes_files(self):
        sys_argv_backup = sys.argv
        sys.argv = [
            "scaffold_github_agent.py",
            "--target", "A",
            "--name", "my-copilot-agent",
            "--description", "My desc",
            "--output-dir", str(self.output_path)
        ]
        
        from io import StringIO
        stdout_backup = sys.stdout
        sys.stdout = StringIO()
        
        try:
            scaffolder.main()
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = stdout_backup
            sys.argv = sys_argv_backup

        manifest = json.loads(output)
        self.assertEqual(manifest["status"], "success")
        
        agent_file = self.output_path / ".github" / "agents" / "my-copilot-agent.agent.md"
        prompt_file = self.output_path / ".github" / "prompts" / "my-copilot-agent.prompt.md"
        
        self.assertTrue(agent_file.exists())
        self.assertTrue(prompt_file.exists())

    def test_scaffold_target_b_writes_files_and_validates(self):
        sys_argv_backup = sys.argv
        sys.argv = [
            "scaffold_github_agent.py",
            "--target", "B",
            "--name", "my-gh-aw-workflow",
            "--description", "My gh-aw workflow desc",
            "--triggers", "push", "pull_request",
            "--output-dir", str(self.output_path)
        ]
        
        from io import StringIO
        stdout_backup = sys.stdout
        sys.stdout = StringIO()
        
        try:
            scaffolder.main()
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = stdout_backup
            sys.argv = sys_argv_backup

        manifest = json.loads(output)
        self.assertEqual(manifest["status"], "success")
        
        workflow_file = self.output_path / ".github" / "workflows" / "my-gh-aw-workflow.md"
        self.assertTrue(workflow_file.exists())

        # Test validate round-trip validation
        fm, body = validator.parse_frontmatter(workflow_file.read_text(encoding="utf-8"))
        errors = validator.validate_target_b(fm, body)
        self.assertEqual(len(errors), 0)

    def test_scaffold_target_c_writes_files_and_validates(self):
        sys_argv_backup = sys.argv
        sys.argv = [
            "scaffold_github_agent.py",
            "--target", "C",
            "--name", "my-smart-fail",
            "--description", "My CI fail gate",
            "--kill-switch", "STOP_EXECUTION",
            "--output-dir", str(self.output_path)
        ]
        
        from io import StringIO
        stdout_backup = sys.stdout
        sys.stdout = StringIO()
        
        try:
            scaffolder.main()
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = stdout_backup
            sys.argv = sys_argv_backup

        manifest = json.loads(output)
        self.assertEqual(manifest["status"], "success")
        
        agent_file = self.output_path / ".github" / "agents" / "my-smart-fail.agent.md"
        runner_file = self.output_path / ".github" / "workflows" / "my-smart-fail-agent.yml"
        
        self.assertTrue(agent_file.exists())
        self.assertTrue(runner_file.exists())

        # Validate agent files
        fm, body = validator.parse_frontmatter(agent_file.read_text(encoding="utf-8"))
        errors = validator.validate_target_c(fm, body, kill_switch="STOP_EXECUTION")
        self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    unittest.main()
