---
concept: vector-db-audit
source: plugin-code
source_file: vector-db/skills/vector-db-audit/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.426486+00:00
cluster: plugin-code
content_hash: c95b5288032a93a9
---

# Vector DB Audit

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[vector-db-initialization]]
- [[acceptance-criteria-vector-db-init]]
- [[acceptance-criteria-vector-db-init]]
- [[vector-db-launch-python-native-server]]
- [[acceptance-criteria-vector-db-launch]]
- [[vector-db-search]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/skills/vector-db-audit/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.426486+00:00
