#!/usr/bin/env python
"""
query_wiki.py
=====================================

Purpose:
    Progressive-disclosure query engine for the Obsidian LLM wiki.
    Returns the cheapest useful answer first — a 1-sentence RLM summary —
    and expands to bullets or full wiki node only on demand.

    Search strategy (3-phase):
        1. Exact slug + token match against wiki/_index.md
        2. Vector DB semantic search (via vector-db plugin's query.py)
           Resolved from .agent/learning/vector_profiles.json automatically.
        3. Full-text keyword scan of wiki/*.md as final fallback

    The --save-as flag files query results back into the wiki as a new node,
    implementing Karpathy's "outputs always add back to the knowledge base" loop.

Layer: Query / Wiki

Usage:
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "authentication flow"
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "api design" --level bullets
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "Oracle Forms" --level full
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root --list
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "auth" --json
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "auth flow" --save-as auth-flow
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "rlm design" --vdb-profile wiki

Related:
    - raw_manifest.py   (WikiSourceConfig for wiki root resolution)
    - distill_wiki.py   (populates the rlm/ summaries)
    - wiki_builder.py   (populates wiki/ nodes)
    - concept_extractor (infer_cluster_from_content for saved nodes)

Key Input Dependencies:
    - {wiki_root}/wiki/*.md nodes, {wiki_root}/rlm/ summaries, agent-memory.json
    - Optional vector-db query.py for Phase 2 semantic search
"""
import sys
import json
import argparse
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from raw_manifest import WikiSourceConfig, now_iso, _find_project_root

DISCLOSURE_LEVELS = ["summary", "bullets", "full", "raw"]

# ─── PROJECT ROOT ─────────────────────────────────────────────────────────────
_PROJECT_ROOT = _find_project_root(SCRIPT_DIR)


def _slug(text: str) -> str:
    """Convert a search term to a concept slug for exact matching."""
    s = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", s).strip("-")


# ─── VECTOR DB PHASE 2 ────────────────────────────────────────────────────────

def _find_vdb_query_script() -> Optional[Path]:
    """
    Discover the vector-db query.py script.

    Resolution order (mirrors how rlm-distill-agent is discovered):
        1. .agent/learning/ sibling to vector_profiles.json (installed skills)
        2. .agents/skills/vector-db-search/scripts/query.py
        3. plugins/agent-memory/scripts/query.py (dev tree)

    Returns:
        Resolved Path to query.py, or None if not found.
    """
    candidates = [
        _PROJECT_ROOT / ".agents" / "skills" / "vector-db-search" / "scripts" / "query.py",
        _PROJECT_ROOT / "plugins" / "vector-db" / "scripts" / "query.py",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _run_vdb_query_subprocess(query_script: Path, term: str, vdb_profile: str, limit: int) -> List[str]:
    """Run the vector-db query.py subprocess and extract 'Source:' file paths from its output."""
    try:
        result = subprocess.run(
            [
                sys.executable, str(query_script),
                term,
                "--profile", vdb_profile,
                "--limit", str(limit),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(_PROJECT_ROOT),
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []

    if result.returncode != 0:
        return []

    source_paths: List[str] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("Source:"):
            src = line[len("Source:"):].strip()
            if src:
                source_paths.append(src)
    return source_paths


def _build_reverse_source_map(wiki_root: Path) -> Optional[Dict[str, str]]:
    """Load agent-memory.json and build a source_file -> concept reverse map. None if unavailable."""
    memory_path = wiki_root / "meta" / "agent-memory.json"
    if not memory_path.exists():
        return None

    try:
        memory: Dict[str, Any] = json.loads(memory_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    reverse_map: Dict[str, str] = {}
    for entry in memory.values():
        concept = entry.get("concept", "")
        src_file = entry.get("source_file", "")
        if concept and src_file:
            # Store normalized path fragments for fuzzy matching
            reverse_map[src_file.replace("\\", "/")] = concept
    return reverse_map


def _map_source_paths_to_concepts(source_paths: List[str], reverse_map: Dict[str, str], existing_slugs: set) -> List[str]:
    """Map vector-db source file paths back to concept slugs via reverse_map, falling back to slug derivation."""
    found: List[str] = []
    seen: set = set()

    for src_path in source_paths:
        # Normalize path for matching
        normalized = src_path.replace("\\", "/")
        # Try suffix match: look for memory entries whose source_file appears in the path
        concept = None
        for mem_file, mem_concept in reverse_map.items():
            if mem_file in normalized or normalized.endswith(mem_file):
                concept = mem_concept
                break
        # Also try direct slug derivation from filename as fallback
        if not concept:
            stem = Path(src_path).stem
            candidate_slug = _slug(stem)
            if candidate_slug in existing_slugs:
                concept = candidate_slug

        if concept and concept not in seen:
            found.append(concept)
            seen.add(concept)

    return found


def _vector_phase2_search(
    term: str,
    wiki_root: Path,
    vdb_profile: str,
    limit: int = 5,
) -> List[str]:
    """
    Run vector DB semantic search and map results back to concept slugs.

    Calls the vector-db query.py as a subprocess, parses 'Source:' lines
    from the output, and reverse-maps file paths to concept slugs via
    agent-memory.json.

    Args:
        term:        Raw search term.
        wiki_root:   Wiki root (for agent-memory.json lookup).
        vdb_profile: Vector DB profile name (default: "wiki").
        limit:       Max results to request.

    Returns:
        Ordered list of concept slugs matching the semantic query.
        Empty list if vector-db is not available.
    """
    query_script = _find_vdb_query_script()
    if not query_script:
        return []

    source_paths = _run_vdb_query_subprocess(query_script, term, vdb_profile, limit)
    if not source_paths:
        return []

    reverse_map = _build_reverse_source_map(wiki_root)
    if reverse_map is None:
        return []

    wiki_dir = wiki_root / "wiki"
    existing_slugs = {f.stem for f in wiki_dir.glob("*.md") if not f.name.startswith("_")} \
        if wiki_dir.exists() else set()

    return _map_source_paths_to_concepts(source_paths, reverse_map, existing_slugs)


# ─── SAVE-AS (file results back into the wiki) ────────────────────────────────

def _build_saved_node_lines(concept_slug: str, source_concept: str, level: str, content: str, term: str) -> List[str]:
    """Build the markdown lines for a query-result-derived wiki node."""
    lines = [
        "---",
        f'concept: "{concept_slug}"',
        f'source_query: "{term}"',
        f'derived_from: "{source_concept}"',
        f'level: "{level}"',
        f'generated_at: "{now_iso()}"',
        f'query_derived: true',
        "---",
        "",
        f"# {concept_slug.replace('-', ' ').title()}",
        "",
        f"> *Derived from query: `{term}`*",
        "",
        "## Content",
        "",
        content,
        "",
    ]

    if source_concept and source_concept != concept_slug:
        lines += [
            "## See Also",
            "",
            f"- [[{source_concept}]] *(original source concept)*",
            "",
        ]
    return lines


def _save_query_result_as_node(
    wiki_root: Path,
    concept_slug: str,
    result: Dict[str, Any],
    term: str,
) -> Path:
    """
    File a query result back into the wiki as a new concept node.

    Implements Karpathy's 'filing outputs back into the wiki' loop:
    query results always add back to the knowledge base, making the
    wiki grow from every session of use.

    Args:
        wiki_root:    Wiki root directory.
        concept_slug: Slug for the new node filename.
        result:       query_concept() result dict.
        term:         Original search term (for attribution).

    Returns:
        Path to the written wiki node.
    """
    wiki_dir = wiki_root / "wiki"
    wiki_dir.mkdir(parents=True, exist_ok=True)
    node_path = wiki_dir / f"{concept_slug}.md"

    source_concept = result.get("concept", "")
    level = result.get("level", "summary")
    content = result.get("content", "")

    lines = _build_saved_node_lines(concept_slug, source_concept, level, content, term)

    node_path.write_text("\n".join(lines), encoding="utf-8")
    return node_path


def list_concepts(wiki_root: Path) -> List[str]:
    """
    Return all indexed concept slugs from the wiki directory.

    Returns:
        Sorted list of concept slugs.
    """
    wiki_dir = wiki_root / "wiki"
    if not wiki_dir.exists():
        return []
    return sorted(f.stem for f in wiki_dir.glob("*.md") if not f.name.startswith("_"))


def _phase1_slug_match(slug: str, concepts: List[str]) -> Optional[str]:
    """Phase 1: exact slug match, substring match, or shared-token match against known concepts."""
    if slug in concepts:
        return slug

    for c in concepts:
        if slug in c or c in slug:
            return c

    search_tokens = set(slug.split("-"))
    best_match = None
    best_score = 0
    for c in concepts:
        c_tokens = set(c.split("-"))
        score = len(search_tokens & c_tokens)
        if score > best_score:
            best_score = score
            best_match = c
    return best_match if best_score > 0 else None


def _phase3_fulltext_scan(wiki_dir: Path, term: str) -> Optional[str]:
    """Phase 3: grep-style full-text scan of wiki node content for the search term."""
    term_lower = term.lower()
    for node_file in wiki_dir.glob("*.md"):
        if node_file.name.startswith("_"):
            continue
        try:
            content = node_file.read_text(encoding="utf-8").lower()
        except Exception:
            continue
        if term_lower in content:
            return node_file.stem
    return None


def find_concept(
    wiki_root: Path,
    term: str,
    vdb_profile: str = "wiki",
) -> Optional[str]:
    """
    Find the best matching concept for the search term (3-phase search).

    Phase 1 — Slug/token matching (O(1), zero cost):
        1a. Exact slug match
        1b. Slug is a substring of a concept name
        1c. Shared token match (e.g. "authentication" matches "authentication-flow")

    Phase 2 — Vector DB semantic search (O(log N), requires vector-db installed):
        Calls vector-db query.py as subprocess, maps results to concept slugs
        via agent-memory.json.

    Phase 3 — Full-text keyword scan (O(N), always available):
        Grep-style scan of wiki/*.md content.

    Args:
        wiki_root:   Root of the wiki output directory.
        term:        Raw search string from the user.
        vdb_profile: Vector DB profile name for Phase 2.

    Returns:
        Best matching concept slug, or None if nothing found.
    """
    slug = _slug(term)
    concepts = list_concepts(wiki_root)

    match = _phase1_slug_match(slug, concepts)
    if match:
        return match

    # Phase 2: Vector DB semantic search
    vdb_candidates = _vector_phase2_search(term, wiki_root, vdb_profile)
    for candidate in vdb_candidates:
        if candidate in concepts:
            return candidate

    # Phase 3: Full-text keyword scan of wiki node content
    return _phase3_fulltext_scan(wiki_root / "wiki", term)


def read_layer(
    wiki_root: Path,
    concept: str,
    layer: str,
    rlm_cache_dir: Optional[Path] = None,
) -> Optional[str]:
    """
    Read one RLM layer file for a concept.

    Args:
        wiki_root:     Root of the wiki output directory.
        concept:       Concept slug.
        layer:         Layer name ('summary', 'bullets', 'deep').
        rlm_cache_dir: Override RLM cache directory (default: {wiki_root}/rlm).

    Returns:
        Cleaned layer text, or None if the file does not exist.
    """
    cache_dir = rlm_cache_dir if rlm_cache_dir else (wiki_root / "rlm")
    layer_path = cache_dir / concept / f"{layer}.md"
    if not layer_path.exists():
        return None
    text = layer_path.read_text(encoding="utf-8").strip()
    # Strip YAML frontmatter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2].strip()
    # Strip heading
    first_line = text.split("\n")[0].strip()
    if first_line.startswith("#"):
        text = "\n".join(text.split("\n")[1:]).strip()
    return text or None


def _resolve_summary_content(wiki_root: Path, concept: str, cache_dir: Path, wiki_node: Path) -> Optional[str]:
    """Resolve 'summary' level content: RLM summary, or first meaningful line of the wiki node."""
    content = read_layer(wiki_root, concept, "summary", cache_dir)
    if content:
        return content
    if wiki_node.exists():
        lines = wiki_node.read_text(encoding="utf-8").splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("---") and not stripped.startswith(">"):
                return stripped
    return None


def _resolve_bullets_content(wiki_root: Path, concept: str, cache_dir: Path) -> str:
    """Resolve 'bullets' level content: RLM bullets, falling back to summary, then a pending placeholder."""
    content = read_layer(wiki_root, concept, "bullets", cache_dir)
    if content:
        return content
    summary = read_layer(wiki_root, concept, "summary", cache_dir)
    return summary or "*(No bullets yet — run /wiki-distill)*"


def _resolve_full_content(wiki_node: Path) -> str:
    """Resolve 'full' level content: the complete wiki node file, or a not-found placeholder."""
    if wiki_node.exists():
        return wiki_node.read_text(encoding="utf-8")
    return "*(Wiki node not found — run /wiki-ingest)*"


def _resolve_raw_content(wiki_root: Path, concept: str) -> str:
    """Resolve 'raw' level content: the original source file behind this concept, via agent-memory.json."""
    from raw_manifest import load_agent_memory
    memory = load_agent_memory(wiki_root)
    found_key = None
    for key, entry in memory.items():
        if entry.get("concept") == concept:
            found_key = key
            break
    if not found_key:
        return "*(No source mapping found in agent-memory.json — run /wiki-ingest)*"

    source_name, rel_path = found_key.split("/", 1)
    try:
        cfg = WikiSourceConfig(source_name, wiki_root=wiki_root)
        raw_path = cfg.source_path / rel_path
        if raw_path.exists():
            return raw_path.read_text(encoding="utf-8")
        return f"*(Source file not found: {raw_path})*"
    except SystemExit:
        return f"*(Source '{source_name}' no longer registered)*"


def _list_available_levels(cache_dir: Path, concept: str, wiki_node: Path) -> List[str]:
    """List which disclosure levels (summary/bullets/deep RLM layers, plus 'full') exist for a concept."""
    available: List[str] = []
    concept_rlm_dir = cache_dir / concept
    for layer in ["summary", "bullets", "deep"]:
        if (concept_rlm_dir / f"{layer}.md").exists():
            available.append(layer)
    if wiki_node.exists():
        available.append("full")
    return available


def query_concept(
    wiki_root: Path,
    concept: str,
    level: str,
    rlm_cache_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Retrieve the requested disclosure level for a concept.

    Args:
        wiki_root:     Root of the wiki output directory.
        concept:       Concept slug to query.
        level:         Disclosure level ('summary', 'bullets', 'full', 'raw').
        rlm_cache_dir: Override RLM cache directory (default: {wiki_root}/rlm).

    Returns:
        Dict with 'concept', 'level', 'content', and 'available_levels' keys.
    """
    cache_dir = rlm_cache_dir if rlm_cache_dir else (wiki_root / "rlm")
    wiki_node = wiki_root / "wiki" / f"{concept}.md"
    available = _list_available_levels(cache_dir, concept, wiki_node)

    content: Optional[str] = None
    if level == "summary":
        content = _resolve_summary_content(wiki_root, concept, cache_dir, wiki_node)
    elif level == "bullets":
        content = _resolve_bullets_content(wiki_root, concept, cache_dir)
    elif level == "full":
        content = _resolve_full_content(wiki_node)
    elif level == "raw":
        content = _resolve_raw_content(wiki_root, concept)

    return {
        "concept": concept,
        "level": level,
        "content": content or "*(No content available — run /wiki-distill and /wiki-ingest)*",
        "available_levels": available,
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser for query_wiki.py."""
    parser = argparse.ArgumentParser(
        description="Progressive-disclosure query against the Obsidian LLM wiki"
    )
    parser.add_argument("term", nargs="?", help="Search term or concept name")
    parser.add_argument("--wiki-root", required=True, help="Path to the wiki root directory")
    parser.add_argument("--level", default="summary", choices=DISCLOSURE_LEVELS,
                        help="Disclosure level (default: summary)")
    parser.add_argument("--list", action="store_true", help="List all indexed concepts")
    parser.add_argument("--json", dest="output_json", action="store_true",
                        help="Output as JSON")
    parser.add_argument(
        "--save-as",
        default=None,
        metavar="CONCEPT_SLUG",
        help=(
            "File the query result back into the wiki as a new concept node. "
            "Implements Karpathy's 'outputs always add back to the wiki' loop. "
            "Example: --save-as my-findings"
        ),
    )
    parser.add_argument(
        "--vdb-profile",
        default="wiki",
        help="Vector DB profile name for Phase 2 semantic search (default: wiki)",
    )
    parser.add_argument(
        "--rlm-cache-dir",
        default=None,
        help="Override RLM cache directory (default: {wiki-root}/rlm)",
    )
    return parser


def _print_concept_list(wiki_root: Path, output_json: bool) -> None:
    """Print all indexed concepts, as JSON or a human-readable list."""
    concepts = list_concepts(wiki_root)
    if output_json:
        print(json.dumps(concepts, indent=2))
    else:
        print(f"[WIKI] {len(concepts)} indexed concepts:\n")
        for c in concepts:
            print(f"  - {c}")


def _print_query_result(concept: str, level: str, result: Dict[str, Any], output_json: bool) -> None:
    """Print the query result, as JSON or a human-readable formatted block."""
    if output_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n[WIKI] {concept}  (level: {level})")
        print(f"       Available: {', '.join(result['available_levels'])}")
        print("-" * 60)
        print(result["content"])
        print("-" * 60)


def _handle_save_as(wiki_root: Path, save_as: str, result: Dict[str, Any], term: str, output_json: bool) -> None:
    """Handle the --save-as flag: file the query result back into the wiki as a new node."""
    save_slug = _slug(save_as)
    node_path = _save_query_result_as_node(wiki_root, save_slug, result, term)
    if not output_json:
        print(f"\n[SAVE] Query result filed as wiki node: {node_path.name}")
    else:
        saved_info = {"saved_as": save_slug, "path": str(node_path)}
        print(json.dumps(saved_info, indent=2))


def main() -> None:
    """Parse CLI arguments and execute progressive-disclosure query."""
    parser = _build_arg_parser()
    args = parser.parse_args()

    wiki_root = Path(args.wiki_root).resolve()
    rlm_cache_dir = Path(args.rlm_cache_dir).resolve() if args.rlm_cache_dir else None

    if args.list:
        _print_concept_list(wiki_root, args.output_json)
        return

    if not args.term:
        parser.print_help()
        sys.exit(1)

    concept = find_concept(wiki_root, args.term, vdb_profile=args.vdb_profile)
    if not concept:
        msg = f"No concept found matching: '{args.term}'"
        if args.output_json:
            print(json.dumps({"error": msg}))
        else:
            print(f"[MISS] {msg}")
            print("       Tip: run /wiki-query --list to see all indexed concepts")
        sys.exit(1)

    result = query_concept(wiki_root, concept, args.level, rlm_cache_dir)
    _print_query_result(concept, args.level, result, args.output_json)

    if args.save_as:
        _handle_save_as(wiki_root, args.save_as, result, args.term, args.output_json)


if __name__ == "__main__":
    main()
