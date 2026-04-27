---
concept: parse-frontmatter-and-content
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/vector-db-cleanup/scripts/vector_consistency_check.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.393534+00:00
cluster: import
content_hash: 92325ed26cf859dc
---

# Parse frontmatter and content

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/vector-db-cleanup/scripts/vector_consistency_check.py -->
#!/usr/bin/env python3
"""
Vector Consistency Stabilizer 

This module implements the Vector DB Consistency Stabilizer from Protocol 126:
QEC-Inspired AI Robustness (Virtual Stabilizer Architecture).

The stabilizer detects semantic drift by re-querying the vector database to verify
that fact atoms are still supported by the knowledge base.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional
import frontmatter


class StabilizerStatus(Enum):
    """Status codes for stabilizer checks."""
    STABLE = "STABLE"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    CONFIDENCE_DEGRADED = "CONFIDENCE_DEGRADED"
    ERROR = "ERROR"


@dataclass
class FactAtom:
    """
    Atomic unit of retrievable information (Virtual Qubit in Protocol 126).
    
    Attributes:
        id: Unique identifier for the fact atom
        content: The actual fact content (monosemantic)
        source_file: Path to the source markdown file
        timestamp_created: When this fact was created
        confidence_score: Optional confidence score from metadata
        metadata: Additional YAML frontmatter metadata
    """
    id: str
    content: str
    source_file: str
    timestamp_created: datetime
    confidence_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StabilizerResult:
    """
    Result of a vector consistency check.
    
    Attributes:
        fact_atom_id: ID of the checked fact atom
        status: Stabilizer status (STABLE, DRIFT_DETECTED, etc.)
        relevance_delta: Change in relevance score (0.0 = perfect match)
        source_in_top_results: Whether original source appears in top 3 results
        top_results: List of top result file paths
        execution_time_ms: Time taken for the check
        error_message: Optional error message if status is ERROR
    """
    fact_atom_id: str
    status: StabilizerStatus
    relevance_delta: float
    source_in_top_results: bool
    top_results: List[str]
    execution_time_ms: float
    error_message: Optional[str] = None


@dataclass
class StabilizerReport:
    """
    Comprehensive report for a stabilizer run.
    
    Attributes:
        topic_dir: Directory that was checked
        total_facts_checked: Total number of fact atoms checked
        stable_count: Number of STABLE facts
        drift_count: Number of DRIFT_DETECTED facts
        degraded_count: Number of CONFIDENCE_DEGRADED facts
        error_count: Number of ERROR facts
        results: List of individual stabilizer results
        recommendations: List of recommended actions
        execution_time_ms: Total execution time
        timestamp: When the report was generated
    """
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
    Parse markdown file and extract fact atoms.
    
    This function extracts individual facts from markdown content. Each paragraph
    or list item is treated as a potential fact atom. YAML frontmatter is parsed
    for metadata.
    
    Args:
        markdown_file: Path to the markdown file to parse
        
    Returns:
        List of FactAtom objects extracted from the file
        
    Raises:
        FileNotFoundError: If the markdown file doesn't exist
        ValueError: If the file cannot be parsed
    """
    if not markdown_file.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_file}")
    
    try:
        # Parse frontmatter and content
        with open(markdown_file, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        metadata = post.metadata
        content = post.

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/vector-db-ingest/scripts/vector_consistency_check.py -->
#!/usr/bin/env python3
"""
Vector Consistency Stabilizer 

This module implements the Vector DB Consistency Stabilizer from Protocol 126:
QEC-Inspired AI Robustness (Virtual Stabilizer Architecture).

The stabilizer detects semantic drift by re-querying the vector database to verify
that fact atoms are still supported by the knowledge base.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional
import frontmatter


class StabilizerStatus(Enum):
    """Status codes for stabilizer checks."""
    STABLE = "STABLE"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    CONFIDENCE_DEGRADED = "CONFIDENCE_DEGRADED"
    ER

*(combined content truncated)*

## See Also

- [[1-read-the-agent-instructions-and-strip-yaml-frontmatter]]
- [[parse-simple-key-value-yaml-frontmatter-between-the-two-----delimiters]]
- [[split-markdown-lines-into-frontmatter-lines-and-body-lines-around-----delimiters]]
- [[1-inspect-workbook-for-sheets-and-tables-using-openpyxl]]
- [[1-parse-the-hook-payload]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/vector-db-cleanup/scripts/vector_consistency_check.py`
- **Indexed:** 2026-04-27T05:21:04.393534+00:00
