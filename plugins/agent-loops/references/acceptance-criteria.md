# Acceptance Criteria: `co-pilot-loop`

This document defines the structural and behavioral expectations for the `co-pilot-loop` skill.

## 1. Trigger Verification
*   The skill must trigger on commands such as `/co-pilot-loop`, `delegate this task to gemini as qa`, and `run cooperative dual agent loop`.
*   The skill must **not** trigger for simple learning tasks or single-agent operations.

## 2. Structural Requirements
*   `SKILL.md` must be placed in `plugins/agent-loops/skills/co-pilot-loop/`.
*   `SKILL.md` description frontmatter must be clear and not exceed 1024 characters.
*   `evals/evals.json` must be populated with at least 2 test cases conforming to the `should_trigger` schema.

## 3. Protocol Alignment
*   The skill instructions must direct the Outer Agent (Claude) to act as the Supervisor/QA role.
*   It must require double-checks on Gemini's specs, plans, and code quality before merging.
*   It must strictly prohibit Gemini (Inner Loop) from executing Git commands.
*   It must detail how Claude uses verification tests to validate Gemini's output.