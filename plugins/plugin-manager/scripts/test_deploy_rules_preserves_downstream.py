#!/usr/bin/env python
"""
test_deploy_rules_preserves_downstream.py
=====================================

Purpose:
    Regression tests for deploy_rules() in plugin_installer.py. Covers two
    incidents:
    1. (2026-09-05) A plugin sync silently overwrote a newer,
       already-updated .agent/rules/git-operations.md with the plugin's stale
       rules/ source copy via a blind shutil.copy2(). deploy_rules() must
       merge-preserve newer downstream content instead of blind-copying over it.
    2. (2026-09-05, reported from a downstream consumer repo) The rule naming
       scheme changed from `<plugin>_<rule>.md` (pre-#502) to bare
       `<rule>.md` (#502+), but deploy_rules() never cleaned up the old
       prefixed file — leaving both the legacy prefixed copy and the new bare
       copy present simultaneously with divergent content. deploy_rules()
       must detect the legacy prefixed filename for a rule it's about to
       write under the bare name, merge any unique content from it into the
       canonical bare-name file, then remove the now-fully-superseded legacy
       file.

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
    """Reproduce the deploy_rules() clobber and assert the merge-preserving fix holds."""
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


def run_legacy_prefix_migration() -> None:
    """Reproduce the InvestmentToolkit orphan report: legacy `<plugin>_<rule>.md` must
    be merged into the bare-name file and removed, not left behind as a duplicate."""
    tmp = Path(tempfile.mkdtemp(prefix="deploy_rules_legacy_test_"))
    try:
        plugin_path = tmp / "plugins" / "dev-utils"
        rules_dir = plugin_path / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "coding-conventions.md").write_text(
            "# Coding Conventions\n\nOrigin content.\n", encoding="utf-8"
        )

        central_rules = tmp / ".agent" / "rules"
        central_rules.mkdir(parents=True)
        legacy_path = central_rules / "dev-utils_coding-conventions.md"
        legacy_path.write_text(
            "# Coding Conventions\n\nOrigin content.\n\n### Custom Team Addition\nNever skip this.\n",
            encoding="utf-8",
        )

        deploy_rules(plugin_path, "dev-utils", targets=[], root=tmp, dry_run=False)

        bare_path = central_rules / "coding-conventions.md"
        if not bare_path.exists():
            print("FAIL: deploy_rules() did not write the canonical bare-name file")
            sys.exit(1)

        bare_content = bare_path.read_text(encoding="utf-8")
        if "Custom Team Addition" not in bare_content:
            print("FAIL: deploy_rules() did not migrate the legacy prefixed file's unique content")
            print(f"  Bare-name content: {bare_content!r}")
            sys.exit(1)

        if legacy_path.exists():
            print("FAIL: deploy_rules() left the legacy prefixed orphan file behind after migration")
            sys.exit(1)

        print("PASS: deploy_rules() migrated legacy prefixed rule content and removed the orphan")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def run_orphan_cleanup_for_removed_rule() -> None:
    """Reproduce the InvestmentToolkit follow-up report: when a rule is fully removed
    from a plugin (not renamed — genuinely deleted), its legacy prefixed orphan is
    never visited by the rules_dir.glob() loop and never cleaned up. deploy_rules()
    must still detect and migrate/remove it via a second, plugin-wide orphan pass."""
    tmp = Path(tempfile.mkdtemp(prefix="deploy_rules_orphan_test_"))
    try:
        plugin_path = tmp / "plugins" / "agent-scaffolders"
        rules_dir = plugin_path / "rules"
        rules_dir.mkdir(parents=True)
        # Plugin still ships one rule (unrelated to the removed one)
        (rules_dir / "plugin-architecture-policy.md").write_text(
            "# Plugin Architecture Policy\n\nContent.\n", encoding="utf-8"
        )

        central_rules = tmp / ".agent" / "rules"
        central_rules.mkdir(parents=True)

        # Case A: rule fully removed, but a bare-name file exists with unique content
        legacy_a = central_rules / "agent-scaffolders_skill-deletion-guard.md"
        legacy_a.write_text(
            "# Skill Deletion Guard\n\nOrigin content.\n\n### Team Note\nDo not skip.\n",
            encoding="utf-8",
        )
        bare_a = central_rules / "skill-deletion-guard.md"
        bare_a.write_text("# Skill Deletion Guard\n\nOrigin content.\n", encoding="utf-8")

        # Case B: rule fully removed, no bare-name file exists at all
        legacy_b = central_rules / "agent-scaffolders_pre-push-audit.md"
        legacy_b.write_text("# Pre-Push Audit\n\nStale, fully dropped.\n", encoding="utf-8")

        deploy_rules(plugin_path, "agent-scaffolders", targets=[], root=tmp, dry_run=False)

        if legacy_a.exists():
            print("FAIL: Case A legacy orphan (with existing bare-name twin) was not removed")
            sys.exit(1)
        merged_a = bare_a.read_text(encoding="utf-8")
        if "Team Note" not in merged_a:
            print("FAIL: Case A legacy orphan's unique content was not migrated into the bare-name file")
            sys.exit(1)

        if legacy_b.exists():
            print("FAIL: Case B legacy orphan (no bare-name twin, rule fully dropped) was not removed")
            sys.exit(1)

        print("PASS: deploy_rules() cleaned up orphans for rules removed entirely from the plugin")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    run()
    run_legacy_prefix_migration()
    run_orphan_cleanup_for_removed_rule()
