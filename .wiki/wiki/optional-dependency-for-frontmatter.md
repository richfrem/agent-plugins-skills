---
concept: optional-dependency-for-frontmatter
source: plugin-code
source_file: vector-db/scripts/vector_consistency_check.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.433561+00:00
cluster: import
content_hash: 3f6f6c0e7d3816cc
---

# Optional dependency for frontmatter

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

#!/usr/bin/env python
"""
vector_consistency_check.py
=====================================

Purpose:
    Implements the Vector DB Consistency Stabilizer (Protocol 126).
    Detects semantic drift by verifying that atomic facts still resolve to their 
    original source documents within the Vector index.

Layer: Retrieve / Curate

Usage:
    python vector_consistency_check.py --profile wiki --topic .agent/learning/
"""

import sys
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional

# Optional dependency for frontmatter
try:
    import frontmatter
except ImportError:
    frontmatter = None

# Robustly discover the Project Root
def _find_project_root(start_path: Path) -> Path:
    """Walks up from start_path to find the first directory containing .git."""
    current = start_path.resolve()
    for parent in [current] + list(current.parents):
        if (parent / ".git").is_dir():
            return parent
    return current.parents[2]

PROJECT_ROOT = _find_project_root(Path(__file__))
SCRIPT_DIR = Path(__file__).resolve().parent

# Ensure local imports work correctly
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:
    from vector_config import VectorConfig
    from operations import VectorDBOperations
except ImportError as e:
    print(f"[ERROR] Could not import vector dependencies: {e}")
    sys.exit(1)


class StabilizerStatus(Enum):
    """Status codes for semantic stability checks."""
    STABLE = "STABLE"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    CONFIDENCE_DEGRADED = "CONFIDENCE_DEGRADED"
    ERROR = "ERROR"


@dataclass
class FactAtom:
    """Atomic unit of retrievable information extracted from source docs."""
    id: str
    content: str
    source_file: str
    timestamp_created: datetime
    confidence_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StabilizerResult:
    """Result metrics for a single fact atom consistency check."""
    fact_atom_id: str
    status: StabilizerStatus
    relevance_delta: float
    source_in_top_results: bool
    top_results: List[str]
    execution_time_ms: float
    error_message: Optional[str] = None


@dataclass
class StabilizerReport:
    """Consolidated report of an entire consistency audit run."""
    topic_dir: str
    total_facts_checked: int
    stable_count: int
    drift_count: int
    degraded_count: int
    error_count: int
    results: List[StabilizerResult]
    recommendations: List[str]
    execution_time_ms: float
    timestamp: datetime


def extract_fact_atoms(markdown_file: Path) -> List[FactAtom]:
    """
    Parses a Markdown file and extracts atomic, monosemantic fact chunks.

    Args:
        markdown_file: Path to the .md file to parse.

    Returns:
        List of extracted FactAtom objects.
    """
    if not markdown_file.exists():
        return []
    
    try:
        content = markdown_file.read_text(encoding='utf-8', errors='replace')
        metadata = {}
        
        if frontmatter:
            try:
                post = frontmatter.loads(content)
                metadata = post.metadata
                content = post.content
            except Exception:
                pass
        
        timestamp = datetime.fromtimestamp(markdown_file.stat().st_mtime)
        fact_atoms: List[FactAtom] = []
        fact_id_counter = 0
        
        # Split into paragraphs/bullets
        lines = content.split('\n')
        current_paragraph: List[str] = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith(('#', '```')):
                if current_paragraph:
                    text = ' '.join(current_paragraph).strip()
                    if len(text) > 20:
                        fact_atoms.append(FactAtom(
                            f"{markdown_file.ste

*(content truncated)*

## See Also

- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]
- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[attempt-to-handle-langchain-version-differences-for-storage]]
- [[capture-optional-leading-so-image-links-are-preserved-correctly]]
- [[check-all-text-files-in-skill-for-regex-py-mentions]]
- [[check-for-broken-symlinks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/scripts/vector_consistency_check.py`
- **Indexed:** 2026-04-27T05:21:04.433561+00:00
