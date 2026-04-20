#!/usr/bin/env python
"""
concept_extractor.py
=====================================

Purpose:
    Cross-source concept synthesis for the Obsidian Wiki Engine.
    Implements the "compile" step from Karpathy's LLM wiki vision:
    multiple raw source files about the same concept are merged into
    one authoritative wiki node instead of producing N separate pages.

    Reads ParsedRecord JSON from stdin (or --input file), groups records by
    concept slug, merges multi-source records into a single synthetic record,
    improves cluster assignment using keyword extraction, and writes the
    deduplicated record list to stdout (or --output file).

    Called by wiki_builder.py between ingest.py and node generation.

Layer: Extract / Wiki

Usage:
    # Pipe from ingest.py
    python ingest.py --wiki-root /path/to/wiki-root | python concept_extractor.py --json

    # From file
    python concept_extractor.py --input /tmp/records.json --output /tmp/merged.json

Related:
    - ingest.py       (produces ParsedRecord input)
    - wiki_builder.py (consumes merged output)
"""
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# ─── STOPWORDS ────────────────────────────────────────────────────────────────
# Common English words that don't carry cluster-level meaning
_STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "this",
    "that", "these", "those", "it", "its", "i", "we", "you", "they",
    "he", "she", "not", "no", "all", "also", "more", "over", "into",
    "about", "up", "out", "if", "then", "than", "so", "yet", "both",
    "each", "when", "there", "here", "how", "what", "which", "who",
    "any", "one", "two", "new", "use", "used", "using", "s",
})


def _extract_keywords(text: str, top_n: int = 3) -> List[str]:
    """
    Extract the top N keyword tokens from text by term frequency.

    Strips markdown syntax, splits on whitespace/punctuation, removes
    stopwords, and returns the most frequent remaining tokens.

    Args:
        text:  Raw content string (markdown).
        top_n: Number of top keywords to return.

    Returns:
        List of keyword strings (lowercase, deduplicated, frequency-sorted).
    """
    # Strip markdown: remove code fences, links, wikilinks, headings syntax
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"#{1,6}\s*", " ", text)
    text = re.sub(r"[^\w\s]", " ", text.lower())

    tokens = text.split()
    freq: Dict[str, int] = {}
    for tok in tokens:
        if len(tok) >= 4 and tok not in _STOPWORDS:
            freq[tok] = freq.get(tok, 0) + 1

    sorted_tokens = sorted(freq.keys(), key=lambda t: -freq[t])
    return sorted_tokens[:top_n]


def infer_cluster_from_content(source_label: str, concept: str, content: str) -> str:
    """
    Infer a semantic cluster name from content keywords.

    Uses top keyword(s) extracted from the content as the cluster name,
    falling back to source_label if extraction yields nothing useful.

    The cluster name is kebab-case and represents the dominant topic of
    the concept, not just its source origin.

    Args:
        source_label: The source label (used as fallback cluster).
        concept:      The concept slug.
        content:      Raw source content for keyword extraction.

    Returns:
        Kebab-case cluster name.
    """
    keywords = _extract_keywords(content, top_n=2)

    # If top keyword is too similar to concept itself, use the second
    concept_tokens = set(concept.split("-"))
    filtered = [k for k in keywords if k not in concept_tokens]
    if filtered:
        return filtered[0]

    # Use source label if no distinguishing keyword found
    return source_label


def _merge_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge multiple ParsedRecords for the same concept into one authoritative record.

    The merged record:
    - Keeps the title from the first (longest) record
    - Combines content from all sources (truncated per-source)
    - Lists all source files in 'source_files' (new multi-source field)
    - Sets 'source_label' to the primary source, 'source_labels' to all
    - Re-runs keyword extraction on combined content for cluster assignment
    - Preserves the latest 'generated_at' timestamp

    Args:
        records: List of ParsedRecord dicts sharing the same concept slug.

    Returns:
        Single merged ParsedRecord dict.
    """
    if len(records) == 1:
        return records[0]

    # Sort: put the record with most content first (primary source)
    records_sorted = sorted(records, key=lambda r: len(r.get("content", "")), reverse=True)
    primary = records_sorted[0]

    # Combine content with source attribution headers
    combined_parts = []
    for r in records_sorted:
        label = r.get("source_label", r.get("source_name", "unknown"))
        src_file = r.get("source_file", "")
        combined_parts.append(f"<!-- Source: {label}/{src_file} -->\n{r.get('content', '')}")

    MAX_COMBINED = 5000
    combined_content = "\n\n".join(combined_parts)
    if len(combined_content) > MAX_COMBINED:
        combined_content = combined_content[:MAX_COMBINED] + "\n\n*(combined content truncated)*"

    # Re-infer cluster from combined content (more representative)
    cluster = infer_cluster_from_content(
        primary.get("source_label", ""),
        primary.get("concept", ""),
        combined_content,
    )

    merged: Dict[str, Any] = {
        **primary,
        "content":       combined_content,
        "cluster":       cluster,
        "source_label":  primary.get("source_label", ""),
        "source_labels": [r.get("source_label", "") for r in records_sorted],
        "source_file":   primary.get("source_file", ""),
        "source_files":  [r.get("source_file", "") for r in records_sorted],
        "source_names":  [r.get("source_name", "") for r in records_sorted],
        "generated_at":  max(r.get("generated_at", "") for r in records_sorted),
        "multi_source":  True,
    }
    return merged


def extract_concepts(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Group records by concept slug, merge multi-source groups, improve clusters.

    This is the "compile" step: N source files → M concept nodes (M ≤ N).
    Files from different sources that share the same concept slug are merged
    into one authoritative wiki node with all source attributions preserved.

    Args:
        records: List of ParsedRecord dicts from ingest.py.

    Returns:
        Deduplicated, merged list of ParsedRecord dicts ready for wiki_builder.
    """
    # Group by concept slug
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        concept = record.get("concept", "")
        if not concept:
            continue
        groups.setdefault(concept, []).append(record)

    # Merge each group + improve cluster assignment
    merged_records: List[Dict[str, Any]] = []
    for concept, group in sorted(groups.items()):
        merged = _merge_records(group)

        # Improve cluster for single-source records too
        if not merged.get("multi_source"):
            merged["cluster"] = infer_cluster_from_content(
                merged.get("source_label", ""),
                concept,
                merged.get("content", ""),
            )

        merged_records.append(merged)

    return merged_records


def main() -> None:
    """Parse CLI args: read records from stdin/file, write merged records to stdout/file."""
    parser = argparse.ArgumentParser(
        description="Merge multi-source ParsedRecords by concept slug (cross-source synthesis)"
    )
    parser.add_argument("--input", default=None, help="Input records JSON file (default: stdin)")
    parser.add_argument("--output", default=None, help="Output merged records JSON file (default: stdout)")
    parser.add_argument("--json", dest="json_output", action="store_true",
                        help="Force JSON output (default when --output not set)")
    parser.add_argument("--stats", action="store_true",
                        help="Print summary stats instead of full JSON")
    args = parser.parse_args()

    # Read input
    if args.input:
        raw_text = Path(args.input).read_text(encoding="utf-8")
    else:
        raw_text = sys.stdin.read()

    try:
        records: List[Dict[str, Any]] = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        print(f"[ERROR] Could not parse input JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    merged = extract_concepts(records)

    if args.stats:
        multi = [r for r in merged if r.get("multi_source")]
        print(f"[EXTRACT] Input records : {len(records)}")
        print(f"[EXTRACT] Output concepts: {len(merged)}")
        print(f"[EXTRACT] Merged nodes  : {len(multi)}")
        clusters = {r["cluster"] for r in merged}
        print(f"[EXTRACT] Clusters found: {len(clusters)}: {sorted(clusters)}")
        return

    result_json = json.dumps(merged, indent=2, ensure_ascii=False)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(result_json, encoding="utf-8")
        print(f"[EXTRACT] {len(records)} records → {len(merged)} concepts written: {args.output}",
              file=sys.stderr)
    else:
        print(result_json)


if __name__ == "__main__":
    main()
