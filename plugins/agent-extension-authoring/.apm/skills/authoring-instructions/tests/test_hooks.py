#!/usr/bin/env python3
"""
Regression tests for the hooks mode of authoring-instructions.

Purpose:
    1. validate_hook_schema.py accepts an empty-string matcher (valid: matches every tool event;
       used by SessionStart/SessionEnd hooks) and rejects a missing matcher key
    2. scaffold_hook.py writes the canonical {"hooks": {Event: [...]}} format into
       <plugin-root>/.apm/hooks/hooks.json, merges repeated runs, and passes validate_hook_schema.py
    3. hook_linter.py lints Python hook scripts without false-positive Bash warnings and flags SF-11 violations

Key Input Dependencies:
    - ../scripts/validate_hook_schema.py, ../scripts/scaffold_hook.py, ../scripts/hook_linter.py
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def run(script, *args, cwd):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)], cwd=cwd,
                          capture_output=True, text=True)


def write_hooks(path: Path, matcher):
    entry = {"hooks": [{"type": "command", "command": "python3 x.py"}]}
    if matcher is not None:
        entry["matcher"] = matcher
    path.write_text(json.dumps({"hooks": {"SessionStart": [entry]}}), encoding="utf-8")


class ValidatorTests(unittest.TestCase):
    def test_empty_matcher_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "hooks.json"
            write_hooks(f, "")
            result = run("validate_hook_schema.py", f, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_missing_matcher_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "hooks.json"
            write_hooks(f, None)
            self.assertNotEqual(run("validate_hook_schema.py", f, cwd=tmp).returncode, 0)


class ScaffoldHookTests(unittest.TestCase):
    def test_creates_canonical_hooks_json_that_validates(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run("scaffold_hook.py", "--event", "PreToolUse", "--name", "check-command", "--plugin-root", tmp, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            hooks = Path(tmp) / ".apm" / "hooks" / "hooks.json"
            data = json.loads(hooks.read_text())
            entry = data["hooks"]["PreToolUse"][0]
            self.assertEqual(entry["hooks"][0]["type"], "command")
            self.assertIn("${CLAUDE_PLUGIN_ROOT}/.apm/hooks/check-command.py", entry["hooks"][0]["command"])
            script = Path(tmp) / ".apm" / "hooks" / "check-command.py"
            self.assertTrue(script.is_file())
            self.assertEqual(run("validate_hook_schema.py", hooks, cwd=tmp).returncode, 0)
            lint_res = run("hook_linter.py", script, cwd=tmp)
            self.assertEqual(lint_res.returncode, 0, lint_res.stdout)
            self.assertIn("No issues found", lint_res.stdout)

    def test_second_run_merges_instead_of_replacing(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("scaffold_hook.py", "--event", "PreToolUse", "--name", "a", "--plugin-root", tmp, cwd=tmp)
            run("scaffold_hook.py", "--event", "Stop", "--name", "b", "--plugin-root", tmp, cwd=tmp)
            data = json.loads((Path(tmp) / ".apm" / "hooks" / "hooks.json").read_text())
            self.assertEqual(sorted(data["hooks"]), ["PreToolUse", "Stop"])

    def test_unknown_event_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run("scaffold_hook.py", "--event", "NotAnEvent", "--name", "x", "--plugin-root", tmp, cwd=tmp)
            self.assertNotEqual(result.returncode, 0)

    def test_hook_linter_flags_sf11_harness_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad_hook = Path(tmp) / "bad_hook.py"
            bad_hook.write_text(
                "#!/usr/bin/env python3\nimport sys\nstate = '.claude/state.json'\nsys.exit(0)\n",
                encoding="utf-8",
            )
            bad_hook.chmod(0o755)
            lint_res = run("hook_linter.py", bad_hook, cwd=tmp)
            self.assertEqual(lint_res.returncode, 0)
            self.assertIn("SF-11", lint_res.stdout)


if __name__ == "__main__":
    unittest.main()
