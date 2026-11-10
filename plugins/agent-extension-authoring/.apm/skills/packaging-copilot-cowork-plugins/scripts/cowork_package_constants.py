"""
Copilot Cowork package constants
================================

Purpose:
    Define the M365 app-package names and checks shared by the local ZIP packager
    and its tests.

Key Input Dependencies:
    None. Values describe the current Cowork app-package layout.

Key Functions:
    None.

Output:
    Imported package-layout, icon, path-safety, and archive constants.
"""

from typing import Dict, Tuple

MANIFEST_FILE_NAME = "manifest.json"
APP_PACKAGE_DIRECTORY_NAME = "appPackage"
ICONS_KEY = "icons"
COLOR_ICON_KEY = "color"
OUTLINE_ICON_KEY = "outline"
COLOR_ICON_FILE_NAME = "color.png"
OUTLINE_ICON_FILE_NAME = "outline.png"
COLOR_ICON_DIMENSIONS = (192, 192)
OUTLINE_ICON_DIMENSIONS = (32, 32)
ICON_DIMENSIONS: Dict[str, Tuple[int, int]] = {
    COLOR_ICON_KEY: COLOR_ICON_DIMENSIONS,
    OUTLINE_ICON_KEY: OUTLINE_ICON_DIMENSIONS,
}
ICON_FILE_NAMES: Dict[str, str] = {
    COLOR_ICON_KEY: COLOR_ICON_FILE_NAME,
    OUTLINE_ICON_KEY: OUTLINE_ICON_FILE_NAME,
}
AGENT_SKILLS_KEY = "agentSkills"
SKILL_FOLDER_KEY = "folder"
SKILLS_DIRECTORY_NAME = "skills"
SKILL_FILE_NAME = "SKILL.md"
ZIP_FILE_SUFFIX = ".zip"
ZIP_COMPRESSION_LEVEL = 9
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_IHDR_CHUNK_TYPE = b"IHDR"
PNG_HEADER_LENGTH = 24
TEMP_ARCHIVE_PREFIX = ".cowork-package-"
FORBIDDEN_PATH_CHARACTERS = frozenset(("\\", ":"))
SENSITIVE_FILE_NAMES = frozenset(("credentials.json", "secrets.json"))
SENSITIVE_FILE_SUFFIXES = frozenset((".env", ".key", ".pem", ".p12", ".pfx", ".token"))
NON_PACKAGE_DIRECTORY_NAMES = frozenset(("evals", "tests"))
# Microsoft Learn "Build plugins for Copilot Cowork": per-skill companion file limits.
MAX_COMPANION_FILES = 20
MAX_COMPANION_FILE_BYTES = 5 * 1024 * 1024
MAX_COMPANION_TOTAL_BYTES = 10 * 1024 * 1024
