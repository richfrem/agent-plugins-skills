---
concept: procedural-fallback-tree-red-team-review
source: plugin-code
source_file: agent-loops/skills/red-team-review/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.730059+00:00
cluster: agent
content_hash: 61147ebbcbded49e
---

# Procedural Fallback Tree: Red Team Review

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Red Team Review

## 1. Manifest Context is Too Large
If `context-bundler` generates a file too massive for the Red Team agent's context window:
- **Action**: Refine the `manifest.json`. Exclude massive unstructured logs or irrelevant boilerplate. Re-run the bundler. Adhere to the principle of "minimum viable context" for the reviewer.

## 2. Reviewer Persona is Missing
If instructed to use a specific persona but the file cannot be found, ask the user to
supply a system prompt directly or install an agent persona plugin.
The `qa-expert` and `security-auditor` persona stubs have been removed — supply your own
system prompt for specialized review agents.

## 3. Continuous Review Deadlock
If the Red Team agent rejects the research 3 or more times consecutively for the same core issue that cannot be resolved:
- **Action**: Break the loop. Bring the deadlocked specific disagreement to the Orchestrator/User for a tie-breaking executive decision. 

## 4. Unactionable Feedback
If the feedback returned from the reviewer is vague (e.g., "This isn't good enough"):
- **Action**: Do not loop back to research yet. Prompt the reviewer agent/human to quantify the failure using the Severity-Stratified schema (Critical/Moderate/Minor) with specific file/line references.


## See Also

- [[red-team-review-loop]]
- [[fallback-to-appending-directly-if-kernel-is-missing]]
- [[t029-lossless-yaml-ruamelyaml-preferred-fallback-warning]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-loops/skills/red-team-review/fallback-tree.md`
- **Indexed:** 2026-04-27T05:21:03.730059+00:00
