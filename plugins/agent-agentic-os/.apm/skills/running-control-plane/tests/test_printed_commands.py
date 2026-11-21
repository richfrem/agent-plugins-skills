"""S5 tests (B4, B18, B19): every printed human command parses cleanly and fits in 100 chars after &&,
and every printed reference link exists on disk."""

from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path

from agent_control import _build_parser
from control_plane.constants import CONTROL_SCRIPTS_DIR
from control_plane.registry import TransitionRegistry


def test_every_printed_edge_command_parses_and_fits_in_100_chars():
    reg = TransitionRegistry.load_default()
    parser = _build_parser()
    templates = reg.get_all_templates()
    assert len(templates) == 34

    for tmpl in templates:
        guidance = reg.get_transition_guidance(tmpl.from_state, tmpl.to_state, task_id_placeholder="t-123")
        cmd = guidance["command"]
        assert " && " in cmd, f"Expected short cd && python3 -m control_plane form: {cmd}"
        after_and = cmd.split(" && ", 1)[1]
        assert len(after_and) <= 100, f"Command after && exceeds 100 chars ({len(after_and)}): {after_and}"
        assert after_and.startswith("python3 -m control_plane ")
        argv = shlex.split(after_and)[3:]  # strip ['python3', '-m', 'control_plane']
        parsed = parser.parse_args(argv)
        assert parsed.subcommand in ("transition", "coordinate-transition", "go")
        assert parsed.task_id == "t-123"
        assert parsed.to == tmpl.to_state


def test_module_entrypoint_runs_help():
    res = subprocess.run(
        [sys.executable, "-m", "control_plane", "--help"],
        cwd=CONTROL_SCRIPTS_DIR,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stderr
    assert "migrate-schema" in res.stdout


def test_printed_pipeline_reference_link_exists():
    """B4: references/modes/intake.md exists (no dead references/intake/workflow.md)."""
    skill_dir = CONTROL_SCRIPTS_DIR.parent
    assert (skill_dir / "references" / "modes" / "intake.md").is_file()
    coord_text = (CONTROL_SCRIPTS_DIR / "control_plane" / "coordinator.py").read_text(encoding="utf-8")
    assert "references/intake/workflow.md" not in coord_text
    assert "'intake' / 'workflow.md'" not in coord_text
