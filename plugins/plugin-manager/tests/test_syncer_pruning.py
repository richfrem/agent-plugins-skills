import sys
import json
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import sync_with_inventory


def test_enforce_retention_pruning_runs_when_manifest_exists(tmp_path: Path):
    root = tmp_path
    ret_file = root / "plugin-retention.json"
    ret_file.write_text(json.dumps({"version": 1, "plugins": {}}), encoding="utf-8")

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        sync_with_inventory.enforce_retention_pruning(root, dry_run=False)

        assert mock_run.called
        cmd = mock_run.call_args[0][0]
        assert "prune_installed_skills.py" in cmd[1]
        assert "--execute" in cmd
        assert "--confirm-token" in cmd
        assert "PRUNE-INSTALLED-SKILLS" in cmd


def test_enforce_retention_pruning_dry_run(tmp_path: Path):
    root = tmp_path
    ret_file = root / "plugin-retention.json"
    ret_file.write_text(json.dumps({"version": 1, "plugins": {}}), encoding="utf-8")

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        sync_with_inventory.enforce_retention_pruning(root, dry_run=True)

        assert mock_run.called
        cmd = mock_run.call_args[0][0]
        assert "prune_installed_skills.py" in cmd[1]
        assert "--dry-run" in cmd
        assert "--execute" not in cmd


def test_enforce_retention_pruning_skips_when_no_manifest(tmp_path: Path):
    root = tmp_path
    with patch("subprocess.run") as mock_run:
        sync_with_inventory.enforce_retention_pruning(root, dry_run=False)
        assert not mock_run.called


def test_main_cli_no_prune_flag(tmp_path: Path, monkeypatch):
    root = tmp_path
    sources_file = root / "plugin-sources.json"
    sources_file.write_text(json.dumps({"sources": []}), encoding="utf-8")

    monkeypatch.chdir(root)
    monkeypatch.setattr(sys, "argv", ["sync_with_inventory.py", "--no-prune", "--dry-run"])

    with patch.object(sync_with_inventory, "enforce_retention_pruning") as mock_enforce:
        sync_with_inventory.main()
        assert not mock_enforce.called
