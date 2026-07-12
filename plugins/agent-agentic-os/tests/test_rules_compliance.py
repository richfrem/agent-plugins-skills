"""
Purpose:
    Unit tests verifying that .agent/rules/ contains only real files, never
    symlinks, since active rule files must be hard copies per policy.

Key Input Dependencies:
    - .agent/rules/ directory in the repo root
"""
import os
import unittest
from pathlib import Path

class TestRulesCompliance(unittest.TestCase):

    def test_no_symlinks_in_agent_rules(self):
        """Guarantee that the active rules folder (.agent/rules/) contains only real files, no symlinks."""
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        rules_dir = repo_root / ".agent" / "rules"
        
        # If rules_dir does not exist yet (e.g. fresh clone before rule copy), skip
        if not rules_dir.exists():
            self.skipTest(".agent/rules/ folder does not exist in this environment")

        for item in rules_dir.iterdir():
            if item.is_file():
                # os.path.islink checks for symbolic links
                is_symlink = item.is_symlink() or os.path.islink(str(item))
                if is_symlink:
                    target = os.readlink(str(item))
                    self.fail(f"Active rule file '{item.name}' must be a hard copy, but it is a symlink pointing to: {target}")

if __name__ == "__main__":
    unittest.main()
