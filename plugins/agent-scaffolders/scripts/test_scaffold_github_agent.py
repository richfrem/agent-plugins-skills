# -*- coding: utf-8 -*-
"""
Purpose:
    Unit and integration tests for scaffold_github_agent, gh_agent_templates,
    and validate_github_agent scripts. Tests cover template generation, validation,
    and scaffolding workflows for GitHub agents (Targets A, B, and C).

Key Input Dependencies:
    - scaffold_github_agent.py module
    - gh_agent_templates.py module
    - validate_github_agent.py module

Key Functions:
    - None (this is a test module with test methods only)
"""

import os
import sys
import unittest
import tempfile
import json
from pathlib import Path

# Resolve imports cleanly from the real directory (resolving symlinks)
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import gh_agent_templates as templates
import validate_github_agent as validator
import scaffold_github_agent as scaffolder


class TestGHAgentTemplates(unittest.TestCase):

    def test_target_a_template(self):
        """Verify agent_md_github template generation for Target A."""
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
        """Verify gh_aw_workflow_md template generation for Target B."""
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
        """Verify smart_failure_agent_md template generation for Target C."""
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
        """Verify validation fails when description is missing for Target A."""
        fm = {"name": "test-agent"}
        body = "body content"
        errors = validator.validate_target_a(fm, body)
        self.assertTrue(any("description" in err for err in errors))

    def test_validate_target_b_missing_on(self):
        """Verify validation fails when 'on' trigger key is missing for Target B."""
        fm = {"engine": "copilot"}
        body = "body content"
        errors = validator.validate_target_b(fm, body)
        self.assertTrue(any("on" in err for err in errors))

    def test_validate_target_b_boolean_on_trap(self):
        """Verify YAML 1.1 round-trip normalizes boolean 'on' to proper dict structure."""
        # YAML 1.1 round-trip: "on:" loads as boolean True
        # Parse frontmatter should normalize True -> "on"
        raw_yaml = "---\non:\n  push:\n    branches: [main]\nengine: copilot\n---\nbody content"
        fm, body = validator.parse_frontmatter(raw_yaml)
        self.assertIn("on", fm)
        self.assertEqual(fm["on"], {"push": {"branches": ["main"]}})

    def test_validate_target_c_missing_kill_switch(self):
        """Verify validation fails when kill switch value is missing for Target C."""
        fm = {"name": "test"}
        body = "escalation trigger taxonomy"
        errors = validator.validate_target_c(fm, body, kill_switch="KILL")
        self.assertTrue(any("kill" in err.lower() for err in errors))

    def test_validate_target_c_case_insensitive(self):
        """Verify kill switch validation is case-insensitive for Target C."""
        # Should pass even if case differs
        fm = {"name": "test"}
        body = "ESCALATION TRIGGER TAXONOMY\nkill switch: FAILED_TEST"
        errors = validator.validate_target_c(fm, body, kill_switch="failed_test")
        self.assertEqual(len(errors), 0)


class TestGHAgentScaffolder(unittest.TestCase):

    def setUp(self):
        """Create a temporary directory for test output."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary directory after test."""
        self.temp_dir.cleanup()

    def test_scaffold_target_a_writes_files(self):
        """Verify Target A scaffolding creates agent and prompt files."""
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
        """Verify Target B scaffolding creates workflow file and passes validation."""
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
        raw_content = workflow_file.read_text(encoding="utf-8")
        self.assertTrue(any(q in raw_content for q in ("'on':", '"on":')))  # Proves the YAML quoting fix at the generation level
        
        fm, body = validator.parse_frontmatter(raw_content)
        self.assertIn("on", fm)
        self.assertIsInstance(fm["on"], dict)
        errors = validator.validate_target_b(fm, body)
        self.assertEqual(len(errors), 0)

    def test_scaffold_target_c_writes_files_and_validates(self):
        """Verify Target C scaffolding creates agent and runner files with kill switch."""
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
        agent_content = agent_file.read_text(encoding="utf-8")
        self.assertIn("STOP_EXECUTION", agent_content)  # Verifies kill switch is present verbatim
        self.assertIn("Escalation Trigger Taxonomy", agent_content)

        fm, body = validator.parse_frontmatter(agent_content)
        errors = validator.validate_target_c(fm, body, kill_switch="STOP_EXECUTION")
        self.assertEqual(len(errors), 0)

    def test_tools_flag_empty_list(self):
        """Verify --tools flag correctly handles empty list and single tool values."""
        sys_argv_backup = sys.argv
        from io import StringIO
        stdout_backup = sys.stdout
        
        sys.argv = [
            "scaffold_github_agent.py",
            "--target", "A",
            "--name", "test-no-tools",
            "--description", "No tools test",
            "--tools", "",
            "--output-dir", str(self.output_path),
            "--force"
        ]
        try:
            sys.stdout = StringIO()
            scaffolder.main()
        finally:
            sys.stdout = stdout_backup
            sys.argv = sys_argv_backup

        agent_file = self.output_path / ".github" / "agents" / "test-no-tools.agent.md"
        self.assertTrue(agent_file.exists())
        content = agent_file.read_text(encoding="utf-8")
        fm, body = validator.parse_frontmatter(content)
        self.assertEqual(fm.get("tools"), [])

        sys.argv = [
            "scaffold_github_agent.py",
            "--target", "A",
            "--name", "test-some-tools",
            "--description", "Some tools test",
            "--tools", "github",
            "--output-dir", str(self.output_path),
            "--force"
        ]
        try:
            sys.stdout = StringIO()
            scaffolder.main()
        finally:
            sys.stdout = stdout_backup
            sys.argv = sys_argv_backup

        agent_file = self.output_path / ".github" / "agents" / "test-some-tools.agent.md"
        self.assertTrue(agent_file.exists())
        content = agent_file.read_text(encoding="utf-8")
        fm, body = validator.parse_frontmatter(content)
        self.assertEqual(fm.get("tools"), ["github"])

    def test_validator_rejects_skill_frontmatter_in_workflows(self):
        """Verify validator rejects SKILL.md frontmatter in workflow files."""
        skill_content = """---
name: create-agentic-workflow
argument-hint: "[skill-dir]"
allowed-tools: Bash, Read, Write
disable-model-invocation: false
---
Some body text
"""
        fm, body = validator.parse_frontmatter(skill_content)
        errors = validator.validate_target_b(fm, body, filepath_str="/path/to/.github/workflows/workflow.md")
        self.assertTrue(any("Skill-style frontmatter in .github/workflows/" in err for err in errors))

    def test_validator_rejects_ghaw_keys_in_agent_md(self):
        """Verify validator rejects GitHub Actions Workflow keys in agent files."""
        invalid_agent_content = """---
description: Test agent
on:
  schedule: daily
---
Some body
"""
        fm, body = validator.parse_frontmatter(invalid_agent_content)
        errors = validator.validate_target_a(fm, body)
        self.assertTrue(any("must not contain gh-aw keys" in err for err in errors))
        
        errors_c = validator.validate_target_c(fm, body, kill_switch="STOP")
        self.assertTrue(any("must not contain gh-aw keys" in err for err in errors_c))

    def test_scaffold_self_validates(self):
        """Verify scaffolder exits with error when generated files fail validation."""
        original_template = templates.agent_md_github
        templates.agent_md_github = lambda **kwargs: "---\ndescription: Test\non:\n  push: {}\n---\n"
        
        sys_argv_backup = sys.argv
        sys.argv = [
            "scaffold_github_agent.py",
            "--target", "A",
            "--name", "invalid-self-val",
            "--output-dir", str(self.output_path),
            "--force"
        ]
        
        try:
            with self.assertRaises(SystemExit) as cm:
                scaffolder.main()
            self.assertEqual(cm.exception.code, 1)
        finally:
            templates.agent_md_github = original_template
            sys.argv = sys_argv_backup


if __name__ == "__main__":
    unittest.main()
