#!/usr/bin/env python3
"""
Unit tests for apm_build_pipeline.py (convert-plugin-to-apm skill).

Purpose:
    Validates the five-stage APM build pipeline against a synthetic git repo:
    1. Inspect reads symlinks from the git index
    2. Normalize dereferences into staging without touching the source tree
    3. Normalize handles a Windows-style checkout (core.symlinks=false text stubs)
    4. Validate reports broken / cross-plugin symlinks with their standard fix ids
    5. Validate allows links to plugin-root files (APM rewrites them), rejects links that
       leave the plugin, and warns on code/text paths that leave the skill (not rewritten)
    6. Package writes apm.yml with manifest target names (agents -> agent-skills)
    7. Normalize materializes copy-manifest entries (one source, per-skill copies)
    8. Test deploy installs and uninstalls with APM; pack builds a bundle whose global
       install has the per-skill copies (only when APM_BIN is set)

Key Input Dependencies:
    - ../scripts/apm_build_pipeline.py (module under test)
    - git on PATH
    - APM_BIN environment variable (optional; enables the test deploy case)
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import apm_build_pipeline as pipeline  # noqa: E402

SKILL_MD = "---\nname: {name}\ndescription: Builds things for tests.\n---\n\n# {name}\n\n{body}\n"


# Run a git command in a directory, failing the test on error.
def _git(cwd: Path, *args: str) -> None:
    """Run git quietly with a fixed identity."""
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   cwd=cwd, check=True, capture_output=True)


# Build a repo with one plugin using hub-and-spoke symlinks, a broken link and a cross-plugin link.
def _make_repo(root: Path) -> None:
    """Create plugins/p (skills s1, s2) and plugins/q, then commit everything."""
    p = root / "plugins" / "p"
    (p / "references").mkdir(parents=True)
    (p / "references" / "shared.md").write_text("shared content\n")
    for skill in ("s1", "s2"):
        (p / "skills" / skill / "references").mkdir(parents=True)
    (p / "skills" / "s1" / "SKILL.md").write_text(
        SKILL_MD.format(name="s1", body="See [shared](../../references/shared.md) and [other](../../../q/rule.md).\n"
                                          "Run `python3 ../../scripts/tool.py`."))
    (p / "skills" / "s2" / "SKILL.md").write_text(SKILL_MD.format(name="s2", body="Plain."))
    os.symlink("../../../references/shared.md", p / "skills" / "s2" / "references" / "shared.md")
    os.symlink("../../../references/missing.md", p / "skills" / "s2" / "references" / "missing.md")
    (root / "plugins" / "q").mkdir(parents=True)
    (root / "plugins" / "q" / "rule.md").write_text("other plugin\n")
    os.symlink("../../../../q/rule.md", p / "skills" / "s2" / "references" / "rule.md")
    (p / "scripts").mkdir()
    (p / "scripts" / "tool.py").write_text("print('tool')\n")
    (root / "symlinks.json").write_text(json.dumps({"version": 1, "links": [
        {"src": "plugins/p/scripts/tool.py", "dst": "plugins/p/skills/s1/scripts/tool.py", "strategy": "copy"},
        {"src": "plugins/p/scripts/tool.py", "dst": "plugins/p/skills/s2/scripts/tool.py", "strategy": "copy"},
    ]}))
    _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "fixture")


class TestApmBuildPipeline(unittest.TestCase):
    """Pipeline stages against a synthetic repository."""

    def setUp(self) -> None:
        """Create a fresh repo in a temp dir."""
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve() / "repo"
        self.root.mkdir()
        _make_repo(self.root)
        self.plugin = self.root / "plugins" / "p"
        self.staging = self.root / "build" / "staging" / "p"

    def tearDown(self) -> None:
        """Remove the temp dir."""
        self.tmp.cleanup()

    def _run_stages(self, repo_root: Path) -> tuple[dict, dict, dict]:
        """Run inspect, normalize and validate against repo_root."""
        inspection = pipeline.inspect_plugin(repo_root, repo_root / "plugins" / "p")
        staging = repo_root / "build" / "staging" / "p"
        normalized = pipeline.normalize_plugin(inspection, staging)
        return inspection, normalized, pipeline.validate_package(staging, normalized)

    def test_inspect_reads_links_from_git_index(self) -> None:
        inspection = pipeline.inspect_plugin(self.root, self.plugin)
        self.assertEqual(inspection["skills"], ["s1", "s2"])
        texts = {Path(e["path"]).name: e["link_text"] for e in inspection["symlinks"]}
        self.assertEqual(texts["shared.md"], "../../../references/shared.md")
        self.assertEqual(len(texts), 3)

    def test_normalize_dereferences_without_touching_source(self) -> None:
        _, normalized, _ = self._run_stages(self.root)
        staged = self.staging / "skills" / "s2" / "references" / "shared.md"
        self.assertFalse(staged.is_symlink())
        self.assertEqual(staged.read_text(), "shared content\n")
        self.assertTrue((self.plugin / "skills" / "s2" / "references" / "shared.md").is_symlink())
        entry = next(e for e in normalized["links"] if e["path"].endswith("s2/references/shared.md"))
        self.assertEqual(entry["target_sha256"], entry["staged_sha256"])

    def test_windows_style_checkout_stubs_are_dereferenced(self) -> None:
        clone = Path(self.tmp.name) / "winclone"
        _git(Path(self.tmp.name), "clone", "-q", "--config", "core.symlinks=false", str(self.root), str(clone))
        stub = clone / "plugins" / "p" / "skills" / "s2" / "references" / "shared.md"
        self.assertFalse(stub.is_symlink())
        self.assertEqual(stub.read_text(), "../../../references/shared.md")
        self._run_stages(clone)
        staged = clone / "build" / "staging" / "p" / "skills" / "s2" / "references" / "shared.md"
        self.assertEqual(staged.read_text(), "shared content\n")

    def test_validate_reports_findings_with_standard_fixes(self) -> None:
        _, _, result = self._run_stages(self.root)
        by_check = {f["check"]: f for f in result["findings"]}
        self.assertFalse(result["passed"])
        self.assertTrue(by_check["broken_symlink"]["fix"].startswith("SF-1"))
        self.assertTrue(by_check["cross_plugin_symlink"]["fix"].startswith("SF-2"))
        self.assertNotIn("symlink_in_package", by_check)

    def test_link_boundary_is_the_plugin(self) -> None:
        _, _, result = self._run_stages(self.root)
        s1 = [f for f in result["findings"] if f["path"] == "skills/s1/SKILL.md"]
        checks = {f["check"]: f for f in s1}
        self.assertEqual(checks["link_escapes_package"]["detail"], "../../../q/rule.md")
        self.assertTrue(checks["link_escapes_package"]["fix"].startswith("SF-3"))
        self.assertNotIn("../../references/shared.md", [f["detail"] for f in s1 if f["level"] == "error"])
        self.assertEqual(checks["path_not_rewritten"]["level"], "warning")
        self.assertEqual(checks["path_not_rewritten"]["detail"], "../../scripts/tool.py")

    def test_copy_manifest_creates_per_skill_copies_in_staging_only(self) -> None:
        _, normalized, result = self._run_stages(self.root)
        for skill in ("s1", "s2"):
            self.assertEqual((self.staging / "skills" / skill / "scripts" / "tool.py").read_text(), "print('tool')\n")
            self.assertFalse((self.plugin / "skills" / skill / "scripts" / "tool.py").exists())
        copies = [e for e in normalized["links"] if e["kind"] == "copy"]
        self.assertEqual(len(copies), 2)
        self.assertTrue(all(e["status"] == "resolved" and e["target_sha256"] == e["staged_sha256"] for e in copies))

    def test_package_maps_agents_target_for_manifest(self) -> None:
        inspection, _, _ = self._run_stages(self.root)
        out = pipeline.package_plugin(self.staging, inspection, ["copilot", "claude", "agents"])
        self.assertEqual(out["manifest"]["targets"], ["copilot", "claude", "agent-skills"])
        self.assertFalse((self.plugin / "apm.yml").exists())

    @unittest.skipUnless(os.environ.get("APM_BIN"), "set APM_BIN to run the APM test deploy")
    def test_deploy_installs_and_uninstalls(self) -> None:
        for name in ("missing.md", "rule.md"):
            (self.plugin / "skills" / "s2" / "references" / name).unlink()
        (self.plugin / "skills" / "s1" / "SKILL.md").write_text(
            SKILL_MD.format(name="s1", body="See [shared](../../references/shared.md)."))
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", "drop bad links")
        inspection, _, _ = self._run_stages(self.root)
        pipeline.package_plugin(self.staging, inspection, ["claude"])
        result = pipeline.run_test_deploy(self.staging, self.root / "build" / "fixture",
                                          ["claude"], os.environ["APM_BIN"], inspection["skills"])
        self.assertTrue(result["passed"], result["findings"])
        self.assertIn(".claude", result["deployed_roots"])

    @unittest.skipUnless(os.environ.get("APM_BIN"), "set APM_BIN to run the APM pack test")
    def test_pack_bundle_global_install_has_copies(self) -> None:
        for name in ("missing.md", "rule.md"):
            (self.plugin / "skills" / "s2" / "references" / name).unlink()
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", "drop bad links")
        inspection, _, _ = self._run_stages(self.root)
        pipeline.package_plugin(self.staging, inspection, ["claude"])
        dist = self.root / "build" / "dist"
        packed = pipeline.pack_plugin(self.staging, dist, os.environ["APM_BIN"])
        self.assertTrue(packed["passed"], packed["steps"])
        home = Path(self.tmp.name) / "home"
        home.mkdir()
        env = dict(os.environ, HOME=str(home), NO_COLOR="1")
        subprocess.run([os.environ["APM_BIN"], "install", packed["bundles"][0], "--global", "--target", "claude"],
                       cwd=self.tmp.name, env=env, check=True, capture_output=True)
        for skill in ("s1", "s2"):
            installed = home / ".claude" / "skills" / skill / "scripts" / "tool.py"
            self.assertTrue(installed.is_file() and not installed.is_symlink())


if __name__ == "__main__":
    unittest.main()
