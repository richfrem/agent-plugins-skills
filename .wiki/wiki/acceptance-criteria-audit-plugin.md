---
concept: acceptance-criteria-audit-plugin
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/audit-plugin/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.719965+00:00
cluster: auditor
content_hash: 999b103124be82b9
---

# Acceptance Criteria: audit-plugin

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: audit-plugin

**Purpose**: Verify the system auditor accurately detects specification failures.

## 1. File Detection
- **[PASSED]**: Auditor throws an error if `../../../.claude-plugin/plugin.json` or `.claude-plugin/` directory is missing.
- **[FAILED]**: Auditor silently passes a plugin that stores its `hooks.json` in the root directory instead of `hooks/hooks.json`.

## 2. Script Restriction  
- **[PASSED]**: Auditor strictly rejects any `.sh` or `.ps1` files residing in `skills/*/scripts/`.
- **[FAILED]**: Auditor allows a bash script to exist inside a skill's dedicated execution directory.


## See Also

- [[acceptance-criteria-audit-plugin-l5nndefine-at-least-two-testable-criteria-or-correctincorrect-operational-patterns-here-to-ensure-the-skill-functions-correctly]]
- [[acceptance-criteria-audit-plugin-l5nndefine-at-least-two-testable-criteria-or-correctincorrect-operational-patterns-here-to-ensure-the-skill-functions-correctly]]
- [[acceptance-criteria-audit-plugin-l5nndefine-at-least-two-testable-criteria-or-correctincorrect-operational-patterns-here-to-ensure-the-skill-functions-correctly]]
- [[acceptance-criteria-analyze-plugin]]
- [[acceptance-criteria-create-plugin]]
- [[acceptance-criteria-plugin-maintenance]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/audit-plugin/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:09.719965+00:00
