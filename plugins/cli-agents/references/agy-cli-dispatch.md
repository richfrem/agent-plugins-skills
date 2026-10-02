# Agy dispatch details

## Contents

- [Models and effort](#models-and-effort)
- [Dispatch and timeout](#dispatch-and-timeout)
- [Native facilities and failures](#native-facilities-and-failures)

## Models and effort

Read `references/agy-models.json` and `references/cheapest_models.json` for
available runtime identifiers and defaults. Delegate stale-catalog maintenance
to update-cli-models; do not substitute direct Claude/API identifiers for Agy aliases.
Use `agy models` only when availability needs verification; listing models does
not authorize a model call. Select a proportionate catalog tier unless the user
already selected the model. Avoid duplicated price tables in runtime instructions.

The wrapper accepts `--effort low|medium|high`. For Agy only, omitted effort derives
from `--tier` (default low), including when a model is explicit. Pass effort
explicitly when the caller specified it; the raw CLI may support additional levels
that the wrapper does not expose.

## Dispatch and timeout

```bash
python3 scripts/run_agent.py agents/architect-review.md <input> <output> "Review supplied source." --cli agy --model <approved-model> --effort medium --print-timeout 15m0s --isolated --require-input
```

Choose a print wait ceiling appropriate to the authorized task. Check `agy --help`
for the installed CLI's default; do not assume a fixed timeout across releases.
The router assembles a prompt file, streams output to the terminal and output file,
and suppresses permission-bypass flags in isolated mode. Use `--executable` when
PATH points to the wrong installation. A version probe may be unavailable.
Avoid shell expansion of large source files. Run foreground and verify exit status,
nonempty output and acceptance criteria before treating the response as usable.

## Native facilities and failures

Check installed help for `--mode plan`, custom agents and `--sandbox` before using
them. Delegate governed worktree setup to worktree-manager when no native worktree
facility is available. Never equate permission bypass with sandboxing or approval.
On authentication, quota, timeout or empty-output failure, halt and surface the exact
failure; do not change backends or restart a running model without authorization.
A heartbeat is a model call: run one only when authorized and needed for connectivity.
