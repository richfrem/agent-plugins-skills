---
concept: vector-profiles
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/vector-db-init/assets/vector_profiles.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.429657+00:00
cluster: knowledge
content_hash: cad6e3cfe4bf8eec
---

# Vector Profiles

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/vector-db-init/assets/vector_profiles.json -->
{
    "version": 2,
    "default_profile": "knowledge",
    "profiles": {
        "knowledge": {
            "description": "General documentation and project knowledge.",
            "manifest": ".agent/learning/vector_knowledge_manifest.json",
            "child_collection": "child_chunks_v5",
            "parent_collection": "parent_documents_v5",
            "chroma_data_path": ".vector_data",
            "chroma_host": "127.0.0.1",
            "chroma_port": 8110
        }
    }
}

<!-- Source: plugin-code/vector-db/references/examples/vector_profiles.json -->
{
    "version": 2,
    "default_profile": "knowledge",
    "profiles": {
        "knowledge": {
            "description": "General documentation and project knowledge.",
            "manifest": ".agent/learning/vector_knowledge_manifest.json",
            "child_collection": "child_chunks_v5",
            "parent_collection": "parent_documents_v5",
            "chroma_data_path": ".vector_data",
            "chroma_host": "127.0.0.1",
            "chroma_port": 8110
        }
    }
}

## See Also

- [[rlm-profiles]]
- [[vector-knowledge-manifest]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/vector-db-init/assets/vector_profiles.json`
- **Indexed:** 2026-04-27T05:21:04.429657+00:00
