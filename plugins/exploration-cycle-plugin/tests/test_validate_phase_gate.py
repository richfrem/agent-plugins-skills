#!/usr/bin/env python3
"""
test_validate_phase_gate.py
=====================================
Purpose:
    Test suite for validate_phase_gate.py validator. Covers Phase 1-4 gate
    checks (missing artifacts, size thresholds, placeholder detection,
    missing section headers, session title/mismatch checks) via subprocess
    invocation of the real validator script against temporary fixtures.

Key Input Dependencies:
    - validate_phase_gate.py (in ../scripts/, invoked as a subprocess)
    - Temporary project directory with exploration/ subdirectory structure
"""
import unittest
import tempfile
import shutil
import os
from pathlib import Path
import sys

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
VALIDATOR_PATH = SCRIPTS_DIR / "validate_phase_gate.py"

class TestValidatePhaseGate(unittest.TestCase):
    def setUp(self):
        """Create a temporary project directory with a fresh exploration-dashboard.md."""
        # Create a temporary project directory structure
        self.test_dir = Path(tempfile.mkdtemp())
        self.exploration_dir = self.test_dir / "exploration"
        self.exploration_dir.mkdir()

        self.dashboard_path = self.exploration_dir / "exploration-dashboard.md"
        self.write_dashboard("My Test Session")

        # Override CLAUDE_PROJECT_DIR environment variable for the subprocess calls
        self.env = os.environ.copy()
        self.env["CLAUDE_PROJECT_DIR"] = str(self.test_dir)

    def tearDown(self):
        """Remove the temporary project directory."""
        # Clean up temporary directories
        shutil.rmtree(self.test_dir)

    def write_dashboard(self, session_name: str):
        """Write an exploration-dashboard.md fixture with the given session name."""
        content = f"""# Exploration Session Dashboard

**Session:** {session_name}
**Session Type:** Greenfield
**Status:** In Progress
**Current Phase:** Phase 1 — Problem Framing
"""
        self.dashboard_path.write_text(content, encoding="utf-8")

    def run_validator(self, phase: int) -> tuple[int, str, str]:
        """Run validate_phase_gate.py as a subprocess for the given phase and return (code, stdout, stderr)."""
        import subprocess
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), str(phase)],
            cwd=str(self.test_dir),
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return proc.returncode, proc.stdout, proc.stderr

    def test_phase_1_missing_plan(self):
        """Verify Phase 1 fails when no Discovery Plan document exists."""
        # Phase 1: no plans directory or md files exist
        code, out, err = self.run_validator(1)
        self.assertEqual(code, 1)
        self.assertIn("No Discovery Plan document found", err)

    def test_phase_1_too_short(self):
        """Verify Phase 1 fails when the Discovery Plan is below the minimum size."""
        plans_dir = self.exploration_dir / "discovery-plans"
        plans_dir.mkdir()
        plan_file = plans_dir / "discovery-plan-2026-06-08.md"
        plan_file.write_text("Short plan", encoding="utf-8")

        code, out, err = self.run_validator(1)
        self.assertEqual(code, 1)
        self.assertIn("is too short", err)

    def test_phase_1_has_placeholder(self):
        """Verify Phase 1 fails when the Discovery Plan contains an unresolved placeholder."""
        plans_dir = self.exploration_dir / "discovery-plans"
        plans_dir.mkdir()
        plan_file = plans_dir / "discovery-plan-2026-06-08.md"
        plan_file.write_text("## Problem Statement\n## Success Criteria\n## Must-Have Requirements\nTODO: fill in later. This is long enough to pass size checks but contains a placeholder word.", encoding="utf-8")

        code, out, err = self.run_validator(1)
        self.assertEqual(code, 1)
        self.assertIn("contains unresolved placeholder", err)

    def test_phase_1_missing_headers(self):
        """Verify Phase 1 fails when the Discovery Plan is missing mandatory section headers."""
        plans_dir = self.exploration_dir / "discovery-plans"
        plans_dir.mkdir()
        plan_file = plans_dir / "discovery-plan-2026-06-08.md"
        plan_file.write_text("This plan is long enough to pass the size requirement, but is missing all the mandatory section headers. Let's make sure it contains no placeholders to isolate missing headers check.", encoding="utf-8")

        code, out, err = self.run_validator(1)
        self.assertEqual(code, 1)
        self.assertIn("Discovery Plan is missing sections", err)

    def test_phase_1_success(self):
        """Verify Phase 1 passes with a complete, well-sized Discovery Plan."""
        plans_dir = self.exploration_dir / "discovery-plans"
        plans_dir.mkdir()
        plan_file = plans_dir / "discovery-plan-2026-06-08.md"
        plan_file.write_text("## Problem Statement\nOur problem is scheduling.\n\n## Success Criteria\nSuccess is easy shifts.\n\n## Must-Have Requirements\nMust track users and times. This is long enough to pass the minimum file size check without issues.", encoding="utf-8")

        code, out, err = self.run_validator(1)
        self.assertEqual(code, 0)
        self.assertIn("SUCCESS: Phase 1 Validated", out)

    def test_phase_2_missing_blueprints(self):
        """Verify Phase 2 fails when no visual layout or document structure artifact exists."""
        code, out, err = self.run_validator(2)
        self.assertEqual(code, 1)
        self.assertIn("No visual layout or document structure artifact found", err)

    def test_phase_2_success(self):
        """Verify Phase 2 passes with a complete, well-sized layout blueprint."""
        captures_dir = self.exploration_dir / "captures"
        captures_dir.mkdir()
        blueprint = captures_dir / "layout-direction.md"
        blueprint.write_text("## Layout Direction\nThis is the layout for our application dashboard. It has navigation panel, main work pane, and status indicators. Long enough to pass size check.", encoding="utf-8")

        code, out, err = self.run_validator(2)
        self.assertEqual(code, 0)
        self.assertIn("SUCCESS: Phase 2 Validated", out)

    def test_phase_3_missing_prototype_files(self):
        """Verify Phase 3 fails when no prototype README exists."""
        code, out, err = self.run_validator(3)
        self.assertEqual(code, 1)
        self.assertIn("Prototype README error", err)

    def test_phase_3_success(self):
        """Verify Phase 3 passes with a complete prototype README, index.html, and notes."""
        prototype_dir = self.exploration_dir / "prototype"
        prototype_dir.mkdir()
        readme = prototype_dir / "README.md"
        readme.write_text("## Prototype README\nThis prototype demonstrates scheduling shifts. Run it with npm run dev. It matches the requirements. Long enough to pass size checks.", encoding="utf-8")

        index_html = prototype_dir / "index.html"
        index_html.write_text("<!DOCTYPE html><html><body><h1>Prototype</h1><p>This is the prototype landing page for Greenfield session. It is long enough to pass size validation.</p></body></html>", encoding="utf-8")

        captures_dir = self.exploration_dir / "captures"
        if not captures_dir.exists():
            captures_dir.mkdir()
        notes = captures_dir / "prototype-notes.md"
        notes.write_text("## Prototype Notes\nObservations: user is happy with layout. Feedback: add shift swap functionality. Tested and verified in dev. Long enough to pass size checks.", encoding="utf-8")

        code, out, err = self.run_validator(3)
        self.assertEqual(code, 0)
        self.assertIn("SUCCESS: Phase 3 Validated", out)

    def test_phase_3_greenfield_missing_index(self):
        """Verify Phase 3 fails for Greenfield sessions when index.html is missing."""
        prototype_dir = self.exploration_dir / "prototype"
        prototype_dir.mkdir()
        readme = prototype_dir / "README.md"
        readme.write_text("## Prototype README\nThis prototype demonstrates scheduling shifts. Run it with npm run dev. It matches the requirements. Long enough to pass size checks.", encoding="utf-8")

        captures_dir = self.exploration_dir / "captures"
        if not captures_dir.exists():
            captures_dir.mkdir()
        notes = captures_dir / "prototype-notes.md"
        notes.write_text("## Prototype Notes\nObservations: user is happy with layout. Feedback: add shift swap functionality. Tested and verified in dev. Long enough to pass size checks.", encoding="utf-8")

        code, out, err = self.run_validator(3)
        self.assertEqual(code, 1)
        self.assertIn("index.html error", err)

    def test_phase_4_missing_handoff(self):
        """Verify Phase 4 fails when handoff-package.md is missing."""
        code, out, err = self.run_validator(4)
        self.assertEqual(code, 1)
        self.assertIn("handoff-package.md is missing", err)

    def test_phase_4_mismatched_title(self):
        """Verify Phase 4 fails when the handoff package references a different session name."""
        handoffs_dir = self.exploration_dir / "handoffs"
        handoffs_dir.mkdir()
        handoff = handoffs_dir / "handoff-package.md"
        handoff.write_text("## Risk Assessment\n**Tier:** 2\nThis handoff package contains all details, but references 'Some Other Session' name, which will cause session title alignment check to fail.", encoding="utf-8")

        code, out, err = self.run_validator(4)
        self.assertEqual(code, 1)
        self.assertIn("Handoff package session mismatch", err)

    def test_phase_4_success(self):
        """Verify Phase 4 passes with a complete, correctly-titled handoff package."""
        handoffs_dir = self.exploration_dir / "handoffs"
        handoffs_dir.mkdir()
        handoff = handoffs_dir / "handoff-package.md"
        handoff.write_text("## Risk Assessment\n**Tier:** 2\nThis is the handoff package for My Test Session. It contains all requirements, prototype outcomes, and deployment strategies. Fully verified.", encoding="utf-8")

        code, out, err = self.run_validator(4)
        self.assertEqual(code, 0)
        self.assertIn("SUCCESS: Phase 4 Validated", out)

if __name__ == "__main__":
    unittest.main()
