# Codex dispatch details

## Contents

- [Selection and authentication](#selection-and-authentication)
- [Execution](#execution)
- [Runtime boundaries](#runtime-boundaries)

## Selection and authentication

Read `references/codex-models.json` for supported catalog identifiers and tiers;
delegate stale-catalog maintenance to update-cli-models. Use the user's selected
model, or a proportionate `--tier` when no model was supplied. Do not hardcode an
old model as the universal default or infer support for every OpenAI endpoint.
Authenticate through the method supported by the installed Codex configuration.
Never print API keys, credentials or raw authentication output in a health check.

## Execution

```bash
python3 scripts/run_agent.py agents/refactor-expert.md <input> <output> "Analyze supplied code." --cli codex --isolated --require-input
```

The router sends the assembled prompt to `codex exec` through stdin, avoiding
large shell arguments. `--model` overrides tier selection. The router's `--effort`
option does not configure Codex reasoning; use a verified native configuration
when a task requires that setting. `--executable` selects a particular installation.
For supplied capability preferences, use `--profile <caller-profile-path>`; profile
availability is not authorization to dispatch or change backends.

## Runtime boundaries

Check `codex --help` and `codex exec --help` for installed sandbox, approval,
review and session facilities. A host's native delegation tools are distinct
from the Codex binary. Do not infer plan, worktree or subagent support from a
model name. Delegate portable worktree coordination to worktree-manager when needed.
`--isolated` adds task restrictions; it is not an OS sandbox. Preserve native
sandbox/approval controls for tool-enabled work. Permission-bypass execution
requires explicit authorization and suitable external containment.
Check exit status and meaningful output; report authentication, quota or execution
failures without silently switching providers or claiming a successful review.
