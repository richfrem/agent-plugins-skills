---
concept: procedural-fallback-tree-synthesize-learnings
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/synthesize-learnings/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.258014+00:00
cluster: analysis
content_hash: a1094b69e72bb35a
---

# Procedural Fallback Tree: Synthesize Learnings

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Synthesize Learnings

## 1. Raw Analysis Context is Too Large
If the user dumps 5 massive analysis reports from `analyze-plugin` into the chat and it causes context limits or truncation:
- **Action**: Do not attempt to synthesize them all blindly. Break them down. Instruct the user to pass them one at a time, or write a summary script to compress the structural findings before feeding them into the synthesis engine.

## 2. Incompatible Analysis Format
If the user provides an unstructured text dump or an old version of an analysis report that lacks the explicit 6-phase output:
- **Action**: Gracefully map what you can to the 9 categories. Explicitly state the gaps in the synthesis report (e.g., "Note: Analysis lacked Phase 5 Security Checks, so no scaffold recommendations generated for security").

## 3. Pattern Catalog Write Conflict (Read-Only FS)
If attempting to append newly discovered patterns to `references/pattern-catalog.md` fails due to filesystem permissions:
- **Action**: Output the formatted new pattern entries directly in the executive summary of the syntax report with a message instructing the user to manually append them to the catalog file.

## 4. Unmapped Sub-Domain
If an observation clearly implies a meta-skill improvement but doesn't map cleanly to `scaffolders`, `specs`, or `analyzer`:
- **Action**: Map it to `Specs` as a generalized "New Ecosystem Standard" recommendation and flag it for human review. Do not silently discard raw learnings.


## See Also

- [[procedural-fallback-tree-adr-management]]
- [[procedural-fallback-tree-agent-swarm]]
- [[procedural-fallback-tree-dual-loop]]
- [[procedural-fallback-tree-learning-loop]]
- [[procedural-fallback-tree-orchestrator-routing]]
- [[procedural-fallback-tree-red-team-review]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/synthesize-learnings/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.258014+00:00
