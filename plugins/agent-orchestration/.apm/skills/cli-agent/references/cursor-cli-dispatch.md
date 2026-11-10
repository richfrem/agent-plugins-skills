# Cursor CLI dispatch details

## Contents

- [Selection and authentication](#selection-and-authentication)
- [Execution and invocation patterns](#execution-and-invocation-patterns)
- [Cloud agents and worker loops](#cloud-agents-and-worker-loops)
- [Runtime boundaries and isolation](#runtime-boundaries-and-isolation)

## Selection and authentication

The Cursor Agent CLI is installed as `agent` (and symlinked as `cursor-agent`).

Authentication is tied directly to the Cursor account tier:
- **Free / Hobby Tier ($0/mo)**: Basic agent requests and composer queries; limited access to first-party/standard models.
- **Pro / Premium Tier ($20–$30/mo)**: Frontier models (Claude 3.5/3.7, GPT-4o, o-series, Grok-2), cloud agents, and automation loops.
- **Enterprise / Super / Ultra**: High-concurrency agent pools and self-hosted worker pooling.

Verify authentication non-destructively:
```bash
agent status
# or
agent whoami
```
When unauthenticated, the CLI outputs `Not logged in` and exits 0. To authenticate, execute `agent login` (or export `CURSOR_API_KEY=<token>`). In headless environments, set `NO_OPEN_BROWSER=1` during login or pass `--api-key <key>`. Do not print API keys or credentials in logs or health probes.

## Execution and invocation patterns

```bash
# Non-interactive analysis/review dispatch
agent -p "Review supplied source code for security vulnerabilities." --output-format text

# Structured JSON output for orchestrator consumption
agent -p "Analyze AST changes" --output-format json

# Explicit model selection (parameterized bracket overrides supported)
agent -p "Generate patch" --model 'claude-opus-4-8[context=1m,effort=high]'
# or Grok models when subscribed:
agent -p "Analyze telemetry" --model grok-2

# Plan-only mode (read-only, no tool or edit side-effects)
agent -p "Propose refactoring plan" --mode plan
```

Key CLI flags for automated agent runners:
- `-p`, `--print`: Print responses to console (for scripts / non-interactive pipelines). Accesses shell and file tools unless restricted.
- `--output-format text | json | stream-json`: Structured parsing format.
- `--mode plan | ask`: Read-only analysis modes (`plan` generates implementation plan without edits; `ask` provides conversational answers).
- `--workspace <path-or-name>`: Root directory for the target project.
- `-w`, `--worktree [name]`: Start in an isolated git worktree at `~/.cursor/worktrees/<repo>/<name>`.
- `--trust`: Trust workspace without interactive security prompts.

## Cloud agents and worker loops

Cursor supports background cloud agent execution and self-hosted worker loops:

- **Self-Hosted Worker (`agent worker`)**:
  Connects to Cursor Cloud and executes remote agent tool calls on the local machine:
  ```bash
  agent worker
  ```
  Without `--pool`, it operates as a personal My Machines worker (available on individual plans). With `--pool`, it joins a team self-hosted pool (requires Enterprise plan + service account API key).
- **Background Persistence (`agent persist`)**:
  Starts or manages an agent session that survives terminal disconnects, suitable for long-running batch migrations or architectural audits.

## Runtime boundaries and isolation

- **Unauthenticated Fail-Closed**: When `agent status` reports `Not logged in`, dispatchers MUST halt and surface authentication requirements rather than failing silently or hanging on interactive browser prompts.
- **Isolation wrapping**: Wrap input in `---SOURCE---` blocks. When operating in an isolated sub-agent context, prepend the isolation instruction:
  > "You are operating as an isolated sub-agent. Do NOT use tools. Do NOT access filesystem. Only use the provided input."
- **Worktree containment**: When write operations are authorized, prefer `-w, --worktree` to prevent dirtying the main working tree.
