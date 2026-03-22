# Acceptance Criteria: synthesize-learnings

To ensure `synthesize-learnings` correctly closes the virtuous cycle loop, it must pass the following criteria when evaluated against a raw plugin analysis report.

## 1. Actionable Recommendations
Every recommendation generated must specify a direct, concrete change to be made to one of the four targets (`agent-scaffolders`, `agent-skill-open-specifications`, `agent-plugin-analyzer`, or `legacy system`). Recommendations must be testable (e.g., "Add the ~category connector abstraction to the create-skill template").

## 2. Proper Categorization
Extracted patterns must be correctly mapped using the defined categories (Structural, Content, Execution, Integration, Quality, Meta, Domain).

## 3. Catalog Expansion
When a completely novel pattern is detected in the input analysis, this skill must explicitly formulate a new markdown section ready to be appended to the `pattern-catalog.md` reference file.

## 4. Priority Tiers
Recommendations must be sorted by priority (High, Medium, Low) based on their blast radius (how many future skills they will improve if adopted).
