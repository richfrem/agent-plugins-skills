# Acceptance Criteria: authoring-subagents

## Mode: create-sub-agent

**Purpose**: Verify the system generates valid multi-agent routing configurations.

## 1. Frontmatter Configuration
- **[PASSED]**: Frontmatter correctly includes `model: inherit` and custom `color` parameters.
- **[FAILED]**: Frontmatter lacks basic Anthropic syntax routing.

## 2. Few-Shot Triggering
- **[PASSED]**: The description body includes 2-4 explicit XML `<example>` structures to train the router when to call this sub-agent natively (including negative or proactive instructions).
- **[FAILED]**: The sub-agent has a descriptive block but lacks concrete semantic trigger phrases.

## Mode: audit-sub-agent

> Written during consolidation; the retired skill pointed at a generic checklist.

- [ ] The audit is read-only and never edits an agent file.
- [ ] Frontmatter is checked for `name`, `description`, `model`, `color` and `tools`; generic names are flagged.
- [ ] The description carries 2-4 `<example>` trigger blocks.
- [ ] Pointer-wrapper stubs that merely delegate to a skill are reported as errors.
- [ ] The system prompt addresses the agent in second person and lists concrete responsibilities.
- [ ] Exit codes are honoured: 0 clean, 1 structural or metadata errors, 2 invalid input; `--strict` fails on warnings.
