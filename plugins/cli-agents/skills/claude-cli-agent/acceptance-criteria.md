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
