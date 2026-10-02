# Acceptance Criteria: create-sub-agent

**Purpose**: Verify the system generates valid multi-agent routing configurations.

## 1. Frontmatter Configuration
- **[PASSED]**: Frontmatter correctly includes `model: inherit` and custom `color` parameters.
- **[FAILED]**: Frontmatter lacks basic Anthropic syntax routing.

## 2. Few-Shot Triggering
- **[PASSED]**: The description body includes 2-4 explicit XML `<example>` structures to train the router when to call this sub-agent natively (including negative or proactive instructions).
- **[FAILED]**: The sub-agent has a descriptive block but lacks concrete semantic trigger phrases.
