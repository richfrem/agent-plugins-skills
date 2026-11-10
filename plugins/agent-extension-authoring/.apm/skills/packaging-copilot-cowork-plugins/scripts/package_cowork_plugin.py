#!/usr/bin/env python
"""
package_cowork_plugin.py (CLI)
==============================

Purpose:
    Build a ZIP from a Cowork M365 app-package directory for manual/local packaging.

Usage Examples:
    python scripts/package_cowork_plugin.py --plugin-path ./plugin \
        --output-path ./dist/plugin.zip
    python scripts/package_cowork_plugin.py --plugin-path ./plugin/appPackage \
        --output-path ./dist/plugin.zip --overwrite

Key Input Dependencies:
    A directory containing manifest.json, Cowork icons, and registered skill folders.
    Use scaffold_cowork_package.py to create that directory from an APM plugin.

Output:
    A ZIP with manifest.json at its root. Does not provision, publish, or share.
    Before zipping it also checks manifest metadata, SKILL.md frontmatter, and relative
    Markdown links, printing anchor warnings and failing on errors (--skip-content-checks
    turns this off; not recommended).

Key Functions:
    resolve_package_root, resolve_manifest_path, validate_icons,
    validate_skill_entries, validate_companion_limits, collect_package_files,
    validate_companion_extensions, run_content_checks, validate_package,
    validate_archive, publish_archive, package_plugin, create_parser, main.

Script Dependencies:
    Python standard library only; cowork_package_constants.py and cowork_content_checks.py
    in this skill.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import struct
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Dict, List, Optional, Sequence, Tuple

from cowork_content_checks import (
    summarize_problems,
    validate_manifest_fields,
    validate_markdown_links,
    validate_skill_frontmatter,
)
from cowork_package_constants import (
    AGENT_SKILLS_KEY,
    APP_PACKAGE_DIRECTORY_NAME,
    FORBIDDEN_PATH_CHARACTERS,
    ICON_DIMENSIONS,
    ICON_FILE_NAMES,
    ICONS_KEY,
    MANIFEST_FILE_NAME,
    MAX_COMPANION_FILE_BYTES,
    MAX_COMPANION_FILES,
    MAX_COMPANION_TOTAL_BYTES,
    NON_PACKAGE_DIRECTORY_NAMES,
    PNG_HEADER_LENGTH,
    PNG_IHDR_CHUNK_TYPE,
    PNG_SIGNATURE,
    SENSITIVE_FILE_NAMES,
    SENSITIVE_FILE_SUFFIXES,
    SKILL_FILE_NAME,
    SKILL_FOLDER_KEY,
    SKILLS_DIRECTORY_NAME,
    SUPPORTED_COMPANION_EXTENSIONS,
    TEMP_ARCHIVE_PREFIX,
    ZIP_COMPRESSION_LEVEL,
    ZIP_FILE_SUFFIX,
)


# Resolve the project or package folder without guessing between two manifests.
def resolve_package_root(plugin_path: Path) -> Path:
    """Resolve a WIQD project root or direct appPackage folder."""
    if plugin_path.is_symlink():
        raise ValueError("The plugin path must not be a symbolic link.")
    if not plugin_path.is_dir():
        raise ValueError("The plugin path must be an existing directory.")

    direct_manifest = plugin_path / MANIFEST_FILE_NAME
    nested_root = plugin_path / APP_PACKAGE_DIRECTORY_NAME
    if nested_root.is_symlink():
        raise ValueError(f"{APP_PACKAGE_DIRECTORY_NAME} must not be a symbolic link.")
    nested_manifest = nested_root / MANIFEST_FILE_NAME
    if direct_manifest.is_file() and nested_manifest.is_file():
        raise ValueError(
            "The plugin path contains two package manifests; pass the intended "
            "appPackage directory explicitly."
        )
    if direct_manifest.is_file():
        return plugin_path.resolve(strict=True)
    if nested_manifest.is_file():
        return nested_root.resolve(strict=True)
    raise ValueError(
        "Expected manifest.json in the plugin path or its appPackage subdirectory."
    )


# Resolve a manifest path while rejecting absolute paths and traversal.
def resolve_manifest_path(package_root: Path, reference: Any, label: str) -> Path:
    """Resolve a safe package-relative path referenced by the manifest."""
    if not isinstance(reference, str) or not reference.strip():
        raise ValueError(f"{label} must be a non-empty relative path.")
    if any(character in reference for character in FORBIDDEN_PATH_CHARACTERS):
        raise ValueError(f"{label} contains a forbidden path character.")

    normalized_reference = reference[2:] if reference.startswith("./") else reference
    relative_path = PurePosixPath(normalized_reference)
    windows_path = PureWindowsPath(normalized_reference)
    if (
        not normalized_reference
        or relative_path.is_absolute()
        or windows_path.is_absolute()
        or windows_path.drive
        or ".." in relative_path.parts
    ):
        raise ValueError(f"{label} must stay within the package directory.")

    resolved_path = (package_root / Path(*relative_path.parts)).resolve(strict=True)
    try:
        resolved_path.relative_to(package_root)
    except ValueError as exc:
        raise ValueError(f"{label} resolves outside the package directory.") from exc
    return resolved_path


# Check that each declared icon is a PNG with the platform-required dimensions.
def validate_icons(package_root: Path, manifest: Dict[str, Any]) -> List[Path]:
    """Validate manifest icon references and return their resolved paths."""
    icons = manifest.get(ICONS_KEY)
    if not isinstance(icons, dict):
        raise ValueError(f"manifest.json must contain an {ICONS_KEY!r} object.")

    icon_paths: List[Path] = []
    for icon_key, expected_dimensions in ICON_DIMENSIONS.items():
        icon_path = resolve_manifest_path(
            package_root,
            icons.get(icon_key),
            f"{ICONS_KEY}.{icon_key}",
        )
        if not icon_path.is_file():
            raise ValueError(f"Icon is not a file: {icon_path}")
        if icon_path.name != ICON_FILE_NAMES[icon_key]:
            raise ValueError(
                f"{ICONS_KEY}.{icon_key} must reference "
                f"{ICON_FILE_NAMES[icon_key]!r}."
            )
        with icon_path.open("rb") as icon_file:
            header = icon_file.read(PNG_HEADER_LENGTH)
        if (
            len(header) < PNG_HEADER_LENGTH
            or header[: len(PNG_SIGNATURE)] != PNG_SIGNATURE
            or header[12:16] != PNG_IHDR_CHUNK_TYPE
        ):
            raise ValueError(f"Icon is not a valid PNG header: {icon_path}")
        dimensions = struct.unpack(">II", header[16:24])
        if dimensions != expected_dimensions:
            raise ValueError(
                f"{icon_key} icon {icon_path.name!r} must be "
                f"{expected_dimensions[0]}x"
                f"{expected_dimensions[1]} pixels; found "
                f"{dimensions[0]}x{dimensions[1]}."
            )
        icon_paths.append(icon_path)
    return icon_paths


# Confirm each registered skill points to a folder containing its entry point.
def validate_skill_entries(package_root: Path, manifest: Dict[str, Any]) -> List[Path]:
    """Validate the Agent Skills folders registered by the package manifest."""
    skill_entries = manifest.get(AGENT_SKILLS_KEY)
    if not isinstance(skill_entries, list) or not skill_entries:
        raise ValueError(f"manifest.json must register at least one {AGENT_SKILLS_KEY}.")

    skill_paths: List[Path] = []
    seen_paths = set()
    for index, entry in enumerate(skill_entries):
        if not isinstance(entry, dict):
            raise ValueError(f"{AGENT_SKILLS_KEY}[{index}] must be an object.")
        skill_path = resolve_manifest_path(
            package_root,
            entry.get(SKILL_FOLDER_KEY),
            f"{AGENT_SKILLS_KEY}[{index}].{SKILL_FOLDER_KEY}",
        )
        relative_path = skill_path.relative_to(package_root)
        if not relative_path.parts or relative_path.parts[0] != SKILLS_DIRECTORY_NAME:
            raise ValueError(
                f"{AGENT_SKILLS_KEY}[{index}] must reference a folder under "
                f"{SKILLS_DIRECTORY_NAME!r}."
            )
        if skill_path in seen_paths:
            raise ValueError(f"Duplicate skill folder reference: {skill_path}")
        if not skill_path.is_dir():
            raise ValueError(f"Skill folder is not a directory: {skill_path}")
        if not (skill_path / SKILL_FILE_NAME).is_file():
            raise ValueError(f"Skill folder is missing {SKILL_FILE_NAME}: {skill_path}")
        seen_paths.add(skill_path)
        skill_paths.append(skill_path)
    return skill_paths


# Enforce the per-skill companion file count and size limits Cowork applies on upload.
def validate_companion_limits(skill_paths: List[Path], package_files: List[Path]) -> None:
    """Reject skills whose packaged companion files exceed Cowork limits."""
    for skill_path in skill_paths:
        companions = [
            path
            for path in package_files
            if skill_path in path.parents and path != skill_path / SKILL_FILE_NAME
        ]
        if len(companions) > MAX_COMPANION_FILES:
            raise ValueError(
                f"Skill {skill_path.name!r} has {len(companions)} companion files; "
                f"Cowork allows {MAX_COMPANION_FILES}."
            )
        sizes = [path.stat().st_size for path in companions]
        if any(size > MAX_COMPANION_FILE_BYTES for size in sizes):
            raise ValueError(
                f"Skill {skill_path.name!r} has a companion file over "
                f"{MAX_COMPANION_FILE_BYTES} bytes."
            )
        if sum(sizes) > MAX_COMPANION_TOTAL_BYTES:
            raise ValueError(
                f"Skill {skill_path.name!r} companion files exceed "
                f"{MAX_COMPANION_TOTAL_BYTES} bytes in total."
            )


# Reject skill files whose extension Microsoft 365 Copilot does not support.
def validate_companion_extensions(
    skill_paths: List[Path],
    package_files: List[Path],
    allowed: frozenset = SUPPORTED_COMPANION_EXTENSIONS,
) -> None:
    """Fail when a skill contains a file type Cowork publish validation rejects (for example .mmd)."""
    offending = sorted(
        path.as_posix()
        for path in package_files
        if path.suffix.lower() not in allowed
        and any(skill_path in path.parents for skill_path in skill_paths)
    )
    if offending:
        raise ValueError(
            "These skill files use extensions Microsoft 365 Copilot does not support: "
            + ", ".join(offending)
            + ". Rebuild with scaffold_cowork_package.py or bundle_skill_companions.py, which filter them out, "
            "remove the files, or pass --allow-extensions if Microsoft has confirmed the type."
        )


# Inventory regular package files and reject links, hidden files, and likely secrets.
def collect_package_files(package_root: Path) -> Tuple[List[Path], List[Path]]:
    """Return package files and omitted source-only directories."""
    package_files: List[Path] = []
    omitted_directories: List[Path] = []
    for current_root, directory_names, file_names in os.walk(
        package_root,
        topdown=True,
        followlinks=False,
    ):
        current_path = Path(current_root)
        for directory_name in list(directory_names):
            directory_path = current_path / directory_name
            if directory_path.is_symlink():
                raise ValueError(f"Package must not contain symbolic links: {directory_path}")
            if directory_name.lower() in NON_PACKAGE_DIRECTORY_NAMES:
                omitted_directories.append(directory_path)
                directory_names.remove(directory_name)
                continue
            if directory_name.startswith("."):
                raise ValueError(f"Package must not contain hidden paths: {directory_path}")
        for file_name in file_names:
            file_path = current_path / file_name
            relative_path = file_path.relative_to(package_root)
            if file_path.is_symlink():
                raise ValueError(f"Package must not contain symbolic links: {file_path}")
            if any(part.startswith(".") for part in relative_path.parts):
                raise ValueError(f"Package must not contain hidden paths: {file_path}")
            lowered_name = file_name.lower()
            if (
                lowered_name in SENSITIVE_FILE_NAMES
                or file_path.suffix.lower() in SENSITIVE_FILE_SUFFIXES
            ):
                raise ValueError(f"Likely sensitive file is not packageable: {file_path}")
            if not file_path.is_file():
                raise ValueError(f"Package entries must be regular files: {file_path}")
            package_files.append(file_path)
    sorted_files = sorted(
        package_files,
        key=lambda path: path.relative_to(package_root).as_posix(),
    )
    sorted_omissions = sorted(
        omitted_directories,
        key=lambda path: path.relative_to(package_root).as_posix(),
    )
    return sorted_files, sorted_omissions


# Run manifest, frontmatter and link checks; print warnings and raise on errors.
def run_content_checks(manifest: Dict[str, Any], skill_paths: List[Path]) -> None:
    """Fail on content errors that the structural checks cannot see; print warnings."""
    errors: List[str] = validate_manifest_fields(manifest)
    warnings: List[str] = []
    for skill_path in skill_paths:
        errors.extend(validate_skill_frontmatter(skill_path))
        link_errors, link_warnings = validate_markdown_links(skill_path)
        errors.extend(link_errors)
        warnings.extend(link_warnings)
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if errors:
        raise ValueError(summarize_problems(errors))


# Validate package metadata and ensure every referenced file is in the archive set.
def validate_package(
    package_root: Path,
    check_content: bool = True,
    allowed_extensions: frozenset = SUPPORTED_COMPANION_EXTENSIONS,
) -> Tuple[List[Path], List[Path]]:
    """Validate package essentials and return files plus source-only omissions."""
    manifest_path = package_root / MANIFEST_FILE_NAME
    if manifest_path.is_symlink():
        raise ValueError("manifest.json must not be a symbolic link.")
    try:
        with manifest_path.open("r", encoding="utf-8") as manifest_file:
            manifest = json.load(manifest_file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"manifest.json is not valid JSON: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError("manifest.json must contain a JSON object.")

    icon_paths = validate_icons(package_root, manifest)
    skill_paths = validate_skill_entries(package_root, manifest)
    package_files, omitted_directories = collect_package_files(package_root)
    validate_companion_limits(skill_paths, package_files)
    validate_companion_extensions(skill_paths, package_files, allowed_extensions)
    if check_content:
        run_content_checks(manifest, skill_paths)
    included_files = set(package_files)
    required_files = {manifest_path, *icon_paths}
    for skill_path in skill_paths:
        required_files.add(skill_path / SKILL_FILE_NAME)
    missing_files = required_files - included_files
    if missing_files:
        missing_names = ", ".join(sorted(path.as_posix() for path in missing_files))
        raise ValueError(f"Required package files are missing from the archive: {missing_names}")
    return package_files, omitted_directories


# Confirm the completed temporary ZIP has exactly the inventoried package files.
def validate_archive(archive_path: Path, package_root: Path, package_files: List[Path]) -> None:
    """Check ZIP integrity and the archive member inventory."""
    expected_names = {
        file_path.relative_to(package_root).as_posix() for file_path in package_files
    }
    with zipfile.ZipFile(archive_path, "r") as archive:
        damaged_member = archive.testzip()
        if damaged_member is not None:
            raise ValueError(f"ZIP integrity check failed for {damaged_member!r}.")
        actual_names = set(archive.namelist())
    if actual_names != expected_names:
        raise ValueError("ZIP contents do not match the validated package inventory.")


# Publish the verified temporary archive without overwriting by default.
def publish_archive(temporary_path: Path, output_path: Path, overwrite: bool) -> None:
    """Move a verified temporary archive to its requested destination."""
    if overwrite:
        os.replace(temporary_path, output_path)
        return

    output_created = False
    try:
        with output_path.open("xb") as output_file:
            output_created = True
            with temporary_path.open("rb") as archive_file:
                shutil.copyfileobj(archive_file, output_file)
            output_file.flush()
            os.fsync(output_file.fileno())
    except OSError:
        if output_created and output_path.exists():
            output_path.unlink()
        raise


# Build a ZIP from a validated package directory and preserve an existing ZIP by default.
def package_plugin(
    plugin_path: Path,
    output_path: Path,
    overwrite: bool,
    check_content: bool = True,
    allow_extensions: Sequence[str] = (),
) -> Tuple[Path, List[Path]]:
    """Create a verified ZIP and return source-only directories it omitted."""
    package_root = resolve_package_root(plugin_path)
    allowed = frozenset(
        SUPPORTED_COMPANION_EXTENSIONS | {("." + e.strip().lstrip(".")).lower() for e in allow_extensions if e.strip()}
    )
    package_files, omitted_directories = validate_package(package_root, check_content, allowed)
    if output_path.is_symlink():
        raise ValueError("The output path must not be a symbolic link.")
    resolved_output = output_path.resolve()
    try:
        resolved_output.relative_to(package_root)
    except ValueError:
        pass
    else:
        raise ValueError("The output ZIP must be outside the package directory.")
    if resolved_output.suffix.lower() != ZIP_FILE_SUFFIX:
        raise ValueError(f"The output path must end in {ZIP_FILE_SUFFIX!r}.")
    if resolved_output.exists() and not resolved_output.is_file():
        raise ValueError("The output path exists and is not a regular file.")
    if resolved_output.exists() and not overwrite:
        raise ValueError("The output file already exists; pass --overwrite to replace it.")

    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=TEMP_ARCHIVE_PREFIX,
        suffix=ZIP_FILE_SUFFIX,
        dir=resolved_output.parent,
        delete=False,
    ) as temporary_file:
        temporary_path = Path(temporary_file.name)
    try:
        with zipfile.ZipFile(
            temporary_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=ZIP_COMPRESSION_LEVEL,
        ) as archive:
            for file_path in package_files:
                archive_name = file_path.relative_to(package_root).as_posix()
                archive.write(file_path, arcname=archive_name)
        validate_archive(temporary_path, package_root, package_files)
        publish_archive(temporary_path, resolved_output, overwrite)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()
    return resolved_output, omitted_directories


# Define the explicit source, destination, and overwrite CLI options.
def create_parser() -> argparse.ArgumentParser:
    """Create the command-line parser for local Cowork ZIP packaging."""
    parser = argparse.ArgumentParser(
        description="Build a ZIP from a validated Cowork M365 app-package directory."
    )
    parser.add_argument(
        "--plugin-path",
        required=True,
        type=Path,
        help="Plugin project root or appPackage directory containing manifest.json.",
    )
    parser.add_argument(
        "--output-path",
        required=True,
        type=Path,
        help="Destination .zip path; existing files are preserved by default.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace the destination ZIP after the new archive passes validation.",
    )
    parser.add_argument(
        "--skip-content-checks",
        action="store_true",
        help="Skip manifest metadata, SKILL.md frontmatter and Markdown link checks (not recommended).",
    )
    parser.add_argument(
        "--allow-extensions",
        type=lambda value: [v for v in value.split(",") if v],
        default=[],
        help="Extra comma-separated skill file extensions to accept beyond the Microsoft 365 Copilot list.",
    )
    return parser


# Run validation, write the archive, and surface failures through argparse.
def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the package CLI and return a process status."""
    parser = create_parser()
    args = parser.parse_args(argv)
    try:
        archive_path, omitted_directories = package_plugin(
            args.plugin_path,
            args.output_path,
            args.overwrite,
            not args.skip_content_checks,
            args.allow_extensions,
        )
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        parser.error(str(exc))
    print(f"Created Cowork app package: {archive_path}")
    if omitted_directories:
        omitted_names = ", ".join(
            path.relative_to(resolve_package_root(args.plugin_path)).as_posix()
            for path in omitted_directories
        )
        print(f"Excluded source-only directories: {omitted_names}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
