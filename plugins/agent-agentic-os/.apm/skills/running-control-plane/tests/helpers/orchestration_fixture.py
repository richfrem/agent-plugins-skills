"""
helpers/orchestration_fixture.py
================================

Purpose:
    A skills root for tests, shaped like an APM install: one folder whose children are sibling skills. It holds
    symlinks to this repository's `orchestrating-agent-work` and `cli-agent` sources, so the control plane
    resolves the strategy registry, validators, graph runner and model catalogs exactly as it does when installed.
    The source tree itself is never used as a runtime location (spec G6), and nothing is written into a skill
    folder (spec G14): the root lives under the test's tmp_path.

Key Functions:
    - ORCHESTRATION_SKILLS_SOURCE -- the agent-orchestration package's source skills folder
    - make_skills_root(tmp_path, skills=...) -- build the fixture root and return it
"""

from pathlib import Path
from typing import Iterable

# tests/helpers -> tests -> running-control-plane -> skills -> .apm -> agent-agentic-os -> plugins
ORCHESTRATION_SKILLS_SOURCE = Path(__file__).resolve().parents[6] / "agent-orchestration" / ".apm" / "skills"
DEFAULT_SIBLINGS = ("orchestrating-agent-work", "cli-agent")


def make_skills_root(tmp_path: Path, skills: Iterable[str] = DEFAULT_SIBLINGS) -> Path:
    """A tmp skills folder holding symlinks to the named source skills; an empty iterable gives an empty root."""
    root = Path(tmp_path) / "installed-skills"
    root.mkdir(parents=True, exist_ok=True)
    for name in skills:
        source = ORCHESTRATION_SKILLS_SOURCE / name
        if not (source / "SKILL.md").is_file():
            raise FileNotFoundError(f"test fixture source skill missing: {source}")
        link = root / name
        if not link.exists():
            link.symlink_to(source, target_is_directory=True)
    return root
