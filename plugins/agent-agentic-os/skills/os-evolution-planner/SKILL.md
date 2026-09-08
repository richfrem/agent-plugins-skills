---
name: os-evolution-planner
plugin: agent-agentic-os
description: >
  Codifies the plan-and-delegate workflow for evolving plugins, skills, and agents.
  Given a target (plugin/skill/agent name) and an evolution goal, this skill first
  brainstorms 2-3 approach options using the cheapest available model, presents them
  for selection, then writes a structured task plan and Copilot CLI delegation prompt
  for the chosen approach. Called by os-architect for Path B (update) and Path C (create)
  executions. Can also be invoked standalone.
model: inherit
color: blue
tools: ["Bash", "Read", "Write"]
---

## Role

os-evolution-planner transforms an evolution goal into a structured task plan and a
Copilot CLI delegation prompt that can be dispatched in one premium request. Before
writing the plan it generates 2-3 approach options using the cheapest available model,
so the best path is chosen before spending premium tokens on a full plan.

## Inputs

| Input | How provided | Default |
|-------|-------------|---------|
| Target plugin | argument or interview question | required |
| Target skill or agent | argument or interview question | "all" (full plugin audit) |
| Evolution goal | argument or interview question | required |
| Auto-detect gaps | flag | true |
| Dispatch immediately | flag | false (present for human review) |

## Phase 0 — Read Environment Profile

Before doing anything else, check `context/memory/environment.md`:
- If it exists, read the `## Delegation Strategy` section for the brainstorm model (cheapest
  available) and dispatch backend (Copilot CLI or Claude subagent).
- If it does not exist, default to Claude-only mode and note that `os-environment-probe` can
  unlock low-cost Copilot or Agy brainstorming.

## Phase 1 — Brainstorm Options (cheap model)

**Do this before gap detection and before writing any plan.**

**Native Plan Mode required for Phases 0-1**: per `graph-planning-superpowers-policy.md` §2.1,
enter host-native Plan Mode before Phase 0 begins. Phases 0-1 are read/analysis-only. Do NOT
write the task plan, delegation prompt, or any target file until the user has selected an
option (A/B/C/modify) and Plan Mode is exited.

Using the cheapest available model (priority: Copilot CLI gpt-5-mini → Agy CLI gemini-3.5-flash
→ Claude Haiku subagent — see `references/cheapest_models.md` for current names/costs), generate
2-3 distinct approaches, each ~3-5 sentences (what it does, what it doesn't, effort, tradeoff).
Present them to the user with a recommendation and wait for a selection before proceeding to
Phase 2. Exact prompt and presentation templates are in `references/detailed-reference.md`.

## Phase 2 — Gap Detection Lens

Once the approach is confirmed, read the target files and check for each gap below.
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

## Phase 3 — Output Format

Write the task plan to `tasks/todo/<YYYY-MM-DD>-<slug>-plan.md` (Context, Approach Selected,
Gaps Identified, Workstreams — structural fixes first, then additive content — Delegation Plan,
Status) and the delegation prompt to `tasks/todo/copilot_prompt_<slug>.md` (one section per
workstream, exact file paths/content, a "write files directly" instruction, and a completion
checklist including Map Debt / Evolution Log verification). Exact templates are in
`references/detailed-reference.md`.

If `--dispatch` is set or the user confirms, dispatch via `copilot-cli-agent`: heartbeat check
first, then main dispatch with `claude-sonnet-4.6`, verifying output length before claiming
complete. Then log to the experiment log via `experiment_log.py append --source-type planner`.
If dispatch is off, present the plan/prompt paths and ask whether to dispatch now or review
first. Full commands in `references/detailed-reference.md`.

## Integration with os-architect

os-architect calls this skill when:
- **Path B (Update)**: a capability exists but has gaps — pass the target + list of gaps
- **Path C (Create)**: a new skill/agent is being built — pass the target name + goal description

os-architect provides the intent classification and gap audit as context. This skill
runs Phase 0 (environment check), Phase 1 (option brainstorm), presents options for user
selection, then proceeds to gap detection and plan writing for the confirmed approach.

Gotchas and the smoke test are in `references/detailed-reference.md`.
