---
concept: acceptance-criteria---manage-marketplace
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/manage-marketplace/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.113502+00:00
cluster: pass
content_hash: 37bff8bb00d594a5
---

# Acceptance Criteria - manage-marketplace

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria - manage-marketplace

To verify the skill correctly guides the user in setting up and managing a marketplace.

| Scenario | Expected Result | Pass/Fail |
|----------|-----------------|-----------|
| **Setup location** | The guide directs the user to place `marketplace.json` inside a `.claude-plugin/` directory at root. | **PASS** |
| **Owner field** | The `owner` field is created and defined as an object: `{"name": "Owner Name"}`. | **PASS** |
| **Name Field** | The `name` field strictly uses **kebab-case** validation. | **PASS** |
| **CLI Directives** | The guide references addition using `/plugin marketplace add` TUI behavior directives. | **PASS** |
| **Variables mapping** | The guide lists `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` absolute references mapped safely for author hooks. | **PASS** |

## Failure Patterns (FAIL)

| Scenario | Incorrect Result |
|----------|-----------------|
| **Wrong file location** | Agent places `marketplace.json` at the repo root without a `.claude-plugin/` parent directory. |
| **String `owner` field** | Generated catalog uses `"owner": "Acme Corp"` instead of `"owner": {"name": "Acme Corp"}`. |
| **Non-kebab-case name** | Generated catalog uses names with spaces or mixed case (e.g., `"My Plugin"` or `"MyPlugin"`). |
| **Wrong CLI command** | Skill tells consumers to run `claude plugins add-marketplace` or any other non-canonical command. |
| **Hardcoded paths in hooks** | Plugin author guidance uses absolute host paths (e.g., `/home/user/.claude/plugins/my-plugin/run.sh`) instead of `${CLAUDE_PLUGIN_ROOT}`. |

## See Also

- [[architecture-reference---manage-marketplace]]
- [[acceptance-criteria-adr-manager]]
- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-guide]]
- [[acceptance-criteria-os-init]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/manage-marketplace/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.113502+00:00
