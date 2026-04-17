---
concept: procedural-fallback-tree-ecosystem-standards-protocol
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/ecosystem-standards/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.061869+00:00
cluster: action
content_hash: 4ca113ca3964042d
---

# Procedural Fallback Tree: Ecosystem Standards Protocol

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Ecosystem Standards Protocol

## 1. Ambiguous Component Boundary
If the target directory appears to contain a mixture of Agent Skills, Workflows, and arbitrary scripts without clear separation:
- **Action**: Do not attempt a unified audit. Isolate the target. Ask the user explicitly: "Are we auditing this as a Plugin, an individual Skill, or a naked Workflow?" Apply only the specific checklist for that isolation primitive.

## 2. Legacy Pattern Matches
If an old plugin perfectly follows V1 standards but fails V2 L5 constraints:
- **Action**: Do not auto-reject the plugin as "broken" unless it violates P0 security rules. Mark it as "V1 Legacy Compliant", list the specific upgrade deltas needed for V2 L5, and assign a lower overall maturity score.

## 3. Tool Interaction Blindspots
If auditing a skill that requires complex Multi-CLI interactions or nested sub-agent environments that you cannot dry-run:
- **Action**: Audit the static structural requirements (frontmatter, structure, diagrams). Explicitly flag the interactive elements as "Untested/Requires Red Team Sandbox" to maintain Source Transparency.

## 4. Unresolvable Standard Conflict
If a plugin violates an ecosystem standard to solve a novel edge-case (e.g., massive inline prompt chunking for specific token-dense tasks):
- **Action**: Flag the violation but label it an "Intentional Deviation". Advise the user to use the `synthesize-learnings` skill to propose an update to the ecosystem specs if this novel edge-case proves valuable.


## See Also

- [[procedural-fallback-tree-ecosystem-authoritative-sources]]
- [[procedural-fallback-tree-ecosystem-authoritative-sources]]
- [[procedural-fallback-tree-adr-management]]
- [[procedural-fallback-tree-agent-swarm]]
- [[procedural-fallback-tree-dual-loop]]
- [[procedural-fallback-tree-learning-loop]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/ecosystem-standards/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.061869+00:00
