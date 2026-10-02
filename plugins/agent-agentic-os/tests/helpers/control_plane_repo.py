"""
helpers/control_plane_repo.py - a realistic throwaway repo for control-plane-mode tests.

Builds a git repo that looks like a consumer install:
  * .git/hooks/pre-commit and pre-push dispatchers wired exactly as init_agentic_os.py wires them
    (plus a custom line and the independent evolution guard, which must survive any toggle)
  * the real guard scripts copied into .git/hooks
  * an ownership file (2-space JSON) listing the manifest members and a few bystanders
  * the installed component folders
  * a context/control_plane.db whose bytes must never change
  * a tiny fake plugin-syncer that mirrors the ownership file onto disk
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[2]
SCRIPTS = PLUGIN / "scripts"
SKILL = PLUGIN / "skills" / "os-control-plane-mode"
MODE_SCRIPT = SKILL / "scripts" / "control_plane_mode.py"
MANIFEST = SKILL / "references" / "control-plane.manifest.json" if (SKILL / "references" / "control-plane.manifest.json").is_file() else (SKILL / "control-plane.manifest.json")

MEMBERS = {
    "skills": ["work-intake", "transition-simulator", "os-signing-setup"],
    "rules": ["state-transition-guidance-compliance"],
    "agents": [],
}
BYSTANDERS = {
    "skills": ["os-init", "os-health-check", "self-evolution"],
    "rules": ["destructive-action-guard"],
    "agents": ["os-architect-agent"],
}

FAKE_SYNCER = '''\
import json, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
root = Path.cwd()
own_path = root / ".agents/ownership/agent-agentic-os.json"
own = json.loads(own_path.read_text())
for kind, comps in own["components"].items():
    for name, entry in comps.items():
        for art in entry["artifacts"]:
            p = root / art
            if entry["should_install"]:
                if p.suffix:
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text("installed\\n")  # the real syncer restores the plugin's identical content
                else:
                    p.mkdir(parents=True, exist_ok=True)
            elif p.exists():
                shutil.rmtree(p) if p.is_dir() else p.unlink()
# The real plugin-syncer rewrites the ownership file and bumps installed_at on every run.
own["installed_at"] = datetime.now(timezone.utc).isoformat()
own_path.write_text(json.dumps(own, indent=2) + "\\n")
print("fake sync ok")
'''

DB_BYTES = b"SQLite-format-3-pretend-task-history\x00\x01\x02" * 8


def _artifact(kind: str, name: str) -> str:
    return {
        "skills": f".agents/skills/{name}",
        "rules": f".agent/rules/{name}.md",
        "agents": f".agents/agents/{name}.md",
    }[kind]


def make_repo(tmp_path: Path, *, installed: bool = True, track_rule: bool = False) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    for cmd in (["git", "init", "-q"], ["git", "config", "user.email", "t@example.com"],
                ["git", "config", "user.name", "Tester"]):
        subprocess.run(cmd, cwd=root, check=True, capture_output=True)

    hooks = root / ".git" / "hooks"
    hooks.mkdir(exist_ok=True)
    (hooks / "pre-commit").write_text(
        "#!/usr/bin/env bash\n"
        'HOOKS_DIR="$(dirname "$0")"\n'
        "echo custom-pre-commit-step\n"
        "\n# Run evolution guard if it exists\n"
        'if [ -x "$HOOKS_DIR/pre-commit-evolution-guard" ]; then\n'
        '    "$HOOKS_DIR/pre-commit-evolution-guard" || exit 1\n'
        "fi\n"
        "\n# Run pipeline execution guard if it exists\n"
        'if [ -x "$HOOKS_DIR/pre-commit-pipeline-guard" ]; then\n'
        '    "$HOOKS_DIR/pre-commit-pipeline-guard" || exit 1\n'
        "fi\n"
        "\nexit 0\n",
        encoding="utf-8",
    )
    # the older minimal style the installer wrote when no pre-push hook existed
    (hooks / "pre-push").write_text(
        "#!/usr/bin/env bash\n"
        "# pre-push hook - installed by init_agentic_os.py\n"
        'HOOKS_DIR="$(dirname "$0")"\n'
        "\n# Run review guard\n"
        'if [ -x "$HOOKS_DIR/pre-push-review-guard" ]; then\n'
        '    "$HOOKS_DIR/pre-push-review-guard" || exit 1\n'
        "fi\n"
        "\nexit 0\n",
        encoding="utf-8",
    )
    for name in ("pre-commit-pipeline-guard", "pre-push-review-guard", "pre-commit-evolution-guard"):
        shutil.copy2(SCRIPTS / name, hooks / name)
        (hooks / name).chmod(0o755)
    for h in ("pre-commit", "pre-push"):
        (hooks / h).chmod(0o755)

    components: dict = {}
    for source in (MEMBERS, BYSTANDERS):
        for kind, names in source.items():
            for name in names:
                components.setdefault(kind, {})[name] = {
                    "should_install": installed or name in BYSTANDERS[kind],
                    "artifacts": [_artifact(kind, name)],
                }
    components["hooks"] = {"hooks": {"should_install": True, "artifacts": [".agents/hooks/agent-agentic-os-hooks.json"]}}
    ownership = {"plugin": "agent-agentic-os", "installed_at": "2026-09-30T00:00:00Z",
                 "components": components, "artifacts": []}
    own_path = root / ".agents" / "ownership" / "agent-agentic-os.json"
    own_path.parent.mkdir(parents=True)
    own_path.write_text(json.dumps(ownership, indent=2) + "\n", encoding="utf-8")

    for comps in components.values():
        for entry in comps.values():
            if entry["should_install"]:
                art = root / entry["artifacts"][0]
                if art.suffix:
                    art.parent.mkdir(parents=True, exist_ok=True)
                    art.write_text("installed\n")
                else:
                    art.mkdir(parents=True, exist_ok=True)

    (root / "context").mkdir()
    (root / "context" / "control_plane.db").write_bytes(DB_BYTES)
    (root / "fake_sync.py").write_text(FAKE_SYNCER, encoding="utf-8")
    if track_rule:
        rule = MEMBERS["rules"][0]
        subprocess.run(["git", "add", "-f", _artifact("rules", rule)], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "track the rule"], cwd=root, check=True, capture_output=True)
    return root


def run_mode(root: Path, *args: str, syncer: bool = True) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(MODE_SCRIPT), *args, "--target", str(root)]
    if syncer and args and args[0] in ("enable", "disable"):
        cmd += ["--syncer", str(root / "fake_sync.py")]
    return subprocess.run(cmd, capture_output=True, text=True)


def snapshot(root: Path) -> dict:
    """Every file under the repo (excluding .git objects) -> bytes, to prove 'nothing changed'."""
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and ".git/objects" not in p.as_posix() and ".git/index" not in p.as_posix():
            out[p.relative_to(root).as_posix()] = p.read_bytes()
    return out
