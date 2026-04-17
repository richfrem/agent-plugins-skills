---
concept: acceptance-criteria-create-sub-agent
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.996727+00:00
cluster: frontmatter
content_hash: 96a002b83760b4c0
---

# Acceptance Criteria: create-sub-agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: create-sub-agent

**Purpose**: Verify the system generates valid multi-agent routing configurations.

## 1. Frontmatter Configuration
- **[PASSED]**: Frontmatter correctly includes `model: inherit` and custom `color` parameters.
- **[FAILED]**: Frontmatter lacks basic Anthropic syntax routing.

## 2. Few-Shot Triggering
- **[PASSED]**: The description body includes 2-4 explicit XML `<example>` structures to train the router when to call this sub-agent natively (including negative or proactive instructions).
- **[FAILED]**: The sub-agent has a descriptive block but lacks concrete semantic trigger phrases.


## See Also

- [[acceptance-criteria-agent-swarm]]
- [[agent-orchestrator-acceptance-criteria]]
- [[acceptance-criteria-create-command]]
- [[acceptance-criteria-create-hook]]
- [[acceptance-criteria-create-mcp-integration]]
- [[acceptance-criteria-create-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:09.996727+00:00
