---
concept: manifest-index
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/tool-inventory/assets/resources/manifest-index.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.372764+00:00
cluster: json
content_hash: 0cb44b4b4996f121
---

# Manifest Index

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/tool-inventory/assets/resources/manifest-index.json -->
{
    "tool": {
        "description": "Tool Discovery (CLI Scripts & Capabilities)",
        "manifest": "plugins/tool_inventory.json",
        "cache": ".agent/learning/rlm_tool_cache.json",
        "parser": "inventory_dict",
        "prompt_path": "prompts/rlm/rlm_summarize_tool.md",
        "env_prefix": "RLM_TOOL",
        "allowed_suffixes": [
            ".py",
            ".js",
            ".sh",
            ".ts"
        ],
        "llm_model": "granite3.2:8b"
    }
}

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/tool-inventory-init/assets/resources/manifest-index.json -->
{
    "tool": {
        "description": "Tool Discovery (CLI Scripts & Capabilities)",
        "manifest": "plugins/tool_inventory.json",
        "cache": ".agent/learning/rlm_tool_cache.json",
        "parser": "inventory_dict",
        "prompt_path": "prompts/rlm/rlm_summarize_tool.md",
        "env_prefix": "RLM_TOOL",
        "allowed_suffixes": [
            ".py",
            ".js",
            ".sh",
            ".ts"
        ],
        "llm_model": "granite3.2:8b"
    }
}

<!-- Source: plugin-code/rlm-factory/assets/resources/manifest-index.json -->
{
    "project": {
        "description": "General Project Knowledge Base (Docs, Readmes)",
        "manifest": "rlm_manifest.json",
        "cache": ".agent/learning/rlm_summary_cache.json",
        "parser": "directory_glob",
        "prompt_path": "",
        "env_prefix": "RLM_SUMMARY",
        "allowed_suffixes": [
            ".md",
            ".txt"
        ],
        "llm_model": "granite3.2:8b"
    }
}

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/ollama-launch/resources/manifest-index.json -->
{
    "project": {
        "description": "General Project Knowledge Base (Docs, Readmes)",
        "manifest": "rlm_manifest.json",
        "cache": ".agent/learning/rlm_summary_cache.json",
        "parser": "directory_glob",
        "prompt_path": "",
        "env_prefix": "RLM_SUMMARY",
        "allowed_suffixes": [
            ".md",
            ".txt"
        ],
        "llm_model": "granite3.2:8b"
    }
}

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/rlm-cleanup-agent/resources/manifest-index.json -->
{
    "project": {
        "description": "General Project Knowledge Base (Docs, Readmes)",
        "manifest": "rlm_manifest.json",
        "cache": ".agent/learning/rlm_summary_cache.json",
        "parser": "directory_glob",
        "prompt_path": "",
        "env_prefix": "RLM_SUMMARY",
        "allowed_suffixes": [
            ".md",
            ".txt"
        ],
        "llm_model": "granite3.2:8b"
    }
}

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/rlm-curator/resources/manifest-index.json -->
{
    "project": {
        "description": "General Project Knowledge Base (Docs, Readmes)",
        "manifest": "rlm_manifest.json",
        "cache": ".agent/learning/rlm_summary_cache.json",
        "parser": "directory_glob",
        "prompt_path": "",
        "env_prefix": "RLM_SUMMARY",
        "allowed_suffixes": [
            ".md",
            ".txt"
        ],
        "llm_model": "granite3.2:8b"
    }
}

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/rlm-distill-agent/resources/manifest-index.json -->
{
    "project": {
        "description": "General Project Knowledge Base (Docs, Readmes)",
        "manifest": "rlm_manifest.json",
        "cache": ".agent/learning/rlm_summary_cache.json",
        "parser": "directory_glob",
        "prompt_path": "",
        "env_prefix": "RLM_SUMMARY",
        "allowed_suffixes": [
            ".md",
            ".txt"
        ],
        "llm_model": "granite3.2:8b"
    }
}

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/rlm-distill-ollama/resources/manifest-index.json -->
{
    "project": {
        "description": "General Project Knowledge Base (Docs, Readmes)",
        "manifest": "rlm_manifest.json",
        "cache": ".agent/learning/rlm_summary_cache.json",
        "parser": "directory_glob",
        "prompt_path": "",
        "env_prefix": "RLM_SUMMARY",
        "allowed_suffixes": [
            ".md",
            ".txt"
        ],
        "llm_model": "granite3.2:8b"
    }
}

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/rlm-init/resources/manifest-index.json -->
{
    "project": {
        "description": "General Project Knowledge Base (Docs, Readmes)",
        "manifest": "rlm_manifest.json",
        "cache": ".agent/learning/rlm_summary_cache.json",
        "parser": "directory_glob",
        "prompt_path": "",
        "env_prefix": "RLM_SUMMARY",
        "allowed_suffixes": [
            ".md",
            ".txt"
        ],
        "llm_model": "granite3.2:8b"
    }
}

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/rlm-search/resources/manifest-index.json -->
{
    "project": {
        "description": "General Proj

*(combined content truncated)*

## See Also

- [[default-file-extensions-to-index-if-manifest-is-empty]]
- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[build-capability-index]]
- [[distiller-manifest]]
- [[file-manifest]]
- [[file-manifest-schema]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/tool-inventory/assets/resources/manifest-index.json`
- **Indexed:** 2026-04-27T05:21:04.372764+00:00
