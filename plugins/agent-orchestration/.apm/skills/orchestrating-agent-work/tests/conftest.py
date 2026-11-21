"""Shared pytest configuration for orchestrating-agent-work tests.

Enforces G14 (no skill-folder or repo docs/plans pollution during a test run).
"""

from __future__ import annotations

from pathlib import Path
import pytest


def _snapshot_tree(root: Path) -> set[str]:
    if not root.exists():
        return set()
    return {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }


@pytest.fixture(scope="session", autouse=True)
def _forbid_skill_folder_pollution():
    """Fail the session if any test writes files into the skill folder or repo docs/plans/."""
    skill_root = Path(__file__).resolve().parent.parent
    repo_root = skill_root.parents[3] if len(skill_root.parents) >= 4 else skill_root.parent
    docs_plans = repo_root / "docs" / "plans"

    before_skill = _snapshot_tree(skill_root)
    before_plans = _snapshot_tree(docs_plans)
    yield
    after_skill = _snapshot_tree(skill_root)
    after_plans = _snapshot_tree(docs_plans)

    new_skill = sorted(after_skill - before_skill)
    new_plans = sorted(after_plans - before_plans)
    problems = []
    if new_skill:
        problems.append(f"Skill folder gained files during test run: {new_skill}")
    if new_plans:
        problems.append(f"Repo docs/plans/ gained files during test run: {new_plans}")
    if problems:
        pytest.fail("G14 violation — " + "; ".join(problems))
