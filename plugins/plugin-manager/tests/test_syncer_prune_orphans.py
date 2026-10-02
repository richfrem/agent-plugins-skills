import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sync_with_inventory as s


def _setup(tmp_path):
    skills = tmp_path / ".agents" / "skills"
    (skills / "kept").mkdir(parents=True)
    (skills / "orphan").mkdir()
    (skills / "users-own-skill").mkdir()
    own = tmp_path / ".agents" / "ownership"
    own.mkdir(parents=True)
    (own / "old.json").write_text('{"artifacts": [".agents/skills/orphan"]}')
    src = tmp_path / "plugins" / "p" / "skills" / "kept"
    src.mkdir(parents=True)
    return skills


def test_report_only_by_default(tmp_path):
    skills = _setup(tmp_path)
    s.validate_agents_state(tmp_path, {"p"})
    assert (skills / "orphan").exists()


def test_prune_dry_run_keeps_dir(tmp_path):
    skills = _setup(tmp_path)
    s.validate_agents_state(tmp_path, {"p"}, prune_orphans=True, dry_run=True)
    assert (skills / "orphan").exists()


def test_prune_removes_only_orphans(tmp_path):
    skills = _setup(tmp_path)
    s.validate_agents_state(tmp_path, {"p"}, prune_orphans=True)
    assert not (skills / "orphan").exists()
    assert (skills / "kept").exists()


def test_prune_never_touches_skills_no_manifest_claims(tmp_path):
    skills = _setup(tmp_path)
    s.validate_agents_state(tmp_path, {"p"}, prune_orphans=True)
    assert (skills / "users-own-skill").exists()
