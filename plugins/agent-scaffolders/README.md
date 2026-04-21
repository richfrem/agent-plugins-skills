# Agent Scaffolders Plugin

Interactive scaffolding system for creating and optimising Claude Code plugins, skills,
hooks, sub-agents, commands, GitHub Actions, MCP integrations, and agentic workflows.

## Skills

| Skill | Trigger | What it builds |
|---|---|---|
| `create-skill` | "create a skill", "scaffold a skill", "run evals on a skill" | Full skill directory with SKILL.md, references/, evals/ |
| `create-plugin` | "create a plugin", "build a new plugin" | Complete plugin with plugin.json, skills/, commands/, agents/, hooks/ |
| `create-sub-agent` | "create an agent", "add an agent to my plugin" | Agent .md file with frontmatter, system prompt, permission grants |
| `create-command` | "create a command", "add a slash command" | Slash command .md with frontmatter, argument handling |
| `create-hook` | "create a hook", "add a PreToolUse hook", "validate tool use" | hooks.json entries or skill-scoped hook frontmatter |
| `create-mcp-integration` | "add an MCP", "setup mcp server" | .mcp.json or plugin.json mcpServers block |
| `create-github-action` | "create a github action", "scaffold CI workflow" | GitHub Actions YAML |
| `create-agentic-workflow` | "create a github agent", "convert skill to copilot agent" | GitHub Agentic Workflow files (IDE or CI/CD) |
| `create-docker-skill` | "containerise this skill", "docker skill" | Dockerfile, pre-flight checker, security override |
| `create-azure-agent` | "create an azure agent", "azure ai foundry agent" | Azure AI Foundry agent boilerplate |
| `create-stateful-skill` | "stateful skill", "skill with state management" | L4-pattern skill with epistemic trust, artifact lifecycle, escalation |
| `continuous-skill-optimizer` | "optimise my skill description", "run the eval loop" | Iterative description improvement via eval loop |
| `manage-marketplace` | "create a marketplace", "publish my plugins" | marketplace.json, distribution guidance |

---

## Hook Support (13 events, 3 handler types)

`create-hook` covers all currently documented Claude Code hook lifecycle events:

| Event | Primary Use |
|---|---|
| `PreToolUse` | Approve, deny, or modify tool calls before execution |
| `PostToolUse` | React to successful tool output; inject `additionalContext` |
| `PostToolUseFailure` | Handle failed tool calls; retry logic, alerting |
| `PermissionRequest` | Auto-approve specific permissions so users aren't prompted repeatedly |
| `UserPromptSubmit` | Add context, validate, or block user prompts |
| `Stop` / `SubagentStop` | Completeness check before agent/subagent stops |
| `SubagentStart` | Inject context or enforce policies at subagent spin-up |
| `SessionStart` / `SessionEnd` | Load/save environment state |
| `PreCompact` | Preserve critical context before compaction |
| `Notification` | Logging and reactions to notifications |
| `ConfigChange` | React to dynamic configuration updates |

Handler types: `command` (bash), `prompt` (LLM-driven), `agent` (spawns subagent with Read/Grep/Glob).

Skill-scoped hooks (declared in SKILL.md frontmatter) are also supported for enforcement
scoped to a skill's active lifetime.

---

## Sub-Agent Frontmatter (current spec)

`create-sub-agent` generates agents using the full current frontmatter schema:

```yaml
---
name: my-agent
description: Use this agent when...
model: inherit            # or pinned: claude-sonnet-4-20250514
maxTokens: 4096
color: green
tools: ["Read", "Write"]
permissions:
  allowedTools:
    - "Read"
    - "Write"
  deny:
    - "Read(./.env)"
    - "Read(./secrets/**)"
hooks:
  Stop:
    - matcher: "*"
      type: prompt
      prompt: "Verify task completion before stopping."
---
```

---

## Agentic Workflow Patterns

`create-agentic-workflow` includes a mandatory complexity gate (Phase 0) that asks whether
an agentic approach is warranted, then supports five patterns:

- **Prompt Chaining** — sequential steps, each passing output to the next
- **Routing** — classify input and dispatch to a specialist sub-agent
- **Parallelisation** — multiple agents on independent sections simultaneously
- **Orchestrator-Workers** — central LLM dynamically decomposes tasks (subtasks not known in advance)
- **Evaluator-Optimizer** — one agent generates, another evaluates in a loop

---

## Optimization Architecture

The benchmarking stack in `scripts/benchmarking/` supports:

- `run_eval.py` — trigger evaluation (live routing check), train/test split, repeated runs
- `improve_description.py` — description optimization via selectable backend (`claude` or `copilot`)
- `run_loop.py` — closed-loop iterative optimization with persistent ledger output
- `aggregate_benchmark.py` — statistical analysis (mean, stddev, min, max) across runs

Iteration ledger format: `iteration  train_score  test_score  decision  notes  description`

Loop governance: baseline-first, one-hypothesis-per-iteration, explicit keep/discard, crash logging.

---

## Dependencies

Most scripts use the standard library only. The Azure scaffolder (`scaffold_azure_agent.py`)
requires:

```bash
pip-compile requirements.in
pip install -r requirements.txt
```

See `requirements.in` for the dependency source and `requirements.txt` for the lockfile.

---

## Architecture Notes

- **ADR-001**: No cross-plugin script execution at runtime — use Agent Skill Delegation instead.
- **ADR-002**: Scripts shared across multiple skills live at `./scripts/`;
  skill directories contain file-level symlinks pointing up to the plugin root.
- **ADR-003**: File-level symlinks only — directory-level symlinks are silently dropped by `npx`.
- **ADR-004**: Plugin is fully self-contained — no runtime dependencies on other plugins.

Full ADR records: `ADRs/` at repo root.

---

## Pattern Library

L4 pattern definitions (65+) are referenced from each skill's `references/patterns/` directory
(file-level symlinks to the `agent-scaffolders` L4-pattern-definitions directory).
Key patterns: Progressive Disclosure, Graduated Autonomy, Escalation Taxonomy, Dual-Mode
Bootstrap, Artifact Lifecycle, Persistent Plugin Configuration, Anti-Pattern Vaccination.
