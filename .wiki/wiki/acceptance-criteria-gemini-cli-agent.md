---
concept: acceptance-criteria-gemini-cli-agent
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/gemini-cli-agent/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.093685+00:00
cluster: output
content_hash: 9e31c63272b5a224
---

# Acceptance Criteria: Gemini CLI Agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Gemini CLI Agent

## 1. Piping Discipline
- [ ] Large inputs are piped via shell redirection, never loaded into agent memory.
- [ ] Output always redirected to a file; view_file used for review.

## 2. Model Selection
- [ ] The -m flag is used appropriately (flash for speed, pro for depth).
- [ ] A different model is never silently substituted without user confirmation.

## 3. Context Isolation
- [ ] Every dispatch prompt includes "Do NOT use tools. Do NOT search filesystem."
- [ ] Prompt is 100% self-contained - no reliance on CLI sub-agent having agent memory.

## 4. Output Schema
- [ ] Security/QA/architecture dispatches explicitly request Severity-Stratified output (CRITICAL/MODERATE/MINOR).
- [ ] Output file is parseable by the Outer Loop agent without post-processing.


## See Also

- [[acceptance-criteria-claude-cli-agent]]
- [[acceptance-criteria-copilot-cli-agent]]
- [[acceptance-criteria-claude-cli-agent]]
- [[acceptance-criteria-claude-cli-agent]]
- [[acceptance-criteria-copilot-cli-agent]]
- [[acceptance-criteria-copilot-cli-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/gemini-cli-agent/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.093685+00:00
