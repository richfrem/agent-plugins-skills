"""
Tests for Cowork package content checks
=======================================

Purpose:
    Verify manifest metadata checks, SKILL.md frontmatter checks, Markdown link checks,
    and the packager's refusal of unsupported file types.

Key Input Dependencies:
    Temporary skill folders under tmp_path; cowork_content_checks.py,
    cowork_markdown_utils.py and package_cowork_plugin.py in this skill's scripts folder.

Key Test Functions:
    test_manifest_fields_*, test_frontmatter_*, test_links_*, test_packager_*.

Output:
    Pytest results; all file-system fixtures are isolated under tmp_path.
"""

import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIRECTORY = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIRECTORY))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cowork_content_checks import (  # noqa: E402
    validate_manifest_fields,
    validate_markdown_links,
    validate_skill_frontmatter,
)
from cowork_markdown_utils import parse_frontmatter, split_frontmatter  # noqa: E402
from test_package_cowork_plugin import (  # noqa: E402
    MANIFEST_FILE_NAME,
    SKILL_FILE_NAME,
    SKILLS_DIRECTORY_NAME,
    TEST_SKILL_DIRECTORY_NAME,
    VALID_METADATA,
    create_package,
    run_packager,
)


# Build a manifest dictionary with one field replaced.
def manifest_with(**changes):
    """Return a copy of the valid metadata with the given top-level keys replaced."""
    manifest = json.loads(json.dumps(VALID_METADATA))
    manifest.update(changes)
    return manifest


# Valid metadata produces no problems.
def test_manifest_fields_valid() -> None:
    """Accept complete, in-range manifest metadata."""
    assert validate_manifest_fields(manifest_with()) == []


# Each bad field is reported by name.
@pytest.mark.parametrize(
    "changes, expected",
    [
        ({"id": "not-a-guid"}, "id must be a GUID"),
        ({"version": "1.0"}, "version must look like"),
        ({"accentColor": "blue"}, "accentColor"),
        ({"name": {"short": "x" * 31, "full": "Full"}}, "name.short is 31 characters"),
        ({"description": {"short": "x" * 81, "full": "Full"}}, "description.short is 81 characters"),
        ({"developer": {"name": "Org", "websiteUrl": "http://insecure.example",
                        "privacyUrl": "https://example.org/p", "termsOfUseUrl": "https://example.org/t"}},
         "websiteUrl must start with https://"),
        ({"developer": {"name": "Org", "websiteUrl": "https://example.org",
                        "termsOfUseUrl": "https://example.org/t"}}, "privacyUrl"),
        ({"manifestVersion": ""}, "manifestVersion is required"),
    ],
)
def test_manifest_fields_reject_bad_values(changes, expected) -> None:
    """Report out-of-range or missing manifest metadata."""
    problems = validate_manifest_fields(manifest_with(**changes))
    assert any(expected in problem for problem in problems), problems


# Write a skill folder with the given SKILL.md text.
def write_skill(root: Path, name: str, text: str) -> Path:
    """Create root/name/SKILL.md and return the skill folder."""
    skill = root / name
    skill.mkdir(parents=True)
    (skill / SKILL_FILE_NAME).write_bytes(text.encode("utf-8"))
    return skill


# Frontmatter in the folded style this repo's own skills use must parse.
def test_frontmatter_folded_description_and_crlf(tmp_path: Path) -> None:
    """Accept folded scalars and CRLF line endings."""
    text = "---\r\nname: sample\r\ndescription: >-\r\n  First line\r\n  second line.\r\n---\r\n# Body\r\n"
    skill = write_skill(tmp_path, "sample", text)
    assert validate_skill_frontmatter(skill) == []
    front, _body = split_frontmatter(text)
    assert parse_frontmatter(front)["description"] == "First line second line."


# Name, description and presence problems are all reported.
@pytest.mark.parametrize(
    "text, expected",
    [
        ("# no frontmatter\n", "must start with YAML frontmatter"),
        ("---\nname: other\ndescription: ok\n---\n", "must equal its folder name"),
        ("---\nname: Bad_Name\ndescription: ok\n---\n", "lowercase letters"),
        ("---\nname: sample\n---\n", "non-empty description"),
        ("---\nname: sample\ndescription: " + "x" * 1025 + "\n---\n", "limit is 1024"),
    ],
)
def test_frontmatter_rejects_bad_skill(tmp_path: Path, text: str, expected: str) -> None:
    """Report frontmatter that does not match Agent Skills rules."""
    skill = write_skill(tmp_path, "sample", text)
    problems = validate_skill_frontmatter(skill)
    assert any(expected in problem for problem in problems), problems


# Build a skill with a linking SKILL.md and two companion files.
def linked_skill(tmp_path: Path, body: str) -> Path:
    """Create a valid skill whose SKILL.md body is the given text."""
    skill = write_skill(tmp_path, "sample", "---\nname: sample\ndescription: ok\n---\n" + body)
    (skill / "references").mkdir()
    (skill / "references" / "guide.md").write_text("# Guide\n\n## Steps\n\ntext\n", encoding="utf-8")
    return skill


# A link to a missing file and a link to a directory are both errors.
def test_links_missing_file_and_directory(tmp_path: Path) -> None:
    """Report broken file links and links that point at a directory."""
    skill = linked_skill(tmp_path, "[a](references/missing.md) [b](references/)\n")
    errors, _warnings = validate_markdown_links(skill)
    assert any("does not exist" in e for e in errors), errors
    assert any("is a directory" in e for e in errors), errors


# A good link and a good anchor produce neither errors nor warnings.
def test_links_valid_file_and_anchor(tmp_path: Path) -> None:
    """Accept links to existing files and existing headings."""
    skill = linked_skill(tmp_path, "[a](references/guide.md#steps)\n")
    assert validate_markdown_links(skill) == ([], [])


# A missing heading is only a warning.
def test_links_missing_anchor_is_warning(tmp_path: Path) -> None:
    """Warn, not fail, when a heading anchor is missing."""
    skill = linked_skill(tmp_path, "[a](references/guide.md#nope)\n")
    errors, warnings = validate_markdown_links(skill)
    assert errors == []
    assert any("#nope" in w for w in warnings), warnings


# Links outside the skill, in code fences, and external links are handled correctly.
def test_links_escape_fence_and_external(tmp_path: Path) -> None:
    """Fail on links leaving the skill; ignore code fences and external URLs."""
    skill = linked_skill(
        tmp_path,
        "[x](../other/file.md)\n[ok](https://example.org/a.md)\n```\n[ignored](nothing.md)\n```\n",
    )
    errors, _warnings = validate_markdown_links(skill)
    assert len(errors) == 1 and "leaves the skill folder" in errors[0], errors


# The packager refuses packages with broken links unless checks are skipped.
def test_packager_rejects_broken_link_and_can_skip(tmp_path: Path) -> None:
    """A directory link fails packaging; --skip-content-checks allows it."""
    package_root = tmp_path / "appPackage"
    package_root.mkdir()
    create_package(package_root)
    skill_md = package_root / SKILLS_DIRECTORY_NAME / TEST_SKILL_DIRECTORY_NAME / SKILL_FILE_NAME
    skill_md.write_text(skill_md.read_text(encoding="utf-8") + "\n[dir](scripts/)\n", encoding="utf-8")
    blocked = run_packager(package_root, tmp_path / "blocked.zip")
    assert blocked.returncode != 0 and "is a directory" in blocked.stderr
    allowed = run_packager(package_root, tmp_path / "allowed.zip", "--skip-content-checks")
    assert allowed.returncode == 0, allowed.stderr


# Incomplete manifest metadata blocks packaging.
def test_packager_rejects_incomplete_manifest(tmp_path: Path) -> None:
    """A manifest without developer details cannot be packaged."""
    package_root = tmp_path / "appPackage"
    package_root.mkdir()
    create_package(package_root)
    manifest_path = package_root / MANIFEST_FILE_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    del manifest["developer"]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = run_packager(package_root, tmp_path / "out.zip")
    assert result.returncode != 0 and "developer must be an object" in result.stderr


# A file type Microsoft 365 Copilot rejects (.mmd) blocks packaging; --allow-extensions overrides.
def test_packager_rejects_unsupported_extension(tmp_path: Path) -> None:
    """Refuse .mmd skill files, and accept them only when explicitly allowed."""
    package_root = tmp_path / "appPackage"
    package_root.mkdir()
    create_package(package_root)
    diagram = package_root / SKILLS_DIRECTORY_NAME / TEST_SKILL_DIRECTORY_NAME / "references" / "flow.mmd"
    diagram.parent.mkdir()
    diagram.write_text("flowchart TD\n A-->B\n", encoding="utf-8")
    blocked = run_packager(package_root, tmp_path / "blocked.zip")
    assert blocked.returncode != 0 and "flow.mmd" in blocked.stderr
    allowed = run_packager(package_root, tmp_path / "allowed.zip", "--allow-extensions", ".mmd")
    assert allowed.returncode == 0, allowed.stderr
