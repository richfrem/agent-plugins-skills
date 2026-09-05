#!/usr/bin/env python
"""
test_deploy_rules_preserves_downstream.py
=====================================

Purpose:
    Regression test for deploy_rules() in plugin_installer.py. Reproduces the
    2026-09-05 incident where a plugin sync silently overwrote a newer,
    already-updated .agent/rules/git-operations.md with the plugin's stale
    rules/ source copy via a blind shutil.copy2(). Asserts deploy_rules()
    merge-preserves newer downstream content in .agent/rules/ instead of
    blind-copying over it.

Key Input Dependencies:
    plugins/plugin-manager/scripts/plugin_installer.py — deploy_rules() under test

Layer: Development / Testing

Usage:
    python plugins/plugin-manager/scripts/test_deploy_rules_preserves_downstream.py
"""

import sys
import shutil
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plugin_installer import deploy_rules  # noqa: E402


def run() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="deploy_rules_test_"))
    try:
        plugin_path = tmp / "plugins" / "dev-utils"
        rules_dir = plugin_path / "rules"
        rules_dir.mkdir(parents=True)

        stale_content = "# Git Operations Policy\n\nOld rule text.\n"
        (rules_dir / "git-operations.md").write_text(stale_content, encoding="utf-8")

        central_rules = tmp / ".agent" / "rules"
        central_rules.mkdir(parents=True)
        newer_content = "# Git Operations Policy\n\nOld rule text.\n\n### 7. New Rule Added Today\nDo not clobber.\n"
        (central_rules / "git-operations.md").write_text(newer_content, encoding="utf-8")

        deploy_rules(plugin_path, "dev-utils", targets=[], root=tmp, dry_run=False)

        result = (central_rules / "git-operations.md").read_text(encoding="utf-8")

        if "New Rule Added Today" not in result:
            print("FAIL: deploy_rules() clobbered newer downstream .agent/rules/ content with stale plugin source")
            print(f"  Expected to find 'New Rule Added Today' preserved in: {result!r}")
            sys.exit(1)

        print("PASS: deploy_rules() preserved newer downstream .agent/rules/ content")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    run()
