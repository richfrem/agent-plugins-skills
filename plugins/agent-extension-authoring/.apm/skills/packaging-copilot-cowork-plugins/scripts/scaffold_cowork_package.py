#!/usr/bin/env python
"""
scaffold_cowork_package.py (CLI)
================================

Purpose:
    Create a Cowork M365 app-package directory (manifest.json, icons, skills/) from an
    APM-style plugin so package_cowork_plugin.py can zip it. For use when WIQD is not
    available. Skills over the 20-companion-file limit are bundled automatically.

Usage Examples:
    python scripts/scaffold_cowork_package.py --apm-plugin ./plugins/my-plugin \
        --output ./build/appPackage --developer-name "Example Org" \
        --website-url https://example.org --privacy-url https://example.org/privacy \
        --terms-url https://example.org/terms --drop-scripts-if-needed

Key Input Dependencies:
    An APM plugin folder with .apm/skills/<skill>/SKILL.md and optional
    .claude-plugin/plugin.json (name, version, description).
    cowork_package_constants.py and bundle_skill_companions.py in this skill.

Key Functions:
    read_plugin_metadata, discover_skills, short_description, build_manifest,
    write_png, render_icon, write_icons, scaffold, create_parser, main.

Output:
    A new appPackage directory. Privacy and terms URLs are required arguments and are never
    invented. No tenant action is taken; validate and zip the result with
    package_cowork_plugin.py and run Microsoft's deep validation before upload.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import uuid
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from bundle_skill_companions import bundle_skill
from cowork_package_constants import (
    ACCENT_COLOR_PATTERN,
    AGENT_SKILLS_KEY,
    APM_SKILLS_RELATIVE_PATH,
    APP_ID_NAMESPACE,
    COLOR_ICON_BARS,
    COLOR_ICON_BASELINE_Y,
    COLOR_ICON_DIMENSIONS,
    COLOR_ICON_FILE_NAME,
    COLOR_ICON_KEY,
    COLOR_ICON_RULE,
    DEFAULT_ACCENT_COLOR,
    DEFAULT_MANIFEST_VERSION,
    DESCRIPTION_SHORT_MAX,
    ICONS_KEY,
    MANIFEST_ACCENT_COLOR_KEY,
    MANIFEST_APP_VERSION_KEY,
    MANIFEST_DESCRIPTION_KEY,
    MANIFEST_DEVELOPER_KEY,
    MANIFEST_FILE_NAME,
    MANIFEST_ID_KEY,
    MANIFEST_NAME_KEY,
    MANIFEST_VERSION_KEY,
    NAME_SHORT_MAX,
    OUTLINE_ICON_BARS,
    OUTLINE_ICON_BASELINE_Y,
    OUTLINE_ICON_DIMENSIONS,
    OUTLINE_ICON_FILE_NAME,
    OUTLINE_ICON_KEY,
    OUTLINE_ICON_RULE,
    PLUGIN_DESCRIPTION_KEY,
    PLUGIN_METADATA_RELATIVE_PATH,
    PLUGIN_NAME_KEY,
    PLUGIN_VERSION_KEY,
    PNG_BIT_DEPTH,
    PNG_COLOR_TYPE_RGBA,
    PNG_COMPRESSION_LEVEL,
    PNG_IHDR_CHUNK_TYPE,
    PNG_SIGNATURE,
    FULL_KEY,
    SHORT_DESCRIPTION_ELLIPSIS,
    SHORT_KEY,
    SKILL_FILE_NAME,
    SKILL_FOLDER_KEY,
    SKILLS_DIRECTORY_NAME,
    TRANSPARENT_RGBA,
    WHITE_RGBA,
)

RGBA = Tuple[int, int, int, int]


# Read name, version and description from .claude-plugin/plugin.json when present.
def read_plugin_metadata(plugin_dir: Path) -> Dict[str, str]:
    """Return plugin metadata, falling back to the folder name."""
    metadata_path = plugin_dir.joinpath(*PLUGIN_METADATA_RELATIVE_PATH)
    metadata: Dict[str, Any] = {}
    if metadata_path.is_file():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return {
        PLUGIN_NAME_KEY: str(metadata.get(PLUGIN_NAME_KEY) or plugin_dir.name),
        PLUGIN_VERSION_KEY: str(metadata.get(PLUGIN_VERSION_KEY) or "0.1.0"),
        PLUGIN_DESCRIPTION_KEY: str(metadata.get(PLUGIN_DESCRIPTION_KEY) or ""),
    }


# Find the skill folders to package, optionally limited to a named list.
def discover_skills(plugin_dir: Path, wanted: Optional[List[str]]) -> List[Path]:
    """Return skill folders under .apm/skills that contain SKILL.md."""
    skills_root = plugin_dir.joinpath(*APM_SKILLS_RELATIVE_PATH)
    if not skills_root.is_dir():
        raise ValueError(f"No skills folder found at {skills_root}.")
    found = sorted(p for p in skills_root.iterdir() if (p / SKILL_FILE_NAME).is_file())
    if wanted:
        missing = sorted(set(wanted) - {p.name for p in found})
        if missing:
            raise ValueError(f"Requested skills not found: {', '.join(missing)}.")
        found = [p for p in found if p.name in wanted]
    if not found:
        raise ValueError("The plugin has no skills to package.")
    return found


# Trim a description to the short-description limit at a word boundary.
def short_description(text: str) -> str:
    """Return the first sentence of text, shortened to fit the short description limit."""
    first = re.split(r"(?<=[.!?])\s", text.strip(), maxsplit=1)[0]
    if len(first) <= DESCRIPTION_SHORT_MAX:
        return first
    room = DESCRIPTION_SHORT_MAX - len(SHORT_DESCRIPTION_ELLIPSIS)
    return first[:room].rsplit(" ", 1)[0].rstrip(",;:") + SHORT_DESCRIPTION_ELLIPSIS


# Build the manifest dictionary from plugin metadata and the supplied developer details.
def build_manifest(meta: Dict[str, str], skills: List[Path], options: argparse.Namespace) -> Dict[str, Any]:
    """Return the app manifest; URLs come only from the caller's arguments."""
    title = meta[PLUGIN_NAME_KEY].replace("-", " ").replace("_", " ").title()
    app_id = options.app_id or str(uuid.uuid5(uuid.NAMESPACE_URL, f"{APP_ID_NAMESPACE}/{meta[PLUGIN_NAME_KEY]}"))
    full_description = options.description_full or meta[PLUGIN_DESCRIPTION_KEY] or title
    return {
        MANIFEST_VERSION_KEY: options.manifest_version,
        MANIFEST_APP_VERSION_KEY: options.app_version or meta[PLUGIN_VERSION_KEY],
        MANIFEST_ID_KEY: app_id,
        MANIFEST_DEVELOPER_KEY: {
            "name": options.developer_name,
            "websiteUrl": options.website_url,
            "privacyUrl": options.privacy_url,
            "termsOfUseUrl": options.terms_url,
        },
        MANIFEST_NAME_KEY: {
            SHORT_KEY: options.name_short or title[:NAME_SHORT_MAX],
            FULL_KEY: options.name_full or title,
        },
        MANIFEST_DESCRIPTION_KEY: {
            SHORT_KEY: options.description_short or short_description(full_description),
            FULL_KEY: full_description,
        },
        ICONS_KEY: {COLOR_ICON_KEY: COLOR_ICON_FILE_NAME, OUTLINE_ICON_KEY: OUTLINE_ICON_FILE_NAME},
        MANIFEST_ACCENT_COLOR_KEY: options.accent_color,
        AGENT_SKILLS_KEY: [{SKILL_FOLDER_KEY: f"{SKILLS_DIRECTORY_NAME}/{skill.name}"} for skill in skills],
    }


# Encode RGBA rows as a PNG file using only the standard library.
def write_png(path: Path, dimensions: Tuple[int, int], pixel) -> None:
    """Write a PNG whose pixel(x, y) function returns an RGBA tuple."""
    width, height = dimensions
    rows = b"".join(
        b"\x00" + b"".join(bytes(pixel(x, y)) for x in range(width)) for y in range(height)
    )

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, height, PNG_BIT_DEPTH, PNG_COLOR_TYPE_RGBA, 0, 0, 0)
    path.write_bytes(
        PNG_SIGNATURE + chunk(PNG_IHDR_CHUNK_TYPE, header)
        + chunk(b"IDAT", zlib.compress(rows, PNG_COMPRESSION_LEVEL)) + chunk(b"IEND", b"")
    )


# Convert #RRGGBB to an RGBA tuple.
def _hex_to_rgba(color: str) -> RGBA:
    """Return the opaque RGBA tuple for a #RRGGBB color."""
    return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16), 255)


# Return a pixel function drawing ascending bars over a baseline.
def render_icon(bars, baseline_y: int, rule, foreground: RGBA, background: RGBA):
    """Return a pixel(x, y) function for the generated bar-chart icon."""
    x_start, x_end, y_start, y_end = rule

    def pixel(x: int, y: int) -> RGBA:
        for left, top, width in bars:
            if left <= x < left + width and top <= y < baseline_y:
                return foreground
        if x_start <= x < x_end and y_start <= y < y_end:
            return foreground
        return background

    return pixel


# Write the required color and outline icons next to the manifest.
def write_icons(output: Path, accent_color: str) -> None:
    """Write generated color (accent background) and outline (white on transparent) icons."""
    write_png(output / COLOR_ICON_FILE_NAME, COLOR_ICON_DIMENSIONS,
              render_icon(COLOR_ICON_BARS, COLOR_ICON_BASELINE_Y, COLOR_ICON_RULE,
                          WHITE_RGBA, _hex_to_rgba(accent_color)))
    write_png(output / OUTLINE_ICON_FILE_NAME, OUTLINE_ICON_DIMENSIONS,
              render_icon(OUTLINE_ICON_BARS, OUTLINE_ICON_BASELINE_Y, OUTLINE_ICON_RULE,
                          WHITE_RGBA, TRANSPARENT_RGBA))


# Create the whole package directory and return per-skill bundle reports.
def scaffold(options: argparse.Namespace) -> List[Dict[str, object]]:
    """Build the appPackage directory from an APM plugin and return skill reports."""
    if not re.fullmatch(ACCENT_COLOR_PATTERN, options.accent_color):
        raise ValueError("--accent-color must be a #RRGGBB color.")
    output = options.output
    if output.exists():
        raise ValueError(f"Output folder already exists: {output}")
    meta = read_plugin_metadata(options.apm_plugin)
    skills = discover_skills(options.apm_plugin, options.skills)
    output.mkdir(parents=True)
    reports = [
        bundle_skill(skill, output / SKILLS_DIRECTORY_NAME / skill.name,
                     drop_scripts_if_needed=options.drop_scripts_if_needed,
                     allow_extensions=options.allow_extensions,
                     drop_extensions=options.drop_extensions,
                     exclude_files=options.exclude_files)
        for skill in skills
    ]
    write_icons(output, options.accent_color)
    manifest = build_manifest(meta, skills, options)
    (output / MANIFEST_FILE_NAME).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return reports


# Define the explicit source, destination and developer-detail options.
def create_parser() -> argparse.ArgumentParser:
    """Create the command-line parser for Cowork package scaffolding."""
    parser = argparse.ArgumentParser(
        description="Create a Cowork app-package directory from an APM plugin (no WIQD)."
    )
    parser.add_argument("--apm-plugin", required=True, type=Path, help="APM plugin folder containing .apm/skills.")
    parser.add_argument("--output", required=True, type=Path, help="New appPackage directory to create.")
    parser.add_argument("--developer-name", required=True, help="Developer or organization name.")
    parser.add_argument("--website-url", required=True, help="Developer website (https).")
    parser.add_argument("--privacy-url", required=True, help="Privacy statement URL (https); never invented.")
    parser.add_argument("--terms-url", required=True, help="Terms of use URL (https); never invented.")
    parser.add_argument("--skills", type=lambda value: [v for v in value.split(",") if v],
                        help="Comma-separated skill folder names (default: all).")
    parser.add_argument("--name-short", help="Short app name, at most 30 characters.")
    parser.add_argument("--name-full", help="Full app name, at most 100 characters.")
    parser.add_argument("--description-short", help="Short description, at most 80 characters.")
    parser.add_argument("--description-full", help="Full description, at most 4000 characters.")
    parser.add_argument("--app-version", help="App version like 1.2.3 (default: plugin version).")
    parser.add_argument("--app-id", help="App GUID (default: stable id derived from the plugin name).")
    parser.add_argument("--manifest-version", default=DEFAULT_MANIFEST_VERSION, help="Manifest version string.")
    parser.add_argument("--accent-color", default=DEFAULT_ACCENT_COLOR, help="#RRGGBB accent and icon color.")
    parser.add_argument("--drop-scripts-if-needed", action="store_true",
                        help="Leave scripts out of skills that are still over the limit after bundling.")
    parser.add_argument("--allow-extensions", type=lambda value: [v for v in value.split(",") if v], default=[],
                        help="Extra comma-separated file extensions to keep (default list: Microsoft 365 Copilot file types).")
    parser.add_argument("--drop-extensions", type=lambda value: [v for v in value.split(",") if v], default=[],
                        help="Comma-separated file extensions to filter out in addition to unsupported types.")
    parser.add_argument("--exclude-files", type=lambda value: [v for v in value.split(",") if v], default=[],
                        help="Comma-separated skill-relative files to leave out of every skill that has them.")
    return parser


# Run the scaffolder and print a summary.
def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the scaffold CLI and return a process status."""
    parser = create_parser()
    args = parser.parse_args(argv)
    try:
        reports = scaffold(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(f"Created Cowork app package folder: {args.output.resolve()}")
    for report in reports:
        print(f"  {report['skill']}: {report['companions_before']} -> {report['companions_after']} companion files"
              f"{' (bundled)' if report['bundles'] else ''}{' (scripts dropped)' if report['scripts_dropped'] else ''}"
              f"{' (filtered: ' + ', '.join(report['files_filtered']) + ')' if report['files_filtered'] else ''}")
    print("Next: python package_cowork_plugin.py --plugin-path <output> --output-path <zip>, then run Microsoft's "
          "deep validation before upload.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
