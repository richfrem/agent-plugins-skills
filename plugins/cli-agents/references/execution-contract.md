# CLI Agents: Execution Contract

Non-negotiable behavioral rules for all cli-agents workflows. These rules exist because
the plugin provides the execution layer — drift here cascades to every workflow above it.

---

## Rule 1 — One Backend Per Task

Every task executes against **exactly one backend**. The choice is made before dispatch.

- Do NOT switch CLI automatically if a backend fails.
- Do NOT silently retry on a different backend without explicit user instruction.
- Backend failure → halt, surface the error, log to `references/map-debt.md`.

```
backend selected → task dispatched → success or halt
                                        ↓
                              log failure, surface to caller
```

## Rule 2 — Mandatory Validation Orchestration

Validation agents exist but only produce value when actually invoked. This table is
the trigger spec — skip any row and you've violated the contract.

| Situation | Required agents |
|---|---|
| Any output affecting production code | `output-validator` |
| Output quality uncertain after a single pass | `self-critic` |
| Code review task | primary reviewer → `output-validator` |
| Architecture / high-risk decision | `architect-review` → `red-team-reviewer` → `debate-synthesizer` |
| Two agents produce conflicting output | `debate-synthesizer` |
| Risk level high (security, data, infra) | `red-team-reviewer` (optionally) |

Skipping a required agent when its trigger fires is a contract violation.

## Rule 3 — Security Contract (Isolation)

Isolation policy is global — not per-adapter.

**When `--isolated` is set:**
- Dangerous permission flags are suppressed for all CLIs (`--yolo`, `--dangerously-skip-permissions`)
- Safety footer is appended to all prompts
- Use for all analysis tasks (reviews, audits, output generation)

**When NOT isolated (task dispatch with tool access):**
- Requires explicit user instruction or approval
- Agent must confirm intent before enabling tools

The default in `run_agent.py` is non-isolated for task dispatch; use `--isolated` for
analysis passes. Do not invert this default silently.

## Rule 4 — No Workarounds

If any of the following occur:

- Backend call fails
- Output is empty or clearly below quality threshold
- A workaround was attempted to bypass a constraint or failure

The agent MUST:

1. **Halt** — do not proceed as if successful
2. **Log** — add a row to `references/map-debt.md` (Tier 0 Friction)
3. **Surface** — report the failure explicitly to the caller

Workarounds = Tier 0 Friction. This is a self-evolution event, not a soft warning.

---

## Backend Selection (non-negotiable)

See `references/backend-capabilities.md` for the capability matrix. Agent MUST
select backend based on task type — do not default blindly.
