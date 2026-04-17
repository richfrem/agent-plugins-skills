---
concept: procedural-fallback-tree-ecosystem-authoritative-sources
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/ecosystem-authoritative-sources/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.033725+00:00
cluster: action
content_hash: f9554b9b5d054310
---

# Procedural Fallback Tree: Ecosystem Authoritative Sources

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Ecosystem Authoritative Sources

## 1. Missing Reference Target
If the table of contents links to a `reference/` file that does not physically exist in the filesystem:
- **Action**: Do not attempt to guess the specification contents. Explicitly state to the user: "The authoritative source file for [Topic] is missing." Fall back to the main repository `README.md` to see if the knowledge was moved globally.

## 2. Conflicting Specifications
If asked a question where the specs in this plugin contradict the global `constitution.md` (e.g., execution rules):
- **Action**: The global `constitution.md` ALWAYS wins. Surface the contradiction to the user and explicitly prioritize the constitutional mandate over the plugin's local reference docs.

## 3. Spec Interpretation Deadlock
If the user repeatedly argues that a generated artifact aligns with the specs, but the agent believes it fails:
- **Action**: Defer to the `ecosystem-standards` skill. Do not debate the user. Run a formal audit against the specific component to get an objective pass/fail checklist.

## 4. Unsupported Ecosystem Query
If asked about a framework pattern (e.g., "CrewAI") not covered by the authoritative sources:
- **Action**: Explicitly state that the framework is not part of the local Open Standard ecosystem. Do not try to map proprietary Claude Plugin constraints onto unsupported engines.


## See Also

- [[procedural-fallback-tree-ecosystem-standards-protocol]]
- [[procedural-fallback-tree-ecosystem-standards-protocol]]
- [[procedural-fallback-tree-ecosystem-standards-protocol]]
- [[procedural-fallback-tree-adr-management]]
- [[procedural-fallback-tree-agent-swarm]]
- [[procedural-fallback-tree-dual-loop]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/ecosystem-authoritative-sources/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.033725+00:00
