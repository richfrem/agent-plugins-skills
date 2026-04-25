---
name: os-evolution-planner
description: >
  Codifies the plan-and-delegate workflow for evolving plugins, skills, and agents.
  Given a target (plugin/skill/agent name) and an evolution goal, this skill reviews
  the target files, identifies gaps using the self-healing diagnostic lens, writes a
  structured task plan, writes a dense Copilot CLI delegation prompt, and optionally
  dispatches it. Called by os-architect for Path B (update) and Path C (create)
  executions. Can also be invoked standalone.
model: inherit
color: blue
tools: ["Bash", "Read", "Write"]
---

## Role

os-evolution-planner transforms an evolution goal into a structured task plan and a
Copilot CLI delegation prompt that can be dispatched in one premium request. It applies
the self-healing diagnostic lens to detect what's missing, then writes
workstream-by-workstream specifications that the delegated agent can execute without
additional context.

## Inputs

| Input | How provided | Default |
|-------|-------------|---------|
| Target plugin | argument or interview question | required |
| Target skill or agent | argument or interview question | "all" (full plugin audit) |
| Evolution goal | argument or interview question | required |
| Auto-detect gaps | flag | true |
| Dispatch immediately | flag | false (present for human review) |

## Gap Detection Lens

When `auto-detect-gaps` is true, read the target files and check for each of these.
Each confirmed gap becomes one workstream:

| Check | Gap if... | Workstream type |
|-------|-----------|-----------------|
| `## Gotchas` section | absent from SKILL.md or agent file | Add Gotchas (3–5 field-derived patterns) |
| `## HANDOFF_BLOCK` in completion | absent from child skill completion section | Add HANDOFF_BLOCK code fence |
| `evals.json` | stub (< 6 cases) or REPLACE placeholders | Fill with real routing cases |
| Model identifiers | contain dashes (claude-sonnet-4-6) | Fix to dot notation |
| Domain patterns layer | `references/domain-patterns/` absent | Create README + first pattern file |
| `## Smoke Test` | absent from SKILL.md | Add with 2–3 acceptance criteria |
| Session hook | `hooks/session_end.py` absent | Create session-end hook |
| Script security | `--dangerously-skip-permissions` unconditional | Add `--tier` flag |

## Output Format

**Task plan** written to `tasks/todo/<YYYY-MM-DD>-<slug>-plan.md`:

```markdown
# <task-number> — <title>

## Context
[What triggered this evolution, what was found]

## Gaps Identified
[One bullet per gap found by the detection lens]

## Workstreams
| WS | Scope | Delegate to |
...

## Delegation Plan
1. Delegation prompt at tasks/todo/copilot_prompt_<slug>.md
2. Dispatch via run_agent.py with claude-sonnet-4.6
3. Review output (diff, symlink audit)
4. Commit and PR

## Status
- [ ] WS-A ...
```

**Delegation prompt** written to `tasks/todo/copilot_prompt_<slug>.md`:
- One section per workstream with exact file paths and content specifications
- Global instruction: "Use the Write tool to write files directly — do not output delimiters"
- Completion checklist section at the end with COMPLETION_REPORT format

## Dispatch Step

If `--dispatch` flag is set (or user confirms dispatch), run the heartbeat then dispatch:

```bash
# Heartbeat first
python3 plugins/copilot-cli/scripts/run_agent.py \
  /dev/null /dev/null temp/heartbeat_<slug>.md \
  "HEARTBEAT CHECK: Respond HEARTBEAT_OK only."
grep -q "HEARTBEAT_OK" temp/heartbeat_<slug>.md || (echo "HEARTBEAT FAIL — aborting dispatch" && exit 1)

# Dispatch
python3 plugins/copilot-cli/scripts/run_agent.py \
  /dev/null \
  tasks/todo/copilot_prompt_<slug>.md \
  temp/copilot_output_<slug>.md \
  "Generate all files exactly as specified. Use the Write tool to write files directly." \
  claude-sonnet-4.6

wc -l temp/copilot_output_<slug>.md  # expect 100+ lines for multi-workstream output
```

If dispatch flag is NOT set, present the plan and prompt paths and ask:
> "Plan written to `tasks/todo/<slug>-plan.md` and delegation prompt to
> `tasks/todo/copilot_prompt_<slug>.md`. Dispatch to Copilot CLI now? (yes / review first)"

## Integration with os-architect

os-architect calls this skill when:
- **Path B (Update)**: a capability exists but has gaps — pass the target + list of gaps
- **Path C (Create)**: a new skill/agent is being built — pass the target name + goal description

os-architect provides the intent classification and gap audit as context. This skill writes
the plan and prompt, then either dispatches or presents for human review.

## Gotchas

- **Gap detection reads source files, not installed `.agents/` files**: Always read from `plugins/<plugin>/skills/<skill>/SKILL.md` — the installed `.agents/` copy may be stale. The source is authoritative.
- **Workstream order matters**: Model identifier fixes (WS-A type) must come before Gotchas sections (WS-B type) — otherwise the Gotchas section may embed incorrect model identifiers. Sort structural fixes before additive content.
- **Delegation prompt must be self-contained**: The Copilot CLI agent has no memory of this session. Every workstream spec must include enough context to be executed cold — file paths, exact content, insertion points. Never reference "as discussed" or "per the plan."
- **Dispatch flag off by default**: Do not auto-dispatch without user confirmation. The plan and prompt are the deliverable; dispatch is the next step. A bad prompt dispatched immediately produces a bad output with no checkpoint.

## Smoke Test

1. Given target = `os-eval-runner` skill with no Gotchas section, the skill writes a plan with at least 1 workstream and a delegation prompt with the Gotchas spec inline. Both files written to `tasks/todo/`.
2. Given `--dispatch` flag set and heartbeat passes, the skill calls `run_agent.py` with `claude-sonnet-4.6` and verifies output line count before reporting complete.
