---
concept: acceptance-criteria-create-skill
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-skill/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.947552+00:00
cluster: generates
content_hash: 14d6a7ea8c9198b3
---

# Acceptance Criteria: create-skill

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: create-skill

**Purpose**: Verify the system generates Microsoft-compliant Skill architectures.

## 1. Directory Structure
- **[PASSED]**: Skill generates `scripts/`, `references/`, and `assets/` folders. It places an `acceptance-criteria.md` inside `references/`.
- **[FAILED]**: Skill fails to create subdirectories, leaving a massive root `./SKILL.md` vulnerable to bloating.

## 2. Shell Enforcement
- **[PASSED]**: Skill uses `.py` Python scripts inside the `scripts/` folder.
- **[FAILED]**: Skill generates legacy bash `.sh` execution scripts.


## See Also

- [[acceptance-criteria-audit-plugin-l5nndefine-at-least-two-testable-criteria-or-correctincorrect-operational-patterns-here-to-ensure-the-skill-functions-correctly]]
- [[acceptance-criteria-create-command]]
- [[acceptance-criteria-create-hook]]
- [[acceptance-criteria-create-mcp-integration]]
- [[acceptance-criteria-create-plugin]]
- [[acceptance-criteria-create-sub-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-skill/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:09.947552+00:00
