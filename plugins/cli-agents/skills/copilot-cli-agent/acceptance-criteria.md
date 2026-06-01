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
