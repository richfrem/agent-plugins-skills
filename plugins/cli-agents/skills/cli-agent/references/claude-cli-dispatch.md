# Claude dispatch details

## Contents

- [Selection](#selection)
- [Execution](#execution)
- [Native facilities](#native-facilities)

## Selection

Use the caller's authorized choice. Read `references/claude-models.json` for
catalog defaults; refresh stale catalogs per [catalog maintenance](model-catalog-maintenance.md).
Capability `--tier` chooses a default model; `--effort low|medium|high` controls
Claude reasoning separately. Omitted Claude effort stays omitted.
Do not refresh models or repeat setup merely because implementation has started.

## Execution

```bash
python3 scripts/run_agent.py agents/architect-review.md <input> <output> "Review supplied source." --cli claude --model <approved-model> --effort medium --isolated --require-input
```

The router always wraps input in `---SOURCE---` blocks. With `--isolated` it also appends
the isolation instruction verbatim; without it, add the instruction to the prompt yourself:
> "You are operating as an isolated sub-agent. Do NOT use tools. Do NOT access filesystem. Only use the provided input."

Use `--executable <selected-cli-path>` when PATH resolves the wrong installation.
The router reports executable/version and Python/version before dispatch. An
unsupported version probe is reported as unavailable; it does not select another binary.
Prompt assembly and the leading newline are handled by the router. Avoid shell
substitution of large source files or ad hoc Python launchers. Exit success alone
is insufficient: verify the requested content and record failure evidence without secrets.

## Native facilities

Confirm installed help before using plan permissions, native worktree sessions,
custom agents or background agents. Prefer native facilities only when Claude Code
is the selected runtime. Otherwise delegate portable worktree coordination to the
os-control-worktree skill. Native autonomy does not replace pipeline approval receipts.
