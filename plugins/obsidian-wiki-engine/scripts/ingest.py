#!/usr/bin/env python3
"""
ingest.py
=====================================

Purpose:
    Raw file ingestion pipeline. Reads all files from sources registered in
    wiki_sources.json, normalizes content, and produces ParsedRecord dicts
    ready for wiki_builder.py. Also updates agent-memory.json with fresh hashes.

Layer: Ingest / Wiki

Usage:
    python ./scripts/ingest.py --wiki-root /path/to/wiki-root
    python ./scripts/ingest.py --wiki-root /path/to/wiki-root --source arch-docs
    python ./scripts/ingest.py --wiki-root /path/to/wiki-root --dry-run

Related:
    - raw_manifest.py  (WikiSourceConfig loader)
    - wiki_builder.py  (consumes ParsedRecord output)
    - audit.py         (stale detection via agent-memory.json)
"""
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from raw_manifest import (
    WikiSourceConfig, load_agent_memory, save_agent_memory,
    compute_hash, is_stale, now_iso
)
from concept_extractor import infer_cluster_from_content

# Maximum raw content characters kept per record before truncation
MAX_CONTENT_CHARS = 4000


def extract_title(content: str, fallback: str) -> str:
    """
    Extract the first H1 heading from markdown, or use filename fallback.

    Args:
        content:  Raw file content.
        fallback: Filename stem to use if no H1 found.

    Returns:
        Title string.
    """
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback.replace("-", " ").replace("_", " ").title()


def extract_concept_name(title: str) -> str:
    """
    Convert a title into a slug-style concept name for wiki node filenames.

    Args:
        title: Human-readable title.

    Returns:
        Lowercase kebab-case concept name.
    """
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug


def infer_cluster(source_label: str, concept: str, content: str = "") -> str:
    """
    Infer a semantic cluster name from content keywords.

    Delegates to concept_extractor.infer_cluster_from_content for keyword-
    based cluster assignment. Falls back to source_label if extraction fails.

    Args:
        source_label: The label of the source (e.g. 'arch-docs').
        concept:      The concept slug.
        content:      Raw file content for keyword extraction.

    Returns:
        Kebab-case cluster name derived from dominant content keywords.
    """
    return infer_cluster_from_content(source_label, concept, content)


def parse_file(
    file_path: Path,
    source_cfg: WikiSourceConfig,
) -> Optional[Dict[str, Any]]:
    """
    Read and normalize one source file into a ParsedRecord dict.

    Returns None if the file cannot be read or is below min size.

    Args:
        file_path:   Absolute path to the source file.
        source_cfg:  WikiSourceConfig for this source.

    Returns:
        ParsedRecord dict or None.
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"[WARN] Cannot read {file_path}: {e}", file=sys.stderr)
        return None

    if len(content.strip()) < 50:
        return None

    rel_path = source_cfg.relative_path(file_path)
    title = extract_title(content, file_path.stem)
    concept = extract_concept_name(title)
    cluster = infer_cluster(source_cfg.label, concept, content)
    content_hash = compute_hash(content)

    # Truncate for wiki node storage
    excerpt = content[:MAX_CONTENT_CHARS]
    if len(content) > MAX_CONTENT_CHARS:
        excerpt += "\n\n*(content truncated)*"

    return {
        "source_name":   source_cfg.source_name,
        "source_label":  source_cfg.label,
        "source_path":   str(source_cfg.source_path),
        "source_file":   rel_path,
        "file_path":     str(file_path),
        "title":         title,
        "concept":       concept,
        "cluster":       cluster,
        "content":       excerpt,
        "content_hash":  content_hash,
        "extension":     file_path.suffix,
        "generated_at":  now_iso(),
    }


def ingest_source(
    source_cfg: WikiSourceConfig,
    memory: Dict[str, Any],
    force: bool = False,
) -> List[Dict[str, Any]]:
    """
    Ingest all eligible files from one source, skipping unchanged files.

    Args:
        source_cfg: WikiSourceConfig for the source to ingest.
        memory:     Current agent-memory.json contents (may be mutated).
        force:      If True, re-ingest even files with matching hashes.

    Returns:
        List of ParsedRecord dicts for new or changed files.
    """
    files = source_cfg.collect_files()
    records: List[Dict[str, Any]] = []

    print(f"\n[INGEST] Source: {source_cfg.source_name} ({len(files)} eligible files)", file=sys.stderr)
    print(f"         Path  : {source_cfg.source_path}", file=sys.stderr)

    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        rel_path = source_cfg.relative_path(file_path)

        if not force and not is_stale(source_cfg.source_name, rel_path, content, memory):
            continue

        record = parse_file(file_path, source_cfg)
        if record is None:
            continue

        # Update agent-memory
        memory_key = f"{source_cfg.source_name}/{rel_path}"
        memory[memory_key] = {
            "hash":       record["content_hash"],
            "indexed_at": record["generated_at"],
            "concept":    record["concept"],
            "wiki_node":  f"wiki/{record['concept']}.md",
        }
        records.append(record)

    print(f"         New/changed: {len(records)}", file=sys.stderr)
    return records


def main() -> None:
    """Parse CLI arguments and run ingestion pipeline."""
    parser = argparse.ArgumentParser(
        description="Ingest raw source files into ParsedRecord format for wiki_builder"
    )
    parser.add_argument("--wiki-root", required=True, help="Path to the wiki root directory")
    parser.add_argument("--source", default=None, help="Ingest one named source only")
    parser.add_argument("--force", action="store_true", help="Re-ingest all files, ignoring hash check")
    parser.add_argument("--dry-run", action="store_true", help="Report what would be ingested without writing")
    parser.add_argument("--output", default=None, help="Write parsed records JSON to this path (default: stdout)")
    args = parser.parse_args()

    wiki_root = Path(args.wiki_root).resolve()
    memory = load_agent_memory(wiki_root)

    if args.source:
        sources = {args.source: WikiSourceConfig(args.source, wiki_root=wiki_root)}
    else:
        sources = WikiSourceConfig.all_sources(wiki_root=wiki_root)

    if not sources:
        print("[ERROR] No sources found. Run /wiki-init first.", file=sys.stderr)
        sys.exit(1)

    all_records: List[Dict[str, Any]] = []
    for name, cfg in sources.items():
        records = ingest_source(cfg, memory, force=args.force)
        all_records.extend(records)

    print(f"\n[INGEST] Total new/changed records: {len(all_records)}", file=sys.stderr)

    if args.dry_run:
        print("[DRY RUN] No files written.", file=sys.stderr)
        for r in all_records:
            print(f"  + {r['source_label']}/{r['source_file']} -> wiki/{r['concept']}.md", file=sys.stderr)
        return

    # Persist updated memory
    save_agent_memory(memory, wiki_root)

    # Write or print records
    records_json = json.dumps(all_records, indent=2, ensure_ascii=False)
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(records_json, encoding="utf-8")
        print(f"[SAVE] Records written: {args.output}", file=sys.stderr)
    else:
        print(records_json)


if __name__ == "__main__":
    main()
