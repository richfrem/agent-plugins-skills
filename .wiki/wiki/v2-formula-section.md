---
concept: v2-formula-section
source: plugin-code
source_file: agent-agentic-os/skills/os-eval-runner/v2-formula-section.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.710755+00:00
cluster: skill
content_hash: b20024e6d9342395
---

# V2 Formula Section

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- INSERT IMMEDIATELY BEFORE "# Skill Improvement Evaluator" in skills/os-eval-runner/SKILL.md -->

## Evaluation Formula

**V1 (current baseline):**
```
quality_score = (routing_accuracy × 0.7) + (heuristic_score × 0.3)
```

**V2 (target — implemented in eval_runner.py when components are measurable):**
```
quality_score = (A × 0.5) + (H × 0.2) + (C × 0.2) + (F × 0.1)
```

| Component | Symbol | Measures | Rule |
|:----------|:-------|:---------|:-----|
| Routing Accuracy | A | Correct trigger/no-trigger decisions | Must exceed baseline by ≥ 0.01 to count as KEEP |
| Heuristic | H | Structural / length / keyword signals | Checked via eval_runner.py heuristic_detail |
| Completeness | C | Coverage of required SKILL.md sections | Penalised if any mandatory section is absent |
| F1 | F | Harmonic mean of precision + recall | Prevents score inflation from skewed eval sets |

## Struggle Signal Tiers

| Consecutive DISCARDs | Signal | Orchestrator Action |
|:---------------------|:-------|:--------------------|
| 1–3 | Normal variance | Continue with fresh hypothesis |
| 4 | Stall — hypothesis scope | Enter circuit_break_scope=hypothesis; try second-order mutation |
| 8+ | Stall — skill scope | Escalate to operator; halt loop |

## Domain-Pattern Lookup

Before formulating a hypothesis in Step A, check:
```bash
[ -f "$LAB_PATH/agent-agentic-os/references/domain-patterns/routing-skill.md" ] && \
  echo "Domain pattern available — apply known escape before trying novel hypothesis"
```
Known patterns reduce wasted iterations on already-solved failure types.

## Guardian Hash Gate (SHA256)

Already implemented in `evaluate.py` via `.lock.hashes`. Behavior:
- On every KEEP: SHA256 of SKILL.md written to `.lock.hashes`.
- On every DISCARD: `evaluate.py` reverts via `git checkout -- .` before exit 1.
- Prevents oscillation: if a proposed hash matches a prior DISCARD hash, skip and log.

## Zero-Context Operational Requirements

This skill must be fully self-contained in the lab. Before handing off to the orchestrator:
- `evaluate.py` and `eval_runner.py` must be present at `$SKILL_EVAL_SOURCE/scripts/`
- `plot_eval_progress.py` must be present at the same path
- `evals/evals.json` must use `should_trigger` boolean schema (not `expected_behavior`)
- `copilot_proposer_prompt.md` must be present in `$SKILL_PATH/references/`
- No network calls to the master `agent-plugins-skills` repo are permitted at runtime


## See Also

*(No related concepts found yet)*

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/skills/os-eval-runner/v2-formula-section.md`
- **Indexed:** 2026-04-27T05:21:03.710755+00:00
