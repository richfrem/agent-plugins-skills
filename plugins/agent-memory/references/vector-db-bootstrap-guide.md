# Vector DB Bootstrap Guide

Step-by-step setup, configuration, and manifest initialization guide for the ChromaDB Vector Database.

## Contents
- [Prerequisites: Dependency Installation](#prerequisites-dependency-installation)
- [Step 0: Setup Mode Selection](#step-0-setup-mode-selection)
- [Step 1: Guided Source Discovery](#step-1-guided-source-discovery)
- [Step 2: Confirm and Write Manifest](#step-2-confirm-and-write-manifest)
- [Step 3: Scaffold Profile](#step-3-scaffold-profile)
- [Step 4: Verification and Next Steps](#step-4-verification-and-next-steps)

---

## Prerequisites: Dependency Installation

Install dependencies from the plugin lockfile using `python -m pip`:
```bash
python -m pip install -r plugins/agent-memory/requirements.txt
```

Verify critical packages:
```bash
python -c "import chromadb; print('chromadb: OK')"
python -c "import einops; print('einops: OK')"
python -c "from sentence_transformers import SentenceTransformer; print('sentence-transformers: OK')"
```

---

## Step 0: Setup Mode Selection

Check installed plugins:
```bash
ls .agents/skills/rlm-init/ 2>/dev/null && echo "rlm-factory: INSTALLED" || echo "rlm-factory: NOT FOUND"
ls .agents/skills/obsidian-wiki-builder/ 2>/dev/null && echo "obsidian-wiki-engine: INSTALLED" || echo "obsidian-wiki-engine: NOT FOUND"
```

Select a mode:
- **Mode A (Standalone):** Vector DB semantic search over indexed folders.
- **Mode B (Vector DB + RLM):** RLM keyword pre-filter before vector search.
- **Mode C (Vector DB + Wiki):** Semantic search integration with wiki concept graph.
- **Mode D (Super-RAG):** All three layers: RLM keyword -> Vector semantic -> Wiki graph.

---

## Step 1: Guided Source Discovery

Scan the project root for candidate directories:
```bash
find . -maxdepth 1 -type d | grep -v '^\.$' | grep -v -E '\.(git|venv|vscode|windsurf|claude|agents|agent|knowledge_vector_data|wiki|vector_data)$' | sort
```

Present candidate directories to the user to choose indexing targets (e.g. `plugins/`, `docs/`).

---

## Step 2: Confirm and Write Manifest

Format the manifest schema and display before writing:
```json
{
  "description": "Globs tracking project documentation and knowledge records.",
  "include": [
    "docs/",
    "plugins/"
  ],
  "exclude": [
    "/.git/",
    "/node_modules/",
    "/.venv/",
    "/__pycache__/",
    "requirements.in",
    "requirements.txt"
  ]
}
```

Write to `.agent/learning/vector_knowledge_manifest.json`.

---

## Step 3: Scaffold Profile

Run the initialization script to scaffold `.agent/learning/vector_profiles.json`:
```bash
python ./scripts/init.py
```

Ensure default profile configuration points to the canonical manifest:
```json
{
  "version": 2,
  "profiles": {
    "wiki": {
      "manifest": ".agent/learning/vector_knowledge_manifest.json"
    }
  },
  "default_profile": "wiki"
}
```

---

## Step 4: Verification and Next Steps

Confirm files generated:
1. `.agent/learning/vector_knowledge_manifest.json`
2. `.agent/learning/vector_profiles.json`

Next actions:
- Ingest content: `vector-db-ingest` (`python ./scripts/ingest.py --profile wiki --full`)
- Search content: `vector-db-search` (`python ./scripts/query.py "query" --profile wiki`)
- Audit coverage: `vector-db-audit`
