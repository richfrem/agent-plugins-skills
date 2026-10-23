# Acceptance Criteria: CLI Agent

Unified acceptance criteria across CLI coding agents and local inference runtimes.

## Contents

- [Universal Dispatch & Isolation](#universal-dispatch--isolation)
- [Claude CLI Backend](#claude-cli-backend)
- [Copilot CLI Backend](#copilot-cli-backend)
- [Codex & Antigravity Backends](#codex--antigravity-backends)
- [Local Llama Backend](#local-llama-backend)
- [Catalog & Setup Lifecycle](#catalog--setup-lifecycle)

## Universal Dispatch & Isolation

- [ ] Every isolated dispatch prompt enforces tool and filesystem containment:
  > "You are operating as an isolated sub-agent. Do NOT use tools. Do NOT access filesystem. Only use the provided input."
- [ ] Large inputs are passed via file redirection or stdin, never loaded into primary agent memory context.
- [ ] Output is written to a designated output file; empty or missing output fails the review.
- [ ] Reviews are gated through `record-critic-review PASS|REVISE|REJECT`; only PASS authorizes progression.
- [ ] Structured reviews provide severity-stratified findings (`CRITICAL`, `MODERATE`, `MINOR`).
- [ ] Single backend per task: fail-closed without silent backend switching.
- [ ] All auxiliary scripts are Python (.py) only — no untracked shell scripts.
- [ ] No cross-plugin relative path dependencies.

## Claude CLI Backend

- [ ] Input files are piped or passed via file argument without blowing context limits.
- [ ] `--dangerously-skip-permissions` is never applied automatically under `--isolated`.
- [ ] Files larger than 5MB are chunked semantically via Python, never forced through a single CLI pipe.
- [ ] Auth failures halt immediately with instructions to run `claude login`.

## Copilot CLI Backend

- [ ] Smoke test (`copilot -p "Reply with exactly: COPILOT_CLI_OK"`) passes before executing multi-turn analysis.
- [ ] Non-isolated flags (`--allow-all-tools`, `--allow-all-paths`) require explicit human confirmation.
- [ ] Batch files use standard `===FILE:` boundary formatting.

## Codex & Antigravity Backends

- [ ] Codex dispatches pass prompt via stdin and do not rely on `--effort` flags.
- [ ] Antigravity commands respect `--print-timeout` limits and tier-derived model selection.
- [ ] Model listings (`agy models`) report status without dispatching unauthorized tasks.

## Local Llama Backend

- [ ] Mode B latency meets the sub-5s response threshold on localhost:8089.
- [ ] Port availability and `/health` probe are verified prior to batch dispatch.
- [ ] Prompt budget stays under 2,000 tokens with bounded `max_tokens`.
- [ ] Server errors or port conflicts halt immediately with instructions to run `scripts/run_server.py`.

## Catalog & Setup Lifecycle

- [ ] Catalog updates via `sync_cheapest_models.py` preserve schema version 2 and mark deprecated models unavailable rather than deleting them.
- [ ] Project setup writes `context/agent-capability-profile.json` with user confirmation before modifying configs.
- [ ] `environment.md` serves as a human-readable summary, not a competing preference store.
