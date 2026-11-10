#!/usr/bin/env python
"""
bundle_skill_companions.py (CLI)
================================

Purpose:
    Copy one APM-style skill into a Cowork package folder and, when it has more than the
    20 companion files Cowork allows, bundle its Markdown guides into fewer files while
    rewriting every link. The source skill is never modified.

Usage Examples:
    python scripts/bundle_skill_companions.py --skill-dir ./.apm/skills/my-skill \
        --output-dir ./appPackage/skills/my-skill
    python scripts/bundle_skill_companions.py --skill-dir ./.apm/skills/my-skill \
        --output-dir ./appPackage/skills/my-skill --drop-scripts-if-needed

Key Input Dependencies:
    A skill folder with SKILL.md and optional references/, assets/ and scripts/.
    cowork_package_constants.py and cowork_markdown_utils.py in this skill.

Key Functions:
    iter_source_files, allowed_extensions, companion_files, plan_bundles, build_link_map,
    rewrite_links, write_bundle, bundle_skill, create_parser, main.

Output:
    A skill folder under --output-dir with SKILL.md plus at most --max-companions
    companion files. Markdown under references/<dir>/ is bundled into references/<dir>.md
    and Markdown under assets/<dir>/ into assets/<dir>.md; other files keep their paths.
    A "Cowork build" section is appended to SKILL.md when anything was bundled or dropped.
    Files whose extension Microsoft 365 Copilot does not support (for example .mmd) are filtered
    out, and links to them become plain text with a short note. Files named with --exclude-files
    are left out the same way (for example scripts that cannot run in Cowork). If folder bundles
    are not enough, loose guides under references/ are merged into references/other.md.
"""

from __future__ import annotations

import argparse
import os
import posixpath
import re
import shutil
from pathlib import Path
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Tuple

from cowork_markdown_utils import first_heading, github_slug, iter_lines, normalize_newlines
from cowork_package_constants import (
    ACCEPTANCE_CRITERIA_FILE_NAME,
    ASSETS_DIRECTORY_NAME,
    BUNDLE_SECTIONS_HEADING,
    CONTENTS_HEADING,
    COWORK_BUILD_HEADING,
    DROPPED_LINK_TARGET,
    EXTERNAL_LINK_PREFIXES,
    FILE_TYPE_NOT_SUPPORTED_NOTE,
    HORIZONTAL_RULE,
    IGNORED_DIRECTORY_NAMES,
    IGNORED_FILE_SUFFIXES,
    LOOSE_GUIDES_BUNDLE,
    MARKDOWN_LINK_PATTERN,
    MARKDOWN_SUFFIX,
    MAX_COMPANION_FILES,
    NON_PACKAGE_DIRECTORY_NAMES,
    REFERENCES_DIRECTORY_NAME,
    SCRIPT_NOT_PACKAGED_NOTE,
    SCRIPTS_DIRECTORY_NAME,
    SKILL_COMPANION_DIRECTORIES,
    SKILL_FILE_NAME,
    SUPPORTED_COMPANION_EXTENSIONS,
)

LinkMap = Dict[str, Tuple[str, Optional[str]]]
BUNDLEABLE_DIRECTORIES = (REFERENCES_DIRECTORY_NAME, ASSETS_DIRECTORY_NAME)


# List every packageable file in a skill as POSIX paths relative to the skill folder.
def iter_source_files(skill_dir: Path) -> List[str]:
    """Return relative paths of regular files, skipping source-only and cache folders."""
    found: List[str] = []
    for current_root, directory_names, file_names in os.walk(skill_dir, followlinks=False):
        directory_names[:] = [
            d for d in directory_names
            if d.lower() not in NON_PACKAGE_DIRECTORY_NAMES and d not in IGNORED_DIRECTORY_NAMES
        ]
        for file_name in file_names:
            path = Path(current_root) / file_name
            if path.is_symlink():
                raise ValueError(f"Skill must not contain symbolic links: {path}")
            if path.suffix.lower() in IGNORED_FILE_SUFFIXES:
                continue
            found.append(path.relative_to(skill_dir).as_posix())
    return sorted(found)


# Normalize an extension list to lowercase with a leading dot.
def _normalize(extensions: Iterable[str]) -> FrozenSet[str]:
    """Return extensions as a set of lowercase strings with a leading dot."""
    return frozenset(("." + e.strip().lstrip(".")).lower() for e in extensions if e.strip())


# Build the effective allowlist from the default list plus caller additions and removals.
def allowed_extensions(allow: Iterable[str] = (), drop: Iterable[str] = ()) -> FrozenSet[str]:
    """Return the file extensions that may be packaged."""
    return frozenset((SUPPORTED_COMPANION_EXTENSIONS | _normalize(allow)) - _normalize(drop))


# Keep only files Cowork counts as companions that this tool would carry over.
def companion_files(
    sources: List[str],
    drop_scripts: bool,
    allowed: Optional[FrozenSet[str]] = None,
) -> List[str]:
    """Return companion paths (references, assets, scripts), minus scripts and unsupported types."""
    result: List[str] = []
    for relative in sources:
        top = relative.split("/")[0]
        if top not in SKILL_COMPANION_DIRECTORIES or "/" not in relative:
            continue
        if drop_scripts and top == SCRIPTS_DIRECTORY_NAME:
            continue
        if allowed is not None and posixpath.splitext(relative)[1].lower() not in allowed:
            continue
        result.append(relative)
    return result


# Sort key that keeps guides alphabetical but places acceptance criteria last in a bundle.
def _section_order(relative: str) -> Tuple[bool, str]:
    """Return a sort key placing acceptance-criteria files after the other guides."""
    return posixpath.basename(relative) == ACCEPTANCE_CRITERIA_FILE_NAME, relative


# Decide which Markdown files group into which bundle (one bundle per first-level folder).
def plan_bundles(companions: List[str], merge_loose: bool = False) -> Dict[str, List[str]]:
    """Group Markdown under references/<dir>/ and assets/<dir>/ into <dir>.md bundles.

    With merge_loose, references/ guides that did not join a folder bundle (single-file folders
    and files directly under references/) are merged into one references/other.md bundle.
    """
    groups: Dict[str, List[str]] = {}
    for relative in companions:
        parts = relative.split("/")
        if parts[0] in BUNDLEABLE_DIRECTORIES and len(parts) >= 3 and relative.lower().endswith(MARKDOWN_SUFFIX):
            groups.setdefault(f"{parts[0]}/{parts[1]}{MARKDOWN_SUFFIX}", []).append(relative)
    bundles = {
        bundle: sorted(files, key=_section_order)
        for bundle, files in sorted(groups.items())
        if len(files) > 1
    }
    if merge_loose:
        bundled = {f for files in bundles.values() for f in files}
        loose = [
            c for c in companions
            if c.startswith(REFERENCES_DIRECTORY_NAME + "/") and c.lower().endswith(MARKDOWN_SUFFIX) and c not in bundled
        ]
        if len(loose) > 1:
            bundles[LOOSE_GUIDES_BUNDLE] = sorted(loose, key=_section_order)
    return bundles


# Count the companion files left after a bundle plan is applied.
def _planned_count(companions: List[str], bundles: Dict[str, List[str]]) -> int:
    """Return how many companion files remain after bundling."""
    bundled = {f for files in bundles.values() for f in files}
    return len(companions) - len(bundled) + len(bundles)


# Choose the least invasive bundle plan that fits the limit.
def _fit_bundles(companions: List[str], limit: int) -> Tuple[Dict[str, List[str]], int]:
    """Return (bundles, resulting_count): folder bundles first, then merged loose guides."""
    bundles = plan_bundles(companions)
    count = _planned_count(companions, bundles)
    if count > limit:
        bundles = plan_bundles(companions, merge_loose=True)
        count = _planned_count(companions, bundles)
    clashes = sorted(set(bundles) & set(companions))
    if clashes:
        raise ValueError(f"bundle name collides with an existing file: {clashes}")
    return bundles, count


# Build the map from each source companion path to its output path and optional anchor.
def build_link_map(
    skill_dir: Path,
    companions: List[str],
    bundles: Dict[str, List[str]],
    filtered: Iterable[str] = (),
) -> Tuple[LinkMap, Dict[str, str]]:
    """Return (link_map, titles); titles maps each bundled source path to its section title."""
    link_map: LinkMap = {relative: (relative, None) for relative in companions}
    for relative in filtered:
        link_map[relative] = (DROPPED_LINK_TARGET, None)
    link_map[SKILL_FILE_NAME] = (SKILL_FILE_NAME, None)
    titles: Dict[str, str] = {}
    for bundle, files in bundles.items():
        used: Dict[str, str] = {}
        for relative in files:
            text = (skill_dir / relative).read_text(encoding="utf-8")
            title = (first_heading(text) or posixpath.basename(relative)).replace("`", "")
            if github_slug(title) in used:
                title = f"{title} ({posixpath.basename(relative)[:-len(MARKDOWN_SUFFIX)]})"
            used[github_slug(title)] = relative
            titles[relative] = title
            link_map[relative] = (bundle, github_slug(title))
    return link_map, titles


# Rewrite relative links so they point at the bundled or retained output files.
def rewrite_links(text: str, source_relative: str, output_relative: str, link_map: LinkMap,
                  dropped_scripts: bool) -> str:
    """Rewrite Markdown links from the source layout to the output layout."""
    lines: List[str] = []
    for in_code, line in iter_lines(text):
        lines.append(line if in_code else re.sub(
            MARKDOWN_LINK_PATTERN,
            lambda m: _rewrite_one(m, source_relative, output_relative, link_map, dropped_scripts),
            line,
        ))
    return "\n".join(lines)


# Rewrite a single Markdown link match.
def _rewrite_one(match: "re.Match[str]", source_relative: str, output_relative: str,
                 link_map: LinkMap, dropped_scripts: bool) -> str:
    """Return the replacement text for one Markdown link."""
    label, target = match.group(1), match.group(2)
    if target.startswith(EXTERNAL_LINK_PREFIXES):
        return match.group(0)
    link_path, _, _fragment = target.partition("#")
    if not link_path:
        return label
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source_relative), link_path))
    if dropped_scripts and resolved.startswith(SCRIPTS_DIRECTORY_NAME + "/"):
        return f"{label} ({SCRIPT_NOT_PACKAGED_NOTE})"
    if resolved not in link_map:
        raise ValueError(f"{source_relative}: link {target!r} does not resolve to a packaged file.")
    out_path, anchor = link_map[resolved]
    if out_path == DROPPED_LINK_TARGET:
        return f"{label} ({FILE_TYPE_NOT_SUPPORTED_NOTE})"
    relative = posixpath.relpath(out_path, posixpath.dirname(output_relative) or ".")
    if out_path == output_relative:
        return f"[{label}](#{anchor})" if anchor else label
    return f"[{label}]({relative}#{anchor})" if anchor else f"[{label}]({relative})"


# Remove the H1 and the Contents block from a section and demote remaining headings.
def _section_body(text: str) -> str:
    """Return a source guide's body ready to nest under a bundle section heading."""
    result: List[str] = []
    skipping = False
    seen_title = False
    for in_code, line in iter_lines(text):
        if not in_code and not seen_title and line.startswith("# "):
            seen_title = True
            continue
        if not in_code and line.strip() == CONTENTS_HEADING:
            skipping = True
            continue
        if skipping:
            if not in_code and (line.startswith("## ") or line.strip() == HORIZONTAL_RULE):
                skipping = False
                if line.strip() == HORIZONTAL_RULE:
                    continue
            else:
                continue
        result.append("#" + line if (not in_code and re.match(r"^#{1,5} ", line)) else line)
    return "\n".join(result).strip("\n")


# Write one bundle file made of rewritten sections.
def write_bundle(skill_dir: Path, output_dir: Path, bundle: str, files: List[str],
                 titles: Dict[str, str], link_map: LinkMap, dropped_scripts: bool) -> None:
    """Write bundle with a section index and one rewritten section per source guide."""
    folder_title = posixpath.basename(bundle)[:-len(MARKDOWN_SUFFIX)].replace("-", " ").capitalize()
    parts = [f"# {folder_title} (bundled for Copilot Cowork)", "",
             "Cowork allows at most 20 companion files per skill, so the guides in this folder "
             "are bundled here. Each section is one source guide.", "", BUNDLE_SECTIONS_HEADING, ""]
    parts += [f"- [{titles[f]}](#{github_slug(titles[f])})" for f in files] + [""]
    for relative in files:
        text = (skill_dir / relative).read_text(encoding="utf-8")
        body = rewrite_links(_section_body(text), relative, bundle, link_map, dropped_scripts)
        parts += [f"## {titles[relative]}", "", body, ""]
    destination = output_dir / bundle
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8", newline="\n")


# Copy one companion file unchanged, rewriting links when it is Markdown.
def _copy_companion(skill_dir: Path, output_dir: Path, relative: str, link_map: LinkMap,
                    dropped_scripts: bool) -> None:
    """Copy a retained companion file into the output skill folder."""
    destination = output_dir / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if relative.lower().endswith(MARKDOWN_SUFFIX):
        text = (skill_dir / relative).read_text(encoding="utf-8")
        rewritten = rewrite_links(text, relative, relative, link_map, dropped_scripts)
        destination.write_text(rewritten, encoding="utf-8", newline="\n")
    else:
        shutil.copy2(skill_dir / relative, destination)


# Append the Cowork build note describing what was bundled or left out.
def _cowork_note(bundles: Dict[str, List[str]], dropped_scripts: bool, left_out: List[str]) -> str:
    """Return the section appended to SKILL.md for a bundled or reduced build."""
    lines = ["", COWORK_BUILD_HEADING, "",
             "This is the Copilot Cowork build of this skill. Cowork allows at most 20 companion "
             "files per skill."]
    if bundles:
        lines += ["", "Guides are bundled by folder (each source guide is a section inside its bundle):", ""]
        lines += [f"- [{bundle}]({bundle})" for bundle in bundles]
    if dropped_scripts:
        lines += ["", "Scripts are not packaged. Where a guide mentions a script, work that step by hand "
                  "or use the full plugin outside Cowork."]
    if left_out:
        lines += ["", "These files are not in the Cowork package. Where a guide mentions one, work that step by "
                  "hand or use the full plugin outside Cowork:", ""]
        lines += [f"- {path}" for path in left_out]
    return "\n".join(lines) + "\n"


# Copy a skill into the output folder, bundling Markdown when it exceeds the companion limit.
def bundle_skill(
    skill_dir: Path,
    output_dir: Path,
    max_companions: int = MAX_COMPANION_FILES,
    drop_scripts_if_needed: bool = False,
    allow_extensions: Iterable[str] = (),
    drop_extensions: Iterable[str] = (),
    exclude_files: Iterable[str] = (),
) -> Dict[str, object]:
    """Create the Cowork build of one skill and return a report dictionary."""
    if not (skill_dir / SKILL_FILE_NAME).is_file():
        raise ValueError(f"{skill_dir} is missing {SKILL_FILE_NAME}.")
    allowed = allowed_extensions(allow_extensions, drop_extensions)
    excluded = {e.strip().replace("\\", "/") for e in exclude_files if e.strip()}
    sources = iter_source_files(skill_dir)
    all_companions = companion_files(sources, drop_scripts=False)
    companions = [c for c in companion_files(sources, drop_scripts=False, allowed=allowed) if c not in excluded]
    filtered = sorted(set(all_companions) - set(companions))
    bundles: Dict[str, List[str]] = {}
    dropped = False
    if len(companions) > max_companions:
        bundles, count = _fit_bundles(companions, max_companions)
        if count > max_companions and drop_scripts_if_needed:
            dropped = True
            companions = [c for c in companion_files(sources, drop_scripts=True, allowed=allowed) if c not in excluded]
            bundles, count = _fit_bundles(companions, max_companions)
        if count > max_companions:
            raise ValueError(
                f"{skill_dir.name}: {count} companion files remain after bundling; Cowork allows "
                f"{max_companions}. Remove files, or pass --drop-scripts-if-needed."
            )
    link_map, titles = build_link_map(skill_dir, companions, bundles, filtered)
    bundled_sources = {f for files in bundles.values() for f in files}
    if output_dir.exists():
        raise ValueError(f"Output folder already exists: {output_dir}")
    output_dir.mkdir(parents=True)
    for bundle, files in bundles.items():
        write_bundle(skill_dir, output_dir, bundle, files, titles, link_map, dropped)
    for relative in companions:
        if relative not in bundled_sources:
            _copy_companion(skill_dir, output_dir, relative, link_map, dropped)
    skill_text = (skill_dir / SKILL_FILE_NAME).read_text(encoding="utf-8")
    rewritten = rewrite_links(skill_text, SKILL_FILE_NAME, SKILL_FILE_NAME, link_map, dropped)
    if bundles or dropped or filtered:
        rewritten = rewritten.rstrip("\n") + "\n" + _cowork_note(bundles, dropped, filtered)
    (output_dir / SKILL_FILE_NAME).write_text(normalize_newlines(rewritten), encoding="utf-8", newline="\n")
    final_count = sum(1 for _ in output_dir.rglob("*") if _.is_file()) - 1
    return {"skill": skill_dir.name, "companions_before": len(all_companions),
            "companions_after": final_count, "bundles": sorted(bundles), "scripts_dropped": dropped,
            "files_filtered": filtered}


# Define the explicit source, destination and limit options.
def create_parser() -> argparse.ArgumentParser:
    """Create the command-line parser for skill bundling."""
    parser = argparse.ArgumentParser(
        description="Copy a skill for Copilot Cowork, bundling Markdown guides if it has too many files."
    )
    parser.add_argument("--skill-dir", required=True, type=Path, help="Source skill folder containing SKILL.md.")
    parser.add_argument("--output-dir", required=True, type=Path, help="New skill folder to create.")
    parser.add_argument("--max-companions", type=int, default=MAX_COMPANION_FILES,
                        help=f"Companion file limit (default {MAX_COMPANION_FILES}).")
    parser.add_argument("--drop-scripts-if-needed", action="store_true",
                        help="If bundling Markdown is not enough, leave scripts out of the package.")
    parser.add_argument("--allow-extensions", type=lambda v: [e for e in v.split(",") if e], default=[],
                        help="Extra comma-separated file extensions to keep (default list: Microsoft 365 Copilot file types).")
    parser.add_argument("--drop-extensions", type=lambda v: [e for e in v.split(",") if e], default=[],
                        help="Comma-separated file extensions to filter out in addition to unsupported types.")
    parser.add_argument("--exclude-files", type=lambda v: [e for e in v.split(",") if e], default=[],
                        help="Comma-separated skill-relative files to leave out, e.g. scripts/app.py.")
    return parser


# Run the bundler and report what changed.
def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the bundling CLI and return a process status."""
    parser = create_parser()
    args = parser.parse_args(argv)
    try:
        report = bundle_skill(args.skill_dir, args.output_dir, args.max_companions,
                              args.drop_scripts_if_needed, args.allow_extensions, args.drop_extensions,
                              args.exclude_files)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"{report['skill']}: {report['companions_before']} -> {report['companions_after']} companion files; "
          f"bundles={len(report['bundles'])}; scripts_dropped={report['scripts_dropped']}; "
          f"files_filtered={len(report['files_filtered'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
