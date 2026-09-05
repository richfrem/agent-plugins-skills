"""
test_evolution_guards.py — Automated Unit & Integration Tests for Evolution Guards
=================================================================================

Purpose:
    Verifies the pre-commit evolution guard and the Stop-hook turn evolution
    guard correctly block/pass commits per the Evolution Integrity Gate rules.

Tests:
1. pre-commit-evolution-guard (Git Hook)
   - Blocks commit when logic files changed without map-debt/wiki
   - Passes commit when map-debt.md is staged with valid schema (8 cols / 9 pipes)
   - Blocks commit when map-debt.md row is malformed (< 9 pipes)
   - Passes commit when wiki/playbook is staged
   - Passes commit when only docs or non-logic files are staged
2. turn_evolution_guard.py (Claude Code Stop Hook)
   - Runs cleanly without syntax error
   - Emits warning to stderr when logic modified without map-debt/wiki
   - Quiet when no logic files modified

Key Input Dependencies:
    - ../scripts/pre-commit-evolution-guard, ../hooks/scripts/turn_evolution_guard.py
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def temp_git_repo(tmp_path):
    """Create and return a freshly git-init'd throwaway repo for guard tests."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    return repo


def test_turn_evolution_guard_ast_valid():
    """turn_evolution_guard.py must parse as valid Python (no syntax errors)."""
    guard_script = Path(__file__).parent.parent / "hooks" / "scripts" / "turn_evolution_guard.py"
    assert guard_script.exists()
    import ast
    ast.parse(guard_script.read_text(encoding="utf-8"))


def test_pre_commit_guard_blocks_logic_without_docs(temp_git_repo):
    """Commit must be blocked when plugins/ logic changed with no map-debt/wiki staged."""
    guard_script = Path(__file__).parent.parent / "scripts" / "pre-commit-evolution-guard"
    
    # Create logic file in plugins/
    plugin_file = temp_git_repo / "plugins" / "my_plugin" / "service.py"
    plugin_file.parent.mkdir(parents=True)
    plugin_file.write_text("print('hello')", encoding="utf-8")
    
    subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
    
    res = subprocess.run([str(guard_script)], cwd=temp_git_repo, capture_output=True, text=True)
    assert res.returncode != 0
    assert "COMMIT BLOCKED: Core logic changed without Evolution & Map Debt logging!" in res.stdout


def test_pre_commit_guard_passes_with_valid_map_debt(temp_git_repo):
    """Commit must pass when a schema-valid map-debt.md row is staged alongside logic."""
    guard_script = Path(__file__).parent.parent / "scripts" / "pre-commit-evolution-guard"
    
    # Logic file
    plugin_file = temp_git_repo / "plugins" / "my_plugin" / "service.py"
    plugin_file.parent.mkdir(parents=True)
    plugin_file.write_text("print('hello')", encoding="utf-8")
    
    # Map debt file with valid 8 columns (9 pipes)
    debt_file = temp_git_repo / "references" / "map-debt.md"
    debt_file.parent.mkdir(parents=True)
    debt_file.write_text(
        "# Map Debt\n\n| ID | Title | Status | Severity | Repeat | First Seen | Description | Resolution Commit |\n"
        "|---|---|---|---|---|---|---|---|\n"
        "| DEBT-20260902-01 | Sample Debt | RESOLVED | Tier 0 | 1 | 2026-09-02 | Sample description | fix-commit |\n",
        encoding="utf-8"
    )
    
    subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
    
    res = subprocess.run([str(guard_script)], cwd=temp_git_repo, capture_output=True, text=True)
    assert res.returncode == 0


def test_pre_commit_guard_blocks_malformed_map_debt_row(temp_git_repo):
    """Commit must be blocked when a staged map-debt.md row has fewer than 9 pipes."""
    guard_script = Path(__file__).parent.parent / "scripts" / "pre-commit-evolution-guard"
    
    # Logic file
    plugin_file = temp_git_repo / "plugins" / "my_plugin" / "service.py"
    plugin_file.parent.mkdir(parents=True)
    plugin_file.write_text("print('hello')", encoding="utf-8")
    
    # Map debt file with invalid column count (only 3 columns / 4 pipes)
    debt_file = temp_git_repo / "references" / "map-debt.md"
    debt_file.parent.mkdir(parents=True)
    debt_file.write_text(
        "# Map Debt\n\n| ID | Title | Status |\n"
        "|---|---|---|\n"
        "| DEBT-20260902-01 | Incomplete Row | RESOLVED |\n",
        encoding="utf-8"
    )
    
    subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
    
    res = subprocess.run([str(guard_script)], cwd=temp_git_repo, capture_output=True, text=True)
    assert res.returncode != 0
    assert "COMMIT BLOCKED: Malformed row in references/map-debt.md" in res.stdout


def test_pre_commit_guard_passes_with_wiki_playbook(temp_git_repo):
    """Commit must pass when a wiki/ playbook is staged instead of a map-debt.md row."""
    guard_script = Path(__file__).parent.parent / "scripts" / "pre-commit-evolution-guard"
    
    # Logic file
    plugin_file = temp_git_repo / "plugins" / "my_plugin" / "service.py"
    plugin_file.parent.mkdir(parents=True)
    plugin_file.write_text("print('hello')", encoding="utf-8")
    
    # Wiki file
    wiki_file = temp_git_repo / "wiki" / "playbook-test.md"
    wiki_file.parent.mkdir(parents=True)
    wiki_file.write_text("# Test Playbook", encoding="utf-8")
    
    subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
    
    res = subprocess.run([str(guard_script)], cwd=temp_git_repo, capture_output=True, text=True)
    assert res.returncode == 0


def test_pre_commit_guard_passes_non_logic_files(temp_git_repo):
    """Commit must pass untouched when no plugins/src/py_services files are staged."""
    guard_script = Path(__file__).parent.parent / "scripts" / "pre-commit-evolution-guard"
    
    # Readme only
    readme = temp_git_repo / "README.md"
    readme.write_text("# Readme", encoding="utf-8")
    
    subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
    
    res = subprocess.run([str(guard_script)], cwd=temp_git_repo, capture_output=True, text=True)
    assert res.returncode == 0

def test_sync_rules_preserves_downstream_custom_sections(tmp_path):
    """
    CRITICAL TEST: Ensures sync_rules() does NOT blindly overwrite downstream custom additions.
    If target .agent/rules/foo.md contains custom sections not in origin, those sections MUST survive the sync.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import init_agentic_os

    # Setup mock origin repo with a rule
    origin_repo = tmp_path / "mock_origin"
    origin_rules = origin_repo / ".agent" / "rules"
    origin_rules.mkdir(parents=True)
    (origin_rules / "sample-policy.md").write_text(
        "# Sample Policy\n\n## Base Rules\nStandard upstream rule text.\n",
        encoding="utf-8"
    )

    # Setup mock target repo with custom downstream section added
    target_repo = tmp_path / "mock_target"
    target_rules = target_repo / ".agent" / "rules"
    target_rules.mkdir(parents=True)
    custom_target_content = (
        "# Sample Policy\n\n"
        "## Base Rules\nStandard upstream rule text.\n\n"
        "## Downstream Custom Additions\n"
        "Do not delete this custom rule added by downstream repo.\n"
    )
    (target_rules / "sample-policy.md").write_text(custom_target_content, encoding="utf-8")

    # Temporarily monkeypatch _get_plugin_root to point to mock_origin
    class MockPluginRoot:
        parent = origin_repo
    
    orig_fn = init_agentic_os._get_plugin_root
    init_agentic_os._get_plugin_root = lambda: origin_repo / "plugins" / "agent-agentic-os"

    try:
        init_agentic_os.sync_rules(target_repo, dry_run=False)
        result_content = (target_rules / "sample-policy.md").read_text(encoding="utf-8")
        
        # Assertion: Downstream additions must survive
        assert "## Downstream Custom Additions" in result_content, "Custom downstream section was clobbered by sync_rules!"
        assert "Do not delete this custom rule added by downstream repo." in result_content
    finally:
        init_agentic_os._get_plugin_root = orig_fn

def test_sync_rules_preserves_intra_section_edits_h3(tmp_path):
    """
    CRITICAL TEST 2 (Literal DEBT-20260902-01 reproduction):
    Target .agent/rules/self-evolution-policy.md contains an edit WITHIN a shared H3 heading
    (### Pre-Completion Self-Evolution Gate) where a blockquote [!IMPORTANT] was inserted
    before existing paragraph text.
    sync_rules must preserve this intra-section addition, NOT clobber it.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import init_agentic_os

    # Mock origin repo with base H3 section
    origin_repo = tmp_path / "mock_origin_h3"
    origin_rules = origin_repo / ".agent" / "rules"
    origin_rules.mkdir(parents=True)
    origin_text = (
        "# Self-Evolution Policy\n\n"
        "### Pre-Completion Self-Evolution Gate\n\n"
        "Before claiming ANY task or iterative turn is complete, output this block verbatim:\n"
        "```\nPRE-COMPLETION GATE:\n```\n"
    )
    (origin_rules / "self-evolution-policy.md").write_text(origin_text, encoding="utf-8")

    # Mock target repo with downstream intra-section addition ([!IMPORTANT] blockquote)
    target_repo = tmp_path / "mock_target_h3"
    target_rules = target_repo / ".agent" / "rules"
    target_rules.mkdir(parents=True)
    custom_target_text = (
        "# Self-Evolution Policy\n\n"
        "### Pre-Completion Self-Evolution Gate\n\n"
        "> [!IMPORTANT]\n"
        "> **Turn-by-Turn Mandatory Protocol**: The PRE-COMPLETION GATE is NOT an optional end-of-session ceremony.\n\n"
        "Before claiming ANY task or iterative turn is complete, output this block verbatim:\n"
        "```\nPRE-COMPLETION GATE:\n```\n"
    )
    (target_rules / "self-evolution-policy.md").write_text(custom_target_text, encoding="utf-8")

    orig_fn = init_agentic_os._get_plugin_root
    init_agentic_os._get_plugin_root = lambda: origin_repo / "plugins" / "agent-agentic-os"

    try:
        init_agentic_os.sync_rules(target_repo, dry_run=False)
        result_content = (target_rules / "self-evolution-policy.md").read_text(encoding="utf-8")
        
        # Intra-section addition MUST survive
        assert "> [!IMPORTANT]" in result_content, "Intra-section blockquote was clobbered by sync_rules!"
        assert "**Turn-by-Turn Mandatory Protocol**" in result_content
    finally:
        init_agentic_os._get_plugin_root = orig_fn

def test_sync_rules_does_not_duplicate_modified_schema_lines(tmp_path):
    """
    Ensures that when both upstream and downstream modify the same logical line
    (e.g., Map Debt schema description line), upstream takes precedence and
    does NOT produce duplicate contradictory lines.
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
    import init_agentic_os

    origin_repo = tmp_path / "mock_origin_replace"
    origin_rules = origin_repo / ".agent" / "rules"
    origin_rules.mkdir(parents=True)
    origin_text = (
        "### Map Debt Management\n\n"
        "- Lives in `references/map-debt.md` (columns: `ID`, `Title`, `Status`, `Severity`, `Repeat`, `First Seen`, `Description`, `Resolution Commit`).\n"
    )
    (origin_rules / "self-evolution-policy.md").write_text(origin_text, encoding="utf-8")

    target_repo = tmp_path / "mock_target_replace"
    target_rules = target_repo / ".agent" / "rules"
    target_rules.mkdir(parents=True)
    stale_target_text = (
        "### Map Debt Management\n\n"
        "- Lives in `references/map-debt.md` (columns: Logged, Cycle ID, Artifact, Friction, Why not fixed, Recommended fix, Evidence, Severity, Repeat, Status).\n"
    )
    (target_rules / "self-evolution-policy.md").write_text(stale_target_text, encoding="utf-8")

    orig_fn = init_agentic_os._get_plugin_root
    init_agentic_os._get_plugin_root = lambda: origin_repo / "plugins" / "agent-agentic-os"

    try:
        init_agentic_os.sync_rules(target_repo, dry_run=False)
        result = (target_rules / "self-evolution-policy.md").read_text(encoding="utf-8")
        
        # Upstream canonical 8-col must win; stale 10-col must NOT be duplicated
        assert "columns: `ID`, `Title`" in result
        assert "Logged, Cycle ID" not in result
        # Must only have one "- Lives in" bullet
        assert result.count("- Lives in") == 1
    finally:
        init_agentic_os._get_plugin_root = orig_fn


def test_pre_commit_guard_blocks_unindexed_playbook(temp_git_repo):
    """Commit must be blocked when a staged wiki playbook is missing from wiki/index.md."""
    guard_script = Path(__file__).parent.parent / "scripts" / "pre-commit-evolution-guard"
    
    # Logic file
    plugin_file = temp_git_repo / "plugins" / "my_plugin" / "service.py"
    plugin_file.parent.mkdir(parents=True)
    plugin_file.write_text("print('hello')", encoding="utf-8")
    
    # Unindexed playbook
    pb_file = temp_git_repo / "wiki" / "playbook-sample-invariant.md"
    pb_file.parent.mkdir(parents=True)
    pb_file.write_text("# Playbook: Sample Invariant\n", encoding="utf-8")

    # wiki/index.md exists but does NOT list the playbook
    index_file = temp_git_repo / "wiki" / "index.md"
    index_file.write_text("# Wiki Index\n- [Other](playbook-other.md)\n", encoding="utf-8")
    
    subprocess.run(["git", "add", "plugins/", "wiki/playbook-sample-invariant.md"], cwd=temp_git_repo, check=True)
    
    res = subprocess.run([str(guard_script)], cwd=temp_git_repo, capture_output=True, text=True)
    assert res.returncode != 0
    assert "COMMIT BLOCKED: Unindexed Layer 2 Wiki Playbook!" in res.stdout


def test_pre_commit_guard_passes_indexed_playbook(temp_git_repo):
    """Commit must pass when the staged wiki playbook is already referenced in wiki/index.md."""
    guard_script = Path(__file__).parent.parent / "scripts" / "pre-commit-evolution-guard"
    
    # Logic file
    plugin_file = temp_git_repo / "plugins" / "my_plugin" / "service.py"
    plugin_file.parent.mkdir(parents=True)
    plugin_file.write_text("print('hello')", encoding="utf-8")
    
    # Staged playbook and indexed in wiki/index.md
    pb_file = temp_git_repo / "wiki" / "playbook-sample-invariant.md"
    pb_file.parent.mkdir(parents=True)
    pb_file.write_text("# Playbook: Sample Invariant\n", encoding="utf-8")

    index_file = temp_git_repo / "wiki" / "index.md"
    index_file.write_text("# Wiki Index\n- [Sample](playbook-sample-invariant.md)\n", encoding="utf-8")
    
    subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
    
    res = subprocess.run([str(guard_script)], cwd=temp_git_repo, capture_output=True, text=True)
    assert res.returncode == 0

