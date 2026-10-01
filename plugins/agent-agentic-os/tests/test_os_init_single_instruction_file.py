#!/usr/bin/env python
"""
test_os_init_single_instruction_file.py
=======================================

Purpose:
    os-init keeps AGENTS.md as the ONLY agent-instruction file and is idempotent:
      - it never creates GEMINI.md or .github/copilot-instructions.md;
      - CLAUDE.md is at most a pointer to AGENTS.md (never enriched with rules);
      - it never overwrites AGENTS.md with CLAUDE.md content (the old fallback replaced a full
        AGENTS.md with a 3-line CLAUDE.md pointer);
      - a CLAUDE.md with real content and no AGENTS.md is migrated into AGENTS.md, not discarded;
      - fresh setup writes AGENTS.md and a pointer CLAUDE.md, no CLAUDE.local.md;
      - a second run changes nothing;
      - --install-hooks installs the current guard scripts (shipped with the os-init skill) and
        touches no instruction file.
    Runs the real init_agentic_os.py as a subprocess against temp git repositories.

Key Input Dependencies:
    plugins/agent-agentic-os/scripts/init_agentic_os.py
    plugins/agent-agentic-os/skills/os-init/scripts/ (installed-skill layout, for the hook sources)

Layer: Development / Testing

Functions:
    - test_retrofit_keeps_agents_md_and_pointer_and_creates_no_duplicates
    - test_retrofit_migrates_full_claude_md_into_agents_md
    - test_fresh_setup_writes_agents_md_and_pointer_only
    - test_existing_duplicate_files_are_left_alone
    - test_retrofit_is_idempotent_for_instruction_files
    - test_install_hooks_installs_current_guards_and_touches_no_instructions

Usage:
    python -m pytest plugins/agent-agentic-os/tests/test_os_init_single_instruction_file.py
"""

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN = Path(__file__).resolve().parents[1]
INIT = PLUGIN / "scripts" / "init_agentic_os.py"
POINTER = "# CLAUDE.md\n\nRead [AGENTS.md](AGENTS.md).\n"
AGENTS = "# AGENTS.md\n\n## Project rules\n\n" + "\n".join(f"- rule {i}" for i in range(200)) + "\n"


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    subprocess.run(["git", "init", "-q", str(r)], check=True)
    return r


def _run(repo: Path, *extra: str, script: Path = INIT) -> subprocess.CompletedProcess:
    res = subprocess.run(
        [sys.executable, str(script), "--target", str(repo), "--contribution-mode", "fork-and-pr", *extra],
        capture_output=True, text=True, timeout=300,
    )
    assert res.returncode == 0, res.stdout[-1500:] + res.stderr[-1500:]
    return res


def _no_duplicates(repo: Path) -> None:
    assert not (repo / "GEMINI.md").exists()
    assert not (repo / ".github" / "copilot-instructions.md").exists()


def _digest(repo: Path) -> dict:
    names = ["AGENTS.md", "CLAUDE.md", "GEMINI.md", ".github/copilot-instructions.md", "CLAUDE.local.md"]
    return {n: hashlib.sha256((repo / n).read_bytes()).hexdigest() for n in names if (repo / n).exists()}


def test_retrofit_keeps_agents_md_and_pointer_and_creates_no_duplicates(repo):
    (repo / "AGENTS.md").write_text(AGENTS)
    (repo / "CLAUDE.md").write_text(POINTER)
    _run(repo, "--retrofit")
    assert (repo / "CLAUDE.md").read_text() == POINTER
    agents = (repo / "AGENTS.md").read_text()
    assert agents.startswith(AGENTS.rstrip("\n")) and "- rule 199" in agents  # never replaced
    _no_duplicates(repo)


def test_retrofit_migrates_full_claude_md_into_agents_md(repo):
    full = "# CLAUDE.md\n\n## Team conventions\n\n- keep it simple\n"
    (repo / "CLAUDE.md").write_text(full)
    _run(repo, "--retrofit")
    assert "keep it simple" in (repo / "AGENTS.md").read_text()
    assert (repo / "CLAUDE.md").read_text() == POINTER
    assert "keep it simple" in (repo / "CLAUDE.md.bak").read_text()
    _no_duplicates(repo)


def test_claude_migration_preserves_an_existing_backup(repo):
    full = "# CLAUDE.md\n\nCurrent project rules.\n"
    backup = "# CLAUDE.md\n\nOlder preserved backup.\n"
    (repo / "CLAUDE.md").write_text(full)
    (repo / "CLAUDE.md.bak").write_text(backup)
    _run(repo, "--retrofit")
    assert (repo / "CLAUDE.md").read_text() == POINTER
    assert (repo / "CLAUDE.md.bak").read_text() == backup
    assert (repo / "CLAUDE.md.1.bak").read_text() == full


def test_fresh_setup_writes_agents_md_and_pointer_only(repo):
    _run(repo)
    assert (repo / "AGENTS.md").exists() and (repo / "AGENTS.md").read_text().strip()
    assert (repo / "CLAUDE.md").read_text() == POINTER
    assert not (repo / "CLAUDE.local.md").exists()
    _no_duplicates(repo)


def test_existing_duplicate_files_are_left_alone(repo):
    (repo / "AGENTS.md").write_text(AGENTS)
    (repo / "CLAUDE.md").write_text(POINTER)
    (repo / "GEMINI.md").write_text("# GEMINI.md\nold\n")
    (repo / ".github").mkdir()
    (repo / ".github" / "copilot-instructions.md").write_text("Copilot instructions\n")
    (repo / "CLAUDE.local.md").write_text("Local Claude instructions\n")
    res = _run(repo, "--retrofit")
    assert (repo / "GEMINI.md").read_text() == "# GEMINI.md\nold\n"  # never deleted or rewritten by os-init
    assert (repo / ".github" / "copilot-instructions.md").read_text() == "Copilot instructions\n"
    assert (repo / "CLAUDE.local.md").read_text() == "Local Claude instructions\n"
    assert "GEMINI.md" in res.stdout  # reported as a duplicate


def test_full_claude_and_agents_files_are_both_left_alone(repo):
    full_claude = "# CLAUDE.md\n\nClaude-specific project notes.\n"
    (repo / "AGENTS.md").write_text(AGENTS)
    (repo / "CLAUDE.md").write_text(full_claude)
    _run(repo, "--retrofit")
    assert (repo / "AGENTS.md").read_text() == AGENTS
    assert (repo / "CLAUDE.md").read_text() == full_claude


def test_retrofit_is_idempotent_for_instruction_files(repo):
    (repo / "AGENTS.md").write_text(AGENTS)
    (repo / "CLAUDE.md").write_text(POINTER)
    _run(repo, "--retrofit")
    first = _digest(repo)
    _run(repo, "--retrofit")
    assert _digest(repo) == first


def test_install_hooks_installs_current_guards_and_touches_no_instructions(repo):
    (repo / "AGENTS.md").write_text(AGENTS)
    (repo / "CLAUDE.md").write_text(POINTER)
    before = _digest(repo)
    installed_skill = repo.parent / "installed" / "os-init"
    installed_scripts = installed_skill / "scripts"
    installed_scripts.mkdir(parents=True)
    installed_init = installed_scripts / "init_agentic_os.py"
    shutil.copy2(INIT, installed_init)
    # The installer copies the whole os-init scripts/ folder with symlinks dereferenced, which
    # includes the shared control_plane_hooks.py helper that init_agentic_os.py imports.
    for name in ("pre-commit-evolution-guard", "pre-commit-pipeline-guard", "pre-push-review-guard",
                 "control_plane_hooks.py"):
        shutil.copy2(PLUGIN / "scripts" / name, installed_scripts / name)
    _run(repo, "--install-hooks", script=installed_init)  # simulate installer-dereferenced skill files
    hooks = repo / ".git" / "hooks"
    assert "verify_gate_evidence" in (hooks / "pre-push-review-guard").read_text()
    assert "control_plane_identity" in (hooks / "pre-commit-pipeline-guard").read_text()
    assert "pre-push-review-guard" in (hooks / "pre-push").read_text()
    assert _digest(repo) == before
    assert not (repo / "context").exists()  # hooks only: nothing else scaffolded
    assert not (repo / ".github").exists()
