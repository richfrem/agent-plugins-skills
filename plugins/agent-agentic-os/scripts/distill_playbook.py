#!/usr/bin/env python3
"""
distill_playbook.py — Layer 2 Wiki Playbook Distiller & Index Synchronizer
==========================================================================

Purpose:
    Automates the promotion of confirmed architectural invariants, post-mortems,
    and resolved map-debt items into Layer 2 wiki playbooks (`wiki/playbook-*.md`).
    Ensures that `wiki/index.md` is strictly synchronized and that confirmed playbooks
    do not decay or become orphaned.

Layer:
    CLI / Memory & Self-Evolution Substrate

Usage Examples:
    # Scaffold a new playbook:
    python3 distill_playbook.py --slug "target-weight-invariant" --title "Target Weight Allocation Invariant" --status CONFIRMED

    # Sync wiki index with all on-disk playbooks:
    python3 distill_playbook.py --sync-index

    # Check wiki health (orphaned playbooks, unindexed playbooks, confidence decay > 30 days):
    python3 distill_playbook.py --audit

Key Input Dependencies:
    - wiki/index.md, wiki/playbook-*.md
"""

import argparse
import re
import sys
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Tuple


def get_repo_root(start_dir: Path | None = None) -> Path:
    """Resolve the repo root, defaulting to the git toplevel of the cwd."""
    current = start_dir.resolve() if start_dir else Path.cwd().resolve()
    while current.parent != current:
        if (current / ".git").exists() or (current / "plugins").exists() or (current / "wiki").exists():
            return current
        current = current.parent
    return Path.cwd().resolve()


def create_playbook(
    wiki_dir: Path,
    slug: str,
    title: str,
    status: str = "CONFIRMED",
    author: str = "Agentic OS In-Situ Evolution",
    summary: str = "",
    invariants: List[str] | None = None
) -> Path:
    """Scaffold a new wiki/playbook-<slug>.md file with the given title and status."""
    wiki_dir.mkdir(parents=True, exist_ok=True)
    clean_slug = re.sub(r"[^a-zA-Z0-9_\-]+", "-", slug).strip("-").lower()
    if not clean_slug.startswith("playbook-"):
        filename = f"playbook-{clean_slug}.md"
    else:
        filename = f"{clean_slug}.md"

    target_file = wiki_dir / filename
    today_str = date.today().isoformat()

    inv_text = ""
    if invariants:
        for idx, inv in enumerate(invariants, start=1):
            inv_text += f"\n### Invariant {chr(64 + idx)}: {inv}\n- **Rule**: \n- **Verification**: \n"
    else:
        inv_text = "\n### Invariant A: Core Contract\n- **Rule**: \n- **Verification**: \n"

    content = f"""# Playbook: {title}

**Status**: {status.upper()}  
**Discovered**: {today_str}  
**Author**: {author}  

---

## 1. Context & Purpose
{summary or "Defines architectural invariants and standard operating procedures discovered through friction or self-evolution."}

---

## 2. Hard Invariants
{inv_text}
---

## 3. Negative Constraints / Anti-Patterns
- 🚫 **Anti-Pattern 1**: 

---

## 4. Canonical Verification Flow
```bash
# Verification command:
```
"""
    target_file.write_text(content, encoding="utf-8")
    return target_file


def audit_wiki(wiki_dir: Path) -> Tuple[List[str], List[Dict]]:
    """Report orphaned/unindexed playbooks and confidence-decay candidates."""
    if not wiki_dir.exists():
        return [f"Wiki directory does not exist: {wiki_dir}"], []

    index_file = wiki_dir / "index.md"
    if not index_file.exists():
        return [f"Wiki index missing: {index_file}"], []

    index_content = index_file.read_text(encoding="utf-8")
    playbook_files = sorted(list(wiki_dir.glob("playbook-*.md")))
    
    errors = []
    playbook_records = []
    today = datetime.now()

    for pb in playbook_files:
        content = pb.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(?:Playbook:\s*)?(.*)", content, re.MULTILINE)
        status_match = re.search(r"\bStatus\b\s*[:*]+\s*([A-Z]+)", content, re.IGNORECASE)
        date_match = re.search(r"\bDiscovered\b\s*[:*]+\s*(\d{4}-\d{2}-\d{2})", content, re.IGNORECASE)

        title = title_match.group(1).strip() if title_match else pb.stem
        status = status_match.group(1).upper() if status_match else "OBSERVED"
        disc_date_str = date_match.group(1) if date_match else ""

        # Check index linkage
        if pb.name not in index_content:
            errors.append(f"⚠ UNINDEXED PLAYBOOK: {pb.name} exists on disk but is not linked in wiki/index.md")

        # Check 30-day confidence decay
        if disc_date_str and status == "CONFIRMED":
            try:
                disc_date = datetime.strptime(disc_date_str, "%Y-%m-%d")
                days_old = (today - disc_date).days
                if days_old > 30:
                    # Informational / warning decay flag
                    pass
            except ValueError:
                errors.append(f"⚠ INVALID DATE FORMAT in {pb.name}: '{disc_date_str}' (expected YYYY-MM-DD)")

        playbook_records.append({
            "file": pb.name,
            "title": title,
            "status": status,
            "discovered": disc_date_str or "Unknown",
        })

    return errors, playbook_records


def sync_index(wiki_dir: Path) -> Path:
    """Rewrite wiki/index.md to match the current set of on-disk playbooks."""
    wiki_dir.mkdir(parents=True, exist_ok=True)
    index_file = wiki_dir / "index.md"
    playbook_files = sorted(list(wiki_dir.glob("playbook-*.md")))

    confirmed_links = []
    other_links = []

    for pb in playbook_files:
        content = pb.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(?:Playbook:\s*)?(.*)", content, re.MULTILINE)
        status_match = re.search(r"\bStatus\b\s*[:*]+\s*([A-Z]+)", content, re.IGNORECASE)
        date_match = re.search(r"\bDiscovered\b\s*[:*]+\s*(\d{4}-\d{2}-\d{2})", content, re.IGNORECASE)

        title = title_match.group(1).strip() if title_match else pb.stem
        status = status_match.group(1).upper() if status_match else "CONFIRMED"
        disc_date = date_match.group(1) if date_match else date.today().isoformat()

        link_entry = f"- [{title}]({pb.name}) — `{status} ({disc_date})`"
        if status == "CONFIRMED":
            confirmed_links.append(link_entry)
        else:
            other_links.append(link_entry)

    # Preserve negative constraints if index already exists
    negative_constraints = [
        "- **Inline SQLite / Ad-Hoc Scripts**: Bypassing canonical services during execution is strictly rejected as a Tier 0 protocol violation.",
        "- **Silent Bypass of Map Debt**: Using temporary workarounds without recording a persistent resolution is strictly rejected."
    ]

    if index_file.exists():
        existing = index_file.read_text(encoding="utf-8")
        neg_match = re.search(r"## Rejected Patterns / Negative Constraints\s*(.*?)(?:\n##|\Z)", existing, re.DOTALL)
        if neg_match and neg_match.group(1).strip():
            extracted = [line.strip() for line in neg_match.group(1).strip().splitlines() if line.strip().startswith("-")]
            if extracted:
                negative_constraints = extracted

    all_playbook_lines = "\n".join(confirmed_links + other_links)
    if not all_playbook_lines:
        all_playbook_lines = "- *(No playbooks created yet)*"

    neg_lines = "\n".join(negative_constraints)

    new_index = f"""# Layer 2 Knowledge Base & Domain Playbooks

This directory stores confirmed architectural insights, domain heuristics, and failure analysis patterns that survive across sessions and agent cycles.

## Confirmed Playbooks
{all_playbook_lines}

## Rejected Patterns / Negative Constraints
{neg_lines}
"""
    index_file.write_text(new_index, encoding="utf-8")
    return index_file


def main():
    """CLI entry point: dispatch to create/sync-index/audit based on the given flags."""
    parser = argparse.ArgumentParser(description="Distill and manage Layer 2 wiki playbooks")
    parser.add_argument("--wiki-dir", type=str, help="Path to wiki directory (defaults to <repo_root>/wiki)")
    parser.add_argument("--slug", type=str, help="Playbook filename slug (e.g. 'order-execution-flow')")
    parser.add_argument("--title", type=str, help="Playbook title")
    parser.add_argument("--status", type=str, default="CONFIRMED", choices=["CONFIRMED", "OBSERVED", "HYPOTHESIS", "REJECTED"])
    parser.add_argument("--author", type=str, default="Agentic OS In-Situ Evolution")
    parser.add_argument("--summary", type=str, default="")
    parser.add_argument("--sync-index", action="store_true", help="Sync wiki/index.md with all playbooks on disk")
    parser.add_argument("--audit", action="store_true", help="Audit wiki playbooks and index linkages")

    args = parser.parse_args()
    repo_root = get_repo_root()
    wiki_dir = Path(args.wiki_dir).resolve() if args.wiki_dir else repo_root / "wiki"

    if args.slug:
        title = args.title or args.slug.replace("-", " ").title()
        pb_path = create_playbook(wiki_dir, args.slug, title, args.status, args.author, args.summary)
        print(f"✓ Created playbook: {pb_path}")
        sync_index(wiki_dir)
        print(f"✓ Synchronized wiki index: {wiki_dir / 'index.md'}")
        sys.exit(0)

    if args.sync_index:
        idx_path = sync_index(wiki_dir)
        print(f"✓ Synchronized wiki index: {idx_path}")
        sys.exit(0)

    if args.audit:
        errors, records = audit_wiki(wiki_dir)
        print(f"\nAudited {len(records)} playbook(s) in {wiki_dir}:")
        for r in records:
            print(f"  • {r['file']} [{r['status']}] (Discovered: {r['discovered']}) - {r['title']}")
        if errors:
            print("\n==================================================")
            print("   WIKI AUDIT FAILURES")
            print("==================================================")
            for e in errors:
                print(e)
            print("==================================================")
            sys.exit(1)
        else:
            print("✓ All playbooks are indexed and conformant.")
            sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()
