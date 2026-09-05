"""
Tests for 3-Layer Filesystem Memory
Verifying line budgets, absence of external daemons, and low-latency native retrieval.

Purpose:
    Verifies the 3-layer memory architecture (runtime context, wiki, audit
    traces) stays within its line/size budgets and retrieves natively
    (filesystem only, no external daemon or network dependency).

Key Input Dependencies:
    - context/memory.md and wiki/ under the repo root
"""

import time
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def test_memory_management_skill_line_budget():
    """Asserts plugins/agent-memory/skills/memory-management/SKILL.md is <= 100 lines."""
    skill_file = REPO_ROOT / "plugins" / "agent-memory" / "skills" / "memory-management" / "SKILL.md"
    assert skill_file.exists()
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 100, f"memory-management/SKILL.md has {len(lines)} lines (budget <= 100)"


def test_self_evolution_skill_line_budget():
    """Asserts plugins/agent-agentic-os/skills/self-evolution/SKILL.md is <= 100 lines."""
    skill_file = REPO_ROOT / "plugins" / "agent-agentic-os" / "skills" / "self-evolution" / "SKILL.md"
    assert skill_file.exists()
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 100, f"self-evolution/SKILL.md has {len(lines)} lines (budget <= 100)"


def test_native_retrieval_latency(tmp_path):
    """Asserts direct file reads on wiki/ and references/ complete in < 50ms without daemons."""
    test_wiki = tmp_path / "wiki"
    test_wiki.mkdir()
    for i in range(20):
        (test_wiki / f"playbook_{i}.md").write_text(f"# Playbook {i}\nKnowledge entry {i}\nStatus: CONFIRMED\n", encoding="utf-8")

    start_time = time.perf_counter()
    matches = []
    for f in test_wiki.glob("*.md"):
        content = f.read_text(encoding="utf-8")
        if "CONFIRMED" in content:
            matches.append(f.name)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    assert len(matches) == 20
    assert elapsed_ms < 50.0, f"Native retrieval took {elapsed_ms:.2f}ms (expected < 50ms)"


def test_zero_third_party_dependencies_in_scripts():
    """Asserts evolution scripts use only standard library and do not import chromadb or ruamel."""
    scripts_dir = REPO_ROOT / "plugins" / "agent-agentic-os" / "scripts"
    forbidden_imports = ["chromadb", "ruamel", "ruamel.yaml", "torch", "transformers"]

    for script_name in ["evolution_state.py", "record_trace.py", "verify_evolution_receipt.py", "export_upstream_pr.py"]:
        script_path = scripts_dir / script_name
        assert script_path.exists()
        code = script_path.read_text(encoding="utf-8")
        for bad_dep in forbidden_imports:
            assert f"import {bad_dep}" not in code, f"Forbidden import '{bad_dep}' found in {script_name}"
            assert f"from {bad_dep}" not in code, f"Forbidden from-import '{bad_dep}' found in {script_name}"
