---
name: vector-db-audit
plugin: agent-memory
description: Audit Vector DB coverage -- compares the live filesystem manifest against the ChromaDB index to identify coverage gaps.
allowed-tools: Bash, Read, Write
---

# Vector DB Audit (`vector-db-audit`)

Systematically audit the Vector Database to identify indexing coverage gaps between the project manifest and document chunks in ChromaDB collections.

## Contents

- [Critical Constraints](#critical-constraints)
- [Capabilities](#capabilities)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)

## Critical Constraints

1. **Read-Only Inspection**: Audit checks evaluate collections and filesystem manifests without writing or deleting index records.
2. **Profile Specification**: Mandatory `--profile` flag to ensure the target collection and manifest are matched accurately.
3. **No Direct SQLite Access**: Must execute via `scripts/audit_vector.py`; never query SQLite backing tables directly.

## Capabilities

- **Coverage Analysis**: Calculates the percentage of project documentation vectorized in ChromaDB.
- **Gap Identification**: Detects files included in the manifest but missing from the collection.
- **Batch Exporting**: Generates CSV lists of missing files for targeted ingestion.
- **Dynamic Configuration**: Automatically loads collection settings from selected profile.

## Quick start

Execute a coverage audit against a specific profile:

```bash
python3 scripts/audit_vector.py --profile wiki --report vector_audit.txt --csv missing_vector.csv
```

## Workflow

1. **Select Profile**: Identify target collection profile (e.g. `wiki`, `codebase`).
2. **Execute Audit**: Run `audit_vector.py` to compare filesystem manifest against the ChromaDB collection.
3. **Review Gaps**: Inspect `vector_audit.txt` and `missing_vector.csv` for missing documents.
4. **Coordinate Ingestion**: Dispatch missing file paths to `vector-db-ingest` for vectorization.

## Verification

Validate report output generation and vector collection connectivity:

```bash
python3 scripts/audit_vector.py --profile wiki --check-only
```
