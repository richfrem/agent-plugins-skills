---
concept: plugin
source: plugin-code
source_file: obsidian-wiki-engine/.claude-plugin/plugin.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.437977+00:00
cluster: agent
content_hash: c49dbd06b78b2fa7
---

# Plugin

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/obsidian-wiki-engine/.claude-plugin/plugin.json -->
{
    "name": "obsidian-wiki-engine",
    "version": "3.1.0",
    "description": "Obsidian Wiki Engine - Karpathy-style LLM wiki + RLM distillation + vector search. Dual-representation knowledge graph: vault operations, cross-source concept synthesis, wiki node generation, RLM distillation, semantic health linting, graph traversal, canvas, bases, and progressive-disclosure query with vector DB Phase 2.",
    "author": {
        "name": "Richard Fremmerlid"
    },
    "repository": "https://github.com/richfrem/agent-plugins-skills",
    "license": "MIT",
    "keywords": [
        "obsidian",
        "vault",
        "knowledge-graph",
        "markdown",
        "canvas",
        "wikilinks",
        "pkm",
        "wiki",
        "rlm",
        "llm",
        "karpathy",
        "distillation",
        "vector-search",
        "semantic-linting",
        "concept-synthesis"
    ],
    "capabilities": [
        "obsidian-wiki-engine",
        "knowledge-management",
        "rlm-distillation",
        "wiki-generation",
        "progressive-query",
        "cross-source-synthesis",
        "semantic-linting",
        "vector-phase2-search"
    ],
    "config": {
        "manifest_path": ".agent/learning/rlm_wiki_raw_sources_manifest.json",
        "rlm_profiles_path": ".agent/learning/rlm_profiles.json",
        "vector_profiles_path": ".agent/learning/vector_profiles.json",
        "vector_knowledge_manifest": ".agent/learning/vector_knowledge_manifest.json"
    },
    "dependencies": {
        "plugins": ["rlm-factory"],
        "plugins_optional": ["vector-db"]
    }
}


<!-- Source: plugin-code/agent-agentic-os/.claude-plugin/plugin.json -->
{
    "name": "agent-agentic-os",
    "version": "1.6.0",
    "description": "An opinionated learning layer and harnessing discipline above what Claude Code ships natively. Provides a structured memory hierarchy, a continuous improvement loop for model instructions, multi-agent event bus coordination, and an eval-gated skill improvement system. Designed for developers running long-horizon workflows who need a cohesive feedback control system rather than isolated orchestration primitives.",
    "author": {
        "name": "Richard Fremmerlid"
    },
    "repository": "https://github.com/richfrem/agent-plugins-skills",
    "license": "MIT",
    "keywords": [
        "agentic-os",
        "agent-harness",
        "eval-runner",
        "continuous-improvement",
        "context-management",
        "memory-management",
        "session-management",
        "autoresearch"
    ],
    "capabilities": [
        "eval-gate",
        "memory",
        "orchestration",
        "continuous-improvement",
        "self-healing",
        "multi-agent-coordination",
        "hooks"
    ],
    "skills": [
        "optimize-agent-instructions",
        "os-clean-locks",
        "os-eval-backport",
        "os-eval-lab-setup",
        "os-eval-runner",
        "os-guide",
        "os-improvement-loop",
        "os-improvement-report",
        "os-init",
        "os-memory-manager",
        "todo-check"
    ],
    "agents": [
        "agentic-os-setup",
        "os-health-check"
    ],
    "commands": [
        "os-init",
        "os-loop",
        "os-memory"
    ],
    "hooks": true
}


<!-- Source: plugin-code/vector-db/.claude-plugin/plugin.json -->
{
    "name": "vector-db",
    "description": "Local Semantic Search Engine powered by ChromaDB with Super-RAG context injection via RLM summaries. Ingest, query, and maintain a persistent vector store.",
    "version": "2.0.0",
    "author": {
        "name": "Richard Fremmerlid"
    },
    "repository": "https://github.com/richfrem/agent-plugins-skills",
    "license": "MIT",
    "security": {
        "whitelists": {
            "python": {
                "imports": [
                    "subprocess"
                ]
            }
        }
    },
    "keywords": [
        "vector-db",
        "chromadb",
        "semantic-search",
        "rag",
        "embeddings",
        "ingest"
    ],
    "runtime": {
        "python_deps": [
            "chromadb",
            "sentence-transformers",
            "python-dotenv"
        ],
        "models": [
            "all-MiniLM-L6-v2 (HuggingFace, auto-downloaded)"
        ]
    },
    "prerequisites": {
        "rlm-factory": "Optional but recommended \u2014 provides Super-RAG context injection"
    },
    "capabilities": [
        "vector-search",
        "embeddings",
        "semantic-retrieval"
    ]
}


<!-- Source: plugin-code/rlm-factory/.claude-plugin/plugin.json -->
{
    "name": "rlm-factory",
    "description": "Recursive Language Model factory \u2014 distill repository files into semantic summaries using agents for instant context retrieval",
    "version": "2.0.0",
    "author": {
        "name": "Richard Fremmerlid"
    },
    "repository": "https://github.com/richfrem/agent-plugins-skills",
    

*(combined content truncated)*

## See Also

- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[adr-003-plugin-skill-resource-sharing-via-mirrored-folder-structure-and-file-level-symlinks]]
- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]
- [[exploration-cycle-plugin-hooks]]
- [[install-plugin-in-a-different-repo-eg-context-bundler-specifically]]
- [[obsidian-wiki-engine-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/.claude-plugin/plugin.json`
- **Indexed:** 2026-04-27T05:21:04.437977+00:00
