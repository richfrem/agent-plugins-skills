#!/usr/bin/env python3
"""
wiki_builder.py
=====================================

Purpose:
    Karpathy-style wiki node formatter and linker.
    Reads ParsedRecord JSON (from ingest.py), formats each record into a
    Karpathy wiki node markdown file, generates cluster pages, and writes/
    updates _index.md and _toc.md.

Layer: Build / Wiki

Usage:
    # Run after ingest.py
    python ./scripts/wiki_builder.py --wiki-root /path/to/wiki-root

    # Build from a pre-existing records JSON
    python ./scripts/wiki_builder.py --wiki-root /path/to/wiki-root --records /tmp/records.json

    # Dry run
    python ./scripts/wiki_builder.py --wiki-root /path/to/wiki-root --dry-run

Related:
    - ingest.py       (produces ParsedRecord input)
    - raw_manifest.py (WikiSourceConfig for path resolution)
    - distill_wiki.py (populates rlm/ summaries used in node frontmatter)
"""
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from raw_manifest import now_iso

TEMPLATE_PATH = SCRIPT_DIR.parent / "assets" / "templates" / "wiki-node.template.md"


def _load_template() -> str:
    """Load the wiki node template, falling back to inline default."""
    if TEMPLATE_PATH.exists():
        return TEMPLATE_PATH.read_text(encoding="utf-8")
    return (
        "---\n"
        "concept: {concept_name}\nsource: {source_label}\n"
        "source_file: {source_file}\nwiki_root: {wiki_root}\n"
        "generated_at: {generated_at}\ncluster: {cluster_name}\n"
        "content_hash: {content_hash}\n---\n\n"
        "# {concept_title}\n\n> {rlm_summary}\n\n"
        "## Key Ideas\n\n{bullets}\n\n## Details\n\n{content_excerpt}\n\n"
        "## See Also\n\n{wikilinks}\n\n## Raw Source\n\n"
        "- **Source:** `{source_label}`\n- **File:** `{source_file}`\n"
        "- **Indexed:** {generated_at}\n"
    )


def _resolve_rlm_cache_dir(wiki_root: Path, rlm_cache_dir: Optional[Path] = None) -> Path:
    """Return the RLM cache directory, defaulting to {wiki_root}/rlm/."""
    if rlm_cache_dir:
        return Path(rlm_cache_dir).resolve()
    return wiki_root / "rlm"


def _load_rlm_summary(rlm_cache_dir: Path, concept: str) -> Optional[str]:
    """
    Load the 1-sentence RLM summary for a concept if it already exists.

    Returns None if distillation has not run yet for this concept.
    """
    summary_path = rlm_cache_dir / concept / "summary.md"
    if not summary_path.exists():
        return None
    text = summary_path.read_text(encoding="utf-8").strip()
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2].strip()
    if text.startswith("# Summary"):
        text = text[len("# Summary"):].strip()
    return text or None


def _load_rlm_bullets(rlm_cache_dir: Path, concept: str) -> Optional[str]:
    """Load bullets.md for a concept if it exists."""
    bullets_path = rlm_cache_dir / concept / "bullets.md"
    if not bullets_path.exists():
        return None
    text = bullets_path.read_text(encoding="utf-8").strip()
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2].strip()
    return text or None


def _find_related_concepts(
    concept: str, all_concepts: List[str], max_links: int = 6
) -> List[str]:
    """
    Find related concepts to wikilink by shared word-token overlap.

    Args:
        concept:      The concept being built.
        all_concepts: All concept slugs known at build time.
        max_links:    Maximum number of wikilinks to generate.

    Returns:
        List of concept slugs to wikilink (sorted by token overlap descending).
    """
    tokens = set(concept.split("-"))
    scored: List[tuple] = []
    for other in all_concepts:
        if other == concept:
            continue
        other_tokens = set(other.split("-"))
        shared = len(tokens & other_tokens)
        scored.append((shared, other))
    scored.sort(key=lambda x: -x[0])
    return [s[1] for s in scored[:max_links] if s[0] > 0]


def build_wiki_node(
    record: Dict[str, Any],
    wiki_root: Path,
    all_concepts: List[str],
    template: str,
    rlm_cache_dir: Path,
    dry_run: bool = False,
) -> Path:
    """
    Format one ParsedRecord into a Karpathy wiki node and write it to disk.

    Args:
        record:        ParsedRecord dict from ingest.py (may cover multiple sources
                       if concept_extractor merged them).
        wiki_root:     Root of the wiki output directory.
        all_concepts:  All known concept slugs (for wikilink generation).
        template:      Wiki node template string.
        rlm_cache_dir: Resolved RLM cache directory for loading existing summaries.
        dry_run:       If True, skip writing.

    Returns:
        Path to the (potentially unwritten) wiki node file.
    """
    concept = record["concept"]
    wiki_dir = wiki_root / "wiki"
    node_path = wiki_dir / f"{concept}.md"

    rlm_summary = _load_rlm_summary(rlm_cache_dir, concept) or "*Summary pending — run /wiki-distill*"
    bullets_raw = _load_rlm_bullets(rlm_cache_dir, concept)

    if bullets_raw:
        bullets = bullets_raw
    else:
        bullets = "- *(Bullets pending — run /wiki-distill)*"

    related = _find_related_concepts(concept, all_concepts)
    if related:
        wikilinks = "\n".join(f"- [[{r}]]" for r in related)
    else:
        wikilinks = "*(No related concepts found yet)*"

    node_content = template.format(
        concept_name=concept,
        concept_title=record["title"],
        source_label=record["source_label"],
        source_file=record["source_file"],
        wiki_root=str(wiki_root),
        generated_at=record["generated_at"],
        cluster_name=record["cluster"],
        content_hash=record["content_hash"],
        rlm_summary=rlm_summary,
        bullets=bullets,
        content_excerpt=record["content"],
        wikilinks=wikilinks,
    )

    if not dry_run:
        wiki_dir.mkdir(parents=True, exist_ok=True)
        node_path.write_text(node_content, encoding="utf-8")

    return node_path


def build_index(
    records: List[Dict[str, Any]],
    wiki_root: Path,
    dry_run: bool = False,
) -> None:
    """
    Write (or overwrite) wiki/_index.md and wiki/_toc.md.

    Args:
        records:  All ParsedRecord dicts built in this run.
        wiki_root: Root of the wiki output directory.
        dry_run:  If True, print but do not write.
    """
    wiki_dir = wiki_root / "wiki"
    now = now_iso()

    # Group by cluster
    clusters: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        clusters.setdefault(r["cluster"], []).append(r)

    # _index.md
    index_lines = [
        "---",
        f"generated_at: {now}",
        f"total_concepts: {len(records)}",
        "---",
        "",
        "# LLM Wiki Index",
        "",
        f"*{len(records)} concepts indexed across {len(clusters)} clusters.*",
        "",
    ]
    for cluster_name in sorted(clusters.keys()):
        index_lines.append(f"## {cluster_name.replace('-', ' ').title()}")
        for r in sorted(clusters[cluster_name], key=lambda x: x["concept"]):
            index_lines.append(f"- [[{r['concept']}]] — {r['title']}")
        index_lines.append("")

    # _toc.md
    toc_lines = [
        "---",
        f"generated_at: {now}",
        "---",
        "",
        "# Table of Contents",
        "",
    ]
    for cluster_name in sorted(clusters.keys()):
        toc_lines.append(f"### [[_{cluster_name}|{cluster_name.replace('-', ' ').title()}]]")
        for r in sorted(clusters[cluster_name], key=lambda x: x["concept"]):
            toc_lines.append(f"  - [[{r['concept']}]]")
        toc_lines.append("")

    if not dry_run:
        wiki_dir.mkdir(parents=True, exist_ok=True)
        (wiki_dir / "_index.md").write_text("\n".join(index_lines), encoding="utf-8")
        (wiki_dir / "_toc.md").write_text("\n".join(toc_lines), encoding="utf-8")
        print(f"[OK] _index.md and _toc.md updated ({len(records)} concepts)")
    else:
        print(f"[DRY RUN] Would write _index.md ({len(records)} concepts, {len(clusters)} clusters)")


def build_cluster_pages(
    records: List[Dict[str, Any]],
    wiki_root: Path,
    dry_run: bool = False,
) -> None:
    """
    Write one _{cluster}.md page per cluster group.

    Args:
        records:   All ParsedRecord dicts.
        wiki_root: Root of the wiki output directory.
        dry_run:   If True, print but do not write.
    """
    wiki_dir = wiki_root / "wiki"
    clusters: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        clusters.setdefault(r["cluster"], []).append(r)

    for cluster_name, cluster_records in clusters.items():
        page_lines = [
            "---",
            f"cluster: {cluster_name}",
            f"concepts: {len(cluster_records)}",
            f"generated_at: {now_iso()}",
            "---",
            "",
            f"# {cluster_name.replace('-', ' ').title()}",
            "",
            f"*{len(cluster_records)} concepts in this cluster.*",
            "",
        ]
        for r in sorted(cluster_records, key=lambda x: x["concept"]):
            page_lines.append(f"- [[{r['concept']}]] — {r['title']}")
        page_lines.append("")

        cluster_path = wiki_dir / f"_{cluster_name}.md"
        if not dry_run:
            wiki_dir.mkdir(parents=True, exist_ok=True)
            cluster_path.write_text("\n".join(page_lines), encoding="utf-8")
        else:
            print(f"[DRY RUN] Would write {cluster_path.name} ({len(cluster_records)} concepts)")


def main() -> None:
    """Parse CLI arguments and build all wiki nodes."""
    parser = argparse.ArgumentParser(description="Build Karpathy-style wiki nodes from parsed records")
    parser.add_argument("--wiki-root", required=True, help="Path to the wiki root directory")
    parser.add_argument("--records", default=None, help="Path to records JSON from ingest.py (default: run ingest inline)")
    parser.add_argument("--source", default=None, help="Build nodes for one named source only")
    parser.add_argument(
        "--rlm-cache-dir",
        default=None,
        help="Override the RLM cache directory (default: {wiki-root}/rlm)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Plan without writing any files")
    args = parser.parse_args()

    wiki_root = Path(args.wiki_root).resolve()
    rlm_cache_dir = _resolve_rlm_cache_dir(wiki_root, args.rlm_cache_dir)
    template = _load_template()

    # Load or generate records
    if args.records:
        records: List[Dict[str, Any]] = json.loads(Path(args.records).read_text(encoding="utf-8"))
    else:
        # Run ingest.py inline then concept_extractor for cross-source synthesis
        ingest_script = SCRIPT_DIR / "ingest.py"
        cmd = [sys.executable, str(ingest_script), "--wiki-root", str(wiki_root)]
        if args.source:
            cmd += ["--source", args.source]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] ingest.py failed:\n{result.stderr}")
            sys.exit(1)
        try:
            raw_records: List[Dict[str, Any]] = json.loads(result.stdout)
        except json.JSONDecodeError:
            print("[ERROR] Could not parse ingest.py output as JSON")
            print(result.stdout[:500])
            sys.exit(1)

        # Run concept extraction + cross-source synthesis
        extractor_script = SCRIPT_DIR / "concept_extractor.py"
        if extractor_script.exists():
            ext_cmd = [sys.executable, str(extractor_script), "--json"]
            ext_result = subprocess.run(
                ext_cmd, input=json.dumps(raw_records), capture_output=True, text=True
            )
            if ext_result.returncode == 0:
                try:
                    records = json.loads(ext_result.stdout)
                    merged = len(raw_records) - len(records)
                    if merged > 0:
                        print(f"[EXTRACT] Merged {merged} duplicate concepts across sources")
                except json.JSONDecodeError:
                    records = raw_records
            else:
                records = raw_records
        else:
            records = raw_records

    if not records:
        print("[OK] No new or changed records to build.")
        return

    all_concepts = [r["concept"] for r in records]
    print(f"\n[BUILD] Building {len(records)} wiki nodes (RLM cache: {rlm_cache_dir})...")

    built = 0
    for record in records:
        node_path = build_wiki_node(
            record, wiki_root, all_concepts, template, rlm_cache_dir, dry_run=args.dry_run
        )
        if not args.dry_run:
            print(f"  [OK] {node_path.name}")
        else:
            print(f"  [DRY] {node_path.name}")
        built += 1

    build_cluster_pages(records, wiki_root, dry_run=args.dry_run)
    build_index(records, wiki_root, dry_run=args.dry_run)

    print(f"\n[DONE] {built} wiki nodes {'planned' if args.dry_run else 'written'}.")


if __name__ == "__main__":
    main()
