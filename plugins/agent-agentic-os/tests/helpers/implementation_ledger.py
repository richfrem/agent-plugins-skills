"""Shared test helper for staging an explicit implementation ledger."""

import json
from pathlib import Path


def stage_implementation_ledger(control_plane, task_id: str, repo_root: Path | None = None) -> Path:
    root = Path(repo_root or getattr(control_plane, "repo_root", None) or control_plane.db_path.parent).resolve()
    control_plane.repo_root = root
    plan_dir = root / "docs" / "plans"
    plan_dir.mkdir(parents=True, exist_ok=True)
    evidence = root / ".implementation-evidence" / f"{task_id}.txt"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text("test fixture implementation evidence\n", encoding="utf-8")
    plan = plan_dir / f"{task_id}-implementation-plan.md"
    entry = [{
        "id": "fixture-implementation",
        "status": "COMPLETE",
        "artifacts": [str(evidence.relative_to(root))],
        "evidence": "pytest -q fixture validation",
    }]
    plan.write_text(
        "# Implementation plan\n\n## Implementation Task Ledger\n```json\n"
        + json.dumps(entry, indent=2)
        + "\n```\n",
        encoding="utf-8",
    )
    return plan
