# CLI backend capabilities

## Contents

- [Selection](#selection)
- [Router behavior](#router-behavior)
- [Native facilities](#native-facilities)

## Selection

Reuse the caller's authorized runtime, model and effort. When selection is open,
match installed access, task requirements and budget to the bundled catalogs.
A model name does not establish CLI capabilities or authorization. Verify missing
capabilities through installed help; delegate stale model catalogs to update-cli-models.
Do not refresh provider setup or start another review during implementation merely
because a different model might be available. No silent backend fallback.

## Router behavior

| Backend | Invocation | Prompt transport | Isolated-mode behavior |
|---|---|---|---|
| Claude | `claude --model ... -p ...` | Assembled prompt argument | Suppresses permission bypass; adds no-tools instructions |
| Copilot | `copilot --model ... -p @...` | Prompt file (PowerShell on Windows) | Suppresses `--yolo`; adds no-tools instructions |
| Agy | `agy --model ... -p @...` | Prompt file | Suppresses permission bypass; adds no-tools instructions |
| Codex | `codex exec --model ... -` | Stdin | Adds no-tools instructions; native sandbox policy remains separate |
| Local llama | HTTP chat completion | Request body | Text-only bridge; no CLI tool dispatch |
| Legacy Gemini | Installed Gemini CLI or configured npx route | Assembled prompt argument | Suppresses `--yolo`; adds no-tools instructions |

Prompt instructions and permission-flag suppression are not an OS sandbox or
proof that a backend cannot use tools. Verify native restrictions for the selected
runtime when containment is required. Non-isolated tool access needs authorization.
The router supports explicit effort for Claude and Agy; other backends require
separately verified native configuration. Capability tiers choose default models.

## Native facilities

Inspect the installed binary's help before relying on planning modes, worktree
creation, custom agents, background tasks, delegation, sandbox or cost-limit flags.
Use native facilities only when that CLI is the selected runtime. Host collaboration
tools are distinct from CLI features; they do not transfer through model selection.
If a native facility is unavailable, delegate governed coordination to the appropriate
worktree/orchestration skill rather than importing another plugin's runtime code.
Preserve control-plane approval and receipt requirements for every selected facility.
