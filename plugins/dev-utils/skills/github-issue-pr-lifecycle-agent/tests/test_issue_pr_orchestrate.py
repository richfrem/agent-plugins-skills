"""Unit tests for issue PR lifecycle orchestration script.

Purpose:
    Verifies dry-run payload generation and execution steps for issue PR lifecycle:
    Issue -> Worktree -> PR -> Close resolution.

Key Input Dependencies:
    - unittest.mock.patch for subprocess.run calls
"""

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from issue_pr_orchestrate import (
    orchestrate_lifecycle,
    generate_lifecycle_payload,
)


class TestIssuePROrchestrate(unittest.TestCase):
    """Tests for issue PR lifecycle orchestration."""

    def test_generate_lifecycle_payload(self) -> None:
        """Test dry-run payload generation for issue PR lifecycle."""
        payload = generate_lifecycle_payload(
            issue_number=42,
            title="Fix login bug",
            body="Resolves crash on empty password",
            base_branch="main",
            draft=True,
        )
        self.assertEqual(payload["issue_number"], 42)
        self.assertEqual(payload["worktree_path"], ".worktrees/issue-42")
        self.assertEqual(payload["branch_name"], "issue-42")
        self.assertIn("Fix login bug", payload["pr_title"])
        self.assertIn("Closes #42", payload["pr_body"])
        self.assertTrue(payload["draft"])

    @patch("subprocess.run")
    def test_orchestrate_lifecycle_dry_run(self, mock_run: MagicMock) -> None:
        """Test orchestrate_lifecycle in dry-run mode (no subprocess calls)."""
        result = orchestrate_lifecycle(
            issue_number=42,
            title="Fix login bug",
            body="Resolves crash on empty password",
            dry_run=True,
        )
        mock_run.assert_not_called()
        self.assertTrue(result["success"])
        self.assertTrue(result["dry_run"])
        self.assertIn("payload", result)

    @patch("subprocess.run")
    def test_orchestrate_lifecycle_full_execution(self, mock_run: MagicMock) -> None:
        """Test orchestrate_lifecycle with full subprocess execution mocks."""
        # Setup mock return values for sequence of subprocess.run calls:
        # 1. worktree add
        # 2. gh pr create
        # 3. gh issue close
        # 4. worktree remove
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Success"
        mock_proc.stderr = ""
        mock_run.returncode = 0
        mock_run.return_value = mock_proc

        result = orchestrate_lifecycle(
            issue_number=42,
            title="Fix login bug",
            body="Resolves crash on empty password",
            dry_run=False,
        )

        self.assertTrue(result["success"])
        self.assertEqual(mock_run.call_count, 4)


if __name__ == "__main__":
    unittest.main()
