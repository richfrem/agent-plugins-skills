---
concept: re-use-engine-detection-llm-call-from-distill-wiki
source: plugin-code
source_file: obsidian-wiki-engine/scripts/lint_wiki.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.014162+00:00
cluster: path
content_hash: e5d7b24a16089520
---

# Re-use engine detection + LLM call from distill_wiki

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
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
        combined = combined[:MAX_PROMPT_CHAR

*(content truncated)*

## See Also

- [[obsidian-wiki-engine-plugin]]
- [[1-configuration-setup-dynamic-from-profile]]
- [[1-handle-absolute-paths-from-repo-root]]
- [[architectural-patterns-adapted-from-obrasuperpowers-mit-httpsgithubcomobrasuperpowers]]
- [[default-discovery-tags-for-llm-retraining-crawlers-override-via-hugging-face-tags-env-var]]
- [[engine-registry-strict-cheap-model-only]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/scripts/lint_wiki.py`
- **Indexed:** 2026-04-27T05:21:04.014162+00:00
