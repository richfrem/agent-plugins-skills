---
concept: code-file-vector-consistency-checkpy
source: plugin-code
source_file: vector-db/assets/resources/stabilizers/vector_consistency_check.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.441725+00:00
cluster: append
content_hash: c12a9990d9396cd6
---

# Code File: vector_consistency_check.py

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Code File: vector_consistency_check.py

**Path:** `../../../scripts/vector_consistency_check.py`
**Language:** Python
**Type:** Code Implementation

## Module Description

Vector Consistency Stabilizer - Protocol 126 Implementation

This module implements the Vector DB Consistency Stabilizer from Protocol 126:
QEC-Inspired AI Robustness (Virtual Stabilizer Architecture).

The stabilizer detects semantic drift by re-querying the vector database to verify
that fact atoms are still supported by the knowledge base.

Mission: LEARN-CLAUDE-003
Author: Antigravity AI
Date: 2025-12-14

## Dependencies

- `json`
- `re`
- `dataclasses.dataclass`
- `dataclasses.field`
- `datetime.datetime`
- `enum.Enum`
- `pathlib.Path`
- `typing.List`
- `typing.Dict`
- `typing.Any`
- ... and 2 more

## Class: `StabilizerStatus`

**Line:** 26

**Documentation:**

Status codes for stabilizer checks.

**Source Code:**

```python
class StabilizerStatus(Enum):
    """Status codes for stabilizer checks."""
    STABLE = "STABLE"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    CONFIDENCE_DEGRADED = "CONFIDENCE_DEGRADED"
    ERROR = "ERROR"
```

## Class: `FactAtom`

**Line:** 35

**Documentation:**

Atomic unit of retrievable information (Virtual Qubit in Protocol 126).

Attributes:
    id: Unique identifier for the fact atom
    content: The actual fact content (monosemantic)
    source_file: Path to the source markdown file
    timestamp_created: When this fact was created
    confidence_score: Optional confidence score from metadata
    metadata: Additional YAML frontmatter metadata

**Source Code:**

```python
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
```

## Class: `StabilizerResult`

**Line:** 56

**Documentation:**

Result of a vector consistency check.

Attributes:
    fact_atom_id: ID of the checked fact atom
    status: Stabilizer status (STABLE, DRIFT_DETECTED, etc.)
    relevance_delta: Change in relevance score (0.0 = perfect match)
    source_in_top_results: Whether original source appears in top 3 results
    top_results: List of top result file paths
    execution_time_ms: Time taken for the check
    error_message: Optional error message if status is ERROR

**Source Code:**

```python
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
```

## Class: `StabilizerReport`

**Line:** 79

**Documentation:**

Comprehensive report for a stabilizer run.

Attributes:
    topic_dir: Directory that was checked
    total_facts_checked: Total number of fact atoms checked
    stable_count: Number of STABLE facts
    drift_count: Number of DRIFT_DETECTED facts
    degraded_count: Number of CONFIDENCE_DEGRADED facts
    error_count: Number of ERROR facts
    results: List of individual stab

*(content truncated)*

## See Also

- [[vector-consistency-stabilizer]]
- [[vector-consistency-stabilizer]]
- [[vector-consistency-stabilizer]]
- [[vector-consistency-stabilizer]]
- [[vector-consistency-stabilizer]]
- [[vector-consistency-stabilizer]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/assets/resources/stabilizers/vector_consistency_check.md`
- **Indexed:** 2026-04-17T06:42:10.441725+00:00
