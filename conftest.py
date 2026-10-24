"""Repository-level pytest collection rules.

The plugin smoke tests are standalone executable programs.  Their shared
filename is intentional for direct invocation, but pytest would import both
as the same top-level ``smoke_test`` module during recursive collection.

Files materialized from the copy manifest (``symlinks.json`` entries with
``strategy: "copy"``, written by materialize_copies.py) are copies of a
canonical file that pytest already collects at its canonical location;
collecting the copies too would import the same module name twice.
"""

import json
from pathlib import Path

collect_ignore = [
    "plugins/agent-agentic-os/skills/running-control-plane/scripts/smoke_test.py",
    "plugins/agent-exploration-cycle/skills/running-exploration-cycle/scripts/smoke_test.py",
    "plugins/agent-orchestration/skills/orchestrating-agent-work/tests/test_swarm_run_models.py",
]

_ROOT = Path(__file__).resolve().parent


# Destinations of copy-manifest entries, as absolute paths.
def _materialized_copies() -> set:
    manifest = _ROOT / "symlinks.json"
    if not manifest.is_file():
        return set()
    links = json.loads(manifest.read_text(encoding="utf-8")).get("links", [])
    return {str((_ROOT / e["dst"]).resolve()) for e in links if e.get("strategy") == "copy"}


_COPIES = _materialized_copies()


def pytest_ignore_collect(collection_path, config):
    """Skip materialized copy-manifest files; their canonical file is collected instead."""
    return True if str(Path(collection_path).resolve()) in _COPIES else None
