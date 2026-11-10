"""
Tests for the Cowork bundler and scaffolder
===========================================

Purpose:
    Verify that skills over the 20-companion-file limit are bundled with correct link
    rewriting, that unsupported and excluded files are filtered cleanly, and that an APM
    plugin can be scaffolded into a package the packager accepts.

Key Input Dependencies:
    Temporary APM-style plugins under tmp_path; bundle_skill_companions.py,
    scaffold_cowork_package.py and package_cowork_plugin.py in this skill's scripts folder.

Key Test Functions:
    test_small_skill_is_copied, test_large_skill_is_bundled, test_excluded_and_unsupported_*,
    test_loose_guides_are_merged, test_scripts_*, test_scaffold_*.

Output:
    Pytest results; all file-system fixtures are isolated under tmp_path.
"""

import json
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Dict, List

import pytest

SCRIPTS_DIRECTORY = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIRECTORY))

from bundle_skill_companions import bundle_skill  # noqa: E402
from cowork_content_checks import validate_markdown_links  # noqa: E402

SCAFFOLD_SCRIPT = SCRIPTS_DIRECTORY / "scaffold_cowork_package.py"
PACKAGER_SCRIPT = SCRIPTS_DIRECTORY / "package_cowork_plugin.py"
FRONTMATTER = "---\nname: {name}\ndescription: A test skill.\n---\n"


# Write text to a path, creating parent folders.
def put(path: Path, text: str) -> None:
    """Write UTF-8 text to path, creating parents."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


# Build a skill with guide folders, each holding several guides and an acceptance file.
def make_big_skill(root: Path, folders: int = 8, per_folder: int = 3) -> Path:
    """Create a skill whose companion count exceeds 20."""
    skill = root / "big-skill"
    links = []
    for f in range(folders):
        for g in range(per_folder):
            name = "acceptance-criteria.md" if g == per_folder - 1 else f"guide-{g}.md"
            body = f"# Guide {f}-{g}\n\n## Contents\n\n- [Steps](#steps)\n\n## Steps\n\nBody {f}-{g}.\n"
            if g == 0 and f + 1 < folders:
                body += f"\nSee [next](../area{f + 1}/guide-0.md#guide-{f + 1}-0).\n"
            put(skill / "references" / f"area{f}" / name, body)
        links.append(f"[area {f}](references/area{f}/guide-0.md)")
    put(skill / "SKILL.md", FRONTMATTER.format(name="big-skill") + "# Big\n\n" + " ".join(links) + "\n")
    return skill


# A skill within the limit is copied without bundling.
def test_small_skill_is_copied(tmp_path: Path) -> None:
    """Do not bundle when the companion count fits."""
    skill = tmp_path / "small"
    put(skill / "SKILL.md", FRONTMATTER.format(name="small") + "[g](references/g.md)\n")
    put(skill / "references" / "g.md", "# G\n\ntext\n")
    report = bundle_skill(skill, tmp_path / "out" / "small")
    assert report["bundles"] == [] and report["companions_after"] == 1
    assert (tmp_path / "out" / "small" / "references" / "g.md").read_text() == "# G\n\ntext\n"


# A large skill is bundled under the limit, links resolve, and acceptance criteria come last.
def test_large_skill_is_bundled(tmp_path: Path) -> None:
    """Bundle folders, keep every link valid, and place acceptance criteria last."""
    skill = make_big_skill(tmp_path)
    out = tmp_path / "out" / "big-skill"
    report = bundle_skill(skill, out)
    assert report["companions_before"] == 24 and report["companions_after"] == 8
    bundle = (out / "references" / "area0.md").read_text(encoding="utf-8")
    assert bundle.index("Guide 0-0") < bundle.index("Guide 0-2")  # acceptance-criteria (g=2) last
    assert "## Contents" not in bundle
    errors, warnings = validate_markdown_links(out)
    assert errors == [] and warnings == [], (errors, warnings)
    assert "## Cowork build" in (out / "SKILL.md").read_text(encoding="utf-8")


# Source files stay untouched.
def test_source_skill_is_not_modified(tmp_path: Path) -> None:
    """The bundler never edits the source skill."""
    skill = make_big_skill(tmp_path)
    before = {p.relative_to(skill).as_posix(): p.read_bytes() for p in skill.rglob("*") if p.is_file()}
    bundle_skill(skill, tmp_path / "out" / "big-skill")
    after = {p.relative_to(skill).as_posix(): p.read_bytes() for p in skill.rglob("*") if p.is_file()}
    assert before == after


# Unsupported extensions and excluded files are filtered; links to them become plain text.
def test_excluded_and_unsupported_files_are_filtered(tmp_path: Path) -> None:
    """Filter .mmd and named files, rewriting links to plain text with a note."""
    skill = tmp_path / "s"
    put(skill / "SKILL.md", FRONTMATTER.format(name="s") + "[flow](references/flow.mmd) [app](scripts/app.py) [ok](scripts/ok.py)\n")
    put(skill / "references" / "flow.mmd", "flowchart TD\n A-->B\n")
    put(skill / "scripts" / "app.py", "print('server')\n")
    put(skill / "scripts" / "ok.py", "print('ok')\n")
    out = tmp_path / "out" / "s"
    report = bundle_skill(skill, out, exclude_files=["scripts/app.py"])
    assert report["files_filtered"] == ["references/flow.mmd", "scripts/app.py"]
    text = (out / "SKILL.md").read_text(encoding="utf-8")
    assert "[flow]" not in text and "flow (file type not supported in Cowork)" in text
    assert "app (file type not supported in Cowork)" in text and "[ok](scripts/ok.py)" in text
    assert not (out / "references" / "flow.mmd").exists() and (out / "scripts" / "ok.py").exists()
    assert validate_markdown_links(out)[0] == []


# --drop-extensions removes a normally supported type; --allow-extensions keeps a rejected one.
def test_allow_and_drop_extensions(tmp_path: Path) -> None:
    """Honor caller changes to the extension allowlist."""
    skill = tmp_path / "s"
    put(skill / "SKILL.md", FRONTMATTER.format(name="s") + "text\n")
    put(skill / "references" / "a.csv", "a,b\n")
    put(skill / "references" / "b.mmd", "flowchart TD\n")
    out = tmp_path / "out" / "s"
    bundle_skill(skill, out, allow_extensions=[".mmd"], drop_extensions=["csv"])
    assert (out / "references" / "b.mmd").exists() and not (out / "references" / "a.csv").exists()


# Loose guides are merged only when folder bundles are not enough.
def test_loose_guides_are_merged(tmp_path: Path) -> None:
    """Merge single-file guides into references/other.md to reach the limit."""
    skill = make_big_skill(tmp_path, folders=8, per_folder=2)   # 16 files -> 8 bundles
    for index in range(14):
        put(skill / "references" / f"solo-{index}.md", f"# Solo {index}\n\ntext\n")
    out = tmp_path / "out" / "big-skill"
    report = bundle_skill(skill, out, max_companions=12)
    assert "references/other.md" in report["bundles"]
    assert report["companions_after"] <= 12


# Scripts are only dropped when asked, and a clear error is raised otherwise.
def test_scripts_dropped_only_when_requested(tmp_path: Path) -> None:
    """Fail with guidance when still over the limit, and succeed with the flag."""
    skill = make_big_skill(tmp_path, folders=4, per_folder=3)
    for index in range(6):
        put(skill / "scripts" / f"s{index}.py", "print(1)\n")
    with pytest.raises(ValueError, match="--drop-scripts-if-needed"):
        bundle_skill(skill, tmp_path / "a" / "big-skill", max_companions=8)
    report = bundle_skill(skill, tmp_path / "b" / "big-skill", max_companions=8, drop_scripts_if_needed=True)
    assert report["scripts_dropped"] is True and report["companions_after"] <= 8


# Build a small APM plugin directory for scaffolding.
def make_plugin(root: Path) -> Path:
    """Create plugin.json and two skills, one large enough to need bundling."""
    plugin = root / "my-plugin"
    put(plugin / ".claude-plugin" / "plugin.json",
        json.dumps({"name": "my-plugin", "version": "2.3.4", "description": "Does useful things. Plus more detail here."}))
    make_big_skill(plugin / ".apm" / "skills")
    put(plugin / ".apm" / "skills" / "tiny" / "SKILL.md", FRONTMATTER.format(name="tiny") + "hello\n")
    return plugin


# Run the scaffold CLI with required developer arguments.
def run_scaffold(plugin: Path, output: Path, *extra: str) -> subprocess.CompletedProcess:
    """Invoke scaffold_cowork_package.py and capture its output."""
    return subprocess.run(
        [sys.executable, str(SCAFFOLD_SCRIPT), "--apm-plugin", str(plugin), "--output", str(output),
         "--developer-name", "Example Org", "--website-url", "https://example.org",
         "--privacy-url", "https://example.org/privacy", "--terms-url", "https://example.org/terms", *extra],
        capture_output=True, text=True, check=False,
    )


# Scaffolding then packaging yields a valid ZIP with the expected manifest.
def test_scaffold_then_package_end_to_end(tmp_path: Path) -> None:
    """Scaffold an APM plugin and zip it with the packager."""
    plugin = make_plugin(tmp_path)
    output = tmp_path / "build" / "appPackage"
    result = run_scaffold(plugin, output)
    assert result.returncode == 0, result.stderr
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "2.3.4" and manifest["name"]["short"] == "My Plugin"
    assert manifest["description"]["short"] == "Does useful things."
    assert [s["folder"] for s in manifest["agentSkills"]] == ["skills/big-skill", "skills/tiny"]
    zip_path = tmp_path / "dist" / "plugin.zip"
    packaged = subprocess.run([sys.executable, str(PACKAGER_SCRIPT), "--plugin-path", str(output),
                               "--output-path", str(zip_path)], capture_output=True, text=True, check=False)
    assert packaged.returncode == 0, packaged.stderr
    with zipfile.ZipFile(zip_path) as archive:
        assert archive.testzip() is None and "manifest.json" in archive.namelist()


# The app id is stable across rebuilds and the output folder is never overwritten.
def test_scaffold_stable_id_and_no_overwrite(tmp_path: Path) -> None:
    """Derive the same app id for the same plugin, and refuse an existing folder."""
    plugin = make_plugin(tmp_path)
    first = tmp_path / "one" / "appPackage"
    second = tmp_path / "two" / "appPackage"
    assert run_scaffold(plugin, first).returncode == 0 and run_scaffold(plugin, second).returncode == 0
    ids = [json.loads((p / "manifest.json").read_text())["id"] for p in (first, second)]
    assert ids[0] == ids[1]
    again = run_scaffold(plugin, first)
    assert again.returncode != 0 and "already exists" in again.stderr


# Developer URLs are required, never invented.
def test_scaffold_requires_privacy_and_terms_urls(tmp_path: Path) -> None:
    """The scaffolder fails without privacy and terms URLs."""
    plugin = make_plugin(tmp_path)
    result = subprocess.run([sys.executable, str(SCAFFOLD_SCRIPT), "--apm-plugin", str(plugin),
                             "--output", str(tmp_path / "x" / "appPackage"), "--developer-name", "Org",
                             "--website-url", "https://example.org"], capture_output=True, text=True, check=False)
    assert result.returncode != 0 and "--privacy-url" in result.stderr
