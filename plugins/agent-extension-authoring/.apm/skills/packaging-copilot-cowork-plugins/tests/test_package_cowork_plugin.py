"""
Tests for package_cowork_plugin.py
==================================

Purpose:
    Verify local Cowork ZIP packaging, package validation, and overwrite protection.

Key Input Dependencies:
    Temporary package directories and constants from cowork_package_constants.py.

Key Test Functions:
    write_png, create_package, run_packager,
    test_creates_rooted_zip_from_project_path, test_rejects_manifest_path_traversal,
    test_rejects_wrong_icon_dimensions, test_preserves_existing_output_by_default,
    test_overwrites_existing_output_only_when_requested,
    test_rejects_too_many_companion_files.

Output:
    Pytest results; all file-system fixtures are isolated under tmp_path.
"""

import json
import struct
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Tuple

import pytest

SCRIPTS_DIRECTORY = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIRECTORY))

from cowork_package_constants import (
    AGENT_SKILLS_KEY,
    APP_PACKAGE_DIRECTORY_NAME,
    COLOR_ICON_DIMENSIONS,
    COLOR_ICON_FILE_NAME,
    COLOR_ICON_KEY,
    ICONS_KEY,
    MANIFEST_FILE_NAME,
    MAX_COMPANION_FILES,
    OUTLINE_ICON_DIMENSIONS,
    OUTLINE_ICON_FILE_NAME,
    OUTLINE_ICON_KEY,
    NON_PACKAGE_DIRECTORY_NAMES,
    PNG_IHDR_CHUNK_TYPE,
    PNG_SIGNATURE,
    SKILL_FILE_NAME,
    SKILL_FOLDER_KEY,
    SKILLS_DIRECTORY_NAME,
)

PACKAGER_SCRIPT = SCRIPTS_DIRECTORY / "package_cowork_plugin.py"
TEST_SKILL_DIRECTORY_NAME = "sample-skill"


# Write the minimal PNG header fields checked by the local packager.
def write_png(path: Path, dimensions: Tuple[int, int]) -> None:
    """Write a PNG header carrying the requested width and height."""
    width, height = dimensions
    png_header = (
        PNG_SIGNATURE
        + struct.pack(">I", 13)
        + PNG_IHDR_CHUNK_TYPE
        + struct.pack(">II", width, height)
    )
    path.write_bytes(png_header)


# Create a valid package fixture using shared package-format constants.
def create_package(
    package_root: Path,
    color_dimensions: Tuple[int, int] = COLOR_ICON_DIMENSIONS,
) -> None:
    """Create a package tree with one registered skill and two icon files."""
    skill_path = package_root / SKILLS_DIRECTORY_NAME / TEST_SKILL_DIRECTORY_NAME
    skill_path.mkdir(parents=True)
    (skill_path / SKILL_FILE_NAME).write_text(
        "---\nname: sample-skill\ndescription: A sample skill.\n---\n",
        encoding="utf-8",
    )
    write_png(package_root / COLOR_ICON_FILE_NAME, color_dimensions)
    write_png(package_root / OUTLINE_ICON_FILE_NAME, OUTLINE_ICON_DIMENSIONS)
    manifest = {
        ICONS_KEY: {
            COLOR_ICON_KEY: COLOR_ICON_FILE_NAME,
            OUTLINE_ICON_KEY: OUTLINE_ICON_FILE_NAME,
        },
        AGENT_SKILLS_KEY: [
            {
                SKILL_FOLDER_KEY: (
                    f"./{SKILLS_DIRECTORY_NAME}/{TEST_SKILL_DIRECTORY_NAME}"
                )
            }
        ],
    }
    (package_root / MANIFEST_FILE_NAME).write_text(
        json.dumps(manifest),
        encoding="utf-8",
    )
    scripts_path = skill_path / "scripts"
    scripts_path.mkdir()
    (scripts_path / "helper.py").write_text("print('helper')\n", encoding="utf-8")
    for directory_name in NON_PACKAGE_DIRECTORY_NAMES:
        source_only_path = skill_path / directory_name
        source_only_path.mkdir()
        (source_only_path / "source-only.txt").write_text(
            "not required at Cowork runtime",
            encoding="utf-8",
        )


# Invoke the package script in a separate process as an end-user would.
def run_packager(
    plugin_path: Path,
    output_path: Path,
    *options: str,
) -> subprocess.CompletedProcess[str]:
    """Run the packager CLI and capture its output."""
    return subprocess.run(
        [
            sys.executable,
            str(PACKAGER_SCRIPT),
            "--plugin-path",
            str(plugin_path),
            "--output-path",
            str(output_path),
            *options,
        ],
        capture_output=True,
        check=False,
        text=True,
    )


# Check project-root input produces a ZIP with manifest paths at its root.
def test_creates_rooted_zip_from_project_path(tmp_path: Path) -> None:
    """Package a WIQD-style project and preserve appPackage-relative ZIP paths."""
    project_path = tmp_path / "project"
    package_root = project_path / APP_PACKAGE_DIRECTORY_NAME
    package_root.mkdir(parents=True)
    create_package(package_root)
    output_path = tmp_path / "dist" / "sample.zip"

    result = run_packager(project_path, output_path)

    assert result.returncode == 0, result.stderr
    with zipfile.ZipFile(output_path, "r") as archive:
        assert MANIFEST_FILE_NAME in archive.namelist()
        assert (
            f"{SKILLS_DIRECTORY_NAME}/{TEST_SKILL_DIRECTORY_NAME}/{SKILL_FILE_NAME}"
            in archive.namelist()
        )
        assert all(
            not any(part in NON_PACKAGE_DIRECTORY_NAMES for part in Path(name).parts)
            for name in archive.namelist()
        )
        assert (
            f"{SKILLS_DIRECTORY_NAME}/{TEST_SKILL_DIRECTORY_NAME}/scripts/helper.py"
            in archive.namelist()
        )
        assert archive.testzip() is None
    assert "Excluded source-only directories" in result.stdout


# Ensure a path traversal in a skill registration is rejected before output.
def test_rejects_manifest_path_traversal(tmp_path: Path) -> None:
    """Reject manifest skill paths that escape the package root."""
    package_root = tmp_path / "appPackage"
    package_root.mkdir()
    create_package(package_root)
    manifest_path = package_root / MANIFEST_FILE_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest[AGENT_SKILLS_KEY][0][SKILL_FOLDER_KEY] = "../outside"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    output_path = tmp_path / "package.zip"

    result = run_packager(package_root, output_path)

    assert result.returncode != 0
    assert not output_path.exists()


# Confirm icon dimensions are checked against the shared package contract.
def test_rejects_wrong_icon_dimensions(tmp_path: Path) -> None:
    """Reject a color icon that does not meet the M365 dimensions."""
    package_root = tmp_path / "appPackage"
    package_root.mkdir()
    invalid_dimensions = (COLOR_ICON_DIMENSIONS[0] - 1, COLOR_ICON_DIMENSIONS[1])
    create_package(package_root, color_dimensions=invalid_dimensions)
    output_path = tmp_path / "package.zip"

    result = run_packager(package_root, output_path)

    assert result.returncode != 0
    assert not output_path.exists()
    assert COLOR_ICON_FILE_NAME in result.stderr


# Verify the default mode never overwrites an existing destination.
def test_preserves_existing_output_by_default(tmp_path: Path) -> None:
    """Preserve an existing ZIP unless the caller passes --overwrite."""
    package_root = tmp_path / "appPackage"
    package_root.mkdir()
    create_package(package_root)
    output_path = tmp_path / "existing.zip"
    original_content = b"existing output"
    output_path.write_bytes(original_content)

    result = run_packager(package_root, output_path)

    assert result.returncode != 0
    assert output_path.read_bytes() == original_content


# Confirm the explicit overwrite option replaces an existing destination with a valid ZIP.
def test_overwrites_existing_output_only_when_requested(tmp_path: Path) -> None:
    """Replace an existing destination only when --overwrite is present."""
    package_root = tmp_path / "appPackage"
    package_root.mkdir()
    create_package(package_root)
    output_path = tmp_path / "existing.zip"
    output_path.write_bytes(b"old archive")

    result = run_packager(package_root, output_path, "--overwrite")

    assert result.returncode == 0, result.stderr
    with zipfile.ZipFile(output_path, "r") as archive:
        assert archive.testzip() is None


# Confirm packaged companion files are capped at Cowork's per-skill limit.
def test_rejects_too_many_companion_files(tmp_path: Path) -> None:
    """Reject a skill whose packaged companion files exceed the Cowork limit."""
    package_root = tmp_path / "appPackage"
    package_root.mkdir()
    create_package(package_root)
    references_path = (
        package_root / SKILLS_DIRECTORY_NAME / TEST_SKILL_DIRECTORY_NAME / "references"
    )
    references_path.mkdir()
    for index in range(MAX_COMPANION_FILES):
        (references_path / f"note-{index}.md").write_text("note", encoding="utf-8")
    output_path = tmp_path / "package.zip"

    result = run_packager(package_root, output_path)

    assert result.returncode != 0
    assert not output_path.exists()
    assert "companion files" in result.stderr