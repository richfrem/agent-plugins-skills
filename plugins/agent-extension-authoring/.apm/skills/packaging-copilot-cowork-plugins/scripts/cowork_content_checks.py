"""
Copilot Cowork package content checks
=====================================

Purpose:
    Catch package problems the structural packager cannot see: incomplete or out-of-range
    manifest metadata, SKILL.md frontmatter that does not match its folder, and relative
    Markdown links that point to missing files, directories, or headings.

Key Input Dependencies:
    A manifest dictionary and packaged skill folders on disk; cowork_package_constants.py
    and cowork_markdown_utils.py in this skill.

Key Functions:
    validate_manifest_fields, validate_skill_frontmatter, packaged_markdown_files,
    validate_markdown_links, summarize_problems.

Output:
    Lists of human-readable error strings and warning strings. Nothing is written to disk.
"""

from __future__ import annotations

import os
import re
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Tuple

from cowork_markdown_utils import (
    heading_anchors,
    iter_lines,
    parse_frontmatter,
    split_frontmatter,
)
from cowork_package_constants import (
    ACCENT_COLOR_PATTERN,
    APP_VERSION_PATTERN,
    DESCRIPTION_FULL_MAX,
    DESCRIPTION_SHORT_MAX,
    DEVELOPER_NAME_KEY,
    DEVELOPER_NAME_MAX,
    DEVELOPER_URL_KEYS,
    EXTERNAL_LINK_PREFIXES,
    FULL_KEY,
    GUID_PATTERN,
    HTTPS_PREFIX,
    MANIFEST_ACCENT_COLOR_KEY,
    MANIFEST_APP_VERSION_KEY,
    MANIFEST_DESCRIPTION_KEY,
    MANIFEST_DEVELOPER_KEY,
    MANIFEST_ID_KEY,
    MANIFEST_NAME_KEY,
    MANIFEST_VERSION_KEY,
    MARKDOWN_LINK_PATTERN,
    MARKDOWN_SUFFIX,
    NAME_FULL_MAX,
    NAME_SHORT_MAX,
    NON_PACKAGE_DIRECTORY_NAMES,
    SHORT_KEY,
    SKILL_DESCRIPTION_MAX,
    SKILL_FILE_NAME,
    SKILL_NAME_MAX,
    SKILL_NAME_PATTERN,
    URL_MAX_LENGTH,
)


# Check one required text field against an optional length limit.
def _check_text(value: Any, label: str, maximum: int, problems: List[str]) -> None:
    """Append a problem when value is not a non-empty string within maximum length."""
    if not isinstance(value, str) or not value.strip():
        problems.append(f"manifest.json {label} must be a non-empty string.")
    elif len(value) > maximum:
        problems.append(f"manifest.json {label} is {len(value)} characters; the limit is {maximum}.")


# Check the developer block, including HTTPS-only URLs.
def _check_developer(manifest: Dict[str, Any], problems: List[str]) -> None:
    """Validate developer name and the three required HTTPS URLs."""
    developer = manifest.get(MANIFEST_DEVELOPER_KEY)
    if not isinstance(developer, dict):
        problems.append(f"manifest.json {MANIFEST_DEVELOPER_KEY} must be an object.")
        return
    _check_text(developer.get(DEVELOPER_NAME_KEY), f"{MANIFEST_DEVELOPER_KEY}.{DEVELOPER_NAME_KEY}",
                DEVELOPER_NAME_MAX, problems)
    for key in DEVELOPER_URL_KEYS:
        url = developer.get(key)
        label = f"{MANIFEST_DEVELOPER_KEY}.{key}"
        _check_text(url, label, URL_MAX_LENGTH, problems)
        if isinstance(url, str) and url.strip() and not url.startswith(HTTPS_PREFIX):
            problems.append(f"manifest.json {label} must start with {HTTPS_PREFIX}.")


# Check a {short, full} text pair such as name or description.
def _check_short_full(
    manifest: Dict[str, Any], key: str, short_max: int, full_max: int, problems: List[str]
) -> None:
    """Validate the short and full variants of a manifest text block."""
    block = manifest.get(key)
    if not isinstance(block, dict):
        problems.append(f"manifest.json {key} must be an object with {SHORT_KEY} and {FULL_KEY}.")
        return
    _check_text(block.get(SHORT_KEY), f"{key}.{SHORT_KEY}", short_max, problems)
    _check_text(block.get(FULL_KEY), f"{key}.{FULL_KEY}", full_max, problems)


# Validate identity, version, text limits, developer block, and accent color.
def validate_manifest_fields(manifest: Dict[str, Any]) -> List[str]:
    """Return problems found in the manifest's required metadata fields."""
    problems: List[str] = []
    if not re.fullmatch(GUID_PATTERN, str(manifest.get(MANIFEST_ID_KEY, ""))):
        problems.append(f"manifest.json {MANIFEST_ID_KEY} must be a GUID.")
    if not re.fullmatch(APP_VERSION_PATTERN, str(manifest.get(MANIFEST_APP_VERSION_KEY, ""))):
        problems.append(f"manifest.json {MANIFEST_APP_VERSION_KEY} must look like 1.2.3.")
    if not str(manifest.get(MANIFEST_VERSION_KEY, "")).strip():
        problems.append(f"manifest.json {MANIFEST_VERSION_KEY} is required.")
    _check_short_full(manifest, MANIFEST_NAME_KEY, NAME_SHORT_MAX, NAME_FULL_MAX, problems)
    _check_short_full(manifest, MANIFEST_DESCRIPTION_KEY, DESCRIPTION_SHORT_MAX,
                      DESCRIPTION_FULL_MAX, problems)
    _check_developer(manifest, problems)
    if not re.fullmatch(ACCENT_COLOR_PATTERN, str(manifest.get(MANIFEST_ACCENT_COLOR_KEY, ""))):
        problems.append(f"manifest.json {MANIFEST_ACCENT_COLOR_KEY} must be a #RRGGBB color.")
    return problems


# Confirm SKILL.md has frontmatter whose name matches its folder and description is bounded.
def validate_skill_frontmatter(skill_path: Path) -> List[str]:
    """Return problems with a packaged skill's SKILL.md frontmatter."""
    label = f"skills/{skill_path.name}/{SKILL_FILE_NAME}"
    text = (skill_path / SKILL_FILE_NAME).read_text(encoding="utf-8")
    frontmatter, _body = split_frontmatter(text)
    if frontmatter is None:
        return [f"{label} must start with YAML frontmatter."]
    fields = parse_frontmatter(frontmatter)
    problems: List[str] = []
    name = fields.get("name", "")
    if not re.fullmatch(SKILL_NAME_PATTERN, name) or len(name) > SKILL_NAME_MAX:
        problems.append(f"{label} name {name!r} must be lowercase letters, digits and hyphens "
                        f"(at most {SKILL_NAME_MAX} characters).")
    elif name != skill_path.name:
        problems.append(f"{label} name {name!r} must equal its folder name {skill_path.name!r}.")
    description = fields.get("description", "")
    if not description.strip():
        problems.append(f"{label} needs a non-empty description.")
    elif len(description) > SKILL_DESCRIPTION_MAX:
        problems.append(f"{label} description is {len(description)} characters; "
                        f"the limit is {SKILL_DESCRIPTION_MAX}.")
    return problems


# List the Markdown files that will be packaged for one skill.
def packaged_markdown_files(skill_path: Path) -> List[Path]:
    """Return SKILL.md and companion Markdown files, skipping source-only folders."""
    files: List[Path] = []
    for current_root, directory_names, file_names in os.walk(skill_path):
        directory_names[:] = [d for d in directory_names if d.lower() not in NON_PACKAGE_DIRECTORY_NAMES]
        for file_name in file_names:
            if file_name.lower().endswith(MARKDOWN_SUFFIX):
                files.append(Path(current_root) / file_name)
    return sorted(files)


# Resolve a link target inside a skill; return None when it escapes the skill folder.
def _resolve_inside(skill_path: Path, source_file: Path, link_path: str) -> Path | None:
    """Resolve link_path relative to source_file; None if outside skill_path."""
    joined = PurePosixPath(source_file.parent.relative_to(skill_path).as_posix()) / link_path
    parts: List[str] = []
    for part in joined.parts:
        if part == "..":
            if not parts:
                return None
            parts.pop()
        elif part != ".":
            parts.append(part)
    return skill_path.joinpath(*parts) if parts else skill_path


# Check every relative link in one Markdown file; errors for files, warnings for anchors.
def _check_file_links(skill_path: Path, markdown_file: Path) -> Tuple[List[str], List[str]]:
    """Return (errors, warnings) for the relative links in one Markdown file."""
    errors: List[str] = []
    warnings: List[str] = []
    text = markdown_file.read_text(encoding="utf-8")
    shown = markdown_file.relative_to(skill_path.parent).as_posix()
    own_anchors = heading_anchors(text)
    for in_code, line in iter_lines(text):
        if in_code:
            continue
        for match in re.finditer(MARKDOWN_LINK_PATTERN, line):
            target = match.group(2)
            if target.startswith(EXTERNAL_LINK_PREFIXES):
                continue
            link_path, _, fragment = target.partition("#")
            if not link_path:
                if fragment and fragment not in own_anchors:
                    warnings.append(f"{shown}: anchor #{fragment} not found in the same file.")
                continue
            resolved = _resolve_inside(skill_path, markdown_file, link_path)
            if resolved is None:
                errors.append(f"{shown}: link {target!r} leaves the skill folder.")
            elif not resolved.is_file():
                kind = "is a directory, link a file" if resolved.is_dir() else "does not exist"
                errors.append(f"{shown}: link {target!r} {kind}.")
            elif fragment and resolved.suffix.lower() == MARKDOWN_SUFFIX:
                anchors = heading_anchors(resolved.read_text(encoding="utf-8"))
                if fragment not in anchors:
                    warnings.append(f"{shown}: anchor #{fragment} not found in {link_path}.")
    return errors, warnings


# Check relative links across every packaged Markdown file in a skill.
def validate_markdown_links(skill_path: Path) -> Tuple[List[str], List[str]]:
    """Return (errors, warnings) for all packaged Markdown links in a skill folder."""
    errors: List[str] = []
    warnings: List[str] = []
    for markdown_file in packaged_markdown_files(skill_path):
        file_errors, file_warnings = _check_file_links(skill_path, markdown_file)
        errors.extend(file_errors)
        warnings.extend(file_warnings)
    return errors, warnings


# Format a list of problems into one readable error message.
def summarize_problems(problems: List[str]) -> str:
    """Return a numbered, multi-line summary of problems."""
    return "Package content checks failed:\n" + "\n".join(
        f"  {index}. {problem}" for index, problem in enumerate(problems, 1)
    )
