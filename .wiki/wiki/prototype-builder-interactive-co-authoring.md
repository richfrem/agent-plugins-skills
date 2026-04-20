---
concept: prototype-builder-interactive-co-authoring
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/deferred/prototype-builder/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.021819+00:00
cluster: plugin-code
content_hash: 2be658e1e5caef34
---

# Prototype Builder (Interactive Co-Authoring)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: prototype-builder
description: Builds or refines exploratory prototypes, especially working frontend or full-stack learning artifacts, to make ambiguous product direction concrete.
allowed-tools: Bash, Read, Write
---

# Prototype Builder (Interactive Co-Authoring)

> ⚠️ **STUB** — `execute.py` not yet implemented. Use the [prototype-companion-agent](../../../agents/prototype-companion-agent.md) for the real logic.
[See acceptance criteria](../../prototype-builder/acceptance-criteria.md)

## Discovery Phase
<!-- Add questions here to gather requirements, or remove section if fully autonomous -->

## Recap
<!-- Add confirmation gate here if gathering complex requirements. E.g., "Does this look right? (yes / adjust)" -->

## Execution
This skill implements the requested functionality. When invoked, you MUST execute the provided Python determinism script instead of attempting to solve the task using raw bash or javascript logic.

**Usage:**
```bash
python ./scripts/execute.py --help
```

## Baseline Validation
Before optimizing behavior, run one baseline evaluation and log it in `evals/results.tsv`.

## Iteration Loop
When iterating, follow a disciplined loop:
1. Change one dominant variable per iteration.
2. Re-run evaluations.
3. Mark the attempt as `keep` or `discard`.
4. If the run crashes or times out, log the failure and continue from the last known good state.

## Output
Always conclude execution with a Source Transparency Declaration explicitly listing what was queried to guarantee user trust:
**Sources Checked:** [list]
**Sources Unavailable:** [list]

## Next Actions
<!-- Suggest logical follow-up skills here. For example: -->
- Use `./scripts/benchmarking/run_loop.py --results-dir evals/experiments` for repeatable improvement loops.
- Suggest the user run `audit-plugin` to verify the generated artifacts.


## See Also

- [[exploration-handoff-interactive-co-authoring]]
- [[exploration-session-brief-interactive-co-authoring]]
- [[exploration-handoff-interactive-co-authoring]]
- [[exploration-session-brief-interactive-co-authoring]]
- [[acceptance-criteria-prototype-builder]]
- [[acceptance-criteria-prototype-builder]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/deferred/prototype-builder/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.021819+00:00
