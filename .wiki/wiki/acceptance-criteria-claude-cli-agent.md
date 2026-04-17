---
concept: acceptance-criteria-claude-cli-agent
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/claude-cli-agent/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.743572+00:00
cluster: output
content_hash: da133a41f9b2f706
---

# Acceptance Criteria: Claude CLI Agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Claude CLI Agent

## 1. Piping Discipline
- [ ] Large inputs are piped via shell redirection, never loaded into agent memory.
- [ ] Output always redirected to a file; view_file used for review.

## 2. Context Isolation
- [ ] Every dispatch prompt includes "Do NOT use tools. Do NOT search filesystem."
- [ ] Prompt is 100% self-contained - no reliance on CLI sub-agent having agent memory.

## 3. Output Schema
- [ ] Security/QA/architecture dispatches explicitly request Severity-Stratified output (CRITICAL/MODERATE/MINOR).
- [ ] Output file is parseable by the Outer Loop agent without post-processing.

## 4. Safety
- [ ] `--dangerously-skip-permissions` is only used when required and documented.
- [ ] Oversized files are chunked via a Python script, not forced through a single pipe.


## See Also

- [[acceptance-criteria-copilot-cli-agent]]
- [[acceptance-criteria-gemini-cli-agent]]
- [[acceptance-criteria-copilot-cli-agent]]
- [[acceptance-criteria-copilot-cli-agent]]
- [[acceptance-criteria-gemini-cli-agent]]
- [[acceptance-criteria-gemini-cli-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/claude-cli-agent/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:09.743572+00:00
