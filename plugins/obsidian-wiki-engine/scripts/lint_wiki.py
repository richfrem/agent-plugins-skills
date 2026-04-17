#!/usr/bin/env python3
"""
lint_wiki.py
=====================================

Purpose:
    Semantic health check for the Obsidian LLM wiki.
    Implements Karpathy's "linting" step: use an LLM to find inconsistencies,
    suggest missing articles, identify stale/contradictory content, and surface
    interesting connection candidates.

    Reads wiki/_index.md + a sample of concept pages, builds a batch health-
    check prompt, calls the cheapest available LLM CLI (same fallback chain as
    distill_wiki.py), and writes the report to meta/lint-report.md.

    Structural checks (orphans, missing summaries) are still handled by audit.py.
    This script handles *semantic* quality: contradictions, gaps, new article ideas.

Layer: Lint / Wiki

Usage:
    python ./scripts/lint_wiki.py --wiki-root /path/to/wiki-root
    python ./scripts/lint_wiki.py --wiki-root /path/to/wiki-root --sample 20
    python ./scripts/lint_wiki.py --wiki-root /path/to/wiki-root --engine claude
    python ./scripts/lint_wiki.py --wiki-root /path/to/wiki-root --dry-run

Related:
    - audit.py         (structural coverage checks)
    - distill_wiki.py  (shares LLM engine detection + call_llm)
    - wiki_builder.py  (generates the wiki nodes being linted)
"""
import sys
import json
import argparse
import random
from pathlib import Path
from typing import List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from raw_manifest import now_iso

# Re-use engine detection + LLM call from distill_wiki
from distill_wiki import detect_engine, call_llm

# Max chars of wiki content to include in the lint prompt
MAX_PROMPT_CHARS = 12_000
# Max concept nodes to sample for deep review
DEFAULT_SAMPLE_SIZE = 15


def _read_index(wiki_root: Path) -> str:
    """Read wiki/_index.md, return empty string if missing."""
    index_path = wiki_root / "wiki" / "_index.md"
    if not index_path.exists():
        return ""
    return index_path.read_text(encoding="utf-8")


def _sample_concept_pages(wiki_root: Path, n: int) -> List[Tuple[str, str]]:
    """
    Sample up to n concept pages from wiki/*.md (excluding _ prefix pages).

    Returns:
        List of (concept_slug, content) tuples.
    """
    wiki_dir = wiki_root / "wiki"
    if not wiki_dir.exists():
        return []

    pages = [f for f in wiki_dir.glob("*.md") if not f.name.startswith("_")]
    if len(pages) > n:
        pages = random.sample(pages, n)

    result = []
    for page in sorted(pages, key=lambda p: p.stem):
        try:
            content = page.read_text(encoding="utf-8")
            # Keep first 800 chars per page to fit the budget
            result.append((page.stem, content[:800]))
        except Exception:
            continue
    return result


def build_lint_prompt(
    index_content: str,
    concept_samples: List[Tuple[str, str]],
) -> str:
    """
    Build the semantic health-check prompt.

    Asks the LLM to analyze the wiki and report:
    1. Inconsistencies or contradictions between articles
    2. Concepts that appear to be missing (implied by others but not present)
    3. Articles that appear stale or outdated (vague dates, superseded info)
    4. Interesting connection candidates (pairs of concepts worth linking)
    5. Suggested new article titles (topics implied but not yet in the wiki)

    Args:
        index_content:   Content of wiki/_index.md.
        concept_samples: List of (slug, excerpt) tuples.

    Returns:
        Prompt string.
    """
    parts = [
        "You are a knowledge base curator reviewing a personal LLM wiki.\n\n",
        "## Wiki Index\n\n",
        index_content[:3000] if index_content else "*(index not available)*",
        "\n\n## Sample Concept Pages\n\n",
    ]

    for slug, excerpt in concept_samples:
        parts.append(f"### {slug}\n{excerpt}\n\n")

    combined = "".join(parts)
    if len(combined) > MAX_PROMPT_CHARS:
        combined = combined[:MAX_PROMPT_CHARS] + "\n\n*(content truncated for brevity)*"

    return combined + (
        "\n\n---\n\n"
        "Based on the wiki content above, produce a structured health report with these sections:\n\n"
        "## 1. Inconsistencies\n"
        "List any factual contradictions or conflicting claims found between articles.\n"
        "Format: `- [concept-a] vs [concept-b]: <describe the inconsistency>`\n\n"
        "## 2. Missing Concepts\n"
        "List concepts that are implied by existing articles but not yet written.\n"
        "Format: `- <concept-name>: implied by [[existing-concept]]`\n\n"
        "## 3. Stale or Weak Articles\n"
        "List articles that appear vague, outdated, or need richer content.\n"
        "Format: `- [[concept]]: <brief reason>`\n\n"
        "## 4. Connection Candidates\n"
        "Suggest wikilink connections that don't exist but should.\n"
        "Format: `- [[concept-a]] ↔ [[concept-b]]: <rationale>`\n\n"
        "## 5. New Article Suggestions\n"
        "Suggest 5-10 new article titles the wiki should have based on the topics covered.\n"
        "Format: `- <proposed-title>: <one-sentence description>`\n\n"
        "Be specific and reference actual article names from the index. "
        "If the sample is small, note that your analysis is limited to the provided sample.\n"
    )


def write_lint_report(wiki_root: Path, report_content: str, engine: str, model: str) -> Path:
    """
    Write the lint report to meta/lint-report.md.

    Args:
        wiki_root:      Wiki root directory.
        report_content: LLM-generated report text.
        engine:         Engine used (for attribution).
        model:          Model used (for attribution).

    Returns:
        Path to the written report.
    """
    meta_dir = wiki_root / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    report_path = meta_dir / "lint-report.md"

    lines = [
        "---",
        f'generated_at: "{now_iso()}"',
        f'engine: "{engine}"',
        f'model: "{model}"',
        "---",
        "",
        "# Wiki Semantic Health Report",
        "",
        f"*Generated by `lint_wiki.py` using {engine} ({model})*",
        "",
        report_content,
        "",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> None:
    """Parse CLI arguments and run the wiki semantic health check."""
    parser = argparse.ArgumentParser(
        description="Semantic health check for the Obsidian LLM wiki"
    )
    parser.add_argument("--wiki-root", required=True, help="Path to the wiki root directory")
    parser.add_argument(
        "--sample",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
        help=f"Number of concept pages to sample for deep review (default: {DEFAULT_SAMPLE_SIZE})",
    )
    parser.add_argument(
        "--engine",
        default=None,
        choices=["copilot", "claude", "gemini"],
        help="Force a specific LLM CLI engine",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build and print the prompt without calling the LLM",
    )
    parser.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        help="Output report path as JSON on completion",
    )
    args = parser.parse_args()

    wiki_root = Path(args.wiki_root).resolve()
    wiki_dir = wiki_root / "wiki"

    if not wiki_dir.exists():
        print("[ERROR] Wiki directory not found. Run /wiki-ingest first.")
        sys.exit(1)

    total_nodes = len([f for f in wiki_dir.glob("*.md") if not f.name.startswith("_")])
    if total_nodes == 0:
        print("[ERROR] No wiki nodes found. Run /wiki-ingest first.")
        sys.exit(1)

    engine, model = detect_engine(args.engine)

    index_content = _read_index(wiki_root)
    concept_samples = _sample_concept_pages(wiki_root, args.sample)

    prompt = build_lint_prompt(index_content, concept_samples)

    print(f"\n[LINT] Wiki semantic health check")
    print(f"       Engine : {engine} ({model})")
    print(f"       Nodes  : {total_nodes} total, {len(concept_samples)} sampled")
    print(f"       Wiki   : {wiki_root}\n")

    if args.dry_run:
        print("[DRY RUN] Lint prompt:\n")
        print(prompt[:2000])
        if len(prompt) > 2000:
            print(f"\n... [{len(prompt) - 2000} more chars truncated]")
        return

    print("[RUN] Calling LLM for semantic analysis...", end=" ", flush=True)
    report_content = call_llm(engine, model, prompt, timeout=180)

    if not report_content:
        print("FAILED")
        print("[ERROR] LLM call failed. Try --engine claude or --engine gemini.")
        sys.exit(1)

    print(f"OK ({len(report_content)} chars)")

    report_path = write_lint_report(wiki_root, report_content, engine, model)
    print(f"[DONE] Lint report written: {report_path}")

    if args.output_json:
        print(json.dumps({"report_path": str(report_path), "engine": engine, "model": model}))


if __name__ == "__main__":
    main()
