import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from simulate_lifecycle import run_lifecycle_simulation


def test_lifecycle_simulation_end_to_end(tmp_path: Path):
    result = run_lifecycle_simulation(target_root=tmp_path, scenario="full")
    assert result["success"] is True
    assert result["stages_completed"] == ["install", "prune", "sync", "remove"]
