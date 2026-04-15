#!/usr/bin/env python3
"""
raw_manifest.py
=====================================

Purpose:
    WikiSourceConfig — centralized configuration loader for the Obsidian Wiki
    Engine. Mirrors the RLMConfig pattern from rlm-factory: loads named source
    entries from wiki_sources.json, giving every wiki script a single
    configuration entry point.

    wiki_sources.json is the wiki-engine equivalent of rlm_profiles.json.
    Each named entry is a raw content directory to be indexed into the wiki.

Layer: Config / Wiki

Usage:
    from raw_manifest import WikiSourceConfig, load_wiki_sources, save_wiki_sources

    # Load one named source
    cfg = WikiSourceConfig(source_name="arch-docs", wiki_root=Path("/path/to/root"))

    # Load all sources
    for name, cfg in WikiSourceConfig.all_sources(wiki_root).items():
        print(cfg.source_path, cfg.label)

    # Collect eligible files from a source
    files = cfg.collect_files()

Related:
    - ingest.py       (raw file parsing)
    - wiki_builder.py (node generation)
    - distill_wiki.py (RLM distillation)
    - query_wiki.py   (progressive query)
    - audit.py        (health checks)
"""
import os
import sys
import json
import fnmatch
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any


# ─── PROJECT ROOT ─────────────────────────────────────────────────────────────
def _find_project_root(start: Path) -> Path:
    """Walk up from start to find the .git root, or fall back to 4 levels up."""
    for p in [start.resolve()] + list(start.resolve().parents):
        if (p / ".git").is_dir():
            return p
    return start.resolve().parents[3]


PROJECT_ROOT = _find_project_root(Path(__file__))


# ─── SOURCES FILE DISCOVERY ───────────────────────────────────────────────────
def _get_sources_path(wiki_root: Optional[Path] = None) -> Path:
    """
    Resolve the wiki_sources.json path.

    Priority:
        1. WIKI_SOURCES_PATH env var
        2. {wiki_root}/meta/wiki_sources.json
        3. {project_root}/.agent/wiki/wiki_sources.json
        4. {project_root}/.agents/wiki/wiki_sources.json
    """
    env_path = os.getenv("WIKI_SOURCES_PATH")
    if env_path:
        p = Path(env_path)
        return p if p.is_absolute() else (PROJECT_ROOT / p).resolve()

    if wiki_root:
        candidate = Path(wiki_root) / "meta" / "wiki_sources.json"
        if candidate.exists():
            return candidate

    for sub in (".agent/wiki", ".agents/wiki"):
        candidate = PROJECT_ROOT / sub / "wiki_sources.json"
        if candidate.exists():
            return candidate

    # Return default even if not yet created (init will create it)
    if wiki_root:
        return Path(wiki_root) / "meta" / "wiki_sources.json"
    return PROJECT_ROOT / ".agent" / "wiki" / "wiki_sources.json"


# ─── LOAD / SAVE ─────────────────────────────────────────────────────────────
def load_wiki_sources(sources_path: Path) -> Dict[str, Any]:
    """
    Load the raw wiki_sources.json data from disk.

    Returns an empty dict structure if the file does not exist.
    """
    if not sources_path.exists():
        return {"namespace": "", "wiki_root": "", "sources": {}, "global_excludes": []}
    try:
        with open(sources_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Error reading wiki_sources.json: {e}")
        return {"namespace": "", "wiki_root": "", "sources": {}, "global_excludes": []}


def save_wiki_sources(data: Dict[str, Any], sources_path: Path) -> None:
    """
    Persist wiki_sources.json to disk, creating parent directories as needed.
    """
    sources_path.parent.mkdir(parents=True, exist_ok=True)
    with open(sources_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[SAVE] wiki_sources.json written: {sources_path}")


# ─── WIKI SOURCE CONFIG ───────────────────────────────────────────────────────
class WikiSourceConfig:
    """
    Named-source configuration for the Obsidian Wiki Engine.

    Mirrors the RLMConfig pattern: loads a single named entry from
    wiki_sources.json, providing all path and filter settings as attributes.
    Every wiki script should instantiate this class rather than reading
    wiki_sources.json directly.

    Attributes:
        source_name:    Name of the loaded source (key in wiki_sources.json).
        wiki_root:      Resolved wiki root directory.
        source_path:    Resolved path to the raw content directory.
        label:          Human-readable label for this source.
        extensions:     List of file extensions to include (e.g. [".md"]).
        excludes:       Per-source substrings/patterns to exclude.
        global_excludes: Project-wide exclude patterns from the top-level key.
        description:    Optional description of the source.
        sources_path:   Path to the wiki_sources.json file that was loaded.
        namespace:      Project namespace string.
    """

    def __init__(
        self,
        source_name: str,
        wiki_root: Optional[Path] = None,
    ) -> None:
        """
        Initialize WikiSourceConfig from a named source entry.

        Args:
            source_name: Key in the wiki_sources.json "sources" dict.
            wiki_root:   Optional override for the wiki root directory.

        Raises:
            SystemExit: If wiki_sources.json is missing or source is not found.
        """
        self.source_name = source_name
        self.sources_path = _get_sources_path(wiki_root)
        data = load_wiki_sources(self.sources_path)

        self.namespace = data.get("namespace", "")
        self.global_excludes: List[str] = data.get("global_excludes", [])

        # Resolve wiki_root: arg > JSON value > project root fallback
        raw_wiki_root = data.get("wiki_root", "")
        if wiki_root:
            self.wiki_root = Path(wiki_root).resolve()
        elif raw_wiki_root:
            p = Path(raw_wiki_root)
            self.wiki_root = p if p.is_absolute() else (PROJECT_ROOT / p).resolve()
        else:
            self.wiki_root = PROJECT_ROOT / "wiki-root"

        sources = data.get("sources", {})
        entry = sources.get(source_name)
        if not entry:
            available = list(sources.keys())
            print(f"[ERROR] Wiki source '{source_name}' not found. Available: {available}")
            print(f"        Sources file: {self.sources_path}")
            sys.exit(1)

        self.label: str = entry.get("label", source_name)
        self.description: str = entry.get("description", "")
        self.extensions: List[str] = entry.get("extensions", [".md"])
        self.excludes: List[str] = entry.get("excludes", [])

        raw_src_path = entry.get("path", "")
        if not raw_src_path:
            print(f"[ERROR] Source '{source_name}' has no 'path' defined.")
            sys.exit(1)

        p = Path(raw_src_path)
        self.source_path: Path = p if p.is_absolute() else (PROJECT_ROOT / p).resolve()

    # ----------------------------------------------------------
    # collect_files — yield eligible files from this source
    # ----------------------------------------------------------
    def collect_files(self) -> List[Path]:
        """
        Collect all eligible files from this source directory.

        Applies per-source excludes AND global_excludes. Files are returned
        sorted and deduplicated.

        Returns:
            Sorted list of absolute Path objects.
        """
        if not self.source_path.exists():
            print(f"[WARN] Source path does not exist: {self.source_path}")
            return []

        all_files: List[Path] = []
        for ext in self.extensions:
            all_files.extend(self.source_path.rglob(f"*{ext}"))

        result = []
        for f in all_files:
            if f.is_file() and not self._should_skip(f):
                result.append(f)

        return sorted(set(result))

    def _should_skip(self, file_path: Path) -> bool:
        """
        Return True if this file should be excluded from indexing.

        Checks per-source excludes and global_excludes as substring/glob matches
        against the full resolved path string.
        """
        path_str = str(file_path.resolve())
        for pattern in self.excludes + self.global_excludes:
            # Substring match first (fast path)
            if pattern in path_str:
                return True
            # Glob pattern match against filename only
            if fnmatch.fnmatch(file_path.name, pattern):
                return True
        return False

    # ----------------------------------------------------------
    # relative_path — normalize for use as a cache/index key
    # ----------------------------------------------------------
    def relative_path(self, file_path: Path) -> str:
        """
        Return the path relative to the source directory, forward-slash normalized.

        This is the canonical key used in agent-memory.json and wiki node frontmatter.
        """
        try:
            return str(file_path.resolve().relative_to(self.source_path)).replace("\\", "/")
        except ValueError:
            return str(file_path.resolve()).replace("\\", "/")

    # ----------------------------------------------------------
    # class methods
    # ----------------------------------------------------------
    @classmethod
    def all_sources(
        cls, wiki_root: Optional[Path] = None
    ) -> Dict[str, "WikiSourceConfig"]:
        """
        Load all named sources from wiki_sources.json.

        Returns:
            Dict mapping source_name -> WikiSourceConfig instance.
        """
        sources_path = _get_sources_path(wiki_root)
        data = load_wiki_sources(sources_path)
        result = {}
        for name in data.get("sources", {}).keys():
            try:
                result[name] = cls(source_name=name, wiki_root=wiki_root)
            except SystemExit:
                pass
        return result

    @classmethod
    def from_sources_file(
        cls, sources_path: Path, source_name: str
    ) -> "WikiSourceConfig":
        """
        Load a named source from an explicit wiki_sources.json path.

        Useful in tests or when the file is not in the default location.
        """
        os.environ["WIKI_SOURCES_PATH"] = str(sources_path)
        try:
            return cls(source_name=source_name)
        finally:
            del os.environ["WIKI_SOURCES_PATH"]


# ─── UTILITIES ────────────────────────────────────────────────────────────────
def compute_hash(content: str) -> str:
    """Return first 16 chars of SHA256 hex digest for change detection."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def load_agent_memory(wiki_root: Path) -> Dict[str, Any]:
    """
    Load agent-memory.json — the stale-file tracking ledger.

    Keys are '{source_name}/{relative_path}', values are dicts with
    'hash', 'indexed_at', 'wiki_node' fields.
    """
    path = wiki_root / "meta" / "agent-memory.json"
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Could not read agent-memory.json: {e}")
        return {}


def save_agent_memory(memory: Dict[str, Any], wiki_root: Path) -> None:
    """Persist agent-memory.json to disk."""
    path = wiki_root / "meta" / "agent-memory.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def is_stale(
    source_name: str,
    rel_path: str,
    content: str,
    memory: Dict[str, Any],
) -> bool:
    """
    Return True if the file is new or its content hash has changed since last index.
    """
    key = f"{source_name}/{rel_path}"
    entry = memory.get(key)
    if not entry:
        return True
    return entry.get("hash") != compute_hash(content)


def now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()
