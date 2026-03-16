# Agent Scaffolders Plugin

## Purpose
`plugins/agent-scaffolders` generates and upgrades skills, plugins, hooks, and workflows using a pattern-driven architecture.

It now uses a "best of both" optimization model:
- **Karpathy-style loop governance**: baseline-first, one-hypothesis iterations, explicit keep/discard, crash logging, persistent ledger.
- **Existing benchmark rigor**: train/test split, repeated runs, score tracking, timing telemetry, and review artifacts.

## Updated Optimization Architecture

The benchmarking stack in `plugins/agent-scaffolders/scripts/benchmarking/` supports:
- `run_eval.py` for trigger evaluation (live routing check).
- `improve_description.py` for description optimization via selectable backend.
- `run_loop.py` for closed-loop iterative optimization with ledger output.

### Model Backends

- **Evaluation backend**: currently `claude` (for live skill trigger detection).
- **Improvement backend**: `claude` or `copilot`.

This enables **Copilot CLI model-driven self-improvement** (for example GPT-5 family models) without running a self-hosted GPU training stack.

## Pattern Source of Truth

Canonical L4 pattern definitions live in:
- `plugins/agent-skill-open-specifications/L4-pattern-definitions/`

To avoid cross-plugin path drift, each scaffolder skill now has local references:
- `references/hitl-interaction-design.md` (symlink)
- `references/pattern-decision-matrix.md` (symlink)
- `references/patterns/*.md` (symlinks to all L4 pattern definitions)

Skills should reference local paths under their own `references/` directory.

## Directory Structure (High Level)

```text
plugins/agent-scaffolders/
  .claude-plugin/plugin.json
  README.md
  references/
  scripts/
    scaffold.py
    benchmarking/
    eval-viewer/
  skills/
    <12 scaffolder/optimizer skills>/
      # Note: audit-plugin moved to agent-plugin-analyzer
      SKILL.md
      references/
      scripts/
      evals/
  templates/
```

## Notes

- `scripts/scaffold.py` now creates `evals/evals.json` and `evals/results.tsv` by default for new skills.
- `evals/results.tsv` is the persistent experiment ledger:
  `iteration  train_score  test_score  decision  notes  description`
