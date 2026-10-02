# Copilot dispatch details

## Contents

- [Model and budget selection](#model-and-budget-selection)
- [Dispatch modes](#dispatch-modes)
- [Batch outputs and verification](#batch-outputs-and-verification)
- [Native facilities](#native-facilities)

## Model and budget selection

Read `references/copilot-models.json` and `references/cheapest_models.json`
for runtime IDs, capability tiers and costs. Delegate stale-catalog maintenance
to update-cli-models. Use the user's selected model; do not start an additional
review or use another provider without authorization. Copilot identifiers can
differ from direct provider IDs: use the supported catalog/runtime spelling.
Do not assume a heartbeat is free or model access follows from installation.
For paid batches, confirm the applicable account budget/spend ceiling; use a
native cost limit only when the installed CLI supports it.

## Dispatch modes

Analysis suppresses `--yolo` and adds the no-tools instruction:

```bash
python3 scripts/run_agent.py agents/security-auditor.md <input> <output> "Find vulnerabilities in supplied source." --cli copilot --isolated --require-input
```

Tool-enabled implementation requires already-established authorization, bounded
scope and appropriate containment. Use a caller-supplied task prompt with
`/dev/null` as the persona when no analytical persona applies. Omitting
`--isolated` enables the wrapper's task-dispatch permission mode; it is not a
sandbox. Always use named flags, including `--cli copilot` and optional
`--model` or `--tier`; never put a model in the legacy backend argument slot.

The router assembles persona/source/instruction blocks and streams output to
the terminal and output file. `--executable` overrides PATH selection.
`--effort` does not configure Copilot reasoning in this wrapper.
For mandatory source use `--require-input`; missing or empty input fails before dispatch.

## Batch outputs and verification

Plan bounded batches before calling. For multiple generated files, specify exact
paths and delimiters and verify coverage before writing extracted content:

```text
===FILE: relative/path/to/file===
[complete file content]
===ENDFILE===
```

Run foreground. Check exit status, nonempty output, expected file markers and
task-specific content; line counts or echoed text do not establish correctness.
Use a catalog-selected, authorized heartbeat before a major orchestration when
connectivity has not been verified. Record its result in task evidence. Halt on
authentication, quota, timeout or empty-output failure without switching backends.
Record gated critic results as PASS/REVISE/REJECT; only PASS satisfies approval.

## Native facilities

Check installed help before using planning, autopilot, custom agents, subsidiary
agents or cost-limit flags. Native delegation is appropriate only for authorized
independent work. Delegate governed worktree setup to worktree-manager when no
native worktree facility exists. Autopilot and permission flags do not replace
human approval or pipeline receipts.
