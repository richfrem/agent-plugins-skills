# Optional skill language review

## Contents

- [Dispatch contract](#dispatch-contract)
- [Rubric](#rubric)
- [Result contract](#result-contract)
- [Batching and verification](#batching-and-verification)

## Dispatch contract

Review only when requested or authorized for the task. Supply the skill entry point
and relevant direct reference content to the existing CLI dispatcher with an explicit
runtime, model and effort. Require nonempty input, an isolated read-only review and
no filesystem/tool access. Use the CLI-agent skill's bundled dispatcher; do not embed
cross-plugin imports or ad hoc launchers in the Python auditor.

## Rubric

- Does the description clearly express capability and trigger scope?
- Can a partial preview reveal the starting action, constraints and resource routes?
- Is the language concise, specific and consistent? Flag repeated instructions,
  unnecessary basics, vague wording and too many equivalent options.
- Are examples meaningful and verification steps observable?
- Flag unnecessary change history, incident retellings, migration narratives and
  conversation-specific context. Preserve rationale needed to operate correctly.
- Shorter text is not automatically better. Identify missing constraints, commands,
  context or failure handling before recommending compression.

## Result contract

Return JSON with status (not_requested, ran, failed), runtime, model, effort,
input_hash, contract_version, exit_code, report_path and findings. Each finding has
evidence path/line/quote, issue, proposed_edit, preservation_risk and confidence.
The proposed edit is a suggestion, not deletion authorization.

Only use ran for a successful nonempty report matching this contract. Failed dispatch
or malformed output is failed with evidence. Keep this result outside deterministic
findings; it never changes the structural passed flag or process exit code.

## Batching and verification

One skill is a review unit. Group at most five units per plugin batch with shared
references supplied once; record a result/failure for every unit. Prioritize changed
or structurally flagged skills. Reuse only an identical input hash, contract/rubric
version and route. Record unchanged/not requested status rather than silently skipping.

Evaluate at least these cases: concise complete skill (preserve it), verbose skill
with repeated basics/history (propose bounded compression), and short incomplete skill
(flag missing behavior). Use observable preservation criteria. Record actual model
results separately; a schema test alone does not prove language-review quality.
