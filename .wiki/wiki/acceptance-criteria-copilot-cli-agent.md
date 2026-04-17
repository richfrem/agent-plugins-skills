---
concept: acceptance-criteria-copilot-cli-agent
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/copilot-cli-agent/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.754132+00:00
cluster: smoke
content_hash: 2b203339871449d8
---

# Acceptance Criteria: Copilot CLI Agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Copilot CLI Agent

## 1. Smoke Test Gate
- [ ] Smoke test ('copilot -p "Reply with exactly: COPILOT_CLI_OK"') passes before any analysis dispatch.
- [ ] Analysis is NEVER dispatched without a successful smoke test.

## 2. Permission Safety
- [ ] Headless sub-agents never receive --allow-all-tools or --allow-all-paths without explicit user confirmation.
- [ ] Reason for any elevated permission flag is documented in the command.

## 3. Context Isolation
- [ ] Every dispatch prompt includes "Do NOT use tools. Do NOT search filesystem."
- [ ] Prompt is 100% self-contained - no reliance on CLI sub-agent having agent memory.

## 4. Output Schema
- [ ] Security/QA/architecture dispatches explicitly request Severity-Stratified output (CRITICAL/MODERATE/MINOR).
- [ ] Output file is parseable by the Outer Loop agent without post-processing.


## See Also

- [[acceptance-criteria-claude-cli-agent]]
- [[acceptance-criteria-gemini-cli-agent]]
- [[acceptance-criteria-claude-cli-agent]]
- [[acceptance-criteria-claude-cli-agent]]
- [[acceptance-criteria-gemini-cli-agent]]
- [[acceptance-criteria-gemini-cli-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/copilot-cli-agent/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:09.754132+00:00
