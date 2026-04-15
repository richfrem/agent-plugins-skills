# vector-db-audit
---
name: vector-db-audit
description: Audit Vector DB coverage compare manifest against ChromaDB index
trigger_phrases:
  - "audit vector db"
  - "check vector coverage"
  - "vector inventory audit"
  - "show missing vector files"
  - "check vector gap"
---

## Purpose
Systematically audit the Vector Database to identify gaps between the project manifest and the actual document chunks stored in ChromaDB.

## Capabilities
- **Coverage Analysis**: Calculates the percentage of project documentation currently vectorized.
- **Gap Identification**: Detects files that are included in the manifest but missing from the ChromaDB collection.
- **Exporting**: Generates CSV lists of missing files for batch ingestion.
- **Validation**: Verifies health of connections to local or remote ChromaDB instances.

## Usage
Run the audit for a specific profile (e.g. wiki) to see what's missing:

`ash
python scripts/audit_vector.py --profile wiki --report vector_audit.txt --csv missing_vector.csv
`

## Related
- **vector-db-ingest**: Use to fill the gaps identified by this audit.
- **vector-db-cleanup**: Use to remove orphaned chunks from the index.
