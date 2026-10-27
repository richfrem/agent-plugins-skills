# Acceptance Criteria: authoring-instructions

## Mode: create-hook

**Purpose**: Verify the system generates compliant `hooks/hooks.json` lifecycle interceptors.

## 1. Event Registration
- **[PASSED]**: Appends a new hook trigger listening to `PreToolUse` or `PostToolUse` directly in the plugin's `hooks.json` array.
- **[FAILED]**: Fails to create the JSON syntax correctly or overrides previous hooks instead of appending.

> The sections below were written during consolidation from each mode's constraints; the previous skills pointed at a generic spec-lookup checklist that did not apply.

## Mode: create-rule

- [ ] Content is a passive constraint, not a multi-step procedure (procedures go in a skill).
- [ ] 30–70 lines, hard ceiling 80; frontmatter has `description` and `globs`.
- [ ] The core invariant ("Iron Law") appears in the first 20 lines; MUST/NEVER bounds are concrete.
- [ ] Zero calendar dates, commit SHAs, usernames or absolute machine paths (the grep check in the mode reference prints PASS).
- [ ] An Evaluation Checklist of deterministic questions is present; no cross-plugin script invocations.

## Mode: audit-rule

- [ ] The audit is read-only and never edits a rule file.
- [ ] `audit_rule.py` reports line budget, dates and paths, and the three canonical sections.
- [ ] Exit codes are honoured: 0 clean, 1 compliance errors, 2 invalid input; `--strict` fails on warnings.
- [ ] Procedure-in-rule drift is reported as a finding, not silently rewritten.

## Mode: create-agents-md

- [ ] An existing `AGENTS.md` or `CLAUDE.md` is never overwritten; a unified diff is proposed instead.
- [ ] `AGENTS.md` follows the five-part skeleton of the contract; `CLAUDE.md` is a bridge of 5 lines or fewer.
- [ ] Invariants are stated inline with uppercase modal tokens; detail is linked, not inlined.
- [ ] `audit_agents_md.py --strict` passes on both files; eager payload is 100 lines or fewer.

## Mode: audit-agents-md

- [ ] Tier 1 deterministic checks run: transitive budget, bridge, dates, machine paths, trees and pitfall catalogs, inline invariants.
- [ ] Tier 2 judgment findings are labelled advisory and use the pruning test.
- [ ] Results state PASS, WARN (over 120 lines) or FAIL (over 200 lines) per file.
