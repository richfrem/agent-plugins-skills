---
description: "Search the vector database for semantically relevant code and documentation"
---

# /vector-db:query

Perform semantic (meaning-based) search across the ingested repository content.

## Usage

### Basic Search
```bash
python3 plugins/vector-db/scripts/query.py "how is bail handled for youth offenders"
```

### Check DB Health
```bash
python3 plugins/vector-db/scripts/query.py --stats
```

## Steps
1. Run the query command with your natural language question.
2. Review the returned chunks (ranked by cosine similarity).
3. Use the file paths and line numbers to navigate to the source.

## Notes
- Returns top-k results (default: 5). Use `--top-k N` to change.
- Results include the original file path, chunk content, and similarity score.
- If results are poor, run `/vector-db:ingest` to rebuild the index.
