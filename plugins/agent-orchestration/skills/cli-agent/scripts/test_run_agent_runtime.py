"""Real process contracts for effort, executable selection and safe diagnostics.

Purpose: Verify dispatcher behavior without calling an external model.
Key Input Dependencies: run_agent.py and fixture executable processes.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("run_agent.py")


def backend(tmp_path, name="claude", exit_code=0):
    """Create a real executable that records argv or returns a backend failure."""
    script = tmp_path / name
    script.write_text(f'#!{sys.executable}\nimport sys,json\nif "--version" in sys.argv:\n print("fixture 2.1.287");sys.exit(0)\nprint(json.dumps(sys.argv[1:]))\nsys.exit({exit_code})\n')
    script.chmod(0o755)
    return script


def dispatch(tmp_path, *extra):
    """Run the router as a real child process against a fixture backend."""
    source = tmp_path / "source.md"
    source.write_text("private-source-marker")
    output = tmp_path / "output.md"
    env = {**os.environ, "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"]}
    result = subprocess.run([sys.executable, str(SCRIPT), "/dev/null", str(source), str(output),
                             "Review supplied source only.", "--cli", "claude", "--model", "claude-opus-5-5",
                             "--isolated", "--require-input", *extra], env=env, capture_output=True, text=True)
    return result, output


def test_claude_medium_reaches_real_subprocess(tmp_path):
    backend(tmp_path)
    result, output = dispatch(tmp_path, "--effort", "medium")
    assert result.returncode == 0, result.stderr + result.stdout
    argv = json.loads(output.read_text())
    assert argv[argv.index("--effort") + 1] == "medium"
    assert "--dangerously-skip-permissions" not in argv


def test_omitted_effort_stays_omitted(tmp_path):
    backend(tmp_path)
    result, output = dispatch(tmp_path)
    assert result.returncode == 0, result.stderr + result.stdout
    assert "--effort" not in json.loads(output.read_text())


def test_explicit_executable_wins_over_path(tmp_path):
    backend(tmp_path, exit_code=9)
    selected = backend(tmp_path, name="selected-claude")
    result, output = dispatch(tmp_path, "--executable", str(selected), "--effort", "low")
    assert result.returncode == 0, result.stderr + result.stdout
    assert str(selected) in result.stdout
    assert "2.1.287" in result.stdout
    argv = json.loads(output.read_text())
    assert argv[argv.index("--effort") + 1] == "low"


def test_failure_does_not_echo_source_prompt(tmp_path):
    backend(tmp_path, exit_code=7)
    result, output = dispatch(tmp_path, "--effort", "high")
    assert result.returncode != 0
    assert "private-source-marker" not in result.stdout + result.stderr
    assert "7" in result.stdout + result.stderr


def test_missing_explicit_executable_fails_clearly(tmp_path):
    result, output = dispatch(tmp_path, "--executable", str(tmp_path / "missing"))
    assert result.returncode != 0
    assert "executable" in (result.stdout + result.stderr).lower()
    assert not output.exists()


def test_backend_without_version_flag_preserves_dispatch(tmp_path):
    selected = tmp_path / "legacy-cli"
    selected.write_text(f'#!{sys.executable}\nimport sys,json\nif "--version" in sys.argv: sys.exit(2)\nprint(json.dumps(sys.argv[1:]))\n')
    selected.chmod(0o755)
    result, output = dispatch(tmp_path, "--executable", str(selected))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "version=unavailable" in result.stdout
    assert output.exists()
