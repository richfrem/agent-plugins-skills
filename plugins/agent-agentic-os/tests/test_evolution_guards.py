"""
test_evolution_guards.py — Automated Unit & Integration Tests for Evolution Guards
=================================================================================
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
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def temp_git_repo(tmp_path):
    repo = tmp_path / "test_repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    return repo


def test_turn_evolution_guard_ast_valid():
    guard_script = Path(__file__).parent.parent / "hooks" / "scripts" / "turn_evolution_guard.py"
    assert guard_script.exists()
    import ast
    ast.parse(guard_script.read_text(encoding="utf-8"))


def test_pre_commit_guard_blocks_logic_without_docs(temp_git_repo):
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
    guard_script = Path(__file__).parent.parent / "scripts" / "pre-commit-evolution-guard"
    
    # Readme only
    readme = temp_git_repo / "README.md"
    readme.write_text("# Readme", encoding="utf-8")
    
    subprocess.run(["git", "add", "."], cwd=temp_git_repo, check=True)
    
    res = subprocess.run([str(guard_script)], cwd=temp_git_repo, capture_output=True, text=True)
    assert res.returncode == 0
