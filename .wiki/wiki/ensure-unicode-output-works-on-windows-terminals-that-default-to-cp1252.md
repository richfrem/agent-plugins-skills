---
concept: ensure-unicode-output-works-on-windows-terminals-that-default-to-cp1252
source: plugin-code
source_file: link-checker/scripts/symlink_manager.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.358146+00:00
cluster: import
content_hash: 05fe03280007101a
---

# Ensure Unicode output works on Windows terminals that default to cp1252

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/link-checker/scripts/symlink_manager.py -->
#!/usr/bin/env python
"""
symlink_manager.py — Cross-platform symlink creation and management.

Works on Windows (with Developer Mode or admin), macOS, and Linux.
Stores a symlinks.json manifest so links can be restored after git reset --hard
or on a fresh checkout on a different OS.

Usage:
  python symlink_manager.py diagnose
  python symlink_manager.py create --src <source> --dst <link>
  python symlink_manager.py restore [--manifest symlinks.json]
  python symlink_manager.py audit   [--manifest symlinks.json]
  python symlink_manager.py list    [--manifest symlinks.json]
  python symlink_manager.py remove  --dst <link>
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

# Ensure Unicode output works on Windows terminals that default to cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

LinkStrategy = Literal["symlink", "junction", "hardlink"]

MANIFEST_FILE = Path("symlinks.json")


@dataclass
class LinkEntry:
    src: str          # target the link points TO  (relative to repo root or absolute)
    dst: str          # path of the link itself    (relative to repo root or absolute)
    strategy: LinkStrategy = "symlink"
    description: str = ""

    def src_path(self, root: Path) -> Path:
        p = Path(self.src)
        return p if p.is_absolute() else root / p

    def dst_path(self, root: Path) -> Path:
        p = Path(self.dst)
        return p if p.is_absolute() else root / p


@dataclass
class Manifest:
    version: int = 1
    links: list[LinkEntry] = field(default_factory=list)

    # --- persistence --------------------------------------------------------

    @classmethod
    def load(cls, path: Path) -> "Manifest":
        if not path.exists():
            return cls()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        links = [LinkEntry(**e) for e in data.get("links", [])]
        return cls(version=data.get("version", 1), links=links)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {"version": self.version, "links": [asdict(e) for e in self.links]},
                f,
                indent=2,
            )

    # --- helpers ------------------------------------------------------------

    def find(self, dst: str) -> LinkEntry | None:
        return next((e for e in self.links if e.dst == dst), None)

    def upsert(self, entry: LinkEntry) -> None:
        for i, e in enumerate(self.links):
            if e.dst == entry.dst:
                self.links[i] = entry
                return
        self.links.append(entry)

    def remove(self, dst: str) -> bool:
        before = len(self.links)
        self.links = [e for e in self.links if e.dst != dst]
        return len(self.links) < before


# ---------------------------------------------------------------------------
# OS detection helpers
# ---------------------------------------------------------------------------

IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"


def is_admin() -> bool:
    """Return True if running with elevated privileges."""
    if IS_WINDOWS:
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False
    return os.geteuid() == 0


def windows_developer_mode_enabled() -> bool:
    ""

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/symlink-manager/scripts/symlink_manager.py -->
#!/usr/bin/env python3
"""
symlink_manager.py — Cross-platform symlink creation and management.

Works on Windows (with Developer Mode or admin), macOS, and Linux.
Stores a symlinks.json manifest so links can be restored after git reset --hard
or on a fresh checkout on a different OS.

Usage:
  python symlink_manager.py diagnose
  python symlink_manager.py create --src <source> --dst <link>
  python symlink_manager.py restore [--manifest symlinks.json]
  python symlink_manager.py audit   [--manifest symlinks.json]
  python symlink_manager.py list    [--manifest symlinks.json]
  python symlink_manager.py remove  --dst <link>
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict,

*(combined content truncated)*

## See Also

- [[ensure-unicode-output-works-on-windows]]
- [[force-utf-8-output-on-windows-if-possible]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[absolute-path-prefixes-that-should-never-be-written-to]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[default-file-extensions-to-index-if-manifest-is-empty]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `link-checker/scripts/symlink_manager.py`
- **Indexed:** 2026-04-27T05:21:04.358146+00:00
