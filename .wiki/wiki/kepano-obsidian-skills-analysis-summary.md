---
concept: kepano-obsidian-skills-analysis-summary
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/obsidian-vault-crud/assets/resources/kepano-analysis-summary.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.131291+00:00
cluster: plugin-code
content_hash: 1f8c20247e7a21e6
---

# Kepano Obsidian Skills: Analysis Summary

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Kepano Obsidian Skills: Analysis Summary

## Source
Repository: [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)
Analyzed during WP02 of the Obsidian Agent Integration Suite.

## Key Findings

### Architecture
Kepano's skills are **prompt-only** — they contain no executable scripts.
Each skill is a markdown file with instructions for the LLM on how to format
Obsidian-specific syntax. The LLM is trusted to follow the formatting rules.

### Skills Analyzed
| Skill | Purpose |
|:------|:--------|
| `obsidian-markdown` | Full Obsidian markdown syntax reference |
| `json-canvas` | JSON Canvas 1.0 spec for programmatic diagrams |
| `obsidian-bases` | Database views (tables, grids) from YAML |

### Contrast with This Plugin
| Aspect | Kepano (Prompt-Only) | This Plugin (Script-Based) |
|:-------|:--------------------|:--------------------------|
| **Execution** | LLM interprets instructions | Python scripts execute deterministically |
| **Safety** | LLM might hallucinate syntax | Regex/AST ensures correct output |
| **Disk I/O** | LLM writes directly | Atomic writes with locking |
| **Portability** | Tied to specific LLM | Works with any agent framework |
| **Testing** | Not testable | Unit tests verify edge cases |

### Patterns Borrowed
1. **Syntax reference tables** — Kepano's clear formatting guides informed our parser regex
2. **Callout type enumeration** — Comprehensive list of callout types adopted
3. **Canvas node/edge schema** — JSON Canvas 1.0 spec structure adopted for WP07

### Patterns Rejected
1. **Prompt-only execution** — Too fragile for production use
2. **No disk safety** — Kepano trusts the LLM to write files safely; we don't
3. **No separation of concerns** — Kepano mixes syntax and I/O; we separate them


## See Also

- [[strategic-analysis-agent-skills-ecosystem-in-azure]]
- [[skills-vision-analysis]]
- [[skills-vision-analysis]]
- [[strategic-analysis-agent-skills-ecosystem-in-azure]]
- [[strategic-analysis-agent-skills-ecosystem-in-azure]]
- [[agent-harness-summary]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/obsidian-vault-crud/assets/resources/kepano-analysis-summary.md`
- **Indexed:** 2026-04-17T06:42:10.131291+00:00
