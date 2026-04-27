---
concept: update-scores-for-an-existing-entry
source: plugin-code
source_file: agent-scaffolders/scripts/update_ranked_skills.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.230019+00:00
cluster: skill
content_hash: b8d40aacd379a772
---

# Update scores for an existing entry

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/update_ranked_skills.py -->
"""
update_ranked_skills.py

CLI utility to update or add entries in summary-ranked-skills.json.
Used by the eval-autoresearch-fit skill after completing an assessment.

Usage:
    # Update scores for an existing entry
    python update_ranked_skills.py \\
        --plugin agent-execution-disciplines \\
        --skill verification-before-completion \\
        --objectivity 8 --speed 7 --frequency 10 --utility 10 \\
        --verdict HIGH \\
        --loop-type LLM_IN_LOOP \\
        --evaluator-command "python evaluate.py --skill SKILL.md --tasks tasks/ --trials 5" \\
        --mutation-target "SKILL.md" \\
        --barriers "Needs golden task set" "LLM non-determinism requires N=5 averaging" \\
        --eval-notes "Goodhart risk: must verify Bash call is a real test command" \\
        --status EVALUATED

    # Add a new entry
    python update_ranked_skills.py \\
        --plugin my-plugin \\
        --skill my-skill \\
        --objectivity 7 --speed 9 --frequency 5 --utility 6 \\
        --verdict MEDIUM \\
        --proposed-benchmark "Exit code from pytest run" \\
        --justification "Fast loop, objective metric" \\
        --status PENDING

    # Show current entry
    python update_ranked_skills.py --plugin my-plugin --skill my-skill --show

    # List all entries with status
    python update_ranked_skills.py --list

    # List only entries matching a status
    python update_ranked_skills.py --list --filter-status EVALUATED

    # Show next 3 highest-scored unevaluated entries (for structured batch)
    python update_ranked_skills.py --next-batch 3

    # Pick 3 random unevaluated entries (for sampling / ad-hoc testing)
    python update_ranked_skills.py --random 3
"""

import argparse
import json
import random
import sys
from datetime import date
from pathlib import Path


# Default path relative to this script's location
DEFAULT_JSON_PATH = Path(__file__).parent.parent / "assets" / "resources" / "summary-ranked-skills.json"


def load_json(path: Path) -> dict:
    """Load the ranked skills JSON file."""
    if not path.exists():
        print(f"ERROR: JSON file not found at {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict, path: Path) -> None:
    """Save the ranked skills JSON file, preserving order."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def find_entry(skills: list, plugin: str, skill: str) -> tuple[int, dict | None]:
    """Find an entry by plugin+skill name. Returns (index, entry) or (-1, None)."""
    for i, entry in enumerate(skills):
        if entry.get("plugin") == plugin and entry.get("skill") == skill:
            return i, entry
    return -1, None


def compute_total(entry: dict) -> int:
    """Recompute total from the four score fields."""
    return (
        entry.get("objectivity_score", 0)
        + entry.get("execution_speed_score", 0)
        + entry.get("frequency_of_use_score", 0)
        + entry.get("potential_utility_score", 0)
    )


def verdict_from_total(total: int) -> str:
    """Derive viability verdict from total score."""
    if total >= 32:
        return "HIGH"
    elif total >= 24:
        return "MEDIUM"
    elif total >= 16:
        return "LOW"
    else:
        return "NOT_VIABLE"


def show_entry(entry: dict) -> None:
    """Pretty-print a single entry."""
    print(f"\n{'='*60}")
    print(f"  {entry['plugin']} / {entry['skill']}")
    print(f"{'='*60}")
    scores = {
        "objectivity": entry.get("objectivity_score", "-"),
        "speed": entry.get("execution_speed_score", "-"),
        "frequency": entry.get("frequency_of_use_score", "-"),
        "utility": entry.get("potential_utility_score", "-"),
    }
    total = entry.get("total_autoresearch_viability", "-")
    refined = entry.get("refined_total")
    print(f"  Scores: obj={scores['objectivity']} spd={scores['spe

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/eval-autoresearch-fit/scripts/update_ranked_skills.py -->
"""
update_ranked_skills.py

CLI utility to update or add entries in summary-ranked-skills.json.
Used by the eval-autoresearch-fit skill after completing an assessment.

Usage:
    # Update scores for an existing entry
    python update_ranked_skills.py \\
        --plugin agent-execution-disciplines \\
        --skill verification-before-completion \\
        --objectivity 8 --speed 7 --frequency 10 --utility 10 \\
        --verdict HIGH \\
        --loop-type LLM_IN_LOOP \\
        --evaluator-command "python evaluate.py --skill SKILL.md --tasks tasks/ --trials 5" \\
        --mutation-target "SKILL.md" \\
        --barriers "Needs golden task set" "LLM non-determinism requires N=5 averaging" \\
        --eval-notes "Goodhart risk: must verify Bash call is a real test

*(combined content truncated)*

## See Also

- [[atomically-replace-an-existing-path-with-a-new-symlink-pointing-to-src]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]
- [[attempt-to-handle-langchain-version-differences-for-storage]]
- [[build-scores-summary]]
- [[check-all-text-files-in-skill-for-regex-py-mentions]]
- [[check-for-broken-symlinks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/update_ranked_skills.py`
- **Indexed:** 2026-04-27T05:21:04.230019+00:00
