# Dispatch Strategies

## Contents
- [Principle](#principle) • [Strategy selection](#strategy-selection) • [Task complexity guide](#task-complexity-guide) • [Cheap Q&A pattern](#token-efficiency-cheap-sub-agents-for-qa) • [Fallback](#fallback-behavior) • [Dispatch by environment](#dispatch-reference-by-environment)

## Principle

The conductor (large context, strongest model) should do coordination and synthesis only. Delegate everything else to the cheapest runtime and model capable of the task.

**Model information is not kept here.** Runtime, model, effort and cost choices, the model catalog, and batching rules belong to the `cli-agent` skill in `agent-orchestration` (its model catalog and the dispatch guides per backend). Name no model IDs or prices in this plugin.

## Strategy selection

The expert chooses a strategy once, at session setup (Block 0 of the workflow):

| Strategy | When | How work is delegated |
|---|---|---|
| `cli-agent` (copilot, agy, claude, codex or local backends) | An external CLI is installed and authorized | Through the `cli-agent` skill; it picks the backend, model and effort and owns the batching and cost rules for that backend |
| `claude-subagents` | Claude Code only, no external CLI | The in-session Agent tool, cheap model class for simple tasks, session model for synthesis |
| `direct` | No sub-agent tooling, or everything runs in session | The current model does all of it |

Notes that outlive any catalog: per-request billing backends reward one dense request over several small ones, so batch related work before calling a premium model (details in the `cli-agent` dispatch guide for that backend). `dispatch.py` (this skill's `scripts/`) only handles the `claude`, `copilot` and `gh-copilot` backends and requires its authorization arguments (`--db-path`, `--approval-id`, `--envelope-json`, `--hmac-key-path`); `agy` goes through the `cli-agent` skill. Record the resolved strategy in the dashboard as `**Dispatch Strategy:**`.

## Task complexity guide

| Task type | Complexity | Dispatch tier |
|---|---|---|
| Single-pass document capture (requirements, stories) | Simple | Cheap |
| Business rule audit against the BRD | Simple | Cheap |
| Filling a template from provided input | Simple | Cheap |
| Re-entry scope drafting | Simple | Cheap |
| Prototype component (scoped, self-contained) | Complex | Premium |
| Handoff synthesis across several captures | Complex | Premium |
| Discovery planning session (interactive) | In-session | Conductor directly |

## Token efficiency: cheap sub-agents for Q&A

Even clarifying questions to the expert can be delegated, reserving the conductor's context for decisions and synthesis.

1. The conductor identifies a clarification need (missing information, ambiguous input).
2. It drafts the exact questions, 3 to 5 numbered.
3. A cheap worker presents them (CLI or lightweight session), collects and structures the answers, and writes `exploration/captures/clarifications-[topic].md`.
4. The conductor reads that file and continues.

**Apply to**: filling gaps in a brief, clarifying ambiguous business rules during BRD review, scoping questions during prototype observation, any Q&A expressible as numbered questions plus structured answers.
**Do not apply to**: the first framing conversation, the Discovery Planning Session (interactive, nuanced), or phase completion gates (need the conductor's judgment).

## Fallback behavior

If the chosen strategy becomes unavailable mid-session: fall back silently to `direct`, tell the expert ("The [strategy] strategy isn't available. I'll handle the rest directly."), and record `direct (fallback)` in the dashboard.

## Dispatch reference by environment

### In-session sub-agents (`claude-subagents`)
Use the Agent tool directly. Give simple tasks a cheap model class and let complex ones inherit the session model; the `cli-agent` skill lists current choices.

- Simple capture: "Read `exploration/session-brief.md`. Mode: problem-framing. Extract the problem statement, user groups, goals and scope hypotheses. Write `exploration/captures/problem-framing.md`. Mark anything not stated as `[NEEDS HUMAN INPUT]`."
- Q&A clarification: "Read `exploration/captures/brd-draft.md`. Find every `[NEEDS HUMAN INPUT]`. Present the 3 most important as plain questions, collect answers, write `exploration/captures/clarifications-brd.md`."
- Business rule audit: "Read `brd-draft.md` and `prototype-notes.md`. For each rule check confirm, contradict or uncertain. Write `exploration/captures/business-rule-audit.md`. Flag CONTRADICTED and UNCERTAIN rules."
- Handoff synthesis (complex, session model): "Read all files in `exploration/captures/`. Synthesise `exploration/handoffs/handoff-package.md` following the handoff-preparer template. Cite source files for every major claim."

### CLI backends (`cli-agent`)
Dispatch the same prompts through the `cli-agent` skill, using the prompt templates in `capturing-business-requirements/assets/prompts/` and `handing-off-to-engineering/assets/prompts/` as the persona. Pack all captures for the synthesis into one dense request. If you use `dispatch.py` directly, supply its authorization arguments:

```bash
python3 scripts/dispatch.py --agent requirements-doc-agent \
  --context exploration/session-brief.md \
  --instruction "Mode: problem-framing. Capture the problem statement, user groups, goals." \
  --output exploration/captures/problem-framing.md \
  --db-path <active_session.sqlite> --approval-id <id> --envelope-json <envelope> --hmac-key-path <key>
```

### `direct`
Run all tasks in the current session. To reduce context carry-forward: summarise each capture pass in 3 bullets before moving on, use `/compact` after Phase 1 and again after Phase 3, and pass file paths to the next phase instead of contents.
