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

# --- Manifest metadata (Microsoft 365 / Teams app manifest rules) ---
MANIFEST_VERSION_KEY = "manifestVersion"
MANIFEST_APP_VERSION_KEY = "version"
MANIFEST_ID_KEY = "id"
MANIFEST_DEVELOPER_KEY = "developer"
MANIFEST_NAME_KEY = "name"
MANIFEST_DESCRIPTION_KEY = "description"
MANIFEST_ACCENT_COLOR_KEY = "accentColor"
SHORT_KEY = "short"
FULL_KEY = "full"
DEVELOPER_NAME_KEY = "name"
DEVELOPER_URL_KEYS = ("websiteUrl", "privacyUrl", "termsOfUseUrl")
DEVELOPER_NAME_MAX = 32
NAME_SHORT_MAX = 30
NAME_FULL_MAX = 100
DESCRIPTION_SHORT_MAX = 80
DESCRIPTION_FULL_MAX = 4000
URL_MAX_LENGTH = 2048
HTTPS_PREFIX = "https://"
GUID_PATTERN = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
APP_VERSION_PATTERN = r"^\d+\.\d+\.\d+$"
ACCENT_COLOR_PATTERN = r"^#[0-9A-Fa-f]{6}$"
DEFAULT_MANIFEST_VERSION = "1.29"
DEFAULT_ACCENT_COLOR = "#2B579A"
APP_ID_NAMESPACE = "https://learn.microsoft.com/copilot/cowork/app-id"

# --- Agent Skills entry point checks ---
SKILL_NAME_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"
SKILL_NAME_MAX = 64
SKILL_DESCRIPTION_MAX = 1024
FRONTMATTER_DELIMITER = "---"

# --- Markdown handling ---
MARKDOWN_SUFFIX = ".md"
MARKDOWN_LINK_PATTERN = r"(?<!!)\[([^\]]*)\]\(([^)\s]+)\)"
CODE_FENCE_PREFIX = "```"
EXTERNAL_LINK_PREFIXES = ("http://", "https://", "mailto:")
CONTENTS_HEADING = "## Contents"
HORIZONTAL_RULE = "---"

# --- Source skill layout, bundling and scaffolding ---
REFERENCES_DIRECTORY_NAME = "references"
ASSETS_DIRECTORY_NAME = "assets"
SCRIPTS_DIRECTORY_NAME = "scripts"
SKILL_COMPANION_DIRECTORIES = (
    REFERENCES_DIRECTORY_NAME,
    ASSETS_DIRECTORY_NAME,
    SCRIPTS_DIRECTORY_NAME,
)
IGNORED_DIRECTORY_NAMES = frozenset(("__pycache__",))
IGNORED_FILE_SUFFIXES = frozenset((".pyc",))
ACCEPTANCE_CRITERIA_FILE_NAME = "acceptance-criteria.md"
LOOSE_GUIDES_BUNDLE = "references/other.md"
# File types Microsoft 365 Copilot works with, from Microsoft Support's list of supported file formats
# (supplied by the user). Cowork publish validation rejected ".mmd" with "not supported ... in
# Microsoft 365 Copilot". This list is not confirmed to be the validator's exact allowlist, so the
# tools accept --allow-extensions to add types and --drop-extensions to remove them.
SUPPORTED_COMPANION_EXTENSIONS = frozenset((
    ".js", ".jsx", ".tsx", ".py", ".java", ".cs", ".cpp", ".c", ".h", ".php", ".dart", ".css",
    ".lua", ".rs", ".pl", ".sql", ".bash", ".sh",
    ".json", ".xml", ".yaml", ".yml", ".ini", ".config", ".utf8",
    ".docx", ".doc", ".docm", ".pdf", ".txt", ".rtf", ".md", ".html", ".htm",
    ".pptx", ".ppt", ".ppsm", ".xlsx", ".xls", ".xlsm", ".csv", ".tsv",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".log", ".loop", ".fluid",
))
FILE_TYPE_NOT_SUPPORTED_NOTE = "file type not supported in Cowork"
DROPPED_LINK_TARGET = ""
SCRIPT_NOT_PACKAGED_NOTE = "script, not packaged in Cowork"
COWORK_BUILD_HEADING = "## Cowork build"
BUNDLE_SECTIONS_HEADING = "## Sections"
APM_SKILLS_RELATIVE_PATH = (".apm", "skills")
PLUGIN_METADATA_RELATIVE_PATH = (".claude-plugin", "plugin.json")
PLUGIN_NAME_KEY = "name"
PLUGIN_VERSION_KEY = "version"
PLUGIN_DESCRIPTION_KEY = "description"
SHORT_DESCRIPTION_ELLIPSIS = "..."

# --- Generated icon geometry ---
COLOR_ICON_BARS = ((36, 120, 32), (80, 90, 32), (124, 56, 32))
COLOR_ICON_BASELINE_Y = 150
COLOR_ICON_RULE = (28, 164, 154, 160)
OUTLINE_ICON_BARS = ((6, 17, 6), (14, 12, 6), (22, 7, 6))
OUTLINE_ICON_BASELINE_Y = 25
OUTLINE_ICON_RULE = (4, 30, 26, 28)
PNG_COLOR_TYPE_RGBA = 6
PNG_BIT_DEPTH = 8
PNG_COMPRESSION_LEVEL = 9
WHITE_RGBA = (255, 255, 255, 255)
TRANSPARENT_RGBA = (0, 0, 0, 0)
