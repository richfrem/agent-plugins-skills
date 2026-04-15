#!/usr/bin/env python3
"""
query_wiki.py
=====================================

Purpose:
    Progressive-disclosure query engine for the Obsidian LLM wiki.
    Returns the cheapest useful answer first — a 1-sentence RLM summary —
    and expands to bullets or full wiki node only on demand.

Layer: Query / Wiki

Usage:
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "authentication flow"
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "api design" --level bullets
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "Oracle Forms" --level full
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root --list
    python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "auth" --json

Related:
    - raw_manifest.py  (WikiSourceConfig for wiki root resolution)
    - distill_wiki.py  (populates the rlm/ summaries)
    - wiki_builder.py  (populates wiki/ nodes)
"""
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from raw_manifest import WikiSourceConfig

DISCLOSURE_LEVELS = ["summary", "bullets", "full", "raw"]


def _slug(text: str) -> str:
    """Convert a search term to a concept slug for exact matching."""
    s = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_]+", "-", s).strip("-")


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


def find_concept(wiki_root: Path, term: str) -> Optional[str]:
    """
    Find the best matching concept for the search term.

    Strategy:
        1. Exact slug match
        2. Slug is a substring of a concept name
        3. Any concept slug token appears in the term
        4. Full-text scan of RLM summary content

    Args:
        wiki_root: Root of the wiki output directory.
        term:      Raw search string from the user.

    Returns:
        Best matching concept slug, or None if nothing found.
    """
    slug = _slug(term)
    concepts = list_concepts(wiki_root)

    # 1. Exact match
    if slug in concepts:
        return slug

    # 2. Slug is a prefix/substring of a concept
    for c in concepts:
        if slug in c or c in slug:
            return c

    # 3. Shared token match (e.g. "authentication" matches "authentication-flow")
    search_tokens = set(slug.split("-"))
    best_match = None
    best_score = 0
    for c in concepts:
        c_tokens = set(c.split("-"))
        score = len(search_tokens & c_tokens)
        if score > best_score:
            best_score = score
            best_match = c
    if best_score > 0:
        return best_match

    # 4. Full-text scan of wiki node summaries
    wiki_dir = wiki_root / "wiki"
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


def read_layer(wiki_root: Path, concept: str, layer: str) -> Optional[str]:
    """
    Read one RLM layer file for a concept.

    Args:
        wiki_root: Root of the wiki output directory.
        concept:   Concept slug.
        layer:     Layer name ('summary', 'bullets', 'deep').

    Returns:
        Cleaned layer text, or None if the file does not exist.
    """
    layer_path = wiki_root / "rlm" / concept / f"{layer}.md"
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


def query_concept(
    wiki_root: Path,
    concept: str,
    level: str,
) -> Dict[str, Any]:
    """
    Retrieve the requested disclosure level for a concept.

    Args:
        wiki_root: Root of the wiki output directory.
        concept:   Concept slug to query.
        level:     Disclosure level ('summary', 'bullets', 'full', 'raw').

    Returns:
        Dict with 'concept', 'level', 'content', and 'available_levels' keys.
    """
    available: List[str] = []
    rlm_dir = wiki_root / "rlm" / concept
    for layer in ["summary", "bullets", "deep"]:
        if (rlm_dir / f"{layer}.md").exists():
            available.append(layer)

    wiki_node = wiki_root / "wiki" / f"{concept}.md"
    if wiki_node.exists():
        available.append("full")

    content: Optional[str] = None

    if level == "summary":
        content = read_layer(wiki_root, concept, "summary")
        if not content:
            # Fall back to first line of wiki node
            if wiki_node.exists():
                lines = wiki_node.read_text(encoding="utf-8").splitlines()
                for line in lines:
                    if line.strip() and not line.startswith("#") and not line.startswith("---") and not line.startswith(">"):
                        content = line.strip()
                        break

    elif level == "bullets":
        content = read_layer(wiki_root, concept, "bullets")
        if not content:
            summary = read_layer(wiki_root, concept, "summary")
            content = summary or "*(No bullets yet — run /wiki-distill)*"

    elif level == "full":
        if wiki_node.exists():
            content = wiki_node.read_text(encoding="utf-8")
        else:
            content = "*(Wiki node not found — run /wiki-ingest)*"

    elif level == "raw":
        # Find the original source file via agent-memory.json
        from raw_manifest import load_agent_memory
        memory = load_agent_memory(wiki_root)
        found_key = None
        for key, entry in memory.items():
            if entry.get("concept") == concept:
                found_key = key
                break
        if found_key:
            source_name, rel_path = found_key.split("/", 1)
            try:
                cfg = WikiSourceConfig(source_name, wiki_root=wiki_root)
                raw_path = cfg.source_path / rel_path
                if raw_path.exists():
                    content = raw_path.read_text(encoding="utf-8")
                else:
                    content = f"*(Source file not found: {raw_path})*"
            except SystemExit:
                content = f"*(Source '{source_name}' no longer registered)*"
        else:
            content = "*(No source mapping found in agent-memory.json — run /wiki-ingest)*"

    return {
        "concept": concept,
        "level": level,
        "content": content or "*(No content available — run /wiki-distill and /wiki-ingest)*",
        "available_levels": available,
    }


def main() -> None:
    """Parse CLI arguments and execute progressive-disclosure query."""
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
    args = parser.parse_args()

    wiki_root = Path(args.wiki_root).resolve()

    if args.list:
        concepts = list_concepts(wiki_root)
        if args.output_json:
            print(json.dumps(concepts, indent=2))
        else:
            print(f"[WIKI] {len(concepts)} indexed concepts:\n")
            for c in concepts:
                print(f"  - {c}")
        return

    if not args.term:
        parser.print_help()
        sys.exit(1)

    concept = find_concept(wiki_root, args.term)
    if not concept:
        msg = f"No concept found matching: '{args.term}'"
        if args.output_json:
            print(json.dumps({"error": msg}))
        else:
            print(f"[MISS] {msg}")
            print("       Tip: run /wiki-query --list to see all indexed concepts")
        sys.exit(1)

    result = query_concept(wiki_root, concept, args.level)

    if args.output_json:
        print(json.dumps(result, indent=2))
        return

    print(f"\n[WIKI] {concept}  (level: {args.level})")
    print(f"       Available: {', '.join(result['available_levels'])}")
    print("-" * 60)
    print(result["content"])
    print("-" * 60)


if __name__ == "__main__":
    main()
