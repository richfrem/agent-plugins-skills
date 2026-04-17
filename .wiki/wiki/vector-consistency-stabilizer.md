---
concept: vector-consistency-stabilizer
source: plugin-code
source_file: vector-db/assets/resources/stabilizers/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.440235+00:00
cluster: protocol
content_hash: 2d095af9fd8d8382
---

# Vector Consistency Stabilizer

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Vector Consistency Stabilizer

**Protocol 126: QEC-Inspired AI Robustness (Virtual Stabilizer Architecture)**

## Overview

The Vector Consistency Stabilizer is the first implementation of Protocol 126's Virtual Stabilizer Architecture. It detects semantic drift by re-querying the vector database to verify that fact atoms are still supported by the knowledge base.

**Mission:** LEARN-CLAUDE-003  
**Author:** Antigravity AI  
**Date:** 2025-12-14  
**Status:** ✅ Implemented

## What is a Stabilizer?

Inspired by Quantum Error Correction (QEC), a stabilizer is a background integrity check that detects errors without disrupting the system state. In our case:

- **Virtual Qubits** = Fact Atoms (atomic units of knowledge)
- **Stabilizers** = Integrity Measurements (vector consistency checks)
- **Correction Frames** = Recovery Mechanisms (re-grounding, re-ingestion)

## Architecture

### Fact Atoms (Virtual Qubits)

Atomic units of retrievable information with:
- Monosemantic content (single concept)
- Source chunk traceability
- Temporal validity tracking
- YAML frontmatter metadata

### Vector Consistency Check (Stabilizer)

The stabilizer performs the following steps:

1. **Extract Fact Atoms** from markdown files
2. **Re-query Vector DB** with fact content
3. **Check Top Results** - Is original source in top 3?
4. **Calculate Relevance Delta** - How much has relevance changed?
5. **Determine Status**:
   - `STABLE`: Original source in top 3 results
   - `DRIFT_DETECTED`: Original source not in top 3 (relevance delta > threshold)
   - `CONFIDENCE_DEGRADED`: Relevance delta > threshold but not drift
   - `ERROR`: Query failed or no results

### Stabilizer Report

Comprehensive report including:
- Total facts checked
- Status breakdown (stable/drift/degraded/error)
- Detailed results for non-stable facts
- Recommendations for action
- Execution metrics

## Usage

### Basic Usage

```python
from pathlib import Path
from scripts.stabilizers.vector_consistency_check import (
    run_stabilizer_check,
    format_report,
    export_report_json
)

# Define your native Python Vector DB query function
def vector_query(query: str, max_results: int = 5) -> dict:
    # Call the actual Vector DB query script here
    # This would use ./scripts/query.py in production
    pass

# Run stabilizer check on a topic directory
topic_dir = Path('LEARNING/topics/quantum-error-correction')
report = run_stabilizer_check(
    topic_dir=topic_dir,
    vector_query_func=vector_query,
    max_results=5,
    relevance_threshold=0.2
)

# Display human-readable report
print(format_report(report))

# Export JSON for machine processing
export_report_json(report, Path('stabilizer_report.json'))
```

### Extract Fact Atoms Only

```python
from pathlib import Path
from scripts.stabilizers.vector_consistency_check import extract_fact_atoms

markdown_file = Path('LEARNING/topics/quantum-error-correction/notes/fundamentals.md')
fact_atoms = extract_fact_atoms(markdown_file)

for fact in fact_atoms:
    print(f"ID: {fact.id}")
    print(f"Content: {fact.content[:100]}...")
    print(f"Source: {fact.source_file}")
    print()
```

### Check Single Fact Atom

```python
from scripts.stabilizers.vector_consistency_check import (
    extract_fact_atoms,
    vector_consistency_check
)

# Extract facts
fact_atoms = extract_fact_atoms(markdown_file)

# Check first fact
result = vector_consistency_check(
    fact_atom=fact_atoms[0],
    vector_query_func=vector_query,
    max_results=5,
    relevance_threshold=0.2
)

print(f"Status: {result.status.value}")
print(f"Relevance Delta: {result.relevance_delta:.3f}")
print(f"Source in Top 3: {result.source_in_top_results}")
```

## Testing

Run the test suite to validate the implementation:

```bash
python scripts/stabilizers/test_stabilizer.py
```

The test suite includes:
1. **Fact Extraction Test** - Validates markdown parsing and fact atom extraction
2. **Baseline Stability Test** - Checks that recent, high-quality facts are STAB

*(content truncated)*

## See Also

- [[code-file-vector-consistency-checkpy]]
- [[code-file-vector-consistency-checkpy]]
- [[code-file-vector-consistency-checkpy]]
- [[code-file-vector-consistency-checkpy]]
- [[code-file-vector-consistency-checkpy]]
- [[code-file-vector-consistency-checkpy]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/assets/resources/stabilizers/README.md`
- **Indexed:** 2026-04-17T06:42:10.440235+00:00
