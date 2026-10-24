"""
Purpose:
    Constants and consumer-project discovery for managing-vector-db.

Key Input Dependencies:
    - Caller working directory and optional consumer-project environment override.
    - Python standard-library os and pathlib.
"""
import os
from pathlib import Path

SKILL_NAME = "managing-vector-db"
PROJECT_ROOT_ENV = "AGENT_MEMORY_PROJECT_ROOT"
PROJECT_MARKERS = (".git", ".agent", "apm.yml")
VECTOR_QUERY_ENV = "AGENT_MEMORY_VECTOR_QUERY"


def consumer_project_root() -> Path:
    """Resolve an explicit consumer root or the nearest caller workspace."""
    override = os.environ.get(PROJECT_ROOT_ENV)
    if override:
        return Path(override).expanduser().resolve()
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if any((candidate / marker).exists() for marker in PROJECT_MARKERS):
            return candidate
    return current
