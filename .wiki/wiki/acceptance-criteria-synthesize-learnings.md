---
concept: acceptance-criteria-synthesize-learnings
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/synthesize-learnings/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.257757+00:00
cluster: must
content_hash: f8a3c287159dbf26
---

# Acceptance Criteria: synthesize-learnings

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: synthesize-learnings

To ensure `synthesize-learnings` correctly closes the virtuous cycle loop, it must pass the following criteria when evaluated against a raw plugin analysis report.

## 1. Actionable Recommendations
Every recommendation generated must specify a direct, concrete change to be made to one of the four targets (`agent-scaffolders`, `agent-skill-open-specifications`, `agent-plugin-analyzer`, or `oracle-legacy-system-analysis`). Recommendations must be testable (e.g., "Add the ~category connector abstraction to the create-skill template").

## 2. Proper Categorization
Extracted patterns must be correctly mapped using the defined categories (Structural, Content, Execution, Integration, Quality, Meta, Domain).

## 3. Catalog Expansion
When a completely novel pattern is detected in the input analysis, this skill must explicitly formulate a new markdown section ready to be appended to the `pattern-catalog.md` reference file.

## 4. Priority Tiers
Recommendations must be sorted by priority (High, Medium, Low) based on their blast radius (how many future skills they will improve if adopted).


## See Also

- [[acceptance-criteria-adr-manager]]
- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-clean-locks]]
- [[acceptance-criteria-os-guide]]
- [[acceptance-criteria-os-init]]
- [[acceptance-criteria-os-memory-manager]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/synthesize-learnings/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.257757+00:00
