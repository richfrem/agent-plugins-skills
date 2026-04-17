---
concept: acceptance-criteria-red-team-review
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/red-team-review/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.194469+00:00
cluster: agent
content_hash: f04df69ad010060a
---

# Acceptance Criteria: Red Team Review

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Red Team Review

## 1. Bundle Discipline
- [ ] Agent relies entirely on `context-bundler` and `manifest.json` to compile review packets, rather than manually `cat`ing files into prompts.
- [ ] Packets always include an explicit "Prompt" guiding the reviewer's focus.

## 2. Iteration Mandate
- [ ] Agent automatically parses the reviewer's verdict and correctly triggers the next loop iteration (Research vs Approval) based on that verdict.
- [ ] Agent refuses to manually override a negative or pending verdict to force an approval.

## 3. Delegation Limits
- [ ] As a specialized loop, it only manages the review cycle. It does not execute the actual implementation or dictate global repo state updates post-approval.


## See Also

- [[acceptance-criteria-red-team-bundler]]
- [[acceptance-criteria-red-team-bundler]]
- [[red-team-review-loop]]
- [[procedural-fallback-tree-red-team-review]]
- [[red-team-review-agent-plugin-analyzer-meta-plugin]]
- [[round-2-red-team-review-refactored-agent-plugin-analyzer]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/red-team-review/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.194469+00:00
