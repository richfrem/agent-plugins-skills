---
name: vector-db-audit
description: Audit Vector DB coverage -- compares the live filesystem manifest against the ChromaDB index to identify coverage gaps.
allowed-tools: Bash, Read, Write
---

# Vector DB Audit

Systematically audits the Vector Database to identify gaps between the project manifest and the actual document chunks stored in ChromaDB.

## Capabilities
- **Coverage Analysis**: Calculates the exact percentage of project documentation currently vectorized.
- **Gap Identification**: Detects files that are included in the manifest but missing from the ChromaDB collection.
- **Exporting**: Generates CSV lists of missing files for targeted batch ingestion.
- **Dynamic Configuration**: Loads connection and collection settings directly from the selected profile.

## Usage

Run the audit for a specific profile (e.g., `wiki`) to generate a coverage report and a CSV of gaps:

```bash
python scripts/audit_vector.py --profile wiki --report vector_audit.txt --csv missing_vector.csv
```

## Protocol
1. **Identify**: Run this skill to find missing content.
2. **Review**: Check `missing_vector.csv`.
3. **Ingest**: Use `vector-db-ingest --profile wiki --file [path]` to fill specific gaps.

## Related
- **vector-db-ingest**: Use to fill the gaps identified by this audit.
- **vector-db-cleanup**: Use to remove orphaned chunks from the index.
